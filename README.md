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

| Requirement | Core game model | Command-line game |
| --- | --- | --- |
| Two players (X and O) | Implemented | Implemented |
| 3x3 board | Implemented | Implemented |
| Alternate turns | Implemented | Implemented |
| Detect winner | Implemented | Implemented |
| Detect draw | Implemented | Implemented |
| Prevent invalid moves | Implemented | Implemented |

The game model and human-versus-human command-line game cover all listed gameplay requirements. Computer opponent, difficulty levels, score tracking, and save/load remain future features.

The current 1.0 candidate scope and status are documented in [RELEASE_NOTES.md](RELEASE_NOTES.md).

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
