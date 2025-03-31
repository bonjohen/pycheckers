import pytest
from src.game.pieces import EMPTY, RED_PIECE, BLACK_PIECE, RED_KING, BLACK_KING

@pytest.fixture
def standard_board():
    """Standard starting position"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = BLACK_PIECE
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = RED_PIECE
    return board

@pytest.fixture
def king_promotion_board():
    """Board setup for testing king promotion scenarios"""
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[1][1] = RED_PIECE  # About to be kinged
    return board