import pygame
from ..ui.constants import STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE
from .pieces import *

def initialize_board():
    """Returns an 8x8 board with 12 pieces per side."""
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

def apply_move(board, move):
    """Applies a move to the board and returns the new board state."""
    start, end = move
    new_board = [row[:] for row in board]
    sr, sc = start
    er, ec = end
    piece = new_board[sr][sc]
    new_board[sr][sc] = EMPTY
    new_board[er][ec] = piece
    
    # Handle captures
    if abs(er - sr) == 2:
        mr, mc = (sr + er) // 2, (sc + ec) // 2
        new_board[mr][mc] = EMPTY
        
    # Handle king promotion
    if piece == RED_PIECE and er == 0:
        new_board[er][ec] = RED_KING
    elif piece == BLACK_PIECE and er == 7:
        new_board[er][ec] = BLACK_KING
        
    return new_board

def board_rect():
    """Returns the rectangle for the board."""
    return pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE, BOARD_SIZE)

def cell_rect(row, col, boardR):
    """Returns the rectangle for a specific cell."""
    cell_w = boardR.width // 8
    cell_h = boardR.height // 8
    x = boardR.x + col * cell_w
    y = boardR.y + row * cell_h
    return pygame.Rect(x, y, cell_w, cell_h)


