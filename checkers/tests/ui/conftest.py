import pytest
import pygame
from src.ui.constants import WIDTH, HEIGHT, SQUARE_SIZE

@pytest.fixture(scope="session")
def pygame_instance():
    """Initialize pygame for UI tests"""
    pygame.init()
    yield pygame
    pygame.quit()

@pytest.fixture
def test_screen():
    """Create a test screen surface"""
    return pygame.Surface((WIDTH, HEIGHT))

@pytest.fixture
def board_coordinates():
    """Common board coordinate calculations"""
    return {
        'square_size': SQUARE_SIZE,
        'center_points': [(r * SQUARE_SIZE + SQUARE_SIZE // 2, 
                          c * SQUARE_SIZE + SQUARE_SIZE // 2) 
                         for r in range(8) for c in range(8)]
    }