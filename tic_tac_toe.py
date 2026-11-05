from collections.abc import Callable, Sequence

from game import Game, GameStatus, InvalidMoveError, Player


def parse_move(value: str) -> tuple[int, int]:
    try:
        position = int(value.strip())
    except ValueError as error:
        raise ValueError("Enter a number from 1 to 9.") from error

    if not 1 <= position <= 9:
        raise ValueError("Position must be from 1 to 9.")

    return divmod(position - 1, 3)


def format_board(board: Sequence[Sequence[Player | None]]) -> str:
    rows = []
    for row_index, row in enumerate(board):
        cells = [
            f" {cell.value if cell is not None else row_index * 3 + column_index + 1} "
            for column_index, cell in enumerate(row)
        ]
        rows.append("|".join(cells))
    return "\n---+---+---\n".join(rows)


def run_game(
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> None:
    if input_fn is None:
        input_fn = input
    if output_fn is None:
        output_fn = print

    game = Game()
    output_fn(format_board(game.board))

    while game.status is GameStatus.IN_PROGRESS:
        try:
            response = input_fn(
                f"Player {game.current_player.value}, choose a position (1-9): "
            )
        except (EOFError, KeyboardInterrupt):
            output_fn("\nGame cancelled.")
            return

        try:
            row, column = parse_move(response)
            game.make_move(row, column)
        except InvalidMoveError as error:
            output_fn(str(error))
            continue
        except ValueError as error:
            output_fn(str(error))
            continue

        output_fn(format_board(game.board))
        if game.status is GameStatus.WON:
            output_fn(f"Player {game.winner.value} wins!")
        elif game.status is GameStatus.DRAW:
            output_fn("The game is a draw.")


def main() -> None:
    run_game()


if __name__ == "__main__":
    main()
