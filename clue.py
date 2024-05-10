import random


class Clue:
    """A game of Clue"""

    DEBUG = True

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

    conclusions = [0, 0]

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

        if self.DEBUG:
            print("SOLUTION: ", self.solution)
            for player in self.players:
                print(f"Player {player.number}: {player.cards}")

        # Complete rounds until someone wins
        while not self.over:
            if self.DEBUG:
                print("----------NEW ROUND----------")
            winner = self.play_round()
        return (self.num_rounds, winner)

    def __take_turn(self, player):
        """Simulate a player's turn"""

        # Get all other players
        others = self.players.copy()
        others.remove(player)

        # Make a guess
        guess = player.guess()

        if self.DEBUG:
            print(f"Player {player.number} guessed: {guess}")

        # Ask the other players to reply to the guess
        response = None
        for other in others:
            reply = other.reply(guess)
            if reply is not None:
                player.receive(reply)
                response = {
                    "guess": guess[0],
                    "guesser": guess[1],
                    "responder": other.number,
                }

                if self.DEBUG:
                    print(f"Player {other.number} replied: {reply}")
                break

        if response is not None:
            for other in others:
                if other.__intelligent__ and other.number != response["responder"]:
                    other.inform(response)
            return False

        return True
