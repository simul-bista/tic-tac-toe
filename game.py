from enum import Enum


class Player(Enum):
    X = "X"
    O = "O"


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAW = "draw"


class InvalidMoveError(ValueError):
    pass


class Game:
    _WINNING_COMBINATIONS = (
        ((0, 0), (0, 1), (0, 2)),
        ((1, 0), (1, 1), (1, 2)),
        ((2, 0), (2, 1), (2, 2)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (2, 2)),
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 1), (2, 0)),
    )

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

    @property
    def winner(self) -> Player | None:
        lines = self.winning_lines
        if not lines:
            return None
        row, column = lines[0][0]
        return self._board[row][column]

    @property
    def winning_lines(self) -> tuple[tuple[tuple[int, int], ...], ...]:
        return tuple(
            combination
            for combination in self._WINNING_COMBINATIONS
            if (player := self._board[combination[0][0]][combination[0][1]])
            is not None
            and all(
                self._board[row][column] is player
                for row, column in combination[1:]
            )
        )

    @property
    def status(self) -> GameStatus:
        if self.winner is not None:
            return GameStatus.WON
        if all(cell is not None for row in self._board for cell in row):
            return GameStatus.DRAW
        return GameStatus.IN_PROGRESS

    def make_move(self, row: int, column: int) -> None:
        if self.status is not GameStatus.IN_PROGRESS:
            raise InvalidMoveError("game is already over")
        if type(row) is not int or type(column) is not int:
            raise TypeError("row and column must be integers")
        if not (0 <= row < 3 and 0 <= column < 3):
            raise InvalidMoveError("row and column must be between 0 and 2")
        if self._board[row][column] is not None:
            raise InvalidMoveError("cell is already occupied")

        self._board[row][column] = self._current_player
        if self.status is GameStatus.IN_PROGRESS:
            self._current_player = (
                Player.O if self._current_player is Player.X else Player.X
            )
