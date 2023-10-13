import logging
import random
from typing import Any, Union

from .board import Board
from .constants import MAX_ROUNDS, NUM_DICES, PLAYER_TOKENS, STARTING_MONEY
from .models import GameState
from .player import Player

log = logging.getLogger("monopoly.game")


class Dice:
    def __init__(self, num_dices: int = 1):
        self.num_dices = num_dices

    def roll(self):
        return sum([random.randint(1, 6) for _ in range(self.num_dices)])


class MonopolyJunior:
    def __init__(self, num_players, game_id: Any = None):
        self.game_id = game_id
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")
        self.num_players = num_players
        self.players: list[Player] = []
        self.board = Board(self)
        self.dice = Dice(NUM_DICES)
        self.turn = 0
        self.game_over = False
        self.winner: Player = None
        self.history: list[dict] = []
        random.shuffle(self.board.chance_cards)

        tokens = PLAYER_TOKENS.copy()
        for i in range(self.num_players):
            token = random.choice(tokens)
            tokens.remove(token)
            self.players.append(
                Player(i, self.board, token,
                       STARTING_MONEY[num_players - 2]))

    def play(self):
        while not self.game_over:
            if self.turn > MAX_ROUNDS:
                log.warning("Game over after max rounds")
                self.game_over = True
                break
            player = self.players[self.turn % self.num_players]
            if not player.game_over:
                player.take_turn(self.dice)
                self.game_over = any(
                    [player.game_over for player in self.players])
            self.history.append(self.state)
            self.turn += 1
        log.info(f"Game over after {self.turn} turns")
        self.winner = self.get_winner()
        log.info(f"Player {self.winner} wins")

    def get_winner(self) -> Union[Player, None]:
        players = [player for player in self.players if not player.game_over]
        max_player_money = max([player.money for player in players])
        players = [player for player in players if player.money ==
                   max_player_money]
        if len(players) == 1:
            return players[0]
        max_player_ownership = max(
            [player.ownership_value for player in players])
        players = [player for player in players
                   if player.ownership_value == max_player_ownership]
        if len(players) == 1:
            return players[0]
        return None

    @property
    def state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            turn=self.turn,
            players=[player.state for player in self.players],
            board=self.board.state,
            game_over=self.game_over)
