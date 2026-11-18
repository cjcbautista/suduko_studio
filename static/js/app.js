"use strict";

const STORAGE_KEYS = { scores: "sudoku-top10-v1", theme: "sudoku-theme" };
const state = {
  gameId: null,
  puzzle: [],
  board: [],
  locked: new Set(),
  difficulty: "medium",
  hints: 0,
  seconds: 0,
  timerId: null,
  selected: null,
  completed: false,
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  Object.assign(elements, {
    board: document.querySelector("#game-board"),
    difficulty: document.querySelector("#difficulty"),
    newGame: document.querySelector("#new-game"),
    hint: document.querySelector("#hint"),
    check: document.querySelector("#check"),
    timer: document.querySelector("#timer"),
    hintCount: document.querySelector("#hint-count"),
    levelLabel: document.querySelector("#level-label"),
    status: document.querySelector("#status"),
    themeToggle: document.querySelector("#theme-toggle"),
    themeIcon: document.querySelector(".theme-icon"),
    themeLabel: document.querySelector(".theme-label"),
    leaderboardBody: document.querySelector("#leaderboard-body"),
    emptyScores: document.querySelector("#empty-scores"),
    clearScores: document.querySelector("#clear-scores"),
    numberPad: document.querySelector(".number-pad"),
    completeDialog: document.querySelector("#complete-dialog"),
    completionSummary: document.querySelector("#completion-summary"),
    scoreForm: document.querySelector("#score-form"),
    playerName: document.querySelector("#player-name"),
    closeDialog: document.querySelector("#close-dialog"),
  });

  bindEvents();
  syncThemeControl();
  renderLeaderboard();
  startNewGame();
});

function bindEvents() {
  elements.newGame.addEventListener("click", startNewGame);
  elements.difficulty.addEventListener("change", startNewGame);
  elements.hint.addEventListener("click", requestHint);
  elements.check.addEventListener("click", () => checkBoard({ announce: true }));
  elements.themeToggle.addEventListener("click", toggleTheme);
  elements.board.addEventListener("input", handleCellInput);
  elements.board.addEventListener("focusin", handleCellFocus);
  elements.board.addEventListener("keydown", handleBoardKeydown);
  elements.numberPad.addEventListener("click", handleNumberPad);
  elements.scoreForm.addEventListener("submit", saveCompletedScore);
  elements.closeDialog.addEventListener("click", () => elements.completeDialog.close());
  elements.clearScores.addEventListener("click", clearLeaderboard);
}

async function startNewGame() {
  stopTimer();
  setControlsBusy(true);
  setStatus("Creating a unique puzzle…");
  state.difficulty = elements.difficulty.value;
  state.hints = 0;
  state.seconds = 0;
  state.completed = false;
  state.selected = null;
  updateStats();

  try {
    const response = await fetch(`/api/puzzle?difficulty=${encodeURIComponent(state.difficulty)}`);
    const data = await parseResponse(response);
    state.gameId = data.game_id;
    state.puzzle = data.puzzle.map(row => [...row]);
    state.board = data.puzzle.map(row => [...row]);
    state.locked = new Set();
    renderBoard();
    setStatus("Puzzle ready. Select an empty cell to begin.");
    startTimer();
  } catch (error) {
    setStatus(error.message, "error");
    elements.board.replaceChildren();
  } finally {
    setControlsBusy(false);
  }
}

function renderBoard() {
  const fragment = document.createDocumentFragment();
  for (let row = 0; row < 9; row += 1) {
    for (let col = 0; col < 9; col += 1) {
      const cell = document.createElement("input");
      const value = state.board[row][col];
      const isGiven = state.puzzle[row][col] !== 0;
      cell.type = "text";
      cell.inputMode = "numeric";
      cell.pattern = "[1-9]";
      cell.maxLength = 1;
      cell.className = "sudoku-cell";
      cell.dataset.row = String(row);
      cell.dataset.col = String(col);
      cell.setAttribute("role", "gridcell");
      cell.setAttribute("aria-label", `Row ${row + 1}, column ${col + 1}${isGiven ? `, given ${value}` : ""}`);
      cell.value = value === 0 ? "" : String(value);
      cell.readOnly = isGiven;
      cell.tabIndex = row === 0 && col === 0 ? 0 : -1;
      if (((Math.floor(row / 3) + Math.floor(col / 3)) % 2) === 1) cell.classList.add("block-alt");
      if (col === 2 || col === 5) cell.classList.add("border-right");
      if (row === 2 || row === 5) cell.classList.add("border-bottom");
      if (isGiven) cell.classList.add("given");
      fragment.append(cell);
    }
  }
  elements.board.replaceChildren(fragment);
  elements.board.setAttribute("aria-busy", "false");
  updateNumberTracking();
}

