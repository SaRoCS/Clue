import random


class Clue:
    """A game of Clue"""

    people = (
        "Miss Scarlett",
        "Colonel Mustard",
        "Mrs. White",
        "Mr. Green",
        "Mrs. Peacock",
        "Professor Plum",
    )

    rooms = (
        "Kitchen",
        "Ballroom",
        "Conservatory",
        "Dining Room",
        "Billiard Room",
        "Library",
        "Lounge",
        "Hall",
        "Study",
    )

    weapons = ("Candlestick", "Knife", "Lead Pipe", "Revolver", "Rope", "Wrench")

    def __init__(self, players):
        self.over = False
        self.players = players
        self.num_rounds = 0

        # Create the game solution
        person = random.choice(self.people)
        room = random.choice(self.rooms)
        weapon = random.choice(self.weapons)
        self.solution = f"{person} in the {room} with the {weapon}"

        # Create the game deck
        self.deck = list(self.people) + list(self.rooms) + list(self.weapons)
        self.deck.remove(person)
        self.deck.remove(room)
        self.deck.remove(weapon)
        random.shuffle(self.deck)

    def deal(self):
        """Deals cards to all of the players"""

        cards_left = len(self.deck)
        num_players = len(self.players)

        for i in range(num_players):
            # Start from the last player and determine the number of cards to give
            player_num = num_players - i
            cards_to_take = cards_left // player_num

            # Give the player the appropriate section of the deck
            self.players[player_num - 1].dealt(
                self.deck[cards_left - cards_to_take : cards_left]
            )

            cards_left -= cards_to_take

    def play_round(self):
        """Simulate one round of the game"""

        self.num_rounds += 1

        # Everyone takes a turn
        for player in self.players:
            # The game is over if this was a winning turn
            if self.__take_turn(player):
                self.over = True
                return player.number
        return None

    def play(self):
        """Simulate the game"""

        # Complete rounds until someone wins
        while not self.over:
            self.play_round()
        return self.num_rounds

    def __take_turn(self, player):
        """Simulate a player's turn"""

        # Get all other players
        others = self.players.copy()
        others.remove(player)

        # Make a guess
        guess = player.guess()

        # Ask the other players to reply to the guess
        for other in others:
            reply = other.reply(guess)
            if reply is not None:
                player.receive(reply)
                return False
        # If no one replied, this is a winning turn
        return True
