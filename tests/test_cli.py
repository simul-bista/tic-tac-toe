import builtins
import subprocess
import sys
from pathlib import Path

import pytest

from game import Game
from tic_tac_toe import format_board, parse_move, run_game


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        ("1", (0, 0)),
        ("2", (0, 1)),
        ("3", (0, 2)),
        ("4", (1, 0)),
        ("5", (1, 1)),
        ("6", (1, 2)),
        ("7", (2, 0)),
        ("8", (2, 1)),
        ("9", (2, 2)),
        (" 5 ", (1, 1)),
    ],
)
def test_parse_move_maps_positions(position: str, expected: tuple[int, int]) -> None:
    assert parse_move(position) == expected


@pytest.mark.parametrize("value", ["", "abc", "1.5", "0", "10", "-1"])
def test_parse_move_rejects_malformed_and_out_of_range_input(value: str) -> None:
    with pytest.raises(ValueError):
        parse_move(value)


def test_format_board_displays_position_labels_and_marks() -> None:
    game = Game()
    game.make_move(0, 1)

    assert format_board(game.board) == (
        " 1 | X | 3 \n"
        "---+---+---\n"
        " 4 | 5 | 6 \n"
        "---+---+---\n"
        " 7 | 8 | 9 "
    )


def play_moves(moves: list[str]) -> tuple[list[str], list[str]]:
    responses = iter(moves)
    prompts: list[str] = []
    output: list[str] = []

    def input_fn(prompt: str) -> str:
        prompts.append(prompt)
        return next(responses)

    run_game(input_fn, output.append)
    return prompts, output


def test_cli_renders_initial_and_each_move_then_announces_x_win() -> None:
    prompts, output = play_moves(["1", "4", "2", "5", "3"])

    assert len(prompts) == 5
    assert [prompt.split(",", 1)[0] for prompt in prompts] == [
        "Player X",
        "Player O",
        "Player X",
        "Player O",
        "Player X",
    ]
    assert len(output) == 7
    assert output[0].startswith(" 1 | 2 | 3 ")
    assert output[-2] == (
        " X | X | X \n"
        "---+---+---\n"
        " O | O | 6 \n"
        "---+---+---\n"
        " 7 | 8 | 9 "
    )
    assert output[-1] == "Player X wins!"


def test_cli_announces_o_win_and_does_not_prompt_after_terminal_move() -> None:
    prompts, output = play_moves(["1", "4", "2", "5", "9", "6"])

    assert len(prompts) == 6
    assert output[-2].splitlines()[2] == " O | O | O "
    assert output[-1] == "Player O wins!"


def test_cli_announces_draw_after_rendering_final_board() -> None:
    prompts, output = play_moves(["1", "2", "3", "5", "4", "7", "6", "9", "8"])

    assert len(prompts) == 9
    assert output[-2] == (
        " X | O | X \n"
        "---+---+---\n"
        " X | O | X \n"
        "---+---+---\n"
        " O | X | O "
    )
    assert output[-1] == "The game is a draw."


def test_invalid_and_occupied_moves_report_errors_without_switching_player() -> None:
    prompts, output = play_moves(["bad", "0", "10", "1", "1", "4", "2", "5", "3"])

    assert [prompt.split(",", 1)[0] for prompt in prompts] == [
        "Player X",
        "Player X",
        "Player X",
        "Player X",
        "Player O",
        "Player O",
        "Player X",
        "Player O",
        "Player X",
    ]
    assert "Enter a number from 1 to 9." in output
    assert "Position must be from 1 to 9." in output
    assert "cell is already occupied" in output
    assert sum("---+---+---" in item for item in output) == 6
    assert output[-1] == "Player X wins!"


@pytest.mark.parametrize(
    "exception",
    [EOFError, KeyboardInterrupt],
    ids=["eof", "keyboard-interrupt"],
)
def test_cli_cancels_cleanly_on_eof_or_keyboard_interrupt(
    exception: type[BaseException],
) -> None:
    output: list[str] = []

    def input_fn(prompt: str) -> str:
        raise exception

    run_game(input_fn, output.append)

    assert output[-1] == "\nGame cancelled."


def test_import_does_not_start_cli() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-c", "import tic_tac_toe"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == ""
    assert result.stderr == ""


def test_main_uses_builtin_input(monkeypatch: pytest.MonkeyPatch) -> None:
    from tic_tac_toe import main

    inputs = iter(["1", "4", "2", "5", "3"])
    output: list[str] = []
    monkeypatch.setattr(builtins, "input", lambda prompt: next(inputs))
    monkeypatch.setattr("builtins.print", output.append)

    main()

    assert output[-1] == "Player X wins!"
