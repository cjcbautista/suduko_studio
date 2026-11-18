# Sudoku Studio

A complete local Flask Sudoku application based on the Udacity `github-copilot-python` starter and project rubric. Every generated puzzle is validated to have exactly one solution.

## Features

- Easy, Medium, and Hard unique-solution puzzles
- Locked original clues and locked, visually distinct hints
- Immediate row/column/3×3 conflict feedback plus server-backed **Check**
- **Hint** that fills one correct empty cell
- Timer, completion dialog, and congratulatory summary
- Browser-local Top 10 with player, time, difficulty, and hints
- Responsive keyboard-friendly interface, visible focus, live status messages, and non-color error cues
- Persistent light/dark mode
- Alternating 3×3 region colors and number tracking
- Modular Python/JavaScript and graceful JSON errors
- Pytest unit and API test suite

## Windows quick start

Prerequisites: Windows 10/11, Python 3.11 or newer, and a current browser.

1. Extract the ZIP to a normal folder such as `C:\Users\YourName\Documents\sudoku-studio`.
2. Double-click **`setup_windows.bat`** once. It creates `.venv` and installs the exact dependencies.
3. Double-click **`run_windows.bat`** whenever you want to play.
4. If the browser does not open automatically, visit <http://127.0.0.1:5000>.
5. Stop the server with **Ctrl+C** in its Command Prompt window.

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for manual commands and troubleshooting.

## Cross-platform manual setup

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

Open <http://127.0.0.1:5000>.

## Run tests

```bash
python -m pytest
```

Optional coverage report:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Project structure

```text
sudoku-studio/
├── .github/copilot-instructions.md  # repository-wide Copilot guidance
├── Screenshots/README.md            # rubric evidence capture checklist
├── static/css/styles.css            # responsive light/dark UI
├── static/js/app.js                 # board, timer, hints, checks, Top 10
├── templates/index.html             # accessible application shell
├── tests/                            # Sudoku and Flask API tests
├── app.py                            # Flask routes and in-memory game store
├── sudoku_logic.py                   # generator, solver, uniqueness counter
├── prompts.json                     # reusable Copilot prompts
├── instruction.md                   # human-readable instruction copy
├── setup_windows.bat                # one-time Windows setup
└── run_windows.bat                  # Windows launcher
```

## Design and security notes

- The solution stays server-side. The browser receives only the puzzle and a random game ID; **Check** and **Hint** use that ID.
- Active games are held in process memory and expire after four hours. Restarting the server starts fresh games, while the leaderboard and theme remain in the browser's `localStorage`.
- Puzzle generation removes clues one at a time and retains a removal only when `count_solutions(..., limit=2)` returns exactly one.
- Difficulty uses target clue counts: Easy 40, Medium 32, Hard 27. A generator pass may retain up to two extra clues if a removal would break uniqueness.
- The local leaderboard sorts by fastest time, then fewest hints, and keeps ten entries. Clearing site data clears it.

## Rubric mapping

| Requirement | Implementation |
|---|---|
| Copilot instruction file | `.github/copilot-instructions.md` and `instruction.md` |
| Testing framework | `pytest.ini`, `requirements-dev.txt`, `tests/` |
| Unique solution | `count_solutions` gate in `generate_puzzle`; parameterized tests |
| Easy/Medium/Hard | selector + `DIFFICULTY_CLUES` |
| Locked clues | read-only given cells in `renderBoard` |
| Invalid-move feedback | event-delegated input handler, duplicate detection, underline + live message |
| Hint and Check | `/api/hint`, `/api/check`, client controls |
| Timer and completion | interval timer and accessible completion dialog |
| Local Top 10 | `localStorage` key `sudoku-top10-v1` |
| Responsive and dark mode | CSS media queries and persisted theme |
| Alternating 3×3 colors | `block-alt` based on region parity |
| Error handling | validated payloads and JSON 400/404/500 responses |

## GitHub Copilot evidence

The application and testable code are complete. The rubric's prompt/response screenshots must be captured from **your own authenticated Copilot session**; they should not be fabricated. `Screenshots/README.md` provides the exact prompt checklist and filenames, while `prompts.json` contains ready-to-use prompts.

## License

MIT — see [LICENSE.txt](LICENSE.txt).
