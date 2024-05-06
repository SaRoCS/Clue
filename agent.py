import random
import boolean

from clue import Clue

# from logic import *


class ClueAgent:
    """A Clue player with random decision making"""

    __intelligent__ = False

    def __init__(self, agent_number):
        self.number = agent_number
        self.cards = None
        self.known_people = None
        self.known_rooms = None
        self.known_weapons = None

    def __str__(self):
        return f"Player {self.number}: {self.known_rooms + self.known_people + self.known_weapons}"

    def dealt(self, cards):
        """Receive starting cards and add them to known cards"""

        self.cards = cards
        self.known_people = [x for x in cards if x in Clue.people]
        self.known_rooms = [x for x in cards if x in Clue.rooms]
        self.known_weapons = [x for x in cards if x in Clue.weapons]

    def receive(self, card):
        """Recieve a single card and add it to known cards"""

        if card in Clue.people and card not in self.known_people:
            self.known_people.append(card)
        elif card in Clue.rooms and card not in self.known_rooms:
            self.known_rooms.append(card)
        elif card in Clue.weapons and card not in self.known_weapons:
            self.known_weapons.append(card)

    def guess(self):
        """Make a random guess from unknown cards"""

        person = random.choice(list(set(Clue.people) - set(self.known_people)))
        room = random.choice(list(set(Clue.rooms) - set(self.known_rooms)))
        weapon = random.choice(list(set(Clue.weapons) - set(self.known_weapons)))
        return [person, room, weapon]

    def reply(self, guess):
        """Respond to another player's guess"""

        # Randomly select a card from ones that match the guess
        reply_options = [x for x in guess if x in self.cards]
        try:
            return random.choice(reply_options)
        except IndexError:
            return None


class ClueIntelligentAgent(ClueAgent):
    """A Clue player that tries to make deductions based on other player's guesses"""

    __intelligent__ = True

    def __init__(self, agent_number):
        super().__init__(agent_number)
        self.__bl = boolean.BooleanAlgebra()
        self.knowledge = self.__bl.AND(
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.people]),
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.rooms]),
            self.__bl.OR(*[self.__bl.Symbol(x) for x in Clue.weapons]),
        )

    def dealt(self, cards):
        super().dealt(cards)
        # Add dealt cards to knowledge
        for card in cards:
            self.knowledge = self.__bl.AND(
                self.knowledge, self.__bl.NOT(self.__bl.Symbol(card))
            )

    def receive(self, card):
        super().receive(card)
        # Add card to knowledge
        self.knowledge = self.__bl.AND(
            self.knowledge, self.__bl.NOT(self.__bl.Symbol(card))
        )

    def guess(self):
        # Simplify and draw conclusions from knowledge before guessing
        self.__update_knowledge()
        return super().guess()

    def inform(self, response):
        # Add the guess to knowledge
        self.knowledge = self.__bl.AND(
            self.knowledge,
            self.__bl.NOT(
                self.__bl.AND(*[self.__bl.Symbol(x) for x in response["guess"]])
            ),
        )

    def __update_knowledge(self):
        # Simplify the logical expression
        self.knowledge = self.knowledge.simplify()

        # Extract terms that are known to be false and update the appropriate field
        literals = [x for x in str(self.knowledge).split("&") if x[0] == "~"]
        for literal in literals:
            symbol = literal[1:]
            if symbol in Clue.people and symbol not in self.known_people:
                self.known_people.append(symbol)
                Clue.conclusions += 1
            elif symbol in Clue.rooms and symbol not in self.known_rooms:
                self.known_rooms.append(symbol)
                Clue.conclusions += 1
            elif symbol in Clue.weapons and symbol not in self.known_weapons:
                self.known_weapons.append(symbol)
                Clue.conclusions += 1