function handleCellInput(event) {
  const cell = event.target.closest(".sudoku-cell");
  if (!cell || cell.readOnly || state.completed) return;
  const value = cell.value.replace(/[^1-9]/g, "").slice(-1);
  cell.value = value;
  const row = Number(cell.dataset.row);
  const col = Number(cell.dataset.col);
  state.board[row][col] = value ? Number(value) : 0;
  cell.classList.remove("incorrect");
  validateVisibleBoard();
  selectCell(row, col);
  updateNumberTracking();
  if (value && isBoardFilled()) checkBoard({ announce: false });
}

function handleCellFocus(event) {
  const cell = event.target.closest(".sudoku-cell");
  if (!cell) return;
  selectCell(Number(cell.dataset.row), Number(cell.dataset.col));
}

function handleBoardKeydown(event) {
  const cell = event.target.closest(".sudoku-cell");
  if (!cell) return;
  const row = Number(cell.dataset.row);
  const col = Number(cell.dataset.col);
  const moves = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
  if (moves[event.key]) {
    event.preventDefault();
    const [deltaRow, deltaCol] = moves[event.key];
    focusCell((row + deltaRow + 9) % 9, (col + deltaCol + 9) % 9);
  } else if ((event.key === "Backspace" || event.key === "Delete") && !cell.readOnly) {
    event.preventDefault();
    setCellValue(row, col, 0);
  }
}

function handleNumberPad(event) {
  const button = event.target.closest("[data-number]");
  if (!button || !state.selected || state.completed) return;
  const [row, col] = state.selected;
  const cell = getCell(row, col);
  if (!cell || cell.readOnly) return;
  setCellValue(row, col, Number(button.dataset.number));
  cell.focus();
}

function setCellValue(row, col, value) {
  const cell = getCell(row, col);
  if (!cell || cell.readOnly) return;
  cell.value = value === 0 ? "" : String(value);
  state.board[row][col] = value;
  cell.classList.remove("incorrect");
  validateVisibleBoard();
  selectCell(row, col);
  updateNumberTracking();
  if (value && isBoardFilled()) checkBoard({ announce: false });
}

function selectCell(row, col) {
  state.selected = [row, col];
  const selectedValue = state.board[row][col];
  document.querySelectorAll(".sudoku-cell").forEach(cell => {
    const cellRow = Number(cell.dataset.row);
    const cellCol = Number(cell.dataset.col);
    const sameBox = Math.floor(cellRow / 3) === Math.floor(row / 3) && Math.floor(cellCol / 3) === Math.floor(col / 3);
    const isSelected = cellRow === row && cellCol === col;
    cell.classList.toggle("selected", isSelected);
    cell.classList.toggle("peer", !isSelected && (cellRow === row || cellCol === col || sameBox));
    cell.classList.toggle("match", !isSelected && selectedValue !== 0 && state.board[cellRow][cellCol] === selectedValue);
    cell.tabIndex = isSelected ? 0 : -1;
  });
}

function focusCell(row, col) {
  const cell = getCell(row, col);
  if (cell) cell.focus();
}

function getCell(row, col) {
  return elements.board.querySelector(`[data-row="${row}"][data-col="${col}"]`);
}

