import math
import random

# ─────────────────────────────────────────────
#  Board Constants
# ─────────────────────────────────────────────
ROWS = 6
COLS = 7

EMPTY   = 0
PLAYER1 = 1   # Human  → "X"
PLAYER2 = 2   # AI     → "O"

# ─────────────────────────────────────────────
#  Board Utilities  (unchanged from starter)
# ─────────────────────────────────────────────
def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    print("\n+" + "---+" * COLS)
    for row in board:
        print("|", end="")
        for cell in row:
            if   cell == PLAYER1: ch = " X "
            elif cell == PLAYER2: ch = " O "
            else:                 ch = "   "
            print(ch + "|", end="")
        print()
        print("+" + "---+" * COLS)
    print("  " + "   ".join(str(i) for i in range(COLS)))
    print()

def is_valid_column(board, col):
    if col < 0 or col >= COLS:
        return False
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def winning_move(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Diagonal down-right
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    # Diagonal up-right
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

def is_board_full(board):
    return all(board[0][c] != EMPTY for c in range(COLS))

def get_valid_columns(board):
    return [c for c in range(COLS) if is_valid_column(board, c)]

def copy_board(board):
    return [row[:] for row in board]

# ─────────────────────────────────────────────
#  AI: Heuristic Scoring
# ─────────────────────────────────────────────
# score_window evaluates a 4-cell "window" and returns a numeric score.
# Higher score  → better for AI (PLAYER2)
# Lower score   → better for human (PLAYER1)

def score_window(window, piece):
    """
    Score a list of 4 cells for 'piece'.

    Algorithm
    ---------
    +100  if piece fills all 4  (win)
    + 10  if piece fills 3, 1 empty
    +  5  if piece fills 2, 2 empty
    - 80  if opponent fills 3, 1 empty  (block threat)
    """
    score     = 0
    opp_piece = PLAYER1 if piece == PLAYER2 else PLAYER2

    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opp_count   = window.count(opp_piece)

    if piece_count == 4:
        score += 100
    elif piece_count == 3 and empty_count == 1:
        score += 10
    elif piece_count == 2 and empty_count == 2:
        score += 5

    if opp_count == 3 and empty_count == 1:
        score -= 80          # must block

    return score


def score_board(board, piece):
    """
    Aggregate heuristic score for the entire board.

    Strategy layers (applied in order of importance)
    -------------------------------------------------
    1. Centre column control – pieces in the centre column score +3 each.
       Rationale: the centre column participates in more winning lines
       than any other column.

    2. Horizontal windows – slide a 4-wide window across every row.

    3. Vertical windows – slide a 4-tall window down every column.

    4. Diagonal windows (both directions).
    """
    score = 0

    # 1. Centre column preference
    centre_col  = COLS // 2
    centre_array = [board[r][centre_col] for r in range(ROWS)]
    score += centre_array.count(piece) * 3

    # 2. Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c+i] for i in range(4)]
            score += score_window(window, piece)

    # 3. Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            window = [board[r+i][c] for i in range(4)]
            score += score_window(window, piece)

    # 4. Diagonal ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, piece)

    # 4. Diagonal ↗
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += score_window(window, piece)

    return score

# ─────────────────────────────────────────────
#  AI: Minimax with Alpha-Beta Pruning
# ─────────────────────────────────────────────
"""
ALGORITHM OVERVIEW
==================

Minimax explores the game tree up to a fixed depth, assuming:
  • The AI (PLAYER2 / maximising player) always picks the best move for itself.
  • The human (PLAYER1 / minimising player) always picks the worst move for AI.

Alpha-Beta Pruning cuts branches that cannot affect the final decision:
  • alpha = best score the MAXIMISER is already guaranteed.
  • beta  = best score the MINIMISER is already guaranteed.
  • If alpha >= beta, the current branch is pruned (skipped).

Depth controls how many moves ahead the AI thinks.
  depth=4  → fast, moderate strength
  depth=6  → stronger but slightly slower (still < 1 s on modern hardware)

Terminal states:
  • AI wins  → return +math.inf
  • Human wins → return -math.inf
  • Board full (draw) → return 0
  • Depth reached → return score_board() heuristic

Move ordering: centre columns are tried first to improve pruning efficiency.
"""

DEPTH = 5   # look-ahead depth (increase for stronger AI, decrease for speed)

def minimax(board, depth, alpha, beta, maximising_player):
    """
    Returns (best_column, best_score).

    Parameters
    ----------
    board              : current board state (2-D list)
    depth              : remaining search depth
    alpha, beta        : pruning bounds
    maximising_player  : True when it is the AI's turn
    """
    valid_cols = get_valid_columns(board)

    # ── Terminal / depth checks ──────────────────────────────────────────
    if winning_move(board, PLAYER2):
        return (None, math.inf)         # AI wins – best possible outcome
    if winning_move(board, PLAYER1):
        return (None, -math.inf)        # Human wins – worst outcome for AI
    if not valid_cols or depth == 0:
        return (None, score_board(board, PLAYER2))

    # ── Move ordering: try centre columns first ──────────────────────────
    ordered = sorted(valid_cols, key=lambda c: -abs(c - COLS // 2) * -1)

    # ── Maximising (AI turn) ─────────────────────────────────────────────
    if maximising_player:
        best_score = -math.inf
        best_col   = random.choice(valid_cols)

        for col in ordered:
            row       = get_next_open_row(board, col)
            temp      = copy_board(board)
            drop_piece(temp, row, col, PLAYER2)
            _, score  = minimax(temp, depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_col   = col

            alpha = max(alpha, score)
            if alpha >= beta:
                break   # β-cutoff (prune remaining branches)

        return best_col, best_score

    # ── Minimising (Human turn – AI simulates opponent) ──────────────────
    else:
        best_score = math.inf
        best_col   = random.choice(valid_cols)

        for col in ordered:
            row       = get_next_open_row(board, col)
            temp      = copy_board(board)
            drop_piece(temp, row, col, PLAYER1)
            _, score  = minimax(temp, depth - 1, alpha, beta, True)

            if score < best_score:
                best_score = score
                best_col   = col

            beta = min(beta, score)
            if alpha >= beta:
                break   # α-cutoff (prune remaining branches)

        return best_col, best_score


def ai_move(board):
    """
    Entry point: ask Minimax for the best column and drop the AI piece.
    Returns the column chosen.
    """
    col, score = minimax(board, DEPTH, -math.inf, math.inf, True)
    # Fallback: if minimax returns None (shouldn't happen), pick random
    if col is None or not is_valid_column(board, col):
        col = random.choice(get_valid_columns(board))
    row = get_next_open_row(board, col)
    drop_piece(board, row, col, PLAYER2)
    return col

# ─────────────────────────────────────────────
#  Game Modes
# ─────────────────────────────────────────────

def human_turn(board, player):
    """Ask a human player to choose a column. Returns chosen column."""
    label = "X" if player == PLAYER1 else "O"
    while True:
        try:
            col = int(input(f"  Player {player} ({label}) – choose column (0-6): "))
        except ValueError:
            print("  ✗ Invalid input. Enter a number 0–6.")
            continue
        if not is_valid_column(board, col):
            print("  ✗ Column is full or out of range. Try again.")
            continue
        return col


def play_game(mode):
    """
    mode:
      "pvp"  – Player 1 (X) vs Player 2 (O), both human
      "pva"  – Player 1 (X) human, Player 2 (O) AI
      "ava"  – Both players controlled by AI
    """
    board     = create_board()
    game_over = False
    turn      = PLAYER1

    print("\n" + "=" * 45)
    mode_labels = {"pvp": "Player vs Player", "pva": "Player vs AI", "ava": "AI vs AI"}
    print(f"  Mode: {mode_labels[mode]}")
    print("=" * 45)

    while not game_over:
        print_board(board)

        # ── Determine who moves ──────────────────────────────────────────
        if mode == "pvp":
            col = human_turn(board, turn)
            drop_piece(board, get_next_open_row(board, col), col, turn)

        elif mode == "pva":
            if turn == PLAYER1:
                col = human_turn(board, turn)
                drop_piece(board, get_next_open_row(board, col), col, turn)
            else:
                print("  AI (O) is thinking …")
                col = ai_move(board)
                print(f"  AI (O) chose column {col}")

        elif mode == "ava":
            if turn == PLAYER1:
                # For AI vs AI, both use minimax – Player 1 minimises from Player 2's view
                col, _ = minimax(board, DEPTH, -math.inf, math.inf, False)
                if col is None or not is_valid_column(board, col):
                    col = random.choice(get_valid_columns(board))
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER1)
                print(f"  AI-1 (X) chose column {col}")
            else:
                print("  AI-2 (O) is thinking …")
                col = ai_move(board)
                print(f"  AI-2 (O) chose column {col}")

            # Small pause so moves are readable in AI vs AI mode
            input("  [Press Enter to continue]")

        # ── Check win / draw ─────────────────────────────────────────────
        if winning_move(board, turn):
            print_board(board)
            label = "X" if turn == PLAYER1 else "O"
            who   = "AI" if (mode == "pva" and turn == PLAYER2) else f"Player {turn}"
            print(f"🏆  {who} ({label}) wins!\n")
            game_over = True

        elif is_board_full(board):
            print_board(board)
            print("🤝  It's a draw!\n")
            game_over = True

        else:
            turn = PLAYER2 if turn == PLAYER1 else PLAYER1


# ─────────────────────────────────────────────
#  Main Menu
# ─────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════╗")
    print("║       CONNECT FOUR  🔴🟡         ║")
    print("╚══════════════════════════════════╝")

    while True:
        print("\nSelect game mode:")
        print("  1 – Player vs Player")
        print("  2 – Player vs AI")
        print("  3 – AI vs AI")
        print("  q – Quit")
        choice = input("\nEnter choice: ").strip().lower()

        if   choice == "1": play_game("pvp")
        elif choice == "2": play_game("pva")
        elif choice == "3": play_game("ava")
        elif choice == "q":
            print("Thanks for playing! Goodbye 👋\n")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or q.")

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! Goodbye 👋\n")
            break

if __name__ == "__main__":
    main()