from ..game.pieces import *
from ..game.move_generator import get_all_moves

def evaluate_board(board):
    """Evaluates the current board state."""
    red_material = 0
    black_material = 0
    for row in board:
        for piece in row:
            if piece == RED_PIECE:
                red_material += 1
            elif piece == RED_KING:
                red_material += 1.5
            elif piece == BLACK_PIECE:
                black_material += 1
            elif piece == BLACK_KING:
                black_material += 1.5
    material = red_material - black_material
    
    # Consider mobility
    red_moves = len(get_all_moves(board, RED_PIECE))
    black_moves = len(get_all_moves(board, BLACK_PIECE))
    mobility = red_moves - black_moves
    
    return material + 0.1 * mobility


