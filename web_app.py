import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any

from game import Game, GameStatus, InvalidMoveError


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tic-Tac-Toe</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center;
           background: #f3f5f8; color: #172033; }
    main { width: min(92vw, 25rem); text-align: center; }
    .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: .55rem;
             margin: 1.5rem 0; position: relative; }
    .cell { aspect-ratio: 1; border: 0; border-radius: .8rem; background: white;
            box-shadow: 0 2px 8px #17203318; color: #2154a3; font-size: 3rem;
            font-weight: 700; cursor: pointer; }
    .cell:focus-visible, .reset:focus-visible { outline: 3px solid #e08b24;
                                                  outline-offset: 3px; }
    .cell:disabled { cursor: default; color: #172033; }
    .strike-overlay { position: absolute; inset: 0; width: 100%; height: 100%;
                      pointer-events: none; overflow: visible; }
    .strike-overlay line { stroke: #d92d20; stroke-width: 8;
                           stroke-linecap: round; }
    .status { min-height: 1.5em; font-size: 1.2rem; font-weight: 600; }
    .error { min-height: 1.5em; color: #a12525; }
    .reset { border: 0; border-radius: .55rem; padding: .7rem 1rem;
             background: #2154a3; color: white; font: inherit; cursor: pointer; }
  </style>
</head>
<body>
  <main>
    <h1>Tic-Tac-Toe</h1>
    <p id="status" class="status" role="status" aria-live="polite">Loading game…</p>
    <div id="board" class="board" role="group" aria-label="Tic-Tac-Toe board">
      <button class="cell" data-position="1" aria-label="Position 1"></button>
      <button class="cell" data-position="2" aria-label="Position 2"></button>
      <button class="cell" data-position="3" aria-label="Position 3"></button>
      <button class="cell" data-position="4" aria-label="Position 4"></button>
      <button class="cell" data-position="5" aria-label="Position 5"></button>
      <button class="cell" data-position="6" aria-label="Position 6"></button>
      <button class="cell" data-position="7" aria-label="Position 7"></button>
      <button class="cell" data-position="8" aria-label="Position 8"></button>
      <button class="cell" data-position="9" aria-label="Position 9"></button>
      <svg class="strike-overlay" viewBox="0 0 300 300" aria-hidden="true"></svg>
    </div>
    <p id="error" class="error" role="alert" aria-live="assertive"></p>
    <button id="new-game" class="reset" type="button">New game</button>
  </main>
  <script>
    const statusNode = document.querySelector("#status");
    const errorNode = document.querySelector("#error");
    const cells = [...document.querySelectorAll(".cell")];
    let busy = false;

    function render(state) {
      window.currentState = state;
      statusNode.textContent = state.status === "in_progress"
        ? `Player ${state.current_player}, choose a square`
        : state.status === "won" ? `Player ${state.winner} wins!` : "It's a draw!";
      cells.forEach((button, index) => {
        const mark = state.board[Math.floor(index / 3)][index % 3];
        button.textContent = mark || "";
        button.setAttribute("aria-label", `Position ${index + 1}${mark ? `, ${mark}` : ""}`);
        button.disabled = busy || state.status !== "in_progress" || mark !== null;
      });
      const overlay = document.querySelector(".strike-overlay");
      overlay.replaceChildren(...state.winning_lines.map(line => {
        const svgRect = overlay.getBoundingClientRect();
        const centers = line.map(([row, column]) => {
          const cellRect = cells[row * 3 + column].getBoundingClientRect();
          return {
            x: ((cellRect.left + cellRect.width / 2 - svgRect.left) / svgRect.width) * 300,
            y: ((cellRect.top + cellRect.height / 2 - svgRect.top) / svgRect.height) * 300
          };
        });
        const strike = document.createElementNS("http://www.w3.org/2000/svg", "line");
        strike.setAttribute("x1", centers[0].x);
        strike.setAttribute("y1", centers[0].y);
        strike.setAttribute("x2", centers[2].x);
        strike.setAttribute("y2", centers[2].y);
        return strike;
      }));
    }

    async function request(path, body) {
      busy = true;
      cells.forEach(button => button.disabled = true);
      errorNode.textContent = "";
      try {
        const response = await fetch(path, body ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        } : {});
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Request failed.");
        render(result);
      } catch (error) {
        errorNode.textContent = error.message || "Unable to reach the game server.";
        await refresh();
      } finally {
        busy = false;
        if (window.currentState) render(window.currentState);
      }
    }

    async function refresh() {
      try {
        const response = await fetch("/api/state");
        const state = await response.json();
        if (!response.ok) throw new Error(state.error || "Unable to load game.");
        window.currentState = state;
        render(state);
      } catch (error) {
        errorNode.textContent = error.message || "Unable to reach the game server.";
      }
    }

    cells.forEach(button => button.addEventListener("click", () => {
      request("/api/move", { position: Number(button.dataset.position) });
    }));
    document.querySelector("#new-game").addEventListener("click", () => {
      request("/api/new-game", {});
    });
    refresh();
  </script>
</body>
</html>
"""


def _game_state(game: Game) -> dict[str, Any]:
    return {
        "board": [
            [cell.value if cell is not None else None for cell in row]
            for row in game.board
        ],
        "current_player": game.current_player.value,
        "winner": game.winner.value if game.winner is not None else None,
        "status": game.status.value,
        "winning_lines": [
            [list(position) for position in line] for line in game.winning_lines
        ],
    }


def create_handler() -> type[BaseHTTPRequestHandler]:
    game = Game()
    game_lock = Lock()

    class GameRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/":
                self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            elif self.path == "/api/state":
                with game_lock:
                    self._send_json(200, _game_state(game))
            else:
                self._send_json(404, {"error": "Not found."})

        def do_POST(self) -> None:
            if self.path not in {"/api/move", "/api/new-game"}:
                self._send_json(404, {"error": "Not found."})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 1024:
                    raise ValueError
                payload = json.loads(self.rfile.read(length))
            except (ValueError, json.JSONDecodeError):
                self._send_json(400, {"error": "Request body must be valid JSON."})
                return

            if not isinstance(payload, dict):
                self._send_json(400, {"error": "Request body must be a JSON object."})
                return

            with game_lock:
                if self.path == "/api/new-game":
                    nonlocal game
                    game = Game()
                    self._send_json(200, _game_state(game))
                    return

                position = payload.get("position")
                if type(position) is not int or not 1 <= position <= 9:
                    self._send_json(400, {"error": "Choose a position from 1 to 9."})
                    return

                row, column = divmod(position - 1, 3)
                try:
                    game.make_move(row, column)
                except InvalidMoveError as error:
                    self._send_json(400, {"error": str(error)})
                    return
                self._send_json(200, _game_state(game))

        def _send_json(self, status: int, value: dict[str, Any]) -> None:
            body = json.dumps(value).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return GameRequestHandler


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("The web game server must bind to IPv4 loopback 127.0.0.1.")
    return ThreadingHTTPServer((host, port), create_handler())


def main() -> None:
    server = create_server(host="127.0.0.1", port=0)
    print(f"Open http://127.0.0.1:{server.server_port}/ to play.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWeb game server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
