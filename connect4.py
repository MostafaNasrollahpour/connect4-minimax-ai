"""Three-player Connect Four for experimenting with Minimax and alpha-beta pruning."""

import random
import time
import tkinter as tk
from tkinter import messagebox

import numpy as np

# Game constants
BOARD_ROWS = 10
BOARD_COLS = 10
WIN_LENGTH = 4
EMPTY = " "
PLAYERS = ["X", "O", "R"]
AI_SYMBOL = "R"
AI_DEPTH = 4
INF = float("inf")

RANDOM_MODE = "random"
SEQUENTIAL_MODE = "sequential"
GAME_MODE_LABELS = {
    RANDOM_MODE: "Random turns",
    SEQUENTIAL_MODE: "Round-robin turns",
}

PLAYER_COLORS = {
    "X": "red",
    "O": "green",
    "R": "yellow",
}

PLAYER_LABELS = {
    "X": "Human 1",
    "O": "Human 2",
    "R": "AI",
}

# GUI constants
CELL_SIZE = 50
BOARD_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
COLUMN_HEADER_HEIGHT = 28
BOARD_COLOR = "blue"
EMPTY_CELL_COLOR = "lightblue"
CELL_OUTLINE_COLOR = "black"


class ConnectFourGame:
    """Manage the board state, turn modes, AI search, and Tkinter interface."""

    def __init__(self):
        self.board = np.full((BOARD_ROWS, BOARD_COLS), EMPTY, dtype=str)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0
        self.sequential_index = -1
        self.game_active = False
        self.after_id = None
        self.game_mode = RANDOM_MODE

        self.root = tk.Tk()
        self.root.title("Connect 4 - Minimax AI")

        self.mode_frame = tk.LabelFrame(self.root, text="Game mode", padx=8, pady=5)
        self.mode_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.mode_var = tk.StringVar(value=RANDOM_MODE)
        tk.Radiobutton(
            self.mode_frame,
            text="Random turns",
            variable=self.mode_var,
            value=RANDOM_MODE,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(
            self.mode_frame,
            text="Round-robin: X → O → R",
            variable=self.mode_var,
            value=SEQUENTIAL_MODE,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            self.mode_frame,
            text="Start / Restart Game",
            command=self.start_game,
        ).pack(side=tk.RIGHT)

        self.turn_label = tk.Label(
            self.root,
            text="Choose a game mode, then start the game.",
            font=("Arial", 14),
        )
        self.turn_label.pack(pady=(2, 4))

        self.column_header = tk.Canvas(
            self.root,
            width=BOARD_WIDTH,
            height=COLUMN_HEADER_HEIGHT,
            highlightthickness=0,
        )
        self.column_header.pack()
        self.draw_column_numbers()

        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_WIDTH,
            height=BOARD_HEIGHT,
            bg=BOARD_COLOR,
        )
        self.canvas.pack()

        self.legend_frame = tk.Frame(self.root)
        self.legend_frame.pack(pady=(6, 4))
        for symbol in PLAYERS:
            item = tk.Frame(self.legend_frame)
            item.pack(side=tk.LEFT, padx=8)
            tk.Label(
                item,
                width=2,
                bg=PLAYER_COLORS[symbol],
                relief=tk.SOLID,
                borderwidth=1,
            ).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(
                item,
                text=f"{symbol} — {PLAYER_LABELS[symbol]}",
            ).pack(side=tk.LEFT)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=(0, 8))

        self.column_buttons = []
        for col in range(BOARD_COLS):
            btn = tk.Button(
                self.button_frame,
                text=str(col + 1),
                width=5,
                height=1,
                command=lambda c=col: self.human_move(c),
            )
            btn.pack(side=tk.LEFT)
            self.column_buttons.append(btn)

        self.disable_buttons()
        self.draw_board()

    def start_game(self):
        """Reset the board and start a game using the selected turn mode."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.board.fill(EMPTY)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0
        self.sequential_index = -1
        self.game_mode = self.mode_var.get()
        self.game_active = True

        self.disable_buttons()
        self.draw_board()
        self.turn_label.config(
            text=f"Starting: {GAME_MODE_LABELS[self.game_mode]}"
        )
        self.schedule_play()

    def schedule_play(self, delay=100):
        """Schedule the next turn while keeping only one pending callback."""
        if not self.game_active:
            return
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(delay, self.play)

    def draw_column_numbers(self):
        """Draw user-facing column numbers from 1 to 10 above the board."""
        self.column_header.delete("all")
        for col in range(BOARD_COLS):
            x = col * CELL_SIZE + CELL_SIZE / 2
            self.column_header.create_text(
                x,
                COLUMN_HEADER_HEIGHT / 2,
                text=str(col + 1),
                font=("Arial", 11, "bold"),
            )

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")
                symbol = self.board[row][col]
                color = PLAYER_COLORS.get(symbol, EMPTY_CELL_COLOR)
                self.canvas.create_oval(
                    x1 + 5,
                    y1 + 5,
                    x2 - 5,
                    y2 - 5,
                    fill=color,
                    outline=CELL_OUTLINE_COLOR,
                )

    def enable_buttons(self):
        for btn in self.column_buttons:
            btn.config(state=tk.NORMAL)

    def disable_buttons(self):
        for btn in self.column_buttons:
            btn.config(state=tk.DISABLED)

    def three_sided_die(self):
        """Select a random player, preventing three identical turns in a row."""
        available = PLAYERS.copy()
        if self.consecutive == 2 and self.last_player in available:
            available.remove(self.last_player)

        choice = random.choice(available)
        if choice == self.last_player:
            self.consecutive += 1
        else:
            self.consecutive = 1

        self.last_player = choice
        self.current_player = choice
        return choice

    def sequential_turn(self):
        """Select players in the fixed order X -> O -> R -> X."""
        self.sequential_index = (self.sequential_index + 1) % len(PLAYERS)
        choice = PLAYERS[self.sequential_index]
        self.last_player = choice
        self.current_player = choice
        self.consecutive = 1
        return choice

    def select_next_player(self):
        if self.game_mode == SEQUENTIAL_MODE:
            return self.sequential_turn()
        return self.three_sided_die()

    def is_column_full(self, col):
        return self.board[0][col] != EMPTY

    def drop_piece(self, col, symbol):
        for row in range(BOARD_ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = symbol
                return row
        return -1

    def check_winner(self, row, col, symbol):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            r, c = row + dr, col + dc
            while (
                0 <= r < BOARD_ROWS
                and 0 <= c < BOARD_COLS
                and self.board[r][c] == symbol
            ):
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while (
                0 <= r < BOARD_ROWS
                and 0 <= c < BOARD_COLS
                and self.board[r][c] == symbol
            ):
                count += 1
                r -= dr
                c -= dc

            if count >= WIN_LENGTH:
                return True
        return False

    def is_board_full(self):
        return all(self.board[0][col] != EMPTY for col in range(BOARD_COLS))

    def get_available_moves(self):
        return [col for col in range(BOARD_COLS) if not self.is_column_full(col)]

    def check_winner_for_symbol(self, symbol):
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.board[r][c] == symbol and self.check_winner(r, c, symbol):
                    return True
        return False

    def evaluate_board(self):
        if self.check_winner_for_symbol(AI_SYMBOL):
            return INF
        if self.check_winner_for_symbol("X") or self.check_winner_for_symbol("O"):
            return -INF

        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        score_levels = [0, 1, 5, 50]  # Scores for 1, 2, or 3 pieces in a line.

        for dr, dc in directions:
            max_r = (
                BOARD_ROWS - (WIN_LENGTH - 1) * abs(dr)
                if dr != 0
                else BOARD_ROWS
            )
            max_c_start = (
                BOARD_COLS - (WIN_LENGTH - 1) * abs(dc)
                if dc > 0
                else BOARD_COLS
            )
            min_c_start = (WIN_LENGTH - 1) * abs(dc) if dc < 0 else 0

            for r in range(max_r):
                for c in range(min_c_start, max_c_start):
                    line = []
                    rr, cc = r, c
                    for _ in range(WIN_LENGTH):
                        if 0 <= rr < BOARD_ROWS and 0 <= cc < BOARD_COLS:
                            line.append(self.board[rr][cc])
                        else:
                            break
                        rr += dr
                        cc += dc

                    if len(line) < WIN_LENGTH:
                        continue

                    count_r = line.count(AI_SYMBOL)
                    count_x = line.count("X")
                    count_o = line.count("O")

                    if count_r > 0 and (count_x > 0 or count_o > 0):
                        continue
                    if count_x > 0 and count_o > 0:
                        continue
                    if 0 < count_r < WIN_LENGTH:
                        score += score_levels[count_r]
                    elif 0 < count_x < WIN_LENGTH:
                        score -= score_levels[count_x]
                    elif 0 < count_o < WIN_LENGTH:
                        score -= score_levels[count_o]

        return score

    # depth: number of remaining search levels
    # alpha: best score for maximizer so far
    # beta: best score for minimizer so far
    # maximizing_player: True for the AI layer, False for opponent layers
    def minimax(self, depth, alpha, beta, maximizing_player):
        score = self.evaluate_board()
        if depth == 0 or abs(score) == INF or self.is_board_full():
            return score

        available_moves = self.get_available_moves()

        if maximizing_player:
            max_eval = -INF
            for col in available_moves:
                row = self.drop_piece(col, AI_SYMBOL)
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                self.board[row][col] = EMPTY
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval

        min_eval = INF
        opponents = [p for p in PLAYERS if p != AI_SYMBOL]
        for opponent in opponents:
            for col in available_moves:
                row = self.drop_piece(col, opponent)
                eval_score = self.minimax(depth - 1, alpha, beta, True)
                self.board[row][col] = EMPTY
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    return min_eval
        return min_eval

    def ai_move(self, depth=AI_DEPTH):
        best_score = -INF
        alpha = -INF
        beta = INF

        available = self.get_available_moves()
        available.sort(key=lambda c: abs(c - BOARD_COLS // 2))

        if not available:
            return None

        best_move = available[0]

        for col in available:
            row = self.drop_piece(col, AI_SYMBOL)
            score = self.minimax(depth - 1, alpha, beta, False)
            self.board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_move = col

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return best_move

    def human_move(self, col):
        if not self.game_active or self.current_player == AI_SYMBOL:
            return
        if self.is_column_full(col):
            messagebox.showerror("Error", f"Column {col + 1} is full!")
            return

        row = self.drop_piece(col, self.current_player)
        self.draw_board()

        if self.check_winner(row, col, self.current_player):
            role = PLAYER_LABELS[self.current_player]
            self.finish_game(f"{role} ({self.current_player}) wins!")
            return
        if self.is_board_full():
            self.finish_game("It's a draw!")
            return

        self.disable_buttons()
        self.schedule_play()

    def finish_game(self, message):
        """Stop the current game while keeping the window open for a restart."""
        self.game_active = False
        self.disable_buttons()
        self.turn_label.config(text=message)
        messagebox.showinfo("Game Over", message)

    def play(self):
        self.after_id = None
        if not self.game_active:
            return

        player = self.select_next_player()
        role = PLAYER_LABELS[player]
        color = PLAYER_COLORS[player].capitalize()
        mode = GAME_MODE_LABELS[self.game_mode]

        self.draw_board()

        if player == AI_SYMBOL:
            self.disable_buttons()
            self.turn_label.config(
                text=f"{mode} — AI ({AI_SYMBOL}, {color}) is thinking..."
            )
            self.root.update_idletasks()

            start_time = time.perf_counter()
            col = self.ai_move(depth=AI_DEPTH)
            elapsed = time.perf_counter() - start_time

            if col is None:
                self.finish_game("It's a draw!")
                return

            row = self.drop_piece(col, player)
            self.draw_board()
            self.turn_label.config(
                text=(
                    f"{mode} — AI chose column {col + 1} "
                    f"in {elapsed:.2f}s"
                )
            )

            if self.check_winner(row, col, player):
                self.finish_game(f"AI ({player}) wins!")
                return
            if self.is_board_full():
                self.finish_game("It's a draw!")
                return

            self.schedule_play()
            return

        self.enable_buttons()
        self.turn_label.config(
            text=f"{mode} — {role} ({player}, {color}), choose a column"
        )


if __name__ == "__main__":
    game = ConnectFourGame()
    game.root.mainloop()
