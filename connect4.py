import numpy as np
import random
import time
import tkinter as tk
from tkinter import messagebox

# Constants
BOARD_ROWS = 10
BOARD_COLS = 10
WIN_LENGTH = 4
EMPTY = ' '
PLAYERS = ['X', 'O', 'R']
AI_SYMBOL = 'R'
INF = float('inf')

# GUI Constants
CELL_SIZE = 50
BOARD_WIDTH = BOARD_COLS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
BUTTON_HEIGHT = 30

# include the main game class: state of board, turns, ai, gui
class ConnectFourGame:
    
    # create main board and gui elements
    def __init__(self):
        self.board = np.full((BOARD_ROWS, BOARD_COLS), EMPTY, dtype=str)
        self.current_player = None
        self.last_player = None
        self.consecutive = 0
        
        self.root = tk.Tk()
        self.root.title("Connect 4 - 10x10 with AI")
        
        self.turn_label = tk.Label(self.root, text="Rolling die...", font=("Arial", 14))
        self.turn_label.pack()
        
        self.canvas = tk.Canvas(self.root, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg="blue")
        self.canvas.pack()
        
        self.column_buttons = []
        for col in range(BOARD_COLS):
            btn = tk.Button(self.root, text=str(col), width=5, height=1, command=lambda c=col: self.human_move(c))
            btn.pack(side=tk.LEFT)
            self.column_buttons.append(btn)
            
        self.disable_buttons()
        self.draw_board()
        
        self.root.after(100, self.play)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")
                if self.board[row][col] == 'X':
                    color = "red"
                elif self.board[row][col] == 'O':
                    color = "green"
                elif self.board[row][col] == 'R':
                    color = "yellow"
                else:
                    color = "lightblue"
                self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color)

    def enable_buttons(self):
        for btn in self.column_buttons:
            btn.config(state=tk.NORMAL)

    def disable_buttons(self):
        for btn in self.column_buttons:
            btn.config(state=tk.DISABLED)

    def three_sided_die(self):
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
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == symbol:
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
                if self.board[r][c] == symbol:
                    if self.check_winner(r, c, symbol):
                        return True
        return False

    def evaluate_board(self):
        if self.check_winner_for_symbol(AI_SYMBOL):
            return INF
        if self.check_winner_for_symbol('X') or self.check_winner_for_symbol('O'):
            return -INF
        
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        score_levels = [0, 1, 5, 50]  # for 1,2,3 in a row
        for dr, dc in directions:
            
            max_r = BOARD_ROWS - (WIN_LENGTH - 1) * abs(dr) if dr != 0 else BOARD_ROWS
            max_c_start = BOARD_COLS - (WIN_LENGTH - 1) * abs(dc) if dc > 0 else BOARD_COLS
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
                    
                    count_R = line.count(AI_SYMBOL)
                    count_X = line.count('X')
                    count_O = line.count('O')
                    count_empty = line.count(EMPTY)
                    if count_R > 0 and (count_X > 0 or count_O > 0):
                        continue
                    if count_X > 0 and count_O > 0:
                        continue
                    if count_R > 0 and count_R < 4:
                        score += score_levels[count_R]
                    elif count_X > 0 and count_X < 4:
                        score -= score_levels[count_X]
                    elif count_O > 0 and count_O < 4:
                        score -= score_levels[count_O]
        return score

    # depth: how many steps remining
    # alpha: best score for maximizer so far
    # beta: best score for minimizer so far
    # maximizing_player: boolean for maximizing or minimizing
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
        else:
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
                        return min_eval  # Break early
            return min_eval

    def ai_move(self, depth=4):
        best_score = -INF
        best_move = None
        alpha = -INF
        beta = INF
        available = self.get_available_moves()
        available.sort(key=lambda c: abs(c - BOARD_COLS // 2))  # Center first
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
        if self.is_column_full(col):
            messagebox.showerror("Error", "Column full!")
            return
        row = self.drop_piece(col, self.current_player)
        self.draw_board()
        if self.check_winner(row, col, self.current_player):
            messagebox.showinfo("Winner", f"Player {self.current_player} wins!")
            self.root.quit()
            return
        if self.is_board_full():
            messagebox.showinfo("Draw", "It's a draw!")
            self.root.quit()
            return
        self.disable_buttons()
        self.root.after(100, self.play)

    def play(self):
        player = self.three_sided_die()
        self.turn_label.config(text=f"Turn: {player} (Die rolled)")
        self.draw_board()
        if player == AI_SYMBOL:
            self.turn_label.config(text="AI thinking...")
            self.root.update()
            
            start_time = time.time()
            
            col = self.ai_move(depth=4)
            elapsed = time.time() - start_time
            row = self.drop_piece(col, player)
            self.draw_board()
            self.turn_label.config(text=f"AI chose {col} in {elapsed:.2f}s")
            if self.check_winner(row, col, player):
                messagebox.showinfo("Winner", f"Player {player} wins!")
                self.root.quit()
                return
            if self.is_board_full():
                messagebox.showinfo("Draw", "It's a draw!")
                self.root.quit()
                return
            self.root.after(100, self.play)
        else:
            self.enable_buttons()
            self.turn_label.config(text=f"Player {player}, choose column")

if __name__ == "__main__":
    game = ConnectFourGame()
    game.root.mainloop()