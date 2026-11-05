# Tic-Tac-Toe

A simple command-line Tic-Tac-Toe game written in Python.

## Goal

Build a clean and well-tested implementation of Tic-Tac-Toe while learning GitHub Copilot's:

- Agent workflows
- Planning capabilities
- Code reviews
- Test generation
- Documentation generation

## Requirements

### Gameplay

- Two players (X and O)
- 3x3 board
- Alternate turns
- Detect winner
- Detect draw
- Prevent invalid moves

### Future Features

- Computer opponent
- Difficulty levels
- Score tracking
- Save/load game

## Implementation Coverage

| Requirement | Core game model | Command-line game | Local web game |
| --- | --- | --- | --- |
| Two players (X and O) | Implemented | Implemented | Implemented |
| 3x3 board | Implemented | Implemented | Implemented |
| Alternate turns | Implemented | Implemented | Implemented |
| Detect winner | Implemented | Implemented | Implemented |
| Detect draw | Implemented | Implemented | Implemented |
| Prevent invalid moves | Implemented | Implemented | Implemented |

The game model and human-versus-human command-line and local web interfaces cover all listed gameplay requirements. Computer opponent, difficulty levels, score tracking, and save/load remain future features.

The current 1.0 candidate scope and status are documented in [RELEASE_NOTES.md](RELEASE_NOTES.md).

## Playing in a Browser

The local web interface lets two players use the same game rules as the command-line game. Start the server from the repository root:

```shell
python web_app.py
```

Open the loopback URL printed by the server in a browser on the same machine. The server asks the operating system for an available port and binds only to `127.0.0.1`. Select an empty square; the board and active-player status update after each move. Winning symbols are crossed by a line, and simultaneous winning lines are all shown. Choose **New game** to reset the board.

## Running the Game

Requires Python 3.10 through 3.14 (the versions covered by CI). From the repository root, start the game with:

```shell
python tic_tac_toe.py
```

Enter a position from 1 to 9, using the numbered board displayed on screen. Surrounding whitespace is accepted. Invalid or occupied positions show an error and let the same player try again. The game exits after a win or draw; press Ctrl+C or send end-of-file to cancel.

## Running Tests

Install the pinned pytest development dependency, then run the test suite:

```shell
python -m pip install -r requirements-dev.txt
python -m pytest
```
