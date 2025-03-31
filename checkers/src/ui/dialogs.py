import pygame
from .constants import *

def show_modal_dialog(screen, font, title, message, buttons):
    """
    Displays a modal dialog with the given title and message.
    Returns the button clicked.
    """
    dialog_width, dialog_height = 400, 200
    dialog_rect = pygame.Rect(
        (WIDTH - dialog_width) // 2,
        (HEIGHT - dialog_height) // 2,
        dialog_width,
        dialog_height
    )
    
    button_width, button_height = 100, 30
    gap = 20
    total_buttons_width = len(buttons) * button_width + (len(buttons) - 1) * gap
    start_x = dialog_rect.x + (dialog_width - total_buttons_width) // 2
    button_y = dialog_rect.y + dialog_height - button_height - 20

    button_rects = {}
    for i, label in enumerate(buttons):
        rect = pygame.Rect(
            start_x + i * (button_width + gap),
            button_y,
            button_width,
            button_height
        )
        button_rects[label] = rect

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for label, rect in button_rects.items():
                    if rect.collidepoint(pos):
                        return label

        # Draw dialog
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        
        # Draw title
        title_surf = font.render(title, True, BLACK)
        screen.blit(title_surf, (dialog_rect.x + 10, dialog_rect.y + 10))
        
        # Draw message
        lines = message.split('\n')
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, BLACK)
            screen.blit(text_surf, (dialog_rect.x + 10, dialog_rect.y + 40 + i * 20))
        
        # Draw buttons
        for label, rect in button_rects.items():
            pygame.draw.rect(screen, MENU_BG, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            text_surf = font.render(label, True, BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
            
        pygame.display.flip()