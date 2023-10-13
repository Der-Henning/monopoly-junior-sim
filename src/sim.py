import logging

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from monopoly import MonopolyJunior
from monopoly.models import GameState, PlayerState

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s%(message)s")

if __name__ == "__main__":
    logging.disable(logging.NOTSET)
    game = MonopolyJunior(4)
    game.play()


def sim():
    logging.disable(logging.WARNING)
    num_players = 4
    winners: list[PlayerState] = []
    rounds = []
    game_states: list[GameState] = []
    for i in tqdm(range(10000)):
        game = MonopolyJunior(num_players, i)
        game.play()
        winners.append(getattr(game.winner, "state", None))
        rounds.append(game.turn)
        game_states.append(game.state)

    # Win Ratio by Player ID
    data = sorted([str(w.id) if w is not None else "draw"
                   for w in winners])
    sns.countplot(x=data, stat="probability")
    plt.xlabel("Player ID")
    plt.title("Win Ratio by Player ID")
    plt.show()

    # Win Ratio by Player Token
    data = sorted([w.token if w is not None else "draw"
                   for w in winners],
                  key=lambda x: 1 if x == "draw" else 0)
    sns.countplot(x=data, stat="probability")
    plt.xlabel("Player Token")
    plt.title("Win Ratio by Player Token")
    plt.show()

    # Distriubution of Game length
    data = list(filter(lambda x: x < 1000, rounds))
    sns.histplot(data, binwidth=5, kde=True)
    plt.title("Game Length Distribution")
    plt.xlabel("Rounds")
    plt.xlim(0, 150)
    plt.show()

    data = pd.DataFrame(
        [[1 if place.owner == winners[game_state.game_id].id else 0
          for place in game_state.board.places] for game_state in game_states
         if winners[game_state.game_id]],
        columns=[place.name for place in game_states[0].board.places])
    colors = [place.color for place in game_states[0].board.places]
    sns.barplot(data=data, palette=colors)
    plt.xlabel("Place")
    plt.xticks(rotation=45)
    plt.title("Win Ratio by owned Place")
    plt.show()
