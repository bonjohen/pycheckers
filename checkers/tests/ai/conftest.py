import pytest
from src.game.pieces import EMPTY, RED_PIECE, BLACK_PIECE, RED_KING, BLACK_KING

@pytest.fixture
def minimax_capture_scenario():
    """Board setup for testing minimax capture decisions"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[2][3] = BLACK_PIECE
    board[3][2] = RED_PIECE
    return board

@pytest.fixture
def alpha_beta_test_board():
    """Complex board setup to test alpha-beta pruning efficiency"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    # Setup multiple capture possibilities
    board[1][1] = RED_PIECE
    board[2][2] = BLACK_PIECE
    board[3][3] = BLACK_PIECE
    return board