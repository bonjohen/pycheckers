import pygame
import sys
import time
import logging
import tkinter as tk
from tkinter import filedialog

# Setup logging for diagnostics.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# ----------------------
# Constants & Colors
# ----------------------
WIDTH, HEIGHT = 1000, 700
MENU_HEIGHT = 30
STATUS_HEIGHT = 30
BOARD_AREA_WIDTH = int(WIDTH * 0.8)
HISTORY_AREA_WIDTH = WIDTH - BOARD_AREA_WIDTH
BOARD_SIZE = HEIGHT - MENU_HEIGHT - STATUS_HEIGHT  # square board area
SQUARE_SIZE = BOARD_SIZE // 8

# The remaining 20% of WIDTH is split equally into left and right storage regions.
STORAGE_WIDTH = (WIDTH - BOARD_AREA_WIDTH) // 2

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (180, 180, 180)
DARK_GRAY  = (100, 100, 100)
RED        = (200, 0, 0)
GREEN      = (0, 200, 0)
BLUE       = (0, 0, 255)
YELLOW     = (240, 240, 0)
BG_COLOR   = (220, 220, 220)
MENU_BG    = (200, 200, 200)
MENU_HOVER = (170, 170, 170)

# Piece definitions
EMPTY       = ' '
RED_PIECE   = 'r'
RED_KING    = 'R'
BLACK_PIECE = 'b'
BLACK_KING  = 'B'

# Game modes
MODE_2P = "2P"
MODE_1P = "1P"  # one-player: human (red) vs AI (black)

# AI search depth
AI_DEPTH = 1 # 3 is really hard!

# ----------------------
# Helper Functions
# ----------------------
def opponent(piece):
    """
    Given a piece ('r', 'R', 'b', or 'B'), returns a tuple of the opponent's pieces.
    For red pieces, returns ('b', 'B'); for black pieces, returns ('r', 'R').
    """
    if piece.lower() == 'r':
        return ('b', 'B')
    elif piece.lower() == 'b':
        return ('r', 'R')
    else:
        return ()

def is_king(piece):
    """
    Returns True if the given piece is a king ('R' or 'B').
    """
    return piece in ('R', 'B')

def parse_move(move_str):
    """
    Parses a move string formatted as "(r,c)->(r,c)" and returns a tuple of tuples: ((r,c), (r,c)).
    If parsing fails, returns None.
    """
    try:
        parts = move_str.split("->")
        start = parts[0].strip().strip("()")
        end = parts[1].strip().strip("()")
        sr, sc = map(int, start.split(","))
        er, ec = map(int, end.split(","))
        return ((sr, sc), (er, ec))
    except Exception as e:
        logging.error(f"Error parsing move '{move_str}': {e}")
        return None

