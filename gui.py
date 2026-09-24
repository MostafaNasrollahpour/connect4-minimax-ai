"""Tkinter interface for the Connect Four game."""

import time
import tkinter as tk
from tkinter import messagebox

from ai import AI_DEPTH, MinimaxAI
from game import (
    AI_SYMBOL,
    BOARD_COLS,
    BOARD_ROWS,
    PLAYERS,
    RANDOM_MODE,
    SEQUENTIAL_MODE,
    ConnectFourGame,
)


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

CELL_SIZE = 50
BOARD_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
COLUMN_HEADER_HEIGHT = 28
BOARD_COLOR = "blue"
EMPTY_CELL_COLOR = "lightblue"
CELL_OUTLINE_COLOR = "black"


class ConnectFourGUI:
    """Manage the Tkinter interface and coordinate the game and AI."""

    def __init__(self):
        self.game = ConnectFourGame()
        self.ai = MinimaxAI(self.game)

        self.game_active = False
        self.after_id = None

        self.root = tk.Tk()
        self.root.title("Connect 4 - Minimax AI")

        self.mode_frame = tk.LabelFrame(
            self.root,
            text="Game mode",
            padx=8,
            pady=5,
        )
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
            button = tk.Button(
                self.button_frame,
                text=str(col + 1),
                width=5,
                height=1,
                command=lambda c=col: self.human_move(c),
            )
            button.pack(side=tk.LEFT)
            self.column_buttons.append(button)

        self.disable_buttons()
        self.draw_board()

    def start_game(self):
        """Reset the board and start a game using the selected turn mode."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.game.reset(self.mode_var.get())
        self.game_active = True

        self.disable_buttons()
        self.draw_board()

        self.turn_label.config(
            text=f"Starting: {GAME_MODE_LABELS[self.game.game_mode]}"
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

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="white",
                )

                symbol = self.game.board[row][col]
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
        for button in self.column_buttons:
            button.config(state=tk.NORMAL)

    def disable_buttons(self):
        for button in self.column_buttons:
            button.config(state=tk.DISABLED)

    def human_move(self, col):
        if (
            not self.game_active
            or self.game.current_player == AI_SYMBOL
        ):
            return

        if self.game.is_column_full(col):
            messagebox.showerror(
                "Error",
                f"Column {col + 1} is full!",
            )
            return

        row = self.game.drop_piece(
            col,
            self.game.current_player,
        )

        self.draw_board()

        if self.game.check_winner(
            row,
            col,
            self.game.current_player,
        ):
            player = self.game.current_player
            role = PLAYER_LABELS[player]

            self.finish_game(
                f"{role} ({player}) wins!"
            )
            return

        if self.game.is_board_full():
            self.finish_game("It's a draw!")
            return

        self.disable_buttons()
        self.schedule_play()

    def finish_game(self, message):
        """Stop the current game while keeping the window open for a restart."""
        self.game_active = False
        self.disable_buttons()
        self.turn_label.config(text=message)

        messagebox.showinfo(
            "Game Over",
            message,
        )

    def play(self):
        self.after_id = None

        if not self.game_active:
            return

        player = self.game.select_next_player()

        role = PLAYER_LABELS[player]
        color = PLAYER_COLORS[player].capitalize()
        mode = GAME_MODE_LABELS[self.game.game_mode]

        self.draw_board()

        if player == AI_SYMBOL:
            self.disable_buttons()

            self.turn_label.config(
                text=(
                    f"{mode} — AI "
                    f"({AI_SYMBOL}, {color}) is thinking..."
                )
            )

            self.root.update_idletasks()

            start_time = time.perf_counter()

            col = self.ai.ai_move(
                depth=AI_DEPTH
            )

            elapsed = time.perf_counter() - start_time

            if col is None:
                self.finish_game("It's a draw!")
                return

            row = self.game.drop_piece(
                col,
                player,
            )

            self.draw_board()

            self.turn_label.config(
                text=(
                    f"{mode} — AI chose column {col + 1} "
                    f"in {elapsed:.2f}s"
                )
            )

            if self.game.check_winner(
                row,
                col,
                player,
            ):
                self.finish_game(
                    f"AI ({player}) wins!"
                )
                return

            if self.game.is_board_full():
                self.finish_game("It's a draw!")
                return

            self.schedule_play()
            return

        self.enable_buttons()

        self.turn_label.config(
            text=(
                f"{mode} — {role} "
                f"({player}, {color}), choose a column"
            )
        )

    def run(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()
