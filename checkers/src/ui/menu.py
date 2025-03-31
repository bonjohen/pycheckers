import pygame
from .constants import *

class MenuBar:
    def __init__(self, font):
        self.font = font
        self.menus = {
            "File": ["New Game", "Load Game", "Save Game", "Play Mode", "Exit"],
            "Help": ["Rules", "About"]
        }
        self.menu_rects = {}
        self.item_rects = {}
        self.active_menu = None
        
        # Calculate menu positions
        x = 5
        for title in self.menus:
            text_surf = self.font.render(title, True, BLACK)
            width = max(text_surf.get_width() + 20, 120)
            rect = pygame.Rect(x, 0, width, MENU_HEIGHT)
            self.menu_rects[title] = rect
            x += width + 5

    def draw(self, screen):
        """Draws the menu bar and active dropdown"""
        pygame.draw.rect(screen, MENU_BG, (0, 0, WIDTH, MENU_HEIGHT))
        
        for title, rect in self.menu_rects.items():
            color = MENU_HOVER if title == self.active_menu else MENU_BG
            pygame.draw.rect(screen, color, rect)
            text = self.font.render(title, True, BLACK)
            screen.blit(text, (rect.x + 10, rect.y + 5))

        if self.active_menu:
            self.draw_dropdown(screen)

    def draw_dropdown(self, screen):
        """Draws the active dropdown menu"""
        items = self.menus[self.active_menu]
        menu_rect = self.menu_rects[self.active_menu]
        
        dropdown_height = len(items) * MENU_HEIGHT
        dropdown_rect = pygame.Rect(
            menu_rect.x,
            MENU_HEIGHT,
            menu_rect.width,
            dropdown_height
        )
        
        pygame.draw.rect(screen, WHITE, dropdown_rect)
        pygame.draw.rect(screen, BLACK, dropdown_rect, 1)
        
        self.item_rects = {}  # Reset item_rects
        for i, item in enumerate(items):
            item_rect = pygame.Rect(
                dropdown_rect.x,
                MENU_HEIGHT + i * MENU_HEIGHT,
                dropdown_rect.width,
                MENU_HEIGHT
            )
            self.item_rects[item] = item_rect
            
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, MENU_HOVER, item_rect)
                
            text = self.font.render(item, True, BLACK)
            screen.blit(text, (item_rect.x + 10, item_rect.y + 5))

    def handle_event(self, event):
        """Handle menu events and return the selected action"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Check menu bar clicks
            for title, rect in self.menu_rects.items():
                if rect.collidepoint(pos):
                    self.active_menu = None if self.active_menu == title else title
                    return None
            
            # Check dropdown menu clicks
            if self.active_menu:
                items = self.menus[self.active_menu]
                for item in items:
                    if self.item_rects.get(item) and self.item_rects[item].collidepoint(pos):
                        action = item
                        self.active_menu = None
                        return action
                self.active_menu = None
        
        return None