function validateVisibleBoard() {
  const conflicts = new Set();
  const markDuplicates = coordinates => {
    const seen = new Map();
    coordinates.forEach(([row, col]) => {
      const value = state.board[row][col];
      if (!value) return;
      if (!seen.has(value)) seen.set(value, []);
      seen.get(value).push([row, col]);
    });
    seen.forEach(cells => {
      if (cells.length > 1) cells.forEach(([row, col]) => conflicts.add(`${row}-${col}`));
    });
  };

  for (let index = 0; index < 9; index += 1) {
    markDuplicates(Array.from({ length: 9 }, (_, col) => [index, col]));
    markDuplicates(Array.from({ length: 9 }, (_, row) => [row, index]));
  }
  for (let boxRow = 0; boxRow < 3; boxRow += 1) {
    for (let boxCol = 0; boxCol < 3; boxCol += 1) {
      const cells = [];
      for (let row = boxRow * 3; row < boxRow * 3 + 3; row += 1) {
        for (let col = boxCol * 3; col < boxCol * 3 + 3; col += 1) cells.push([row, col]);
      }
      markDuplicates(cells);
    }
  }

  document.querySelectorAll(".sudoku-cell").forEach(cell => {
    const key = `${cell.dataset.row}-${cell.dataset.col}`;
    const invalid = conflicts.has(key);
    cell.classList.toggle("invalid", invalid);
    cell.setAttribute("aria-invalid", invalid ? "true" : "false");
    if (invalid) cell.title = "This number conflicts with its row, column, or region.";
    else if (!cell.classList.contains("incorrect")) cell.removeAttribute("title");
  });
  if (conflicts.size) setStatus("Conflict found. Repeated numbers are underlined.", "error");
  return conflicts.size === 0;
}

async function checkBoard({ announce }) {
  if (!state.gameId || state.completed) return;
  if (!validateVisibleBoard()) return;
  setControlsBusy(true);
  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game_id: state.gameId, board: state.board }),
    });
    const data = await parseResponse(response);
    const wrong = new Set(data.incorrect.map(([row, col]) => `${row}-${col}`));
    document.querySelectorAll(".sudoku-cell").forEach(cell => {
      const isWrong = wrong.has(`${cell.dataset.row}-${cell.dataset.col}`);
      cell.classList.toggle("incorrect", isWrong);
      if (isWrong) {
        cell.setAttribute("aria-invalid", "true");
        cell.title = "This value is not correct for this cell.";
      }
    });
    if (data.complete) finishGame();
    else if (announce || isBoardFilled()) {
      setStatus(wrong.size ? `${wrong.size} ${wrong.size === 1 ? "cell needs" : "cells need"} another look.` : "No mistakes so far. Keep going!", wrong.size ? "error" : "success");
    }
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    setControlsBusy(false);
  }
}

async function requestHint() {
  if (!state.gameId || state.completed) return;
  setControlsBusy(true);
  try {
    const response = await fetch("/api/hint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game_id: state.gameId, board: state.board }),
    });
    const data = await parseResponse(response);
    const cell = getCell(data.row, data.col);
    state.board[data.row][data.col] = data.value;
    state.locked.add(`${data.row}-${data.col}`);
    cell.value = String(data.value);
    cell.readOnly = true;
    cell.classList.remove("invalid", "incorrect");
    cell.classList.add("hint-cell");
    cell.setAttribute("aria-label", `Row ${data.row + 1}, column ${data.col + 1}, hint ${data.value}`);
    state.hints += 1;
    updateStats();
    validateVisibleBoard();
    selectCell(data.row, data.col);
    updateNumberTracking();
    setStatus(`Hint placed in row ${data.row + 1}, column ${data.col + 1}.`, "success");
    if (isBoardFilled()) checkBoard({ announce: false });
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    setControlsBusy(false);
  }
}

function finishGame() {
  if (state.completed) return;
  state.completed = true;
  updateStats();
  stopTimer();
  document.querySelectorAll(".sudoku-cell").forEach(cell => { cell.readOnly = true; });
  const summary = `${formatTime(state.seconds)} · ${capitalize(state.difficulty)} · ${state.hints} ${state.hints === 1 ? "hint" : "hints"}`;
  elements.completionSummary.textContent = `You finished in ${summary}.`;
  setStatus(`Congratulations! Solved in ${formatTime(state.seconds)}.`, "success");
  elements.playerName.value = "";
  elements.completeDialog.showModal();
  window.setTimeout(() => elements.playerName.focus(), 50);
}

