from .evaluator import evaluate_board
from ..game.move_generator import get_possible_moves, get_all_moves, apply_move
from ..game.pieces import RED_PIECE, BLACK_PIECE

def minimax(board, depth, maximizing, alpha, beta, player):
    """
    Implements minimax algorithm with alpha-beta pruning.
    Returns (evaluation, best_move)
    
    Critical Fix (20250330-1): Previous version didn't switch players during recursive calls,
    causing the AI to evaluate the same player's moves at all levels. This led to poor
    decision making as it wasn't properly considering opponent responses.
    """
    moves = get_all_moves(board, player)
    if depth == 0 or not moves:
        return evaluate_board(board), None

    best_move = None
    # Switch players for the next recursive call
    opponent_player = RED_PIECE if player == BLACK_PIECE else BLACK_PIECE

    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_val, _ = minimax(new_board, depth-1, False, alpha, beta, opponent_player)
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
            eval_val, _ = minimax(new_board, depth-1, True, alpha, beta, opponent_player)
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move
