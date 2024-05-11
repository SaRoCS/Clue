# Clue
This is a simulator for the guessing element of the board game Clue. Different types of players or agents are provided.

## Clue Agent
This is a basic agent that makes random guesses and only records the cards it is shown in response to those guesses.

## Intelligent Agent
This is a knowledge-based agent that collects information about other players' guesses and responses. Using logical expressions, the agent draws conclusions from that information about other players' hands and the game's solution.

## Strategic Agent
This agent uses its knowledge to make better decisions about which card to show, so that other players know as little about its hand as possible. Without the added challenge of moving between rooms, there is never any reason to make a guess containing known cards, so this agent does not have any advantages in this simulation.