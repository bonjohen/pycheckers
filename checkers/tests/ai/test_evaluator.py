import pytest
from src.ai.evaluator import evaluate_board
from src.game.pieces import RED_PIECE, BLACK_PIECE, RED_KING, BLACK_KING, EMPTY

def test_empty_board_evaluation():
    """Test that an empty board evaluates to 0"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    assert evaluate_board(board) == 0

def test_material_advantage():
    """Test that material advantage is reflected in evaluation"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    # Add one extra red piece
    board[0][0] = RED_PIECE
    board[7][7] = BLACK_PIECE
    board[6][6] = RED_PIECE
    
    eval_score = evaluate_board(board)
    assert eval_score > 0  # Red should be winning

def test_king_value():
    """Test that kings are valued more than regular pieces"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    
    # Board with one red king vs one black piece
    board[0][0] = RED_KING
    board[7][7] = BLACK_PIECE
    
    eval_score = evaluate_board(board)
    assert eval_score > 0.5  # King should be worth more than a regular piece

def test_mobility_factor():
    """Test that mobility affects evaluation"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    
    # Setup where red has more moves available
    board[3][3] = RED_PIECE
    board[7][7] = BLACK_PIECE  # Blocked in corner
    
    eval_mobile = evaluate_board(board)
    
    # Compare with equal material but less mobility
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[0][0] = RED_PIECE  # Both pieces in corners
    board[7][7] = BLACK_PIECE
    
    eval_immobile = evaluate_board(board)
    
    assert eval_mobile > eval_immobile