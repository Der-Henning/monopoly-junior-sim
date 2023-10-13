import logging
import random
from typing import TYPE_CHECKING

from .cards import (BirthdayCard, ChanceCard, ChooseColorCard, ChooseJumpCard,
                    GetOutOfJailFreeCard, HomeworkCard, JumpCard,
                    MoveOneOrChanceCard, MoveToGoCard, MoveUpToXFieldsCard,
                    SweetsCard)
from .constants import AVAILABLE_MONEY, PLAYER_TOKENS
from .models import BoardState
from .spaces import Chance, FreeParking, Go, GoToJail, Jail, Place, Space

if TYPE_CHECKING:
    from .game import MonopolyJunior

log = logging.getLogger("monopoly.board")


class Bank:
    def __init__(self):
        self.money = AVAILABLE_MONEY

    def withdraw(self, amount: int) -> int:
        if self.money < amount:
            amount = self.money
            log.info("Bank is out of money")
        self.money -= amount
        return amount

    def deposit(self, amount: int) -> int:
        self.money += amount
        return amount

    @property
    def state(self) -> dict:
        return {
            "money": self.money}


class Board:
    def __init__(self, game: 'MonopolyJunior'):
        self.game = game
        self.bank = Bank()
        self.spaces: list[Space] = [
            Go(),
            Place("Taco Truck", 1, "brown"),
            Place("Pizza House", 1, "brown"),
            Chance(self),
            Place("Bakery", 1, "lightblue"),
            Place("Ice Cream Parlor", 1, "lightblue"),
            Jail(),
            Place("Museum", 2, "pink"),
            Place("Library", 2, "pink"),
            Chance(self),
            Place("Go_Karts", 2, "orange"),
            Place("Swimming Pool", 2, "orange"),
            FreeParking(),
            Place("Ferris Wheel", 3, "red"),
            Place("Roller Coaster", 3, "red"),
            Chance(self),
            Place("Toy Store", 3, "yellow"),
            Place("Pet Store", 3, "yellow"),
            GoToJail(6),
            Place("Aquarium", 4, "green"),
            Place("The Zoo", 4, "green"),
            Chance(self),
            Place("Park Place", 5, "blue"),
            Place("Broadwalk", 5, "blue")
        ]
        self.chance_cards: list[ChanceCard] = [
            GetOutOfJailFreeCard(self),
            MoveToGoCard(self),
            HomeworkCard(self),
            SweetsCard(self),
            BirthdayCard(self),
            JumpCard(self, 10, True),
            JumpCard(self, 23, False),
            ChooseColorCard(self, ["orange"]),
            ChooseColorCard(self, ["lightblue"]),
            ChooseColorCard(self, ["pink", "blue"]),
            ChooseColorCard(self, ["lightblue", "red"]),
            ChooseColorCard(self, ["brown", "yellow"]),
            ChooseColorCard(self, ["orange", "green"]),
            MoveOneOrChanceCard(self),
            MoveUpToXFieldsCard(self, 5)
        ]
        for token in PLAYER_TOKENS:
            self.chance_cards.append(ChooseJumpCard(self, token))
        self.used_chance_cards: list[ChanceCard] = []
        random.shuffle(self.chance_cards)

    def draw_chance_card(self) -> ChanceCard:
        if len(self.chance_cards) == 0:
            self.chance_cards = self.used_chance_cards
            self.used_chance_cards = []
            random.shuffle(self.chance_cards)
        return self.chance_cards.pop()

    @property
    def state(self) -> BoardState:
        return BoardState(
            bank=self.bank.state,
            places=[space.state for space in self.spaces
                    if isinstance(space, Place)])
