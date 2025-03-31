from .evaluator import evaluate_board
from ..game.move_generator import get_possible_moves, apply_move

def minimax(board, depth, maximizing, alpha, beta, player):
    """
    Implements minimax algorithm with alpha-beta pruning.
    Returns (evaluation, best_move)
    """
    if depth == 0:
        return evaluate_board(board), None

    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c].lower() == player:
                moves.extend(get_possible_moves(board, r, c))

    if not moves:
        return -float('inf') if maximizing else float('inf'), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_val, _ = minimax(new_board, depth-1, False, alpha, beta, player)
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_val, _ = minimax(new_board, depth-1, True, alpha, beta, player)
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move