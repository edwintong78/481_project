ROWS = 6
COLS = 7

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
# this return a 2d list representing the board, initialized with EMPTY (0) in all cells
# to access the 2d list you can use board[row][col]
# top is row 0 and bottom is row 5, leftmost column is col 0 and rightmost is col 6

def print_board(board):
    # Print top to bottom visually (row 0 at top)
    for row in board:
        print("|", end="")
        for cell in row:
            if cell == PLAYER1:
                ch = "X"
            elif cell == PLAYER2:
                ch = "O"
            else:
                ch = " "
            print(f" {ch} ", end="")
        print("|")
    print("  " + "  ".join(str(i) for i in range(COLS)))


def is_valid_column(board, col):
    if col < 0 or col >= COLS:
        return False
    return board[0][col] == EMPTY  # top cell empty means column not full

def get_next_open_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None  # column full

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def winning_move(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r][c+1] == piece and
                board[r][c+2] == piece and
                board[r][c+3] == piece):
                return True

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if (board[r][c] == piece and
                board[r+1][c] == piece and
                board[r+2][c] == piece and
                board[r+3][c] == piece):
                return True

    # Diagonal down-right
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r+1][c+1] == piece and
                board[r+2][c+2] == piece and
                board[r+3][c+3] == piece):
                return True

    # Diagonal up-right
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r-1][c+1] == piece and
                board[r-2][c+2] == piece and
                board[r-3][c+3] == piece):
                return True

    return False

def is_board_full(board):
    return all(board[0][c] != EMPTY for c in range(COLS))

def main():
    board = create_board()
    game_over = False
    turn = PLAYER1  # X starts

    while not game_over:
        print_board(board)
        print(f"Player {turn} turn ({'X' if turn == PLAYER1 else 'O'})")

        try:
            col = int(input("Choose a column (0-6): "))
        except ValueError:
            print("Invalid input. Enter a number 0-6.")
            continue

        if not is_valid_column(board, col):
            print("Column full or out of range. Try again.")
            continue

        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn)

        if winning_move(board, turn):
            print_board(board)
            print(f"Player {turn} ({'X' if turn == PLAYER1 else 'O'}) wins!")
            game_over = True
        elif is_board_full(board):
            print_board(board)
            print("It's a draw!")
            game_over = True
        else:
            turn = PLAYER2 if turn == PLAYER1 else PLAYER1

if __name__ == "__main__":
    main()
    # player 1 is x 
    # player 2 is o and it the ai 
    
