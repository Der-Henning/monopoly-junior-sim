from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cards import ChanceCard


@dataclass
class PlayerState:
    id: int
    token: str
    position: int
    money: int
    game_over: bool
    in_jail: bool
    chance_cards: list['ChanceCard']


@dataclass
class BankState:
    money: int


@dataclass
class PlaceState:
    name: str
    owner: int
    price: int
    color: str


@dataclass
class BoardState:
    bank: BankState
    places: list[PlaceState]


@dataclass
class GameState:
    game_id: int
    turn: int
    game_over: bool
    players: list[PlayerState]
    board: BoardState
