import logging
import random
from typing import TYPE_CHECKING

from .constants import BIRTHDAY_MONEY, GO_MONEY
from .spaces import Place

if TYPE_CHECKING:
    from .board import Board
    from .player import Player

log = logging.getLogger("monopoly.cards")


class ChanceCard:
    def __init__(self, name: str, board: 'Board'):
        self.name = name
        self.board = board

    def draw(self, player: 'Player'):
        log.info(f"Player {player} drew {self}")

    def __repr__(self) -> str:
        return self.name


class GetOutOfJailFreeCard(ChanceCard):
    def __init__(self, board: 'Board'):
        super().__init__("Get Out of Jail Free", board)

    def draw(self, player: 'Player'):
        super().draw(player)
        player.chance_cards.append(self)


class MoveToGoCard(ChanceCard):
    def __init__(self, board: 'Board'):
        super().__init__("Move to Go", board)

    def draw(self, player: 'Player'):
        super().draw(player)
        player.position = 0
        player.money += self.board.bank.withdraw(GO_MONEY)
        self.board.used_chance_cards.append(self)


class MoneyCard(ChanceCard):
    def __init__(self, name: str, board: 'Board', price: int):
        super().__init__(name, board)
        self.price = price

    def draw(self, player: 'Player'):
        super().draw(player)
        player.money += self.board.bank.withdraw(self.price)
        self.board.used_chance_cards.append(self)


class HomeworkCard(MoneyCard):
    def __init__(self, board: 'Board'):
        super().__init__("Homework", board, 2)


class PenaltyCard(ChanceCard):
    def __init__(self, name: str, board: 'Board', price: int):
        super().__init__(name, board)
        self.price = price

    def draw(self, player: 'Player'):
        super().draw(player)
        player.money -= self.board.bank.deposit(self.price)
        self.board.used_chance_cards.append(self)


class SweetsCard(PenaltyCard):
    def __init__(self, board: 'Board'):
        super().__init__("Sweets", board, -2)


class BirthdayCard(ChanceCard):
    def __init__(self, board: 'Board'):
        super().__init__("Birthday", board)

    def draw(self, player: 'Player'):
        super().draw(player)
        for other_player in player.board.game.players:
            if other_player != player:
                player.money += BIRTHDAY_MONEY
                other_player.money -= BIRTHDAY_MONEY
        self.board.used_chance_cards.append(self)


class MoveToCard(ChanceCard):
    def choose(self, player: 'Player', places: list[Place]) -> Place:
        selected_places = [place for place in places if place.owner is None
                           and place.price <= player.money]
        if len(selected_places) == 0:
            selected_places = [place for place in places
                               if place.owner == player]
        if len(selected_places) == 0:
            selected_places = places
        return random.choice(selected_places)


class JumpCard(ChanceCard):
    def __init__(self,
                 board: 'Board',
                 position: int,
                 free_of_charge: bool = False):
        super().__init__(f"Jump to {board.spaces[position].name}", board)
        self.position = position
        self.free_of_charge = free_of_charge

    def draw(self, player: 'Player'):
        super().draw(player)
        player.position = self.position
        self.board.spaces[self.position].land(player, self.free_of_charge)
        self.board.used_chance_cards.append(self)


class ChooseColorCard(MoveToCard):
    def __init__(self,
                 board: 'Board',
                 colors: list[str]):
        super().__init__(f"Jump to {' or '.join(colors)}", board)
        self.colors = colors

    def draw(self, player: 'Player'):
        super().draw(player)
        spaces = [space for space in self.board.spaces
                  if isinstance(space, Place) and
                  space.color in self.colors]
        choice = self.choose(player, spaces)
        log.info(f"Player {player} chose {choice}")
        player.position = self.board.spaces.index(choice)
        self.board.spaces[player.position].land(player, True)
        self.board.used_chance_cards.append(self)


class MoveOneOrChanceCard(ChanceCard):
    def __init__(self, board: 'Board'):
        super().__init__("Move one or new Chance", board)

    def draw(self, player: 'Player'):
        super().draw(player)
        choice = random.choice(["move", "chance"])
        log.info(f"Player {player} chose {choice}")
        if choice == "move":
            player.move(1)
        else:
            card = self.board.draw_chance_card()
            card.draw(player)
        self.board.used_chance_cards.append(self)


class MoveUpToXFieldsCard(ChanceCard):
    def __init__(self, board: 'Board', fields: int):
        super().__init__(f"Move up to {fields} fields", board)
        self.fields = fields

    def draw(self, player: 'Player'):
        super().draw(player)
        choice = random.randint(0, self.fields)
        log.info(f"Player {player} chose to move {choice} fields")
        player.move(choice)
        self.board.used_chance_cards.append(self)


class ChooseJumpCard(MoveToCard):
    def __init__(self, board: 'Board', token: str):
        super().__init__(f"{token} Jump", board)
        self.token = token

    def draw(self, player: 'Player'):
        super().draw(player)
        token_player = next(
            (player for player in player.board.game.players
             if player.token == self.token), None)
        if token_player:
            token_player.chance_cards.append(self)
        new_card = self.board.draw_chance_card()
        new_card.draw(player)

    def jump(self, player: 'Player'):
        places = [space for space in self.board.spaces
                  if isinstance(space, Place)]
        choice = self.choose(player, places)
        player.position = self.board.spaces.index(choice)
        log.info(f"Player {player} chose to jump to {choice}")
        self.board.spaces[player.position].land(player)
        player.chance_cards.remove(self)
        self.board.used_chance_cards.append(self)
