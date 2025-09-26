import tkinter as tk
from tkinter import messagebox
import random

# ---------- Global State ----------
current_player = "X"   # Track whose turn it is
board = []             # 2D list for the game board
buttons = []           # Button widgets for the board
board_size = 3
mode = "PvP"
player1_name = "Player 1"
player2_name = "Player 2"
player_scores = {"X": 0, "O": 0}
ai_difficulty = 1
loser_starts_toggle = False
last_loser = None      # Keeps track of loser if toggle is enabled


# ---------- Core Game Logic ----------
def initialize_board(size):
    """Create a fresh, empty board of given size."""
    return [[" " for _ in range(size)] for _ in range(size)]


def get_available_moves(board):
    """Return a list of (row, col) positions that are empty."""
    return [(i, j) for i in range(len(board)) for j in range(len(board)) if board[i][j] == " "]


def is_winner(board, player):
    """Check if the given player has won the game."""
    n = len(board)

    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True

    # Check columns
    for col in range(n):
        if all(board[row][col] == player for row in range(n)):
            return True

    # Check diagonals
    if all(board[i][i] == player for i in range(n)):
        return True
    if all(board[i][n - i - 1] == player for i in range(n)):
        return True

    return False


def is_board_full(board):
    """Return True if the board has no empty spaces."""
    return all(cell != " " for row in board for cell in row)


def minimax(board, depth, is_maximizing, ai, human):
    """
    Minimax algorithm for decision making.
    Recursively simulate moves to evaluate the best possible outcome.
    """
    if is_winner(board, ai):
        return 1
    if is_winner(board, human):
        return -1
    if is_board_full(board):
        return 0

    if is_maximizing:  # AI's turn
        best_score = -float("inf")
        for (i, j) in get_available_moves(board):
            board[i][j] = ai
            score = minimax(board, depth + 1, False, ai, human)
            board[i][j] = " "
            best_score = max(best_score, score)
        return best_score
    else:  # Human's turn
        best_score = float("inf")
        for (i, j) in get_available_moves(board):
            board[i][j] = human
            score = minimax(board, depth + 1, True, ai, human)
            board[i][j] = " "
            best_score = min(best_score, score)
        return best_score


def best_ai_move(board, difficulty, ai, human):
    """Pick the AI's move depending on difficulty level."""
    moves = get_available_moves(board)
    if not moves:
        return None

    if difficulty == 1:  # Easy → random
        return random.choice(moves)
    elif difficulty == 2:  # Medium → half random, half minimax
        if random.random() < 0.5:
            return random.choice(moves)
        else:
            return best_minimax_move(board, ai, human, depth_limit=len(board) - 1)
    else:  # Hard → full minimax
        return best_minimax_move(board, ai, human)


def best_minimax_move(board, ai, human, depth_limit=None):
    """Run minimax on all moves and return the best move for the AI."""
    best_score = -float("inf")
    best_move = None
    for (i, j) in get_available_moves(board):
        board[i][j] = ai
        score = minimax(board, 0, False, ai, human)
        board[i][j] = " "
        if score > best_score:
            best_score = score
            best_move = (i, j)
    return best_move


# ---------- GUI Functions ----------
def start_game(selected_mode, size, p1, p2=None, difficulty=1, loser_toggle=False):
    """Initialize a new game with selected settings."""
    global board_size, mode, player1_name, player2_name, board
    global ai_difficulty, loser_starts_toggle

    board_size = size
    mode = selected_mode
    player1_name = p1 if p1 else "Player 1"
    player2_name = p2 if p2 else ("Computer" if mode == "PvC" else "Player 2")
    ai_difficulty = difficulty
    loser_starts_toggle = loser_toggle

    reset_board()


def show_main_menu():
    """Display the main menu."""
    global player_scores, last_loser
    # Reset scores when going back to menu
    player_scores = {"X": 0, "O": 0}
    last_loser = None

    clear_window()
    tk.Label(root, text="Tic-Tac-Toe", font=("Arial", 22, "bold")).pack(pady=15)

    tk.Button(root, text="Player vs Player", width=20, command=lambda: show_name_input("PvP")).pack(pady=5)
    tk.Button(root, text="Player vs Computer", width=20, command=lambda: show_name_input("PvC")).pack(pady=5)


