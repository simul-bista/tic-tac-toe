from enum import Enum


class Player(Enum):
    X = "X"
    O = "O"


class InvalidMoveError(ValueError):
    pass


class Game:
    def __init__(self) -> None:
        self._board: list[list[Player | None]] = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        self._current_player = Player.X

    @property
    def board(self) -> tuple[tuple[Player | None, ...], ...]:
        return tuple(tuple(row) for row in self._board)

    @property
    def current_player(self) -> Player:
        return self._current_player

    def make_move(self, row: int, column: int) -> None:
        if type(row) is not int or type(column) is not int:
            raise TypeError("row and column must be integers")
        if not (0 <= row < 3 and 0 <= column < 3):
            raise InvalidMoveError("row and column must be between 0 and 2")
        if self._board[row][column] is not None:
            raise InvalidMoveError("cell is already occupied")

        self._board[row][column] = self._current_player
        self._current_player = (
            Player.O if self._current_player is Player.X else Player.X
        )
