import time
import multiprocessing as mp

from agent import ClueAgent, ClueIntelligentAgent, ClueStrategicAgent
from clue import Clue


def main():
    num_players = -1
    while num_players < 2 or num_players > 6:
        try:
            num_players = int(input("Enter the number of players (2-6): "))
        except ValueError:
            pass

    multi = True
    rounds = 0
    games = 1
    wins = [0 for _ in range(num_players)]
    start_time = time.time()

    if multi:
        with mp.Pool(mp.cpu_count()) as p:
            l = p.starmap(play_game, [[num_players] for _ in range(games)])

        for x in l:
            wins[x[1]] += 1

        rounds = sum(x[0] for x in l)
    else:
        for _ in range(games):
            res = play_game(num_players)
            rounds += res[0]
            wins[res[1]] += 1

    print(rounds / games)
    print(wins)
    print(f"--- {time.time() - start_time} seconds ---")


def play_game(num_players):
    players = []

    for i in range(num_players):
        players.append(ClueIntelligentAgent(i, num_players))

    game = Clue(players)
    game.deal()
    return game.play()


if __name__ == "__main__":
    main()
