# GitHub Copilot repository instructions

## Project context

This repository is a local Sudoku web application built with Python 3.11+, Flask, semantic HTML, plain CSS, and dependency-free browser JavaScript. Preserve that lightweight stack unless a task explicitly requires a dependency.

## Required behavior

- Generated puzzles must have exactly one solution.
- Keep difficulty values limited to `easy`, `medium`, and `hard`.
- Original clues and hint-filled cells must remain locked.
- Hint fills one correct empty cell. Check marks all filled incorrect cells.
- Input must receive immediate row, column, and 3×3 conflict feedback.
- Timer stops only on a confirmed correct completion.
- Top 10 stays in browser `localStorage` and contains name, seconds, difficulty, and hint count.
- Preserve responsive light/dark styling and alternating 3×3 region colors.
- Do not expose the puzzle solution in the initial API response.

## Python guidance

- Keep Sudoku rules in `sudoku_logic.py`, independent of Flask.
- Add type hints and concise docstrings to public functions.
- Validate all request data and return useful JSON errors with correct HTTP status codes.
- Use the MRV heuristic for solver/count performance, and stop uniqueness counts at two.
- Avoid mutable default arguments and broad `except Exception` blocks in core logic.
- Add or update pytest coverage for every logic or endpoint change.

## JavaScript guidance

- Use event delegation for board input.
- Build DOM text with `textContent`, not `innerHTML`, when values can come from users.
- Keep visible and assistive feedback synchronized with `aria-invalid`, live regions, labels, and focus.
- Avoid adding a build step. Use modern browser APIs supported by current Edge, Chrome, and Firefox.
- Persist only theme and Top 10 scores; do not store or trust the solution in the browser.

## CSS and accessibility guidance

- Maintain keyboard operation, visible focus, and a minimum 320px viewport.
- Do not communicate errors by color alone; retain the underline and status text.
- Keep contrast usable in both themes and respect `prefers-reduced-motion`.
- Use relative or fluid sizing for the board.

## Definition of done

1. `python -m pytest` passes.
2. Easy, Medium, and Hard each generate a valid unique puzzle.
3. Flask starts with `python app.py` and `/api/puzzle`, `/api/check`, and `/api/hint` respond correctly.
4. Desktop and narrow layouts remain usable in light and dark mode.
5. README and Windows steps still match actual commands.
