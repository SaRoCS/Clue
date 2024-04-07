from clue import Clue
from agent import ClueAgent


num_players = -1
while num_players < 2 or num_players > 6:
    try:
        num_players = int(input("Enter the number of players (2-6): "))
    except ValueError:
        pass

rounds = 0
games = 5000

for i in range(games):
    players = []

    for i in range(num_players):
        players.append(ClueAgent(i))

    game = Clue(players)
    game.deal()

    rounds += game.play()

print(rounds / games)
