import random

import pytest

from sudoku_logic import (
    DIFFICULTY_CLUES,
    count_solutions,
    generate_puzzle,
    incorrect_cells,
    is_valid_board,
    normalize_board,
    puzzle_matches_solution,
    solve_sudoku,
)


KNOWN_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def test_solver_returns_valid_complete_grid():
    solved = solve_sudoku(KNOWN_PUZZLE)
    assert solved is not None
    assert is_valid_board(solved, complete=True)
    assert puzzle_matches_solution(KNOWN_PUZZLE, solved)


def test_known_puzzle_has_one_solution():
    assert count_solutions(KNOWN_PUZZLE) == 1


def test_invalid_board_has_no_solution():
    invalid = [row[:] for row in KNOWN_PUZZLE]
    invalid[0][2] = 5
    assert count_solutions(invalid) == 0
    assert solve_sudoku(invalid) is None


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generated_puzzle_is_valid_unique_and_in_difficulty_band(difficulty):
    puzzle, solution = generate_puzzle(difficulty, rng=random.Random(100 + len(difficulty)))
    clue_count = sum(value != 0 for row in puzzle for value in row)
    assert DIFFICULTY_CLUES[difficulty] <= clue_count <= DIFFICULTY_CLUES[difficulty] + 2
    assert is_valid_board(puzzle)
    assert is_valid_board(solution, complete=True)
    assert puzzle_matches_solution(puzzle, solution)
    assert count_solutions(puzzle) == 1
    assert solve_sudoku(puzzle) == solution


def test_incorrect_cells_reports_only_filled_mistakes():
    puzzle, solution = generate_puzzle("easy", rng=random.Random(7))
    board = [row[:] for row in puzzle]
    row, col = next((r, c) for r in range(9) for c in range(9) if board[r][c] == 0)
    board[row][col] = (solution[row][col] % 9) + 1
    assert [row, col] in incorrect_cells(board, solution)


@pytest.mark.parametrize("bad_board", [None, [], [[0] * 9] * 8, [[10] * 9 for _ in range(9)]])
def test_normalize_board_rejects_malformed_input(bad_board):
    with pytest.raises(ValueError):
        normalize_board(bad_board)


def test_unknown_difficulty_is_rejected():
    with pytest.raises(ValueError, match="Difficulty"):
        generate_puzzle("extreme")
