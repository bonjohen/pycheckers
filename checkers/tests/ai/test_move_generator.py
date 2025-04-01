import pytest
from src.game.pieces import RED_PIECE, BLACK_PIECE, EMPTY
from src.game.move_generator import get_possible_moves

def test_must_capture_setting():
    """Test that MUST_CAPTURE setting correctly affects available moves"""
    # Setup a board where red has both regular moves and capture moves available
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    
    # Place a red piece that has both regular and capture moves
    board[5][2] = RED_PIECE
    # Place a black piece that can be captured
    board[4][3] = BLACK_PIECE
    # Leave empty spaces for both regular moves and capture landing
    board[4][1] = EMPTY  # Regular move
    board[3][4] = EMPTY  # Capture landing

    # Test with must_capture=True
    moves_must_capture = get_possible_moves(board, 5, 2, must_capture=True)
    assert len(moves_must_capture) == 1
    assert ((5, 2), (3, 4)) in moves_must_capture  # Only the capture move
    assert ((5, 2), (4, 1)) not in moves_must_capture  # Regular move should not be included

    # Test with must_capture=False
    moves_optional_capture = get_possible_moves(board, 5, 2, must_capture=False)
    assert len(moves_optional_capture) == 2
    assert ((5, 2), (3, 4)) in moves_optional_capture  # Capture move should be included
    assert ((5, 2), (4, 1)) in moves_optional_capture  # Regular move should also be included

def test_must_capture_multiple_options():
    """Test behavior when multiple captures are available"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    
    # Place a red piece with multiple capture opportunities
    board[6][1] = RED_PIECE
    # Place black pieces that can be captured
    board[5][2] = BLACK_PIECE
    board[5][0] = BLACK_PIECE
    # Empty landing spots
    board[4][3] = EMPTY
    board[4][1] = EMPTY

    # With must_capture=True, should only show capture moves
    moves_must_capture = get_possible_moves(board, 6, 1, must_capture=True)
    assert len(moves_must_capture) == 2
    assert all(abs(start[0] - end[0]) == 2 for start, end in moves_must_capture)  # All moves should be captures

    # With must_capture=False, should show both regular and capture moves
    moves_optional_capture = get_possible_moves(board, 6, 1, must_capture=False)
    assert len(moves_optional_capture) >= 2  # Should include at least the capture moves
    # Should include both captures and any available regular moves
    assert any(abs(start[0] - end[0]) == 2 for start, end in moves_optional_capture)  # Should have captures