import random
import boolean

from clue import Clue


class ClueAgent:
    """A Clue player with random decision making"""

    __intelligent__ = False

    def __init__(self, agent_number):
        self.number = agent_number
        self.cards = []
        self.known_people = None
        self.known_rooms = None
        self.known_weapons = None

    def __str__(self):
        return f"Player {self.number}: {self.known_rooms + self.known_people + self.known_weapons}"

    def dealt(self, cards):
        """Receive starting cards and add them to known cards"""

        self.cards = cards
        self.known_people = set(x for x in cards if x in Clue.people)
        self.known_rooms = set(x for x in cards if x in Clue.rooms)
        self.known_weapons = set(x for x in cards if x in Clue.weapons)

    def receive(self, reply):
        """Recieve a single card and add it to known cards"""

        card = reply["card"]

        if card in Clue.people:
            self.known_people.add(card)
        elif card in Clue.rooms:
            self.known_rooms.add(card)
        elif card in Clue.weapons:
            self.known_weapons.add(card)

    def guess(self):
        """Make a random guess from unknown cards"""

        person = random.choice(list(set(Clue.people) - self.known_people))
        room = random.choice(list(set(Clue.rooms) - self.known_rooms))
        weapon = random.choice(list(set(Clue.weapons) - self.known_weapons))
        return ([person, room, weapon], self.number)

    def reply(self, guess):
        """Respond to another player's guess"""

        # Randomly select a card from ones that match the guess
        reply_options = [x for x in guess[0] if x in self.cards]
        try:
            return {"card": random.choice(reply_options), "player": self.number}
        except IndexError:
            return None


class ClueIntelligentAgent(ClueAgent):
    """A Clue player that tries to make deductions based on other player's guesses"""

    __intelligent__ = True

    def __init__(self, agent_number, num_players):
        super().__init__(agent_number)
        self.__bl = boolean.BooleanAlgebra()
        self.knowledge = [
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.people]),
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.rooms]),
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.weapons]),
        ]
        self.hands = []
        self.hands_knowledge = []
        for _ in range(num_players):
            self.hands.append(set())
            self.hands_knowledge.append([])

    def dealt(self, cards):
        super().dealt(cards)

        self.hands[self.number] = set(cards)

        # Add dealt cards to knowledge
        for card in cards:
            self.knowledge.append(self.__bl.NOT(self.__bl.Symbol(card)))

            # Other players do not have these cards
            for i, hand in enumerate(self.hands_knowledge):
                if i != self.number:
                    hand.append(self.__bl.NOT(self.__bl.Symbol(card)))

    def receive(self, reply):
        super().receive(reply)
        # Add card to knowledge
        self.knowledge.append(self.__bl.NOT(self.__bl.Symbol(reply["card"])))

        # Add card to other player's hand
        self.hands[reply["player"]].add(reply["card"])
        self.hands_knowledge[reply["player"]].append(self.__bl.Symbol(reply["card"]))

        # Other players do not have this card
        for i, hand in enumerate(self.hands_knowledge):
            if i not in (self.number, reply["player"]):
                hand.append(self.__bl.NOT(self.__bl.Symbol(reply["card"])))

    def guess(self):
        # Simplify and draw conclusions from knowledge before guessing
        self.__update_knowledge()
        self.__update_hand_knowledge()

        return super().guess()

    def inform(self, response):
        """Receives information about other players' guesses and who replied to them"""

        # Gets knowledge about all hands except the responder's
        other_hands = [
            x
            for i, hand in enumerate(self.hands)
            for x in hand
            if i != response["responder"] and x != "Blank"
        ]
        # Filters out cards that are known to be in other players' hands and
        # therefore could not have been the card that the responder showed
        symbols = [
            self.__bl.Symbol(x) for x in response["guess"] if x not in other_hands
        ]
        # Add the guess to knowledge
        if len(symbols) > 0:
            if len(symbols) > 1:
                new_knowledge = self.__bl.NOT(self.__bl.AND(*symbols))
            elif len(symbols) == 1:
                new_knowledge = self.__bl.NOT(symbols[0])

            self.knowledge.append(new_knowledge)

            # Add the guess to knowledge about the players' hands
            responder = response["responder"]
            guesser = response["guesser"]

            if responder != self.number:
                if len(symbols) > 1:
                    new_knowledge = self.__bl.OR(*symbols)
                elif len(symbols) == 1:
                    new_knowledge = symbols[0]
                self.hands_knowledge[responder].append(new_knowledge)

            if guesser != self.number:
                if len(symbols) > 1:
                    new_knowledge = self.__bl.NOT(self.__bl.AND(*symbols))
                elif len(symbols) == 1:
                    new_knowledge = self.__bl.NOT(symbols[0])
                self.hands_knowledge[guesser].append(new_knowledge)

    def __update_knowledge(self):
        # Simplify the logical expression
        knowledge = self.__bl.AND(*self.knowledge).simplify()
        self.knowledge = list(knowledge.args)

        # Extract terms that are known to be false and update the appropriate field
        literals = [
            str(x)[1:] for x in knowledge.args if isinstance(x, boolean.boolean.NOT)
        ]
        for literal in literals:
            if literal in Clue.people:
                self.known_people.add(literal)
            elif literal in Clue.rooms:
                self.known_rooms.add(literal)
            elif literal in Clue.weapons:
                self.known_weapons.add(literal)

    def __update_hand_knowledge(self):
        for i, hand in enumerate(self.hands_knowledge):
            if i != self.number and len(hand) > 1:
                new_hand = self.__bl.AND(*hand).simplify()
                self.hands_knowledge[i] = list(new_hand.args)

                # Get symbols known to be true and add them to the player's hand
                known = [
                    str(x)
                    for x in new_hand.args
                    if isinstance(x, boolean.boolean.Symbol)
                ]

                for card in known:
                    if card not in self.hands[i]:
                        self.hands[i].add(card)


class ClueStrategicAgent(ClueIntelligentAgent):
    """A Clue player that tries makes strategic guesses and replies"""

    def __init__(self, agent_number, num_players):
        super().__init__(agent_number, num_players)
        self.shown = []
        for _ in range(num_players):
            self.shown.append(set())

    def reply(self, guess):
        # Attempt to minimize exposure of its hand by replying with already shown cards if possible

        # Reorder the hands to have cards previously shown to the guesser at the front so that it
        # will attempt to show the guesser a card it has already seen
        shown = self.shown[guess[1] :] + self.shown[: guess[1]]
        card = None

        for person in shown:
            if person:
                card = random.choice(person)
                break
        else:
            # If none of the guessed cards have previously been shown, pick a random card to reveal
            options = [x for x in guess[0] if x in self.cards]
            if options:
                card = random.choice(options)

        if card:
            return {"card": card, "player": self.number}
        return None