def show_name_input(selected_mode):
    """Ask players for names and game settings before starting."""
    clear_window()
    tk.Label(root, text="Setup Game", font=("Arial", 16, "bold")).pack(pady=10)

    # Player 1 input
    tk.Label(root, text="Player 1 Name:").pack()
    p1_entry = tk.Entry(root)
    p1_entry.insert(0, "Player 1")
    p1_entry.pack()

    if selected_mode == "PvP":
        # Player 2 input for PvP
        tk.Label(root, text="Player 2 Name:").pack()
        p2_entry = tk.Entry(root)
        p2_entry.insert(0, "Player 2")
        p2_entry.pack()
    else:
        # PvC settings
        p2_entry = None
        tk.Label(root, text="Difficulty (1=Easy, 2=Med, 3=Hard):").pack()
        diff_var = tk.IntVar(value=1)
        tk.OptionMenu(root, diff_var, 1, 2, 3).pack()

    # Board size
    tk.Label(root, text="Board Size (3-5):").pack()
    size_var = tk.IntVar(value=3)
    tk.OptionMenu(root, size_var, 3, 4, 5).pack()

    # Loser starts toggle
    loser_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Loser starts next game", variable=loser_var).pack(pady=5)

    tk.Button(
        root,
        text="Start Game",
        command=lambda: start_game(
            selected_mode,
            size_var.get(),
            p1_entry.get(),
            p2_entry.get() if p2_entry else None,
            diff_var.get() if selected_mode == "PvC" else 1,
            loser_var.get(),
        ),
    ).pack(pady=10)


def show_game_screen():
    """Draw the scoreboard and the game board."""
    clear_window()

    # Scoreboard
    score_frame = tk.Frame(root)
    score_frame.pack(pady=5)
    tk.Label(score_frame, text=f"{player1_name} (X): {player_scores['X']}", fg="blue", font=("Arial", 12)).pack(side="left", padx=20)
    tk.Label(score_frame, text=f"{player2_name} (O): {player_scores['O']}", fg="red", font=("Arial", 12)).pack(side="right", padx=20)

    # Game board
    game_frame = tk.Frame(root)
    game_frame.pack()
    global buttons
    buttons = []
    for i in range(board_size):
        row_btns = []
        for j in range(board_size):
            btn = tk.Button(
                game_frame,
                text=" ",
                width=4,
                height=2,
                font=("Arial", 20),
                command=lambda r=i, c=j: cell_click(r, c),
            )
            btn.grid(row=i, column=j)
            row_btns.append(btn)
        buttons.append(row_btns)

    # Controls
    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)
    tk.Button(control_frame, text="Play Again", command=reset_board).pack(side="left", padx=10)
    tk.Button(control_frame, text="Back to Menu", command=show_main_menu).pack(side="right", padx=10)


def cell_click(row, col, by_ai=False):
    """Handle a cell being clicked (by human or AI)."""
    global current_player, last_loser

    # Prevent human clicks during AI's turn
    if not by_ai and mode == "PvC" and current_player == "O":
        return

    if board[row][col] != " ":
        return

    # Decide which symbol to place
    symbol = "O" if by_ai else current_player
    board[row][col] = symbol
    buttons[row][col].config(text=symbol, fg=("blue" if symbol == "X" else "red"))

    # Check game status
    if is_winner(board, symbol):
        player_scores[symbol] += 1
        highlight_winner(symbol)
        last_loser = "O" if symbol == "X" else "X"
        return
    elif is_board_full(board):
        last_loser = None
        messagebox.showinfo("Game Over", "It's a tie!")
        return

    # Switch turns
    current_player = "X" if by_ai else ("O" if current_player == "X" else "X")

    # If it's AI's turn, let it move
    if mode == "PvC" and current_player == "O":
        root.after(400, computer_move)


def computer_move():
    """Trigger the AI's move."""
    move = best_ai_move(board, ai_difficulty, "O", "X")
    if move:
        cell_click(move[0], move[1], by_ai=True)


def highlight_winner(player):
    """Highlight the winning line and show a message."""
    n = len(board)
    win_cells = []

    # Check winning row/col/diagonal and store coordinates
    for i in range(n):
        if all(board[i][j] == player for j in range(n)):
            win_cells = [(i, j) for j in range(n)]
        if all(board[j][i] == player for j in range(n)):
            win_cells = [(j, i) for j in range(n)]
    if all(board[i][i] == player for i in range(n)):
        win_cells = [(i, i) for i in range(n)]
    if all(board[i][n - i - 1] == player for i in range(n)):
        win_cells = [(i, n - i - 1) for i in range(n)]

    for (r, c) in win_cells:
        buttons[r][c].config(bg="yellow")

    messagebox.showinfo("Game Over", f"{get_player_name(player)} wins!")


def reset_board():
    """Reset the board for a new round."""
    global board, current_player

    # Decide who starts
    if loser_starts_toggle and last_loser is not None:
        current_player = last_loser
    else:
        current_player = "X"

    board = initialize_board(board_size)
    show_game_screen()

    # If AI starts, trigger its first move
    if mode == "PvC" and current_player == "O":
        root.after(400, computer_move)


def get_player_name(symbol):
    return player1_name if symbol == "X" else player2_name


def clear_window():
    """Clear all widgets from the root window."""
    for widget in root.winfo_children():
        widget.destroy()


# ---------- Main ----------
root = tk.Tk()
root.title("Tic-Tac-Toe")
show_main_menu()
root.mainloop()
