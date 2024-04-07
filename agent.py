import random

from clue import Clue


class ClueAgent:
    """A Clue player with random decision making"""

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
        return {"person": person, "room": room, "weapon": weapon}

    def reply(self, guess):
        """Respond to another player's guess"""

        # Randomly select a card from ones that match the guess
        reply_options = [x for x in guess.values() if x in self.cards]
        try:
            return random.choice(reply_options)
        except IndexError:
            return None
