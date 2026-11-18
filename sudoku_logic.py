"""Sudoku generation, solving, and validation utilities.

The generator starts from a randomized valid grid and removes clues only when the
remaining puzzle still has exactly one solution.  Keeping this module independent
from Flask makes the core rules easy to test and reuse.
"""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Iterable, List, Sequence

Board = List[List[int]]
BOARD_SIZE = 9
BOX_SIZE = 3
DIGITS = set(range(1, 10))
DIFFICULTY_CLUES = {"easy": 40, "medium": 32, "hard": 27}


def _is_board_shape_valid(board: Sequence[Sequence[int]]) -> bool:
    return (
        isinstance(board, (list, tuple))
        and len(board) == BOARD_SIZE
        and all(isinstance(row, (list, tuple)) and len(row) == BOARD_SIZE for row in board)
    )


def normalize_board(board: Sequence[Sequence[int]]) -> Board:
    """Return a validated integer board, raising ValueError for malformed input."""
    if not _is_board_shape_valid(board):
        raise ValueError("Board must contain exactly 9 rows of 9 cells.")

    normalized: Board = []
    for row in board:
        normalized_row: list[int] = []
        for value in row:
            if isinstance(value, bool):
                raise ValueError("Board values must be integers from 0 to 9.")
            try:
                number = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError("Board values must be integers from 0 to 9.") from exc
            if number < 0 or number > 9:
                raise ValueError("Board values must be integers from 0 to 9.")
            normalized_row.append(number)
        normalized.append(normalized_row)
    return normalized


def _unit_has_no_duplicates(values: Iterable[int]) -> bool:
    filled = [value for value in values if value != 0]
    return len(filled) == len(set(filled))


def is_valid_board(board: Sequence[Sequence[int]], *, complete: bool = False) -> bool:
    """Return whether a board obeys Sudoku row, column, and box constraints."""
    try:
        grid = normalize_board(board)
    except ValueError:
        return False

    if complete and any(0 in row for row in grid):
        return False

    for index in range(BOARD_SIZE):
        if not _unit_has_no_duplicates(grid[index]):
            return False
        if not _unit_has_no_duplicates(grid[row][index] for row in range(BOARD_SIZE)):
            return False

    for box_row in range(0, BOARD_SIZE, BOX_SIZE):
        for box_col in range(0, BOARD_SIZE, BOX_SIZE):
            values = (
                grid[row][col]
                for row in range(box_row, box_row + BOX_SIZE)
                for col in range(box_col, box_col + BOX_SIZE)
            )
            if not _unit_has_no_duplicates(values):
                return False
    return True


def candidates(board: Board, row: int, col: int) -> set[int]:
    """Return valid candidate digits for an empty cell."""
    if board[row][col] != 0:
        return set()
    used = set(board[row])
    used.update(board[r][col] for r in range(BOARD_SIZE))
    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    used.update(
        board[r][c]
        for r in range(start_row, start_row + BOX_SIZE)
        for c in range(start_col, start_col + BOX_SIZE)
    )
    return DIGITS - used


def _next_empty_cell(board: Board) -> tuple[int, int, set[int]] | None:
    """Choose the empty cell with the fewest candidates (MRV heuristic)."""
    best: tuple[int, int, set[int]] | None = None
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 0:
                options = candidates(board, row, col)
                if not options:
                    return row, col, set()
                if best is None or len(options) < len(best[2]):
                    best = (row, col, options)
                    if len(options) == 1:
                        return best
    return best


def solve_sudoku(board: Sequence[Sequence[int]], *, randomize: bool = False) -> Board | None:
    """Solve a Sudoku board and return a new grid, or None if it is unsolvable."""
    grid = normalize_board(board)
    if not is_valid_board(grid):
        return None

    def search() -> bool:
        choice = _next_empty_cell(grid)
        if choice is None:
            return True
        row, col, options = choice
        if not options:
            return False
        values = list(options)
        if randomize:
            random.shuffle(values)
        else:
            values.sort()
        for value in values:
            grid[row][col] = value
            if search():
                return True
            grid[row][col] = 0
        return False

    return grid if search() else None


