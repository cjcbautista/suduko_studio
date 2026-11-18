import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def create_game(client, difficulty="easy"):
    response = client.get(f"/api/puzzle?difficulty={difficulty}")
    assert response.status_code == 200
    return response.get_json()


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sudoku Studio" in response.data
    assert b"Top 10" in response.data


def test_puzzle_endpoint_returns_requested_level_without_solution(client):
    data = create_game(client, "medium")
    assert data["difficulty"] == "medium"
    assert len(data["puzzle"]) == 9
    assert "solution" not in data
    assert len(data["game_id"]) == 32


def test_invalid_difficulty_returns_helpful_error(client):
    response = client.get("/api/puzzle?difficulty=impossible")
    assert response.status_code == 400
    assert "easy, medium, or hard" in response.get_json()["error"]


def test_check_and_hint_work_for_active_game(client):
    game = create_game(client)
    board = game["puzzle"]

    check = client.post("/api/check", json={"game_id": game["game_id"], "board": board})
    assert check.status_code == 200
    assert check.get_json()["complete"] is False

    hint = client.post("/api/hint", json={"game_id": game["game_id"], "board": board})
    assert hint.status_code == 200
    hint_data = hint.get_json()
    assert board[hint_data["row"]][hint_data["col"]] == 0
    assert 1 <= hint_data["value"] <= 9


def test_hints_remain_available_after_five(client):
    game = create_game(client)
    board = [row[:] for row in game["puzzle"]]

    for _ in range(6):
        hint = client.post("/api/hint", json={"game_id": game["game_id"], "board": board})
        assert hint.status_code == 200
        hint_data = hint.get_json()
        board[hint_data["row"]][hint_data["col"]] = hint_data["value"]


def test_check_rejects_bad_board_and_unknown_game(client):
    response = client.post("/api/check", json={"game_id": "missing", "board": [[0] * 9 for _ in range(9)]})
    assert response.status_code == 404

    game = create_game(client)
    response = client.post("/api/check", json={"game_id": game["game_id"], "board": [[0]]})
    assert response.status_code == 400
    assert "9 rows of 9 cells" in response.get_json()["error"]


def test_api_404_is_json(client):
    response = client.get("/api/not-real")
    assert response.status_code == 404
    assert response.is_json
