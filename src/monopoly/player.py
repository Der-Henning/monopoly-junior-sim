import logging
from typing import TYPE_CHECKING

from .cards import ChanceCard, ChooseJumpCard, GetOutOfJailFreeCard
from .constants import GO_MONEY, OUT_OF_JAIL_FEE
from .models import PlayerState
from .spaces import Place

if TYPE_CHECKING:
    from .board import Board
    from .game import Dice

log = logging.getLogger("monopoly.player")


class Player:
    def __init__(self, id: int, board: 'Board', token: str, money: int = 20):
        self.id = id
        self.board = board
        self.position = 0
        self.money = self.board.bank.withdraw(money)
        self.token = token
        self.game_over = False
        self.in_jail = False
        self.chance_cards: list[ChanceCard] = []

    def take_turn(self, dice: 'Dice'):
        if self.in_jail:
            get_out_of_jail_card = next(
                (card for card in self.chance_cards
                 if isinstance(card, GetOutOfJailFreeCard)), None)
            if get_out_of_jail_card:
                self.chance_cards.remove(get_out_of_jail_card)
                self.board.used_chance_cards.append(get_out_of_jail_card)
                self.in_jail = False
            elif self.money < OUT_OF_JAIL_FEE:
                log.info(f"Player {self} is bankrupt")
                self.game_over = True
                return
            else:
                self.money -= self.board.bank.deposit(OUT_OF_JAIL_FEE)
                self.in_jail = False
        choose_jump_card = next((
            card for card in self.chance_cards
            if isinstance(card, ChooseJumpCard)), None)
        if choose_jump_card:
            choose_jump_card.jump(self)
        else:
            roll = dice.roll()
            log.info(f"Player {self} rolled a {roll}")
            self.move(roll)

    def move(self, steps: int):
        self.position += steps
        if self.position > len(self.board.spaces):
            self.money += self.board.bank.withdraw(GO_MONEY)
        self.position %= len(self.board.spaces)
        self.board.spaces[self.position].land(self)

    @property
    def ownership_value(self) -> int:
        return sum([space.price for space in self.board.spaces
                    if isinstance(space, Place) and space.owner == self])

    @property
    def state(self) -> PlayerState:
        return PlayerState(
            id=self.id,
            token=self.token,
            position=self.position,
            money=self.money,
            game_over=self.game_over,
            in_jail=self.in_jail,
            chance_cards=self.chance_cards)

    def __repr__(self) -> str:
        return f"{self.id} {self.token}"