function saveCompletedScore(event) {
  event.preventDefault();
  const name = elements.playerName.value.trim();
  if (!name) {
    elements.playerName.focus();
    return;
  }
  const scores = loadScores();
  const entry = {
    id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`,
    name: name.slice(0, 24),
    time: state.seconds,
    difficulty: state.difficulty,
    hints: state.hints,
    savedAt: new Date().toISOString(),
  };
  scores.push(entry);
  scores.sort((a, b) => a.time - b.time || a.hints - b.hints || a.name.localeCompare(b.name));
  const topTen = scores.slice(0, 10);
  localStorage.setItem(STORAGE_KEYS.scores, JSON.stringify(topTen));
  elements.completeDialog.close();
  renderLeaderboard();
  setStatus(topTen.some(score => score.id === entry.id)
    ? "Score saved to this browser's Top 10."
    : "Great solve! This time fell outside the current Top 10.", "success");
}

function loadScores() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEYS.scores) || "[]");
    return Array.isArray(parsed) ? parsed.filter(score => score && typeof score.name === "string" && Number.isFinite(score.time)) : [];
  } catch (_error) {
    return [];
  }
}

function renderLeaderboard() {
  const scores = loadScores().slice(0, 10);
  const fragment = document.createDocumentFragment();
  scores.forEach((score, index) => {
    const row = document.createElement("tr");
    [String(index + 1), score.name, formatTime(score.time), capitalize(score.difficulty), String(score.hints)].forEach(value => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    fragment.append(row);
  });
  elements.leaderboardBody.replaceChildren(fragment);
  elements.emptyScores.hidden = scores.length > 0;
  elements.clearScores.hidden = scores.length === 0;
}

function clearLeaderboard() {
  if (!loadScores().length) return;
  if (window.confirm("Clear all locally saved Top 10 scores?")) {
    localStorage.removeItem(STORAGE_KEYS.scores);
    renderLeaderboard();
    setStatus("Local leaderboard cleared.");
  }
}

function startTimer() {
  stopTimer();
  state.timerId = window.setInterval(() => {
    state.seconds += 1;
    elements.timer.textContent = formatTime(state.seconds);
  }, 1000);
}

function stopTimer() {
  if (state.timerId) window.clearInterval(state.timerId);
  state.timerId = null;
}

function updateStats() {
  elements.timer.textContent = formatTime(state.seconds);
  elements.hintCount.textContent = String(state.hints);
  elements.levelLabel.textContent = capitalize(state.difficulty);
  elements.hint.disabled = state.completed;
}

function updateNumberTracking() {
  for (let number = 1; number <= 9; number += 1) {
    const count = state.board.flat().filter(value => value === number).length;
    const button = elements.numberPad?.querySelector(`[data-number="${number}"]`);
    if (button) {
      button.classList.toggle("complete-number", count === 9);
      button.setAttribute("aria-label", count === 9 ? `${number}, all nine placed` : `${number}, ${count} of nine placed`);
    }
  }
}

function isBoardFilled() {
  return state.board.length === 9 && state.board.every(row => row.every(value => value !== 0));
}

function setControlsBusy(isBusy) {
  elements.newGame.disabled = isBusy;
  elements.check.disabled = isBusy;
  elements.hint.disabled = isBusy || state.completed;
}

function setStatus(message, kind = "") {
  elements.status.textContent = message;
  elements.status.className = `status${kind ? ` ${kind}` : ""}`;
}

function toggleTheme() {
  const isDark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = isDark ? "light" : "dark";
  localStorage.setItem(STORAGE_KEYS.theme, isDark ? "light" : "dark");
  syncThemeControl();
}

function syncThemeControl() {
  const isDark = document.documentElement.dataset.theme === "dark";
  elements.themeToggle.setAttribute("aria-pressed", String(isDark));
  elements.themeToggle.setAttribute("aria-label", `Switch to ${isDark ? "light" : "dark"} mode`);
  elements.themeIcon.textContent = isDark ? "☀" : "☾";
  elements.themeLabel.textContent = isDark ? "Light" : "Dark";
}

async function parseResponse(response) {
  let data;
  try { data = await response.json(); }
  catch (_error) { throw new Error("The server returned an unreadable response."); }
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function capitalize(value) {
  return value ? value[0].toUpperCase() + value.slice(1) : "";
}
