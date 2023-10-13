import logging
from typing import TYPE_CHECKING

from .models import PlaceState

if TYPE_CHECKING:
    from .board import Board
    from .player import Player

log = logging.getLogger("monopoly.spaces")


class Space:
    def __init__(self, name: str):
        self.name = name

    def land(self, player: 'Player'):
        log.info(f"Player {player} landed on {self}")

    def __repr__(self) -> str:
        return self.name


class Go(Space):
    def __init__(self):
        super().__init__("Go")


class Place(Space):
    def __init__(self, name: str, price: int, color: str = None):
        super().__init__(name)
        self.price = price
        self.owner = None
        self.color = color

    def land(self, player: 'Player', free_of_charge: bool = False):
        super().land(player)
        if self.owner is None:
            self.buy(player, free_of_charge)
        elif self.owner != player:
            self.pay_rent(player)

    def buy(self, player: 'Player', free_of_charge: bool = False):
        if free_of_charge:
            self.owner = player
            log.info(f"Player {player} got {self} for free")
        elif player.money >= self.price:
            player.money -= player.board.bank.deposit(self.price)
            self.owner = player
            log.info(f"Player {player} bought {self}")
        else:
            log.info(
                f"Player {player} does not have enough money to buy {self}")
            player.game_over = True

    def pay_rent(self, player: 'Player'):
        owns_color = all([
            space.color == self.color for space in self.owner.board.spaces
            if isinstance(space, Place) and space.owner == self.owner])
        rent = self.price * 2 if owns_color else self.price
        if player.money >= rent:
            player.money -= rent
            self.owner.money += rent
            log.info(
                f"Player {player} paid rent {rent} to Player {self.owner}")
        else:
            log.info(f"Player {player} does not have enough money to pay "
                     f"rent to Player {self.owner}")
            player.game_over = True

    @property
    def state(self) -> PlaceState:
        return PlaceState(
            name=self.name,
            owner=self.owner.id if self.owner else None,
            price=self.price,
            color=self.color)


class Chance(Space):
    def __init__(self, board: 'Board'):
        super().__init__("Chance")
        self.board = board

    def land(self, player: 'Player'):
        super().land(player)
        card = self.board.draw_chance_card()
        card.draw(player)


class FreeParking(Space):
    def __init__(self):
        super().__init__("Free Parking")


class GoToJail(Space):
    def __init__(self, jail_position: int = 6):
        super().__init__("Go To Jail")
        self.jail_position = jail_position

    def land(self, player: 'Player'):
        super().land(player)
        log.info(f"Player {player} is going to jail")
        player.in_jail = True
        player.position = self.jail_position


class Jail(Space):
    def __init__(self):
        super().__init__("Jail")

    def land(self, player: 'Player'):
        super().land(player)
        log.info(f"Player {player} visits jail")
