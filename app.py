"""Flask entry point for Sudoku Studio."""

from __future__ import annotations

import os
import random
import time
import uuid
from dataclasses import dataclass
from threading import Lock
from typing import Any

from flask import Flask, jsonify, render_template, request

from sudoku_logic import generate_puzzle, incorrect_cells, normalize_board

GAME_TTL_SECONDS = 4 * 60 * 60
MAX_GAMES = 200


@dataclass
class Game:
    puzzle: list[list[int]]
    solution: list[list[int]]
    difficulty: str
    created_at: float


class GameStore:
    """Small, thread-safe in-memory game store suitable for a local app."""

    def __init__(self) -> None:
        self._games: dict[str, Game] = {}
        self._lock = Lock()

    def _discard_expired(self) -> None:
        cutoff = time.time() - GAME_TTL_SECONDS
        expired = [game_id for game_id, game in self._games.items() if game.created_at < cutoff]
        for game_id in expired:
            self._games.pop(game_id, None)
        if len(self._games) > MAX_GAMES:
            oldest = sorted(self._games, key=lambda game_id: self._games[game_id].created_at)
            for game_id in oldest[: len(self._games) - MAX_GAMES]:
                self._games.pop(game_id, None)

    def add(self, game: Game) -> str:
        with self._lock:
            self._discard_expired()
            game_id = uuid.uuid4().hex
            self._games[game_id] = game
            return game_id

    def get(self, game_id: str) -> Game | None:
        with self._lock:
            self._discard_expired()
            return self._games.get(game_id)

def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "local-development-only"),
        JSON_SORT_KEYS=False,
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)

    game_store = GameStore()
    rng = random.Random(2026) if app.config.get("TESTING") else None

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/puzzle")
    def new_puzzle():
        difficulty = request.args.get("difficulty", "medium").lower().strip()
        if difficulty not in {"easy", "medium", "hard"}:
            return jsonify(error="Difficulty must be easy, medium, or hard."), 400

        puzzle, solution = generate_puzzle(difficulty, rng=rng)
        game_id = game_store.add(
            Game(puzzle=puzzle, solution=solution, difficulty=difficulty, created_at=time.time())
        )
        return jsonify(game_id=game_id, puzzle=puzzle, difficulty=difficulty)

    def parse_game_request() -> tuple[Game | None, list[list[int]] | None, tuple[Any, int] | None]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None, None, (jsonify(error="A JSON request body is required."), 400)

        game_id = payload.get("game_id")
        if not isinstance(game_id, str) or not game_id:
            return None, None, (jsonify(error="A valid game_id is required."), 400)
        game = game_store.get(game_id)
        if game is None:
            return None, None, (jsonify(error="Game not found or expired. Start a new puzzle."), 404)

        try:
            board = normalize_board(payload.get("board"))
        except ValueError as exc:
            return None, None, (jsonify(error=str(exc)), 400)
        return game, board, None

    @app.post("/api/check")
    def check_puzzle():
        game, board, error = parse_game_request()
        if error:
            return error
        assert game is not None and board is not None
        wrong = incorrect_cells(board, game.solution)
        complete = not wrong and all(value != 0 for row in board for value in row)
        return jsonify(incorrect=wrong, complete=complete)

    @app.post("/api/hint")
    def hint():
        game, board, error = parse_game_request()
        if error:
            return error
        assert game is not None and board is not None

        available = [
            (row, col)
            for row in range(9)
            for col in range(9)
            if board[row][col] == 0
        ]
        if not available:
            return jsonify(error="No empty cells are available for a hint."), 409
        row, col = random.choice(available)
        return jsonify(row=row, col=col, value=game.solution[row][col])

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="API route not found."), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        app.logger.exception("Unexpected application error")
        if request.path.startswith("/api/"):
            return jsonify(error="An unexpected error occurred. Please try again."), 500
        return "An unexpected error occurred.", 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
