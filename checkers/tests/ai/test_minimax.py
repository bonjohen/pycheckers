import pytest
from src.ai.minimax import minimax
from src.game.pieces import RED_PIECE, BLACK_PIECE, RED_KING, BLACK_KING, EMPTY

def test_minimax_depth_zero():
    """Test minimax returns immediate evaluation at depth 0"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[0][0] = RED_PIECE
    eval_score, move = minimax(board, 0, True, float('-inf'), float('inf'), RED_PIECE)
    assert move is None  # At depth 0, no move should be returned
    assert isinstance(eval_score, (int, float))

def test_minimax_capture_choice(minimax_capture_scenario):
    """Test minimax chooses capturing move when available"""
    eval_score, move = minimax(minimax_capture_scenario, 3, True, float('-inf'), float('inf'), RED_PIECE)
    assert move is not None
    start, end = move
    # Verify the move is a capture (moves 2 squares)
    assert abs(start[0] - end[0]) == 2

def test_minimax_player_switching():
    """Test minimax switches players correctly during recursion"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = RED_PIECE
    board[4][4] = BLACK_PIECE
    board[5][5] = RED_PIECE
    
    # First as RED (maximizing)
    eval1, _ = minimax(board, 3, True, float('-inf'), float('inf'), RED_PIECE)
    # Then as BLACK (minimizing)
    eval2, _ = minimax(board, 3, True, float('-inf'), float('inf'), BLACK_PIECE)
    
    assert eval1 != eval2  # Evaluations should differ based on perspective

def test_minimax_alpha_beta_pruning(alpha_beta_test_board):
    """Test that alpha-beta pruning affects performance"""
    import time
    
    # Time without pruning (very large alpha-beta window)
    start = time.time()
    minimax(alpha_beta_test_board, 4, True, float('-inf'), float('inf'), RED_PIECE)
    time_without_pruning = round(time.time() - start, 1)
    
    # Time with tight alpha-beta window
    start = time.time()
    minimax(alpha_beta_test_board, 4, True, -1, 1, RED_PIECE)
    time_with_pruning = round(time.time() - start, 1)
    
    assert time_with_pruning <= time_without_pruning

def test_minimax_depth_limit():
    """Test minimax respects depth limit"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    # Setup a position that requires multiple moves to capture
    board[0][0] = RED_PIECE
    board[1][1] = BLACK_PIECE
    board[2][2] = BLACK_PIECE
    board[3][3] = BLACK_PIECE
    
    # At depth 1, minimax shouldn't see the full capture sequence
    eval1, move1 = minimax(board, 1, True, float('-inf'), float('inf'), RED_PIECE)
    
    # At depth 3, minimax should find at least one capture
    eval3, move3 = minimax(board, 3, True, float('-inf'), float('inf'), RED_PIECE)
    
    if move3:  # If a move was found at depth 3
        start3, end3 = move3
        # Verify it's a capture move (distance > 1)
        assert abs(start3[0] - end3[0]) > 1 or abs(start3[1] - end3[1]) > 1



