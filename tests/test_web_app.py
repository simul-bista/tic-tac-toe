import json
import threading
from collections.abc import Iterator
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from web_app import create_server


@pytest.fixture
def web_url() -> Iterator[str]:
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join()
    server.server_close()


def request_json(
    url: str, path: str, payload: dict[str, object] | None = None
) -> tuple[int, dict[str, object]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{url}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    try:
        response = urlopen(request)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.loads(response.read())


def test_home_page_has_accessible_board_controls_and_new_game(web_url: str) -> None:
    with urlopen(web_url) as response:
        page = response.read().decode("utf-8")

    assert response.status == 200
    assert 'aria-label="Tic-Tac-Toe board"' in page
    assert all(f'aria-label="Position {position}"' in page for position in range(1, 10))
    assert 'aria-live="polite"' in page
    assert 'id="new-game"' in page


@pytest.mark.parametrize(
    ("position", "row", "column"),
    [(position, (position - 1) // 3, (position - 1) % 3) for position in range(1, 10)],
)
def test_api_maps_positions_and_alternates_players(
    web_url: str, position: int, row: int, column: int
) -> None:
    status, state = request_json(web_url, "/api/move", {"position": position})

    assert status == 200
    board = state["board"]
    assert board[row][column] == "X"
    assert state["current_player"] == "O"
    assert state["winning_lines"] == []


@pytest.mark.parametrize("position", [0, 10, True, "1", None])
def test_api_rejects_invalid_positions_without_mutation(
    web_url: str, position: object
) -> None:
    before_status, before = request_json(web_url, "/api/state")
    status, result = request_json(web_url, "/api/move", {"position": position})
    after_status, after = request_json(web_url, "/api/state")

    assert before_status == after_status == 200
    assert status == 400
    assert "position from 1 to 9" in result["error"]
    assert after == before


def test_api_rejects_occupied_cell_and_keeps_turn(web_url: str) -> None:
    request_json(web_url, "/api/move", {"position": 5})
    status, result = request_json(web_url, "/api/move", {"position": 5})
    _, state = request_json(web_url, "/api/state")

    assert status == 400
    assert result["error"] == "cell is already occupied"
    assert state["current_player"] == "O"
    assert state["board"][1][1] == "X"


def test_api_reports_winner_and_rejects_moves_after_game_over(web_url: str) -> None:
    for position in (1, 4, 2, 5, 3):
        status, state = request_json(web_url, "/api/move", {"position": position})
        assert status == 200

    assert state["status"] == "won"
    assert state["winner"] == "X"
    assert state["current_player"] == "X"
    assert state["winning_lines"] == [[[0, 0], [0, 1], [0, 2]]]
    status, result = request_json(web_url, "/api/move", {"position": 9})
    assert status == 400
    assert result["error"] == "game is already over"
    status, reset_state = request_json(web_url, "/api/new-game", {})
    assert status == 200
    assert reset_state["winning_lines"] == []


def test_api_reports_draw_and_new_game_resets_state(web_url: str) -> None:
    state: dict[str, object] = {}
    for position in (1, 2, 3, 5, 4, 7, 6, 9, 8):
        status, state = request_json(web_url, "/api/move", {"position": position})
        assert status == 200
    assert state["status"] == "draw"
    assert state["winner"] is None
    assert state["winning_lines"] == []
    status, error = request_json(web_url, "/api/move", {"position": 1})
    assert status == 400
    assert error["error"] == "game is already over"

    status, reset_state = request_json(web_url, "/api/new-game", {})
    assert status == 200
    assert reset_state["status"] == "in_progress"
    assert reset_state["current_player"] == "X"
    assert reset_state["winner"] is None
    assert reset_state["board"] == [[None] * 3 for _ in range(3)]
    assert reset_state["winning_lines"] == []


@pytest.mark.parametrize(
    ("moves", "expected_line"),
    [
        ((1, 4, 2, 5, 3), [[0, 0], [0, 1], [0, 2]]),
        ((1, 4, 2, 5, 9, 6), [[1, 0], [1, 1], [1, 2]]),
        ((1, 2, 5, 3, 9), [[0, 0], [1, 1], [2, 2]]),
        ((1, 2, 3, 5, 4, 8), [[0, 1], [1, 1], [2, 1]]),
        ((1, 3, 2, 5, 4, 7), [[0, 2], [1, 1], [2, 0]]),
    ],
)
def test_api_returns_winning_line_coordinates(
    web_url: str, moves: tuple[int, ...], expected_line: list[list[int]]
) -> None:
    for position in moves:
        status, state = request_json(web_url, "/api/move", {"position": position})
        assert status == 200

    assert state["status"] == "won"
    assert expected_line in state["winning_lines"]


@pytest.mark.parametrize("host", ["0.0.0.0", "192.0.2.1", "::1", "localhost"])
def test_server_refuses_non_loopback_bind_addresses(host: str) -> None:
    with pytest.raises(ValueError, match="loopback"):
        create_server(host=host, port=0)
