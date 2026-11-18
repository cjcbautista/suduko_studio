# Copilot instructions: Sudoku Studio

Use `.github/copilot-instructions.md` as the repository-wide source of truth.

Build and maintain a modular Flask Sudoku application using Python, HTML, CSS, and JavaScript. Every generated puzzle must have exactly one solution and must support Easy, Medium, and Hard. Keep given and hint cells locked; give immediate accessible conflict feedback; preserve Hint, Check, the timer, completion dialog, dark mode, responsive styling, and the local Top 10 fields (player name, time, difficulty, and hints).

Keep Sudoku logic independent of Flask, validate API input, do not return the solution to the browser, use event delegation, avoid unsafe user HTML, and add pytest coverage for behavior changes. A change is complete only when the automated tests pass and the UI remains keyboard-usable in both themes.
