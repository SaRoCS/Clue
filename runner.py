import time

from agent import ClueAgent, ClueIntelligentAgent, ClueStrategicAgent
from clue import Clue

num_players = -1
while num_players < 2 or num_players > 6:
    try:
        num_players = int(input("Enter the number of players (2-6): "))
    except ValueError:
        pass

start_time = time.time()
rounds = 0
games = 1
wins = [0 for _ in range(num_players)]

for i in range(games):
    players = []

    for i in range(num_players):
        players.append(ClueStrategicAgent(i, num_players))

    game = Clue(players)
    game.deal()
    res = game.play()
    rounds += res[0]
    wins[res[1]] += 1

print(rounds / games)
print(game.conclusions)
print(wins)
print(f"--- {time.time() - start_time} seconds ---")
