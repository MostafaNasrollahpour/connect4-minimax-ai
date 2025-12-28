import numpy as np
import random
import time

# Constants
BOARD_ROWS = 10
BOARD_COLS = 10
WIN_LENGTH = 4
EMPTY = ' '
PLAYERS = ['X', 'O', 'R']
AI_SYMBOL = 'R'
INF = float('inf')

class ConnectFourGame:
    def __init__(self):
        self.board = np.full((BOARD_ROWS, BOARD_COLS), EMPTY, dtype=str)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0

    def print_board(self):
        """Display the board."""
        print("\n   " + " ".join(str(i) for i in range(BOARD_COLS)))
        for r in range(BOARD_ROWS):
            row_display = " ".join(self.board[r])
            print(f"{r} |{row_display}|")
        print()

    def is_column_full(self, col):
        """Check if a column is full."""
        return self.board[0][col] != EMPTY

    def drop_piece(self, col, symbol):
        """Drop a piece in the given column."""
        for row in range(BOARD_ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = symbol
                return row
        return -1

    def three_sided_die(self):
        """Roll a 3-sided die to choose player, avoiding same player 3 times in a row."""
        available = PLAYERS.copy()
        if self.consecutive == 2:
            if self.last_player in available:
                available.remove(self.last_player)
        choice = random.choice(available)
        if choice == self.last_player:
            self.consecutive += 1
        else:
            self.consecutive = 1
        self.last_player = choice
        self.current_player = choice
        return choice

    def check_winner(self, row, col, symbol):
        """Check if the last move wins the game."""
        directions = [
            (0, 1),  # horizontal
            (1, 0),  # vertical
            (1, 1),  # diagonal /
            (1, -1)  # diagonal \
        ]
        for dr, dc in directions:
            count = 1
            # Forward direction
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            # Backward direction
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc
            if count >= WIN_LENGTH:
                return True
        return False

    def is_board_full(self):
        """Check if board is completely filled."""
        return all(self.board[0][col] != EMPTY for col in range(BOARD_COLS))

    def get_available_moves(self):
        """Return list of non-full columns."""
        return [col for col in range(BOARD_COLS) if not self.is_column_full(col)]

    def check_winner_for_symbol(self, symbol):
        """Check if given symbol has won anywhere on board."""
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if self.board[r][c] == symbol:
                    if self.check_winner(r, c, symbol):
                        return True
        return False

    def evaluate_board(self):
        """Improved heuristic evaluation from AI's perspective."""
        if self.check_winner_for_symbol(AI_SYMBOL):
            return INF
        if self.check_winner_for_symbol('X') or self.check_winner_for_symbol('O'):
            return -INF

        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        score_levels = [0, 1, 5, 50]  # for 1,2,3 in a row

        for dr, dc in directions:
            max_r = BOARD_ROWS - (WIN_LENGTH - 1) * dr if dr > 0 else BOARD_ROWS
            max_c_start = BOARD_COLS - (WIN_LENGTH - 1) * abs(dc) if dc > 0 else BOARD_COLS
            min_c_start = (WIN_LENGTH - 1) if dc < 0 else 0

            for r in range(max_r):
                for c in range(min_c_start, max_c_start):
                    line = []
                    rr, cc = r, c
                    for _ in range(WIN_LENGTH):
                        line.append(self.board[rr][cc])
                        rr += dr
                        cc += dc

                    count_R = line.count(AI_SYMBOL)
                    count_X = line.count('X')
                    count_O = line.count('O')
                    count_empty = line.count(EMPTY)

                    if count_R > 0 and (count_X > 0 or count_O > 0):
                        continue  # blocked
                    if count_X > 0 and count_O > 0:
                        continue  # blocked

                    if count_R > 0:
                        if count_R < 4:
                            score += score_levels[count_R - 1]
                    elif count_X > 0:
                        if count_X < 4:
                            score -= score_levels[count_X - 1]
                    elif count_O > 0:
                        if count_O < 4:
                            score -= score_levels[count_O - 1]

        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax with Alpha-Beta pruning."""
        score = self.evaluate_board()
        if depth == 0 or abs(score) == INF or self.is_board_full():
            return score

        available_moves = self.get_available_moves()

        if maximizing_player:
            max_eval = -INF
            for col in available_moves:
                row = self.drop_piece(col, AI_SYMBOL)
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                self.board[row][col] = EMPTY  # Undo
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = INF
            opponents = [p for p in PLAYERS if p != AI_SYMBOL]
            should_break_outer = False
            for opponent in opponents:
                if should_break_outer:
                    break
                for col in available_moves:
                    row = self.drop_piece(col, opponent)
                    eval_score = self.minimax(depth - 1, alpha, beta, True)
                    self.board[row][col] = EMPTY  # Undo
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        should_break_outer = True
                        break
            return min_eval

    def ai_move(self, depth=4):
        """AI chooses best move using Minimax with Alpha-Beta."""
        best_score = -INF
        best_move = None
        alpha = -INF
        beta = INF
        available = self.get_available_moves()
        # Sort moves to check center first for better pruning
        available.sort(key=lambda c: -abs(c - BOARD_COLS // 2))
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

    def play(self):
        """Main game loop."""
        print("🎮 Connect 4 - 10x10 - 3 Players (2 Humans + 1 AI)")
        print("Players: X (Human1), O (Human2), R (AI)")
        print("Three-sided die decides turn order each round.\n")

        while True:
            player = self.three_sided_die()
            print(f"🎲 Die roll: {player}'s turn")

            self.print_board()

            if player == AI_SYMBOL:
                print("🤖 AI is thinking...")
                start_time = time.time()
                col = self.ai_move(depth=4)
                elapsed = time.time() - start_time
                print(f"⏱ AI chose column {col} in {elapsed:.2f}s")
            else:
                while True:
                    try:
                        col = int(input(f"Player {player}, enter column (0-9): "))
                        if 0 <= col < BOARD_COLS and not self.is_column_full(col):
                            break
                        else:
                            print("Invalid or full column. Try again.")
                    except ValueError:
                        print("Please enter a number.")

            row = self.drop_piece(col, player)
            if self.check_winner(row, col, player):
                self.print_board()
                print(f"🎉 Player {player} wins!")
                break
            if self.is_board_full():
                self.print_board()
                print("🤝 It's a draw!")
                break

if __name__ == "__main__":
    game = ConnectFourGame()
    game.play()