def count_solutions(board: Sequence[Sequence[int]], limit: int = 2) -> int:
    """Count solutions up to ``limit``; stopping at two makes uniqueness checks fast."""
    if limit < 1:
        raise ValueError("Solution-count limit must be at least 1.")
    grid = normalize_board(board)
    if not is_valid_board(grid):
        return 0

    found = 0

    def search() -> None:
        nonlocal found
        if found >= limit:
            return
        choice = _next_empty_cell(grid)
        if choice is None:
            found += 1
            return
        row, col, options = choice
        if not options:
            return
        for value in sorted(options):
            grid[row][col] = value
            search()
            grid[row][col] = 0
            if found >= limit:
                return

    search()
    return found


def generate_solution(rng: random.Random | None = None) -> Board:
    """Generate a randomized, fully solved grid using Sudoku-preserving shuffles."""
    rng = rng or random.Random()

    def shuffled(values: Iterable[int]) -> list[int]:
        result = list(values)
        rng.shuffle(result)
        return result

    rows = [group * BOX_SIZE + row for group in shuffled(range(BOX_SIZE)) for row in shuffled(range(BOX_SIZE))]
    cols = [group * BOX_SIZE + col for group in shuffled(range(BOX_SIZE)) for col in shuffled(range(BOX_SIZE))]
    numbers = shuffled(range(1, BOARD_SIZE + 1))

    def pattern(row: int, col: int) -> int:
        return (BOX_SIZE * (row % BOX_SIZE) + row // BOX_SIZE + col) % BOARD_SIZE

    return [[numbers[pattern(row, col)] for col in cols] for row in rows]


def generate_puzzle(
    difficulty: str = "medium",
    *,
    rng: random.Random | None = None,
) -> tuple[Board, Board]:
    """Generate a unique-solution puzzle and its solution for the requested level."""
    level = difficulty.lower().strip()
    if level not in DIFFICULTY_CLUES:
        raise ValueError("Difficulty must be easy, medium, or hard.")

    rng = rng or random.Random()
    solution = generate_solution(rng)
    puzzle = deepcopy(solution)
    positions = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]
    rng.shuffle(positions)
    clues = BOARD_SIZE * BOARD_SIZE
    target = DIFFICULTY_CLUES[level]

    for row, col in positions:
        if clues <= target:
            break
        saved = puzzle[row][col]
        puzzle[row][col] = 0
        if count_solutions(puzzle, limit=2) != 1:
            puzzle[row][col] = saved
        else:
            clues -= 1

    # A particular removal order can occasionally stall above the target.  The
    # level remains valid and unique; regenerate a few times to hit its clue band.
    if clues > target + 2:
        return generate_puzzle(level, rng=rng)
    return puzzle, solution


def incorrect_cells(board: Sequence[Sequence[int]], solution: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return coordinates of filled cells that differ from the known solution."""
    grid = normalize_board(board)
    solved = normalize_board(solution)
    return [
        [row, col]
        for row in range(BOARD_SIZE)
        for col in range(BOARD_SIZE)
        if grid[row][col] != 0 and grid[row][col] != solved[row][col]
    ]


def puzzle_matches_solution(puzzle: Sequence[Sequence[int]], solution: Sequence[Sequence[int]]) -> bool:
    """Return whether every clue in ``puzzle`` agrees with ``solution``."""
    try:
        start = normalize_board(puzzle)
        solved = normalize_board(solution)
    except ValueError:
        return False
    return is_valid_board(solved, complete=True) and all(
        start[row][col] in (0, solved[row][col])
        for row in range(BOARD_SIZE)
        for col in range(BOARD_SIZE)
    )
