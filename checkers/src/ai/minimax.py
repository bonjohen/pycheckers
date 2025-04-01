from .evaluator import evaluate_board
from ..game.move_generator import get_possible_moves, get_all_moves, apply_move
from ..game.pieces import RED_PIECE, BLACK_PIECE

def minimax(board, depth, maximizing, alpha, beta, player):
    """
    Implements minimax algorithm with alpha-beta pruning.
    Returns (evaluation, best_move)
    """
    if depth < 0:
        raise ValueError("Depth must be non-negative")
        
    opponent_player = BLACK_PIECE if player == RED_PIECE else RED_PIECE
    moves = get_all_moves(board, player if maximizing else opponent_player, True)
    
    if depth == 0 or not moves:
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in moves:
            current = player if maximizing else opponent_player
            new_board = apply_move(board, move, current)
            eval_score, _ = minimax(new_board, depth - 1, False, alpha, beta, player)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            current = player if maximizing else opponent_player
            new_board = apply_move(board, move, current)
            eval_score, _ = minimax(new_board, depth - 1, True, alpha, beta, player)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


