# Connect Four with AI Opponent 🔴🟡

A terminal-based Connect Four game written in Python featuring an AI opponent powered by the **Minimax algorithm with Alpha-Beta Pruning**. Supports three game modes: Player vs Player, Player vs AI, and AI vs AI.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [Game Modes](#game-modes)
- [AI Algorithm](#ai-algorithm)
- [Heuristic Scoring](#heuristic-scoring)
- [Configuration](#configuration)
- [Example Output](#example-output)

---

## Overview

Connect Four is a two-player strategy game played on a 6-row × 7-column vertical grid. Players alternate dropping discs into columns; the first to align four discs horizontally, vertically, or diagonally wins.

This project implements the full game engine alongside an AI opponent that uses adversarial search to play strategically. The AI looks 5 moves ahead by default and applies a board heuristic to evaluate non-terminal positions.

---

## Features

- ✅ Full Connect Four game engine (move validation, win detection, draw detection)
- 🤖 AI opponent using Minimax + Alpha-Beta Pruning (depth = 5)
- 🎮 Three game modes: PvP, PvA, AvA
- 📊 Heuristic board evaluation (centre control, threat detection, blocking)
- 🔁 Play-again loop from main menu

---

## Project Structure

```
connect_four/
├── connect_four.py      # Main game file (all logic in one module)
└── README.md            # This file
```

### Module Layout inside `connect_four.py`

| Section | Functions | Description |
|---|---|---|
| Board Utilities | `create_board`, `print_board`, `drop_piece`, `is_valid_column`, `get_next_open_row`, `is_board_full`, `get_valid_columns`, `copy_board` | Core game engine |
| Win Detection | `winning_move` | Checks all 4-in-a-row directions |
| AI Heuristic | `score_window`, `score_board` | Board evaluation function |
| AI Search | `minimax`, `ai_move` | Minimax with alpha-beta pruning |
| Game Modes | `human_turn`, `play_game` | Turn management and I/O |
| Entry Point | `main` | Menu loop |

---

## Requirements

- Python 3.7 or higher
- No external libraries required (uses only `math` and `random` from the standard library)

---

## How to Run

```bash
python connect_four.py
```

You will see a menu:

```
╔══════════════════════════════════╗
║       CONNECT FOUR  🔴🟡         ║
╚══════════════════════════════════╝

Select game mode:
  1 – Player vs Player
  2 – Player vs AI
  3 – AI vs AI
  q – Quit
```

Enter `1`, `2`, `3`, or `q` and press Enter.

---

## Game Modes

| Mode | Key | Description |
|------|-----|-------------|
| Player vs Player | `1` | Two humans alternate turns on the same machine |
| Player vs AI | `2` | Human plays as X; AI plays as O |
| AI vs AI | `3` | Watch two AI instances play each other (press Enter between moves) |

---

## AI Algorithm

The AI uses **Minimax with Alpha-Beta Pruning**, a classical adversarial search algorithm.

### How it works — step by step

```
1. AI receives a copy of the current board state.

2. minimax() is called with:
     depth = 5  (look-ahead moves)
     alpha = -∞, beta = +∞
     maximising_player = True  (AI's turn)

3. For each valid column (centre columns tried first):
     a. Simulate dropping the AI's disc into that column.
     b. Recursively call minimax() with depth-1, player flipped.

4. At each recursive call, check terminal conditions first:
     • AI wins  → return +∞
     • Human wins → return -∞
     • Board full or depth = 0 → return score_board() heuristic

5. Update alpha (maximiser) or beta (minimiser) after each child.
   If alpha ≥ beta → prune remaining branches (stop exploring).

6. Return the column with the highest guaranteed score.
```

### Why Alpha-Beta Pruning?

Without pruning, Minimax evaluates every node in the tree. Alpha-beta skips branches that cannot change the outcome, reducing the effective branching factor from ~7 to ~√7 ≈ 2.6 in the best case — allowing deeper search in the same time.

### Search Tree Diagram

```
              [Board State]
              maximising (AI)
            /       |        \
         col0     col3      col6      ← try each valid column
          |         |         |
       [state]  [state]   [state]
       minimise  minimise  minimise   ← simulate human response
        / \       / \       / \
       …   …     …   …     …   …     ← depth continues to 5
                                        then heuristic score
```

---

## Heuristic Scoring

When the search reaches its depth limit (no terminal state), `score_board()` estimates how good the position is for the AI.

### score_window() — evaluating a 4-cell window

| Pattern | Score |
|---------|-------|
| AI has 4 in window | +100 |
| AI has 3 + 1 empty | +10 |
| AI has 2 + 2 empty | +5 |
| Opponent has 3 + 1 empty | −80 (block threat) |

### score_board() — full board evaluation

1. **Centre column bonus** — each AI piece in column 3 scores +3 (centre participates in the most winning lines)
2. **Horizontal** — slide 4-wide windows across every row
3. **Vertical** — slide 4-tall windows down every column
4. **Diagonal ↘** and **Diagonal ↗** — slide windows along both diagonal directions

The total score guides the AI toward positions with more threats and away from positions where the opponent is about to win.

---

## Configuration

You can tune the AI by changing constants at the top of the AI section in `connect_four.py`:

```python
DEPTH = 5   # look-ahead depth
            # 4 → faster, slightly weaker
            # 6 → stronger, ~2-3s per move
```

Board size constants (changing these requires no other edits):

```python
ROWS = 6
COLS = 7
```

---

## Example Output

```
+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+
|   |   |   | O |   |   |   |
+---+---+---+---+---+---+---+
|   |   |   | X | O |   |   |
+---+---+---+---+---+---+---+
|   |   | X | O | X |   |   |
+---+---+---+---+---+---+---+
|   | X | O | X | O | X |   |
+---+---+---+---+---+---+---+
  0   1   2   3   4   5   6

  Player 1 (X) – choose column (0-6):
```

---

## Authors

| Name | Role |
|------|------|
| Ngoc Chung Tran | Implement PvA modes. Minimax, alpha-beta pruning AvA mode. |
| Edwin Tong | Implement board game engine, PVP modes.|
| Brian Memishi | UI, unit testing, heuristic scoring, final report. |

---

## License

This project is submitted as coursework for an Artificial Intelligence course. All code is original.
