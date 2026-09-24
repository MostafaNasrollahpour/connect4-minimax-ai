"""Minimax AI with alpha-beta pruning for Connect Four."""

from game import (
    AI_SYMBOL,
    BOARD_COLS,
    BOARD_ROWS,
    EMPTY,
    PLAYERS,
    WIN_LENGTH,
)


AI_DEPTH = 4
INF = float("inf")


class MinimaxAI:
    """Choose moves using depth-limited Minimax with alpha-beta pruning."""

    def __init__(self, game):
        self.game = game

    def evaluate_board(self):
        if self.game.check_winner_for_symbol(AI_SYMBOL):
            return INF

        if (
            self.game.check_winner_for_symbol("X")
            or self.game.check_winner_for_symbol("O")
        ):
            return -INF

        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        score_levels = [0, 1, 5, 50]

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

            min_c_start = (
                (WIN_LENGTH - 1) * abs(dc)
                if dc < 0
                else 0
            )

            for row in range(max_r):
                for col in range(min_c_start, max_c_start):
                    line = []
                    current_row, current_col = row, col

                    for _ in range(WIN_LENGTH):
                        if (
                            0 <= current_row < BOARD_ROWS
                            and 0 <= current_col < BOARD_COLS
                        ):
                            line.append(
                                self.game.board[current_row][current_col]
                            )
                        else:
                            break

                        current_row += dr
                        current_col += dc

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

    def minimax(self, depth, alpha, beta, maximizing_player):
        score = self.evaluate_board()

        if (
            depth == 0
            or abs(score) == INF
            or self.game.is_board_full()
        ):
            return score

        available_moves = self.game.get_available_moves()

        if maximizing_player:
            max_eval = -INF

            for col in available_moves:
                row = self.game.drop_piece(col, AI_SYMBOL)

                eval_score = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    False,
                )

                self.game.board[row][col] = EMPTY

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break

            return max_eval

        min_eval = INF
        opponents = [
            player
            for player in PLAYERS
            if player != AI_SYMBOL
        ]

        for opponent in opponents:
            for col in available_moves:
                row = self.game.drop_piece(col, opponent)

                eval_score = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    True,
                )

                self.game.board[row][col] = EMPTY

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    return min_eval

        return min_eval

    def ai_move(self, depth=AI_DEPTH):
        best_score = -INF
        alpha = -INF
        beta = INF

        available = self.game.get_available_moves()
        available.sort(key=lambda col: abs(col - BOARD_COLS // 2))

        if not available:
            return None

        best_move = available[0]

        for col in available:
            row = self.game.drop_piece(col, AI_SYMBOL)

            score = self.minimax(
                depth - 1,
                alpha,
                beta,
                False,
            )

            self.game.board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_move = col

            alpha = max(alpha, score)

            if beta <= alpha:
                break

        return best_move
