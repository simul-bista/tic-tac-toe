from collections.abc import Callable

import pytest

from game import Game, GameStatus, InvalidMoveError, Player


WINNING_LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


def test_valid_move_places_current_player_and_switches_turn() -> None:
    game = Game()
    assert game.status is GameStatus.IN_PROGRESS

    game.make_move(1, 2)

    assert game.board[1][2] is Player.X
    assert game.current_player is Player.O
    assert game.status is GameStatus.IN_PROGRESS


def test_alternating_valid_moves_switch_players() -> None:
    game = Game()

    game.make_move(0, 0)
    game.make_move(2, 1)

    assert game.board[0][0] is Player.X
    assert game.board[2][1] is Player.O
    assert game.current_player is Player.X


@pytest.mark.parametrize(
    ("row", "column", "error"),
    [
        (True, 0, TypeError),
        (0, False, TypeError),
        (1.0, 0, TypeError),
        (0, "1", TypeError),
        (-1, 0, InvalidMoveError),
        (3, 0, InvalidMoveError),
        (0, -1, InvalidMoveError),
        (0, 3, InvalidMoveError),
    ],
)
def test_invalid_move_is_rejected_without_changing_game(
    row: object, column: object, error: type[Exception]
) -> None:
    game = Game()
    before_board = game.board
    before_player = game.current_player

    with pytest.raises(error):
        game.make_move(row, column)  # type: ignore[arg-type]

    assert game.board == before_board
    assert game.current_player is before_player


def test_occupied_square_is_rejected_without_changing_game() -> None:
    game = Game()
    game.make_move(1, 1)
    before_board = game.board
    before_player = game.current_player

    with pytest.raises(InvalidMoveError):
        game.make_move(1, 1)

    assert game.board == before_board
    assert game.current_player is before_player


def test_new_game_has_no_winner() -> None:
    game = Game()

    assert game.winner is None


@pytest.mark.parametrize("winning_line", WINNING_LINES)
@pytest.mark.parametrize("winner", [Player.X, Player.O])
def test_detects_each_winning_line_for_both_players(
    winning_line: tuple[tuple[int, int], ...], winner: Player
) -> None:
    game = Game()
    opponent = Player.O if winner is Player.X else Player.X

    for index, (row, column) in enumerate(winning_line):
        if game.current_player is opponent:
            board = game.board
            filler = next(
                (r, c)
                for r in range(3)
                for c in range(3)
                if board[r][c] is None
                and (r, c) not in winning_line
                and not any(
                    all(
                        board[line_row][line_column] is opponent
                        or (line_row, line_column) == (r, c)
                        for line_row, line_column in line
                    )
                    for line in WINNING_LINES
                )
            )
            game.make_move(*filler)
            assert game.winner is None

        game.make_move(row, column)
        if index < len(winning_line) - 1:
            assert game.winner is None

    assert game.winner is winner
    assert game.current_player is winner
    assert game.status is GameStatus.WON
    assert game.winning_lines == (winning_line,)


def test_move_completing_winning_line_as_final_empty_cell_wins() -> None:
    game = Game()
    moves = (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 0),
    )
    for move in moves:
        game.make_move(*move)

    assert sum(cell is None for row in game.board for cell in row) == 1
    assert game.winner is None

    game.make_move(2, 2)

    assert game.winner is Player.X
    assert game.board[2][2] is Player.X
    assert game.current_player is Player.X
    assert game.status is GameStatus.WON


def test_nonwinning_prefix_has_no_winner() -> None:
    game = Game()

    for move in ((0, 0), (1, 1), (0, 1), (2, 0)):
        game.make_move(*move)
        assert game.winner is None


def test_move_after_win_is_rejected_without_changing_game() -> None:
    game = Game()
    for move in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2)):
        game.make_move(*move)
    before_board = game.board
    before_player = game.current_player

    with pytest.raises(InvalidMoveError):
        game.make_move(2, 2)

    assert game.board == before_board
    assert game.current_player is before_player is Player.X
    assert game.winner is Player.X
    assert game.status is GameStatus.WON


DRAW_SEQUENCE = (
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 1),
    (1, 0),
    (2, 0),
    (1, 2),
    (2, 2),
    (2, 1),
)


def make_won_game() -> Game:
    game = Game()
    for move in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2)):
        game.make_move(*move)
    return game


def make_drawn_game() -> Game:
    game = Game()
    for move in DRAW_SEQUENCE:
        game.make_move(*move)
    return game


def test_nearly_full_nonwinning_board_is_in_progress() -> None:
    game = Game()
    for move in DRAW_SEQUENCE[:-1]:
        game.make_move(*move)

    assert sum(cell is None for row in game.board for cell in row) == 1
    assert game.winner is None
    assert game.status is GameStatus.IN_PROGRESS


def test_full_board_without_winner_is_draw() -> None:
    game = make_drawn_game()

    assert all(cell is not None for row in game.board for cell in row)
    assert game.winner is None
    assert game.status is GameStatus.DRAW
    assert game.current_player is Player.X
    assert game.winning_lines == ()


def test_final_move_can_complete_multiple_winning_lines() -> None:
    game = Game()
    moves = (
        (1, 0),  # X
        (0, 1),  # O
        (1, 2),  # X
        (2, 1),  # O
        (0, 0),  # X
        (2, 0),  # O
        (2, 2),  # X
        (0, 2),  # O
        (1, 1),  # X completes row and diagonal
    )
    for move in moves:
        game.make_move(*move)

    assert game.winner is Player.X
    assert game.winning_lines == (
        ((1, 0), (1, 1), (1, 2)),
        ((0, 0), (1, 1), (2, 2)),
    )


@pytest.mark.parametrize(
    "make_game",
    [make_won_game, make_drawn_game],
    ids=["won", "drawn"],
)
@pytest.mark.parametrize(
    ("row", "column"),
    [
        (2, 2),
        (0, 0),
        (-1, 0),
        (3, 0),
        (0, -1),
        (0, 3),
        (True, 0),
        (0, False),
    ],
)
def test_terminal_games_reject_all_moves_without_changing_state(
    make_game: Callable[[], Game], row: object, column: object
) -> None:
    game = make_game()
    before_state = (game.board, game.current_player, game.winner, game.status)

    with pytest.raises(InvalidMoveError):
        game.make_move(row, column)  # type: ignore[arg-type]

    assert (game.board, game.current_player, game.winner, game.status) == before_state