# ----------------------
# Global Modal Dialog Functions
# ----------------------
def show_modal_dialog(screen, font, title, message, buttons):
    """
    Displays a modal dialog with the given title and multi-line message.
    Blocks until the user clicks one of the buttons and returns that button's label.
    """
    logging.debug(f"Showing modal dialog: {title}")
    dialog_width, dialog_height = 400, 200
    dialog_rect = pygame.Rect((WIDTH - dialog_width) // 2, (HEIGHT - dialog_height) // 2,
                              dialog_width, dialog_height)
    button_width, button_height = 100, 30
    gap = 20
    total_buttons_width = len(buttons) * button_width + (len(buttons) - 1) * gap
    start_x = dialog_rect.x + (dialog_width - total_buttons_width) // 2
    button_y = dialog_rect.y + dialog_height - button_height - 20

    button_rects = {}
    for i, label in enumerate(buttons):
        rect = pygame.Rect(start_x + i * (button_width + gap), button_y, button_width, button_height)
        button_rects[label] = rect

    lines = message.split('\n')
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for label, rect in button_rects.items():
                    if rect.collidepoint(pos):
                        return label
            elif event.type == pygame.KEYDOWN:
                pass

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_surf = font.render(title, True, BLACK)
        screen.blit(title_surf, (dialog_rect.x + 20, dialog_rect.y + 20))
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, BLACK)
            screen.blit(line_surf, (dialog_rect.x + 20, dialog_rect.y + 60 + i * font.get_height()))
        for label, rect in button_rects.items():
            pygame.draw.rect(screen, MENU_BG, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            label_surf = font.render(label, True, BLACK)
            screen.blit(label_surf, (rect.centerx - label_surf.get_width() // 2,
                                     rect.centery - label_surf.get_height() // 2))
        pygame.display.flip()

def show_rules_dialog(screen, font):
    rules_text = (
        "Checkers Rules:\n\n"
        "1. Played on an 8x8 board with 12 pieces per side.\n"
        "2. Pieces move diagonally on dark squares.\n"
        "3. Captures are not forced; you may choose a safe move.\n"
        "4. When a piece reaches the opposite end, it becomes a king.\n"
        "5. Extra hops are allowed; press Escape to skip extra hops.\n\n"
        "Press any key to close."
    )
    show_modal_dialog(screen, font, "Rules", rules_text, ["OK"])

def show_about_dialog(screen, font):
    about_text = (
        "Amazing Checkers\n"
        "by John Boen.\n"
        "A vibe coding exercise using Pygame."
    )
    show_modal_dialog(screen, font, "About", about_text, ["OK"])

# ----------------------
# File Dialog Helpers (using Tkinter)
# ----------------------
def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(title="Load Game", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    root.destroy()
    return filename

def save_file_dialog():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(title="Save Game", defaultextension=".txt",
                                            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    root.destroy()
    return filename

# ----------------------
# Board Helpers
# ----------------------
def initialize_board():
    """
    Returns an 8x8 board with 12 pieces per side.
    Black pieces occupy dark squares in the top 3 rows; Red pieces in the bottom 3 rows.
    """
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = BLACK_PIECE
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = RED_PIECE
    logging.debug("Board initialized.")
    return board

def board_rect():
    """
    Returns the rectangle for the board.
    The board is offset to the right by STORAGE_WIDTH so that the left storage region is visible.
    """
    return pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE, BOARD_SIZE)

def cell_rect(row, col, boardR):
    cell_w = boardR.width // 8
    cell_h = boardR.height // 8
    x = boardR.x + col * cell_w
    y = boardR.y + row * cell_h
    return pygame.Rect(x, y, cell_w, cell_h)

def apply_move(board, move):
    """
    Returns a new board with the move applied, handling captures and king promotion.
    """
    new_board = [row[:] for row in board]
    (sr, sc), (er, ec) = move
    piece = new_board[sr][sc]
    new_board[er][ec] = piece
    new_board[sr][sc] = EMPTY
    if abs(er - sr) == 2:
        mid_r, mid_c = (sr + er) // 2, (sc + ec) // 2
        new_board[mid_r][mid_c] = EMPTY
    if piece == RED_PIECE and er == 0:
        new_board[er][ec] = RED_KING
    elif piece == BLACK_PIECE and er == 7:
        new_board[er][ec] = BLACK_KING
    return new_board

# ----------------------
# Move Generation & Multi-Jump Logic
# ----------------------
def get_possible_moves(board, row, col):
    """
    Returns a list of legal moves for the piece at (row, col).
    Both safe moves and capturing moves are returned.
    """
    moves = []
    piece = board[row][col]
    if piece == EMPTY:
        return moves
    if piece == RED_PIECE:
        directions = [(-1, -1), (-1, 1)]
    elif piece == BLACK_PIECE:
        directions = [(1, -1), (1, 1)]
    else:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        new_r, new_c = row + dr, col + dc
        if 0 <= new_r < 8 and 0 <= new_c < 8 and board[new_r][new_c] == EMPTY:
            moves.append(((row, col), (new_r, new_c)))
    capture_moves = []
    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2 * dr, col + 2 * dc
        if (0 <= mid_r < 8 and 0 <= mid_c < 8 and 0 <= end_r < 8 and 0 <= end_c < 8):
            if board[mid_r][mid_c] in opponent(piece) and board[end_r][end_c] == EMPTY:
                capture_moves.append(((row, col), (end_r, end_c)))
    return moves + capture_moves

def get_all_moves(board, player):
    """
    Returns all legal moves for the given player.
    """
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c].lower() == player:
                moves.extend(get_possible_moves(board, r, c))
    return moves

def get_capturing_moves_from(board, row, col):
    """
    Returns only the capturing moves available from (row, col).
    """
    moves = []
    piece = board[row][col]
    if piece == EMPTY:
        return moves
    if piece == RED_PIECE:
        directions = [(-1, -1), (-1, 1)]
    elif piece == BLACK_PIECE:
        directions = [(1, -1), (1, 1)]
    else:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2 * dr, col + 2 * dc
        if (0 <= mid_r < 8 and 0 <= mid_c < 8 and 0 <= end_r < 8 and 0 <= end_c < 8):
            if board[mid_r][mid_c] in opponent(piece) and board[end_r][end_c] == EMPTY:
                moves.append(((row, col), (end_r, end_c)))
    return moves

# ----------------------
# Evaluation & AI (Minimax with Alpha-Beta)
# ----------------------
def evaluate_board(board):
    red_material = 0
    black_material = 0
    for row in board:
        for piece in row:
            if piece == RED_PIECE:
                red_material += 1
            elif piece == RED_KING:
                red_material += 1.5
            elif piece == BLACK_PIECE:
                black_material += 1
            elif piece == BLACK_KING:
                black_material += 1.5
    material = red_material - black_material
    red_moves = len(get_all_moves(board, RED_PIECE))
    black_moves = len(get_all_moves(board, BLACK_PIECE))
    mobility = red_moves - black_moves
    return material + 0.1 * mobility

def minimax(board, depth, maximizing, alpha, beta, player):
    moves = get_all_moves(board, player)
    if depth == 0 or not moves:
        return evaluate_board(board), None
    best_move = None
    opponent_player = RED_PIECE if player == BLACK_PIECE else BLACK_PIECE
    if maximizing:
        max_eval = -float('inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_val, _ = minimax(new_board, depth - 1, False, alpha, beta, opponent_player)
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(board, move)
            eval_val, _ = minimax(new_board, depth - 1, True, alpha, beta, opponent_player)
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move

# ----------------------
# Custom MenuBar with Fixed Width Drop-Down
# ----------------------
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
        x = 5
        for title in self.menus:
            text_surf = self.font.render(title, True, BLACK)
            width = max(text_surf.get_width() + 20, 120)
            rect = pygame.Rect(x, 0, width, MENU_HEIGHT)
            self.menu_rects[title] = rect
            x += width + 5
        logging.debug("MenuBar initialized.")

    def draw(self, surface):
        pygame.draw.rect(surface, MENU_BG, (0, 0, WIDTH, MENU_HEIGHT))
        for title, rect in self.menu_rects.items():
            color = MENU_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else MENU_BG
            pygame.draw.rect(surface, color, rect)
            text_surf = self.font.render(title, True, BLACK)
            surface.blit(text_surf, (rect.x + 10, rect.y + (MENU_HEIGHT - text_surf.get_height()) // 2))
            # Underline the first letter.
            first_letter_surf = self.font.render(title[0], True, BLACK)
            start = (rect.x + 10, rect.y + (MENU_HEIGHT - first_letter_surf.get_height()) // 2 + first_letter_surf.get_height())
            end = (start[0] + first_letter_surf.get_width(), start[1])
            pygame.draw.line(surface, BLACK, start, end, 2)
        if self.active_menu:
            items = self.menus[self.active_menu]
            max_item_width = max(self.font.render(item, True, BLACK).get_width() for item in items) + 20
            base_rect = self.menu_rects[self.active_menu]
            self.item_rects[self.active_menu] = []
            for i, item in enumerate(items):
                item_rect = pygame.Rect(base_rect.x, MENU_HEIGHT + i * MENU_HEIGHT, max_item_width, MENU_HEIGHT)
                self.item_rects[self.active_menu].append(item_rect)
                pygame.draw.rect(surface, MENU_BG, item_rect)
                item_surf = self.font.render(item, True, BLACK)
                surface.blit(item_surf, (item_rect.x + 10, item_rect.y + (MENU_HEIGHT - item_surf.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for title, rect in self.menu_rects.items():
                if rect.collidepoint(pos):
                    logging.debug(f"Top-level menu '{title}' clicked.")
                    self.active_menu = None if self.active_menu == title else title
                    return None
            if self.active_menu:
                for i, rect in enumerate(self.item_rects.get(self.active_menu, [])):
                    if rect.collidepoint(pos):
                        action = self.menus[self.active_menu][i]
                        logging.debug(f"Menu item '{action}' from '{self.active_menu}' clicked.")
                        self.active_menu = None
                        return action
                self.active_menu = None
        return None

# ----------------------
# Main Checkers Game Class
# ----------------------
class CheckersGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Checkers")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.board = initialize_board()
        self.current_player = RED_PIECE  # Red always starts.
        self.mode = MODE_1P
        self.selected_piece = None
        self.valid_moves = []
        # Accumulate half-turn moves for each side.
        self.current_red_moves = []
        self.current_black_moves = []
        self.turn_number = 0
        self.move_history = []  # Aggregated turn history.
        self.time_red = 0
        self.time_black = 0
        self.last_timer_update = time.time()
        self.menu_bar = MenuBar(self.font)
        self.history_scroll = 0
        self.dirty = False
        self.multi_hop_message = False
        # Initialize captured pieces storage.
        self.captured_black = []   # Black pieces captured by Red.
        self.captured_red = []     # Red pieces captured by Black.
        logging.debug("CheckersGame initialized in 1-player mode.")

    def handle_menu_action(self, action):
        logging.debug(f"Menu action received: {action}")
        if action == "New Game":
            if self.dirty:
                result = show_modal_dialog(self.screen, self.font, "Warning",
                                             "Game data has changed since the last save.",
                                             ["X", "Cancel", "Continue"])
                if result != "Continue":
                    return
            self.new_game()
        elif action == "Load Game":
            if self.dirty:
                result = show_modal_dialog(self.screen, self.font, "Warning",
                                             "Game data has changed since the last save.",
                                             ["X", "Cancel", "Continue"])
                if result != "Continue":
                    return
            self.load_game()
        elif action == "Save Game":
            self.save_game()
        elif action == "Play Mode":
            self.mode = MODE_1P if self.mode == MODE_2P else MODE_2P
            self.current_red_moves.append(f"Play Mode changed to {self.mode}")
            self.dirty = True
        elif action == "Exit":
            self.attempt_exit()
        elif action == "Rules":
            rules_text = ("Checkers is played on an 8x8 board with 12 pieces per side. "
                          "Pieces move diagonally on dark squares. Captures are mandatory. "
                          "When a piece reaches the far side, it becomes a king. "
                          "During a capture, you may skip extra hops by pressing the escape key.")
            show_modal_dialog(self.screen, self.font, "Rules", rules_text, ["OK"])
        elif action == "About":
            about_text = ("Checkers Game by ChatGPT.\n"
                          "Developed with Python and PyGame.\n"
                          "Enjoy playing!")
            show_modal_dialog(self.screen, self.font, "About", about_text, ["OK"])

    def new_game(self):
        logging.debug("Starting new game.")
        self.board = initialize_board()
        self.current_player = RED_PIECE
        self.move_history.clear()
        self.current_red_moves.clear()
        self.current_black_moves.clear()
        self.turn_number = 0
        self.selected_piece = None
        self.valid_moves = []
        self.time_red = 0
        self.time_black = 0
        self.last_timer_update = time.time()
        self.dirty = False
        self.multi_hop_message = False
        self.captured_black.clear()
        self.captured_red.clear()

    def load_game(self):
        filename = open_file_dialog()
        if not filename:
            return
        try:
            with open(filename, "r") as f:
                lines = f.read().splitlines()
            # Reset game.
            self.new_game()
            # We assume each turn has two lines: one for Red and one for Black.
            # We'll parse these lines, then replay the moves sequentially.
            turns = {}
            for line in lines:
                if line.startswith("Turn"):
                    # Expected format: "Turn X R: (r,c)->(r,c) | (r,c)->(r,c)"
                    parts = line.split()
                    turn_num = int(parts[1])
                    side = parts[2].strip(':')
                    moves_str = line.split(":", 1)[1].strip()
                    if moves_str == "--":
                        continue
                    moves_list = [m.strip() for m in moves_str.split("|")]
                    if turn_num not in turns:
                        turns[turn_num] = {}
                    turns[turn_num][side] = moves_list
                    # Also record the move history entry.
                    self.move_history.append(line)
            # Replay moves in order.
            for t in sorted(turns.keys()):
                # Replay Red's moves.
                if "R" in turns[t]:
                    for move_str in turns[t]["R"]:
                        move = parse_move(move_str)
                        if move:
                            self.board = apply_move(self.board, move)
                # Replay Black's moves.
                if "B" in turns[t]:
                    for move_str in turns[t]["B"]:
                        move = parse_move(move_str)
                        if move:
                            self.board = apply_move(self.board, move)
            logging.debug("Game loaded and moves replayed from file.")
        except Exception as e:
            logging.error(f"Error loading game: {e}")

    def save_game(self):
        filename = save_file_dialog()
        if not filename:
            return
        try:
            with open(filename, "w") as f:
                for line in self.move_history:
                    f.write(line + "\n")
            logging.debug("Game saved to file.")
        except Exception as e:
            logging.error(f"Error saving game: {e}")

    def finish_half_turn(self, player, move_str):
        if player == RED_PIECE:
            self.current_red_moves.append(move_str)
        else:
            self.current_black_moves.append(move_str)

    def complete_turn(self):
        """Aggregate the current half-turn moves into two history entries with the same turn number."""
        self.turn_number += 1
        red_entry = f"Turn {self.turn_number} R: " + " | ".join(self.current_red_moves) if self.current_red_moves else f"Turn {self.turn_number} R: --"
        black_entry = f"Turn {self.turn_number} B: " + " | ".join(self.current_black_moves) if self.current_black_moves else f"Turn {self.turn_number} B: --"
        self.move_history.append(red_entry)
        self.move_history.append(black_entry)
        logging.debug(f"Completed turn {self.turn_number}: {red_entry} || {black_entry}")
        self.current_red_moves.clear()
        self.current_black_moves.clear()

    def switch_turn(self):
        if self.current_player == BLACK_PIECE:
            self.complete_turn()
        self.current_player = RED_PIECE if self.current_player == BLACK_PIECE else BLACK_PIECE
        logging.debug(f"Switched turn. Now it's {'RED' if self.current_player == RED_PIECE else 'BLACK'}'s turn.")

    def ai_move(self):
        logging.debug("AI turn triggered.")
        _, best_move = minimax(self.board, AI_DEPTH, False, -float('inf'), float('inf'), BLACK_PIECE)
        if best_move:
            (sr, sc), (er, ec) = best_move
            move_str = f"({sr},{sc})->({er},{ec})"
            self.finish_half_turn(BLACK_PIECE, move_str)
            logging.debug(f"AI move executed: {move_str}")
            self.board = apply_move(self.board, best_move)
            self.switch_turn()
        else:
            self.finish_half_turn(BLACK_PIECE, "No moves")
            logging.debug("AI has no moves.")

    def handle_board_click(self, pos):
        boardR = board_rect()
        cell_w = boardR.width // 8
        cell_h = boardR.height // 8
        col = (pos[0] - boardR.x) // cell_w
        row = (pos[1] - boardR.y) // cell_h
        logging.debug(f"Cell clicked: ({row}, {col})")
        if self.selected_piece:
            move = (self.selected_piece, (row, col))
            possible = get_possible_moves(self.board, self.selected_piece[0], self.selected_piece[1])
            if move in possible:
                move_str = f"({self.selected_piece[0]},{self.selected_piece[1]})->({row},{col})"
                self.finish_half_turn(self.current_player, move_str)
                self.board = apply_move(self.board, move)
                if abs(row - self.selected_piece[0]) == 2:
                    further = get_capturing_moves_from(self.board, row, col)
                    if further:
                        self.multi_hop_message = True
                        self.selected_piece = (row, col)
                        self.valid_moves = further
                        logging.debug("Extra hops available. Waiting for player input or escape.")
                        return
                self.switch_turn()
                self.selected_piece = None
                self.valid_moves = []
                self.multi_hop_message = False
                if self.mode == MODE_1P and self.current_player == BLACK_PIECE:
                    self.ai_move()
            else:
                # If the clicked cell is empty, clear selection.
                if self.board[row][col] == EMPTY:
                    logging.debug("Clicked empty cell. Unselecting piece.")
                    self.selected_piece = None
                    self.valid_moves = []
                # Else if clicked on a piece of the current player, change selection.
                elif self.board[row][col].lower() == self.current_player:
                    self.selected_piece = (row, col)
                    self.valid_moves = get_possible_moves(self.board, row, col)
                    logging.debug(f"Selection changed to piece at ({row}, {col}).")
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            if self.board[row][col].lower() == self.current_player:
                self.selected_piece = (row, col)
                self.valid_moves = get_possible_moves(self.board, row, col)
                logging.debug(f"Piece at ({row}, {col}) selected.")
            else:
                self.selected_piece = None
                self.valid_moves = []

    def skip_extra_hops(self):
        self.finish_half_turn(self.current_player, "Extra hops skipped")
        self.switch_turn()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                logging.debug(f"KEYDOWN: key={event.key} mod={event.mod}")
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_f:
                        self.menu_bar.active_menu = "File"
                    elif event.key == pygame.K_h:
                        self.menu_bar.active_menu = "Help"
                if event.key == pygame.K_ESCAPE and self.multi_hop_message:
                    self.skip_extra_hops()
            action = self.menu_bar.handle_event(event)
            if action:
                self.handle_menu_action(action)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    if event.button == 4:
                        self.history_scroll = max(self.history_scroll - 20, 0)
                    else:
                        self.history_scroll += 20
                board_area = pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_AREA_WIDTH, BOARD_SIZE)
                if board_area.collidepoint(event.pos):
                    if self.mode == MODE_2P or (self.mode == MODE_1P and self.current_player == RED_PIECE):
                        self.handle_board_click(event.pos)

    def check_game_over(self):
        moves = get_all_moves(self.board, self.current_player)
        if not moves:
            logging.debug("Game over: No moves for current player.")
            res = show_modal_dialog(self.screen, self.font, "Game Over",
                                    "Thank you for a good game! Play again?", ["Yes", "No"])
            if res == "Yes":
                self.new_game()
            else:
                pygame.quit(); sys.exit()
            return True
        return False

    def update_timers(self):
        now = time.time()
        delta = now - self.last_timer_update
        self.last_timer_update = now
        if self.current_player == RED_PIECE:
            self.time_red += delta
        else:
            self.time_black += delta

    def draw(self):
        self.screen.fill(BG_COLOR)
        # Draw board area.
        board_area_rect = pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_AREA_WIDTH, BOARD_SIZE)
        pygame.draw.rect(self.screen, DARK_GRAY, board_area_rect)
        boardR = board_rect()
        for row in range(8):
            for col in range(8):
                cell = pygame.Rect(boardR.x + col * SQUARE_SIZE,
                                   boardR.y + row * SQUARE_SIZE,
                                   SQUARE_SIZE, SQUARE_SIZE)
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(self.screen, color, cell)
                if self.selected_piece == (row, col):
                    pygame.draw.rect(self.screen, YELLOW, cell, 3)
                elif any(m[1] == (row, col) for m in self.valid_moves):
                    pygame.draw.rect(self.screen, BLUE, cell, 3)
                piece = self.board[row][col]
                if piece != EMPTY:
                    center = (cell.x + SQUARE_SIZE // 2, cell.y + SQUARE_SIZE // 2)
                    radius = SQUARE_SIZE // 2 - 5
                    col_color = RED if piece.lower() == RED_PIECE else BLACK
                    pygame.draw.circle(self.screen, col_color, center, radius)
                    if is_king(piece):
                        pygame.draw.circle(self.screen, YELLOW, center, radius // 2)
        # Draw storage regions.
        left_storage = pygame.Rect(0, MENU_HEIGHT, STORAGE_WIDTH, BOARD_SIZE)
        right_storage = pygame.Rect(STORAGE_WIDTH + BOARD_AREA_WIDTH, MENU_HEIGHT, STORAGE_WIDTH, BOARD_SIZE)
        pygame.draw.rect(self.screen, DARK_GRAY, left_storage)
        pygame.draw.rect(self.screen, DARK_GRAY, right_storage)
        for i, piece in enumerate(self.captured_black):
            pos = (10 + i * 40, MENU_HEIGHT + 10)
            pygame.draw.circle(self.screen, BLACK, pos, 18)
            if is_king(piece):
                pygame.draw.circle(self.screen, YELLOW, pos, 9)
        for i, piece in enumerate(self.captured_red):
            pos = (right_storage.x + 10 + i * 40, MENU_HEIGHT + 10)
            pygame.draw.circle(self.screen, RED, pos, 18)
            if is_king(piece):
                pygame.draw.circle(self.screen, YELLOW, pos, 9)
        # Draw move history.
        history_rect = pygame.Rect(BOARD_AREA_WIDTH, MENU_HEIGHT, HISTORY_AREA_WIDTH, BOARD_SIZE)
        pygame.draw.rect(self.screen, WHITE, history_rect)
        pygame.draw.rect(self.screen, BLACK, history_rect, 2)
        line_h = self.font.get_height() + 2
        y_off = history_rect.y + 5 - self.history_scroll
        for line in self.move_history:
            row_color = RED if line.startswith("Turn") and " R:" in line else BLACK
            surf = self.font.render(line, True, row_color)
            self.screen.blit(surf, (history_rect.x + 5, y_off))
            y_off += line_h
        # Draw status bar.
        status_rect = pygame.Rect(0, HEIGHT - STATUS_HEIGHT, WIDTH, STATUS_HEIGHT)
        pygame.draw.rect(self.screen, MENU_BG, status_rect)
        red_count = sum(row.count(RED_PIECE) + row.count(RED_KING) for row in self.board)
        black_count = sum(row.count(BLACK_PIECE) + row.count(BLACK_KING) for row in self.board)
        red_time = time.strftime("%H:%M:%S", time.gmtime(self.time_red))
        black_time = time.strftime("%H:%M:%S", time.gmtime(self.time_black))
        mode_text = "One Player" if self.mode == MODE_1P else "Two Player"
        red_text = self.font.render(f"Red: {red_time} Pieces: {red_count}", True, RED)
        black_text = self.font.render(f"Black: {black_time} Pieces: {black_count}", True, BLACK)
        mode_surf = self.font.render(mode_text, True, BLUE)
        self.screen.blit(red_text, (10, HEIGHT - STATUS_HEIGHT + 5))
        self.screen.blit(black_text, (WIDTH - black_text.get_width() - 10, HEIGHT - STATUS_HEIGHT + 5))
        self.screen.blit(mode_surf, ((WIDTH - mode_surf.get_width()) // 2, HEIGHT - STATUS_HEIGHT + 5))
        # Draw menu last so it stays on top.
        self.menu_bar.draw(self.screen)

    def run(self):
        while True:
            self.clock.tick(30)
            self.handle_events()
            self.update_timers()
            if self.check_game_over():
                continue
            if self.mode == MODE_1P and self.current_player == BLACK_PIECE:
                self.ai_move()
            self.draw()
            pygame.display.flip()

# ----------------------
# Main Entry Point
# ----------------------
if __name__ == "__main__":
    game = CheckersGame()
    game.run()
