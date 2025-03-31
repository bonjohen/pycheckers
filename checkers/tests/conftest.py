import pytest
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add any shared fixtures here
@pytest.fixture
def empty_board():
    """Returns an empty 8x8 board"""
    from src.game.pieces import EMPTY
    return [[EMPTY for _ in range(8)] for _ in range(8)]