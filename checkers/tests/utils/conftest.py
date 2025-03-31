import pytest
import tempfile
import os

@pytest.fixture
def temp_save_file():
    """Temporary file for testing save/load operations"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tf:
        yield tf.name
    os.unlink(tf.name)

@pytest.fixture
def sample_game_state():
    """Sample game state for testing file operations"""
    return {
        'board': [[' ' for _ in range(8)] for _ in range(8)],
        'current_player': 'r',
        'move_history': ['e3-d4', 'f6-e5']
    }