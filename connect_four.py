import math
import random
from typing import Optional

# ─────────────────────────────────────────────
# Board Constants
# ─────────────────────────────────────────────
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER1 = 1  # Human / X
PLAYER2 = 2  # AI / O

DEPTH = 5  # AI look-ahead depth


# ─────────────────────────────────────────────
# Board Utilities
# ─────────────────────────────────────────────
def create_board() -> list[list[int]]:
    """Create and return an empty Connect Four board."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def print_board(board: list[list[int]]) -> None:
    """Print the board in a readable terminal format."""
    print("\n+" + "---+" * COLS)

    for row in board:
        print("|", end="")
        for cell in row:
            if cell == PLAYER1:
                ch = " X "
            elif cell == PLAYER2:
                ch = " O "
            else:
                ch = "   "
            print(ch + "|", end="")
        print()
        print("+" + "---+" * COLS)

    print(" " + "   ".join(str(i) for i in range(COLS)))
    print()


def is_valid_column(board: list[list[int]], col: int) -> bool:
    """Return True if col is inside the board and not full."""
    return 0 <= col < COLS and board[0][col] == EMPTY


def get_next_open_row(board: list[list[int]], col: int) -> Optional[int]:
    """Return the lowest available row in a column, or None if full."""
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board: list[list[int]], row: int, col: int, piece: int) -> None:
    """Place a piece on the board."""
    board[row][col] = piece


def is_board_full(board: list[list[int]]) -> bool:
    """Return True if the board has no open columns."""
    return all(board[0][col] != EMPTY for col in range(COLS))


def get_valid_columns(board: list[list[int]]) -> list[int]:
    """Return all columns that can currently accept a piece."""
    return [col for col in range(COLS) if is_valid_column(board, col)]


def copy_board(board: list[list[int]]) -> list[list[int]]:
    """Return a deep copy of the board."""
    return [row[:] for row in board]


# ─────────────────────────────────────────────
# Win Detection
# ─────────────────────────────────────────────
def winning_move(board: list[list[int]], piece: int) -> bool:
    """Check whether the given piece has four in a row."""

    # Horizontal wins
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == piece for i in range(4)):
                return True

    # Vertical wins
    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == piece for i in range(4)):
                return True

    # Diagonal down-right wins
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == piece for i in range(4)):
                return True

    # Diagonal up-right wins
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == piece for i in range(4)):
                return True

    return False


# ─────────────────────────────────────────────
# AI Heuristic Scoring
# ─────────────────────────────────────────────
def score_window(window: list[int], piece: int) -> int:
    """
    Score a 4-cell window for the AI heuristic.

    Positive scores favor the selected piece.
    Negative scores punish dangerous opponent threats.
    """
    score = 0
    opponent = PLAYER1 if piece == PLAYER2 else PLAYER2

    piece_count = window.count(piece)
    empty_count = window.count(EMPTY)
    opponent_count = window.count(opponent)

    if piece_count == 4:
        score += 100
    elif piece_count == 3 and empty_count == 1:
        score += 10
    elif piece_count == 2 and empty_count == 2:
        score += 5

    # Strong penalty so the AI prioritizes blocking immediate threats.
    if opponent_count == 3 and empty_count == 1:
        score -= 80

    return score


def score_board(board: list[list[int]], piece: int) -> int:
    """Evaluate the board position for the given piece."""
    score = 0

    # Center control is valuable because the center participates in many lines.
    center_col = COLS // 2
    center_array = [board[row][center_col] for row in range(ROWS)]
    score += center_array.count(piece) * 3

    # Horizontal windows
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [board[row][col + i] for i in range(4)]
            score += score_window(window, piece)

    # Vertical windows
    for col in range(COLS):
        for row in range(ROWS - 3):
            window = [board[row + i][col] for i in range(4)]
            score += score_window(window, piece)

    # Diagonal down-right windows
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += score_window(window, piece)

    # Diagonal up-right windows
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += score_window(window, piece)

    return score


# ─────────────────────────────────────────────
# AI Search: Minimax with Alpha-Beta Pruning
# ─────────────────────────────────────────────
def order_columns(valid_columns: list[int]) -> list[int]:
    """Try center columns first to improve alpha-beta pruning efficiency."""
    center = COLS // 2
    return sorted(valid_columns, key=lambda col: abs(center - col))


def minimax(
    board: list[list[int]],
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,
) -> tuple[Optional[int], float]:
    """
    Return the best column and score using Minimax with Alpha-Beta Pruning.

    The AI is PLAYER2 and tries to maximize the board score.
    The simulated opponent is PLAYER1 and tries to minimize the board score.
    """
    valid_columns = get_valid_columns(board)

    # Terminal checks
    if winning_move(board, PLAYER2):
        return None, math.inf
    if winning_move(board, PLAYER1):
        return None, -math.inf
    if not valid_columns:
        return None, 0
    if depth == 0:
        return None, score_board(board, PLAYER2)

    ordered_columns = order_columns(valid_columns)

    if maximizing_player:
        best_score = -math.inf
        best_col = random.choice(valid_columns)

        for col in ordered_columns:
            row = get_next_open_row(board, col)
            if row is None:
                continue

            temp_board = copy_board(board)
            drop_piece(temp_board, row, col, PLAYER2)

            _, score = minimax(temp_board, depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_col = col

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_col, best_score

    best_score = math.inf
    best_col = random.choice(valid_columns)

    for col in ordered_columns:
        row = get_next_open_row(board, col)
        if row is None:
            continue

        temp_board = copy_board(board)
        drop_piece(temp_board, row, col, PLAYER1)

        _, score = minimax(temp_board, depth - 1, alpha, beta, True)

        if score < best_score:
            best_score = score
            best_col = col

        beta = min(beta, best_score)
        if alpha >= beta:
            break

    return best_col, best_score


def ai_move(board: list[list[int]], piece: int = PLAYER2) -> int:
    """Choose and make an AI move. Returns the selected column."""
    if piece == PLAYER2:
        col, _ = minimax(board, DEPTH, -math.inf, math.inf, True)
    else:
        # In AI vs AI mode, PLAYER1 acts as the minimizing player.
        col, _ = minimax(board, DEPTH, -math.inf, math.inf, False)

    valid_columns = get_valid_columns(board)
    if col is None or col not in valid_columns:
        col = random.choice(valid_columns)

    row = get_next_open_row(board, col)
    if row is None:
        raise ValueError("AI selected a full column.")

    drop_piece(board, row, col, piece)
    return col


# ─────────────────────────────────────────────
# Game Modes and Input
# ─────────────────────────────────────────────
def human_turn(board: list[list[int]], player: int) -> int:
    """Ask a human player to choose a valid column."""
    label = "X" if player == PLAYER1 else "O"

    while True:
        try:
            col = int(input(f"Player {player} ({label}) - choose column (0-{COLS - 1}): "))
        except ValueError:
            print(f"Invalid input. Enter a number from 0 to {COLS - 1}.")
            continue

        if not is_valid_column(board, col):
            print("Column is full or out of range. Try again.")
            continue

        return col


def get_winner_name(mode: str, turn: int) -> str:
    """Return a clean winner label based on game mode and current turn."""
    label = "X" if turn == PLAYER1 else "O"

    if mode == "pva" and turn == PLAYER2:
        return f"AI ({label})"
    if mode == "ava":
        return f"AI-{turn} ({label})"
    return f"Player {turn} ({label})"


def play_game(mode: str) -> None:
    """
    Play one game.

    Modes:
    pvp - Player vs Player
    pva - Player vs AI
    ava - AI vs AI
    """
    board = create_board()
    turn = PLAYER1
    game_over = False

    mode_labels = {
        "pvp": "Player vs Player",
        "pva": "Player vs AI",
        "ava": "AI vs AI",
    }

    print("\n" + "=" * 45)
    print(f"Mode: {mode_labels[mode]}")
    print("=" * 45)

    while not game_over:
        print_board(board)

        if mode == "pvp":
            col = human_turn(board, turn)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, turn)

        elif mode == "pva":
            if turn == PLAYER1:
                col = human_turn(board, turn)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, turn)
            else:
                print("AI (O) is thinking...")
                col = ai_move(board, PLAYER2)
                print(f"AI (O) chose column {col}")

        elif mode == "ava":
            if turn == PLAYER1:
                print("AI-1 (X) is thinking...")
                col = ai_move(board, PLAYER1)
                print(f"AI-1 (X) chose column {col}")
            else:
                print("AI-2 (O) is thinking...")
                col = ai_move(board, PLAYER2)
                print(f"AI-2 (O) chose column {col}")

            input("Press Enter to continue...")

        if winning_move(board, turn):
            print_board(board)
            print(f"{get_winner_name(mode, turn)} wins!\n")
            game_over = True
        elif is_board_full(board):
            print_board(board)
            print("It's a draw!\n")
            game_over = True
        else:
            turn = PLAYER2 if turn == PLAYER1 else PLAYER1


# ─────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────
def main() -> None:
    """Display the main menu and run selected game modes."""
    print("\n╔══════════════════════════════════╗")
    print("║           CONNECT FOUR           ║")
    print("╚══════════════════════════════════╝")

    while True:
        print("\nSelect game mode:")
        print(" 1 - Player vs Player")
        print(" 2 - Player vs AI")
        print(" 3 - AI vs AI")
        print(" q - Quit")

        choice = input("\nEnter choice: ").strip().lower()

        if choice == "1":
            play_game("pvp")
        elif choice == "2":
            play_game("pva")
        elif choice == "3":
            play_game("ava")
        elif choice == "q":
            print("Thanks for playing! Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or q.")
            continue

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! Goodbye.")
            break


if __name__ == "__main__":
    main()
