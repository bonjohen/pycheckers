import pygame
from .constants import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 16)

    def draw_board(self, board, selected_piece, valid_moves):
        """Draws the checker board and pieces"""
        boardR = pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE, BOARD_SIZE)
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = DARK_GRAY if (row + col) % 2 else WHITE
                rect = pygame.Rect(
                    boardR.x + col * SQUARE_SIZE,
                    boardR.y + row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)

                # Draw pieces
                piece = board[row][col]
                if piece != ' ':
                    self.draw_piece(row, col, piece, selected_piece)

        # Highlight valid moves
        for move in valid_moves:
            _, (row, col) = move
            pygame.draw.circle(
                self.screen,
                GREEN,
                (boardR.x + col * SQUARE_SIZE + SQUARE_SIZE//2,
                 boardR.y + row * SQUARE_SIZE + SQUARE_SIZE//2),
                10
            )

    def draw_piece(self, row, col, piece, selected_piece):
        """Draws a single piece"""
        boardR = pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE, BOARD_SIZE)
        center = (
            boardR.x + col * SQUARE_SIZE + SQUARE_SIZE//2,
            boardR.y + row * SQUARE_SIZE + SQUARE_SIZE//2
        )
        
        color = RED if piece.lower() == 'r' else BLACK
        pygame.draw.circle(self.screen, color, center, SQUARE_SIZE//2 - 4)
        
        if piece.isupper():  # King piece
            pygame.draw.circle(self.screen, YELLOW, center, 10)
            
        if selected_piece and (row, col) == selected_piece:
            pygame.draw.circle(self.screen, GREEN, center, SQUARE_SIZE//2 - 2, 2)