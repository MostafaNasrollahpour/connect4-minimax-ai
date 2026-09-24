"""Core game state and rules for the three-player Connect Four game."""

import random

import numpy as np


BOARD_ROWS = 10
BOARD_COLS = 10
WIN_LENGTH = 4
EMPTY = " "

PLAYERS = ["X", "O", "R"]
AI_SYMBOL = "R"

RANDOM_MODE = "random"
SEQUENTIAL_MODE = "sequential"


class ConnectFourGame:
    """Manage the board state, game rules, and turn selection."""

    def __init__(self):
        self.board = np.full((BOARD_ROWS, BOARD_COLS), EMPTY, dtype=str)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0
        self.sequential_index = -1
        self.game_mode = RANDOM_MODE

    def reset(self, game_mode=RANDOM_MODE):
        """Reset the board and turn state for a new game."""
        self.board.fill(EMPTY)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0
        self.sequential_index = -1
        self.game_mode = game_mode

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
        """Select the next player according to the active game mode."""
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
        return [
            col
            for col in range(BOARD_COLS)
            if not self.is_column_full(col)
        ]

    def check_winner_for_symbol(self, symbol):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if (
                    self.board[row][col] == symbol
                    and self.check_winner(row, col, symbol)
                ):
                    return True

        return False
