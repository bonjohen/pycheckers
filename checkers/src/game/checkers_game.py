import pygame
import time
import sys
import logging
from src.ui.constants import *
from src.ui.renderer import Renderer
from src.ui.menu import MenuBar
from src.ui.dialogs import show_modal_dialog
from src.utils.file_handler import save_game, load_game, save_file_dialog, open_file_dialog
from src.utils.logger import setup_logger
from src.ai.minimax import minimax
from src.game.board import initialize_board, apply_move, board_rect
from src.game.move_generator import get_possible_moves, get_capturing_moves_from, parse_move, get_all_moves
from src.game.pieces import *
from src.ui.constants import *

# Setup logging
setup_logger()

class CheckersGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Checkers")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        self.renderer = Renderer(self.screen)
        self.menu_bar = MenuBar(self.font)
        
        # Game state
        self.board = initialize_board()
        self.current_player = RED_PIECE  # Red always starts
        self.mode = "1P"  # "1P" or "2P"
        self.engine_first = False
        self.selected_piece = None
        self.valid_moves = []
        self.must_capture = True
        self.status = "ACTIVE"  # "ACTIVE", "PAUSED", or "COMPLETED"
        
        # Move tracking
        self.current_red_moves = []
        self.current_black_moves = []
        self.turn_number = 0
        self.move_history = []
        self.history_scroll = 0  # Added missing attribute
        
        # UI state
        self.multi_hop_message = False  # Added missing attribute
        
        # Time tracking
        self.time_red = 0
        self.time_black = 0
        self.last_timer_update = time.time()
        self.dirty = False

    def new_game(self, engine_first=False):
        """Initializes a new game"""
        self.board = initialize_board()
        self.current_player = RED_PIECE
        self.engine_first = engine_first
        self.selected_piece = None
        self.valid_moves = []
        self.move_history = []
        self.history_scroll = 0  # Reset scroll position
        self.multi_hop_message = False  # Reset message state
        self.time_red = 0
        self.time_black = 0
        self.last_timer_update = time.time()
        self.mode = "1P"
        self.status = "ACTIVE"  # Reset status to ACTIVE
        self.dirty = False
        self.current_red_moves = []  # Reset move tracking
        self.current_black_moves = []
        self.turn_number = 0
        
        logging.debug(f"New game initialized (engine_first={engine_first})")
        
        # If engine should move first, switch sides
        if engine_first:
            self.current_player = BLACK_PIECE

    def pause_game(self):
        """Pause the game"""
        if self.status == "ACTIVE":
            self.status = "PAUSED"
            logging.debug("Game paused")

    def resume_game(self):
        """Resume the game"""
        if self.status == "PAUSED":
            self.status = "ACTIVE"
            self.last_timer_update = time.time()  # Reset timer
            logging.debug("Game resumed")

    def end_game(self, winner=None):
        """End the game"""
        self.status = "COMPLETED"
        logging.debug(f"Game ended. Winner: {winner}")

    def run(self):
        """Main game loop"""
        # If engine moves first, make the first move
        if self.engine_first and self.mode == "1P":
            self.current_player = BLACK_PIECE  # Set current player to black first
            self.ai_move()
        
        while True:
            self.clock.tick(30)
            self.handle_events()
            self.update_timers()
            
            if self.mode == "1P" and self.current_player == BLACK_PIECE:
                self.ai_move()
                
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.menu_bar.active_menu = "File"
                elif event.key == pygame.K_h:
                    self.menu_bar.active_menu = "Help"
            
            # Handle menu events
            menu_action = self.menu_bar.handle_event(event)
            if menu_action:
                self.handle_menu_action(menu_action)
                continue
            
            # Handle mouse clicks on the board
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):  # Mouse wheel
                    if event.button == 4:  # Scroll up
                        self.history_scroll = max(self.history_scroll - 20, 0)
                    else:  # Scroll down
                        self.history_scroll += 20
                else:  # Regular click
                    # Check if click is within board boundaries
                    board_rect = pygame.Rect(STORAGE_WIDTH, MENU_HEIGHT, BOARD_SIZE, BOARD_SIZE)
                    if board_rect.collidepoint(event.pos):
                        if self.mode == "2P" or (self.mode == "1P" and self.current_player == RED_PIECE):
                            self.handle_board_click(event.pos)

    def handle_board_click(self, pos):
        """Handle mouse clicks on the game board"""
        if self.status != "ACTIVE":
            return
        
        boardR = board_rect()
        cell_w = boardR.width // 8
        cell_h = boardR.height // 8
        col = (pos[0] - boardR.x) // cell_w
        row = (pos[1] - boardR.y) // cell_h
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        logging.debug(f"[handle_click] Cell clicked: ({row}, {col})")
        logging.debug(f"[handle_click] Current player: {self.current_player}")
        logging.debug(f"[handle_click] Board state at clicked position: {self.board[row][col]}")

        if self.selected_piece:
            move = (self.selected_piece, (row, col))
            possible = get_possible_moves(self.board, self.selected_piece[0], self.selected_piece[1], self.must_capture)
            
            if move in possible:
                # Apply the move
                self.board = apply_move(self.board, move, self.current_player)
                move_str = f"({self.selected_piece[0]},{self.selected_piece[1]})->({row},{col})"
                self.finish_half_turn(self.current_player, move_str)
                
                # Check for additional captures
                if abs(row - self.selected_piece[0]) == 2:
                    further = get_capturing_moves_from(self.board, row, col)
                    if further:
                        self.multi_hop_message = True
                        self.selected_piece = (row, col)
                        self.valid_moves = further
                        logging.debug("Extra hops available")
                        return
                
                # Clear selection and switch turns
                self.selected_piece = None
                self.valid_moves = []
                self.multi_hop_message = False
                self.switch_turn()
                
                # If it's AI's turn, make the move
                if self.mode == "1P" and self.current_player == BLACK_PIECE:
                    self.ai_move()
            else:
                # If clicking on own piece, select it instead
                if self.board[row][col].lower() == self.current_player:
                    self.selected_piece = (row, col)
                    self.valid_moves = get_possible_moves(self.board, row, col, self.must_capture)
                else:
                    # Invalid move, clear selection
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Select piece if it belongs to current player
            if self.board[row][col].lower() == self.current_player:
                self.selected_piece = (row, col)
                self.valid_moves = get_possible_moves(self.board, row, col, self.must_capture)
                logging.debug(f"Selected piece at ({row}, {col})")
                logging.debug(f"Valid moves: {self.valid_moves}")

    def draw(self):
        """Draw the game state"""
        self.screen.fill(BG_COLOR)
        self.renderer.draw_board(self.board, self.selected_piece, self.valid_moves)
        self.menu_bar.draw(self.screen)
        
        # Draw move history
        history_rect = pygame.Rect(BOARD_AREA_WIDTH, MENU_HEIGHT, 
                                 HISTORY_AREA_WIDTH, HEIGHT - MENU_HEIGHT - STATUS_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, history_rect)
        
        # Draw move list title
        title = self.font.render("Move History", True, BLACK)
        self.screen.blit(title, (BOARD_AREA_WIDTH + 10, MENU_HEIGHT + 10))
        
        # Draw moves
        y = MENU_HEIGHT + 40
        visible_moves = self.move_history[self.history_scroll:]
        for move in visible_moves:
            if y + 20 > HEIGHT - STATUS_HEIGHT:
                break
            text = self.font.render(move, True, BLACK)
            self.screen.blit(text, (BOARD_AREA_WIDTH + 10, y))
            y += 20
        
        # Draw status bar with piece counts and times
        status_rect = pygame.Rect(0, HEIGHT - STATUS_HEIGHT, WIDTH, STATUS_HEIGHT)
        pygame.draw.rect(self.screen, MENU_BG, status_rect)
        
        red_count = sum(row.count(RED_PIECE) + row.count(RED_KING) for row in self.board)
        black_count = sum(row.count(BLACK_PIECE) + row.count(BLACK_KING) for row in self.board)
        
        red_time = time.strftime("%H:%M:%S", time.gmtime(self.time_red))
        black_time = time.strftime("%H:%M:%S", time.gmtime(self.time_black))
        
        red_text = self.font.render(f"Red: {red_time} Pieces: {red_count}", True, RED)
        black_text = self.font.render(f"Black: {black_time} Pieces: {black_count}", True, BLACK)
        mode_text = self.font.render(f"Mode: {self.mode}", True, BLUE)
        
        self.screen.blit(red_text, (10, HEIGHT - STATUS_HEIGHT + 5))
        self.screen.blit(black_text, (WIDTH - black_text.get_width() - 10, HEIGHT - STATUS_HEIGHT + 5))
        self.screen.blit(mode_text, ((WIDTH - mode_text.get_width()) // 2, HEIGHT - STATUS_HEIGHT + 5))

    def update_timers(self):
        """Update game timers"""
        current_time = time.time()
        elapsed = current_time - self.last_timer_update
        
        if self.status == "ACTIVE":  # Only update if game is active
            if self.current_player == RED_PIECE:
                self.time_red += elapsed
            else:
                self.time_black += elapsed
        
        self.last_timer_update = current_time

    def ai_move(self):
        """Execute AI's move"""
        logging.debug("[ai_move] AI turn triggered.")
        # Verify we're actually black's turn
        if self.current_player != BLACK_PIECE:
            logging.error(f"[ai_move] AI move attempted during {self.current_player}'s turn")
            return
        
        _, best_move = minimax(self.board, AI_DEPTH, True, -float('inf'), float('inf'), BLACK_PIECE)
        if best_move:
            (sr, sc), (er, ec) = best_move
            # Verify we're moving a black piece
            if self.board[sr][sc].lower() != BLACK_PIECE:
                logging.error(f"[ai_move] Invalid move attempt: trying to move {self.board[sr][sc]} piece at ({sr},{sc})")
                return
            
            move_str = f"({sr},{sc})->({er},{ec})"
            logging.debug(f"[ai_move] Moving black piece from ({sr},{sc}) to ({er},{ec})")
            self.board = apply_move(self.board, best_move, BLACK_PIECE)
            self.finish_half_turn(BLACK_PIECE, move_str)
            logging.debug(f"[ai_move] AI move executed: {move_str}")
            self.switch_turn()  # This should switch to RED_PIECE
        else:
            self.finish_half_turn(BLACK_PIECE, "No moves")
            logging.debug("[ai_move] AI has no moves.")

    def handle_menu_action(self, action):
        logging.debug(f"Menu action received: {action}")
        if action == "New Game":
            if self.dirty:
                result = show_modal_dialog(self.screen, self.font, "Warning",
                                         "Game data has changed since the last save.",
                                         ["X", "Cancel", "Continue"])
                if result != "Continue":
                    return
            self.new_game(self.engine_first)
        elif action == "Engine First":
            # Toggle who moves first and start new game
            self.engine_first = not self.engine_first
            self.new_game(self.engine_first)
            self.current_red_moves.append(f"Engine First: {self.engine_first}")
            self.dirty = True
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
            self.mode = "2P" if self.mode == "1P" else "1P"
            self.dirty = True
        elif action == "Exit":
            if self.dirty:
                result = show_modal_dialog(self.screen, self.font, "Warning",
                                         "Game data has changed since the last save.",
                                         ["Cancel", "Continue"])
                if result != "Continue":
                    return
            pygame.quit()
            sys.exit()
        elif action == "Rules":
            rules_text = ("Checkers is played on an 8x8 board with 12 pieces per side. "
                         "Pieces move diagonally on dark squares. Captures are mandatory. "
                         "When a piece reaches the far side, it becomes a king.")
            show_modal_dialog(self.screen, self.font, "Rules", rules_text, ["OK"])
        elif action == "About":
            about_text = ("Minmax Checkers\n"
                         "by John Boen\n"
                         "Enjoy playing!")
            show_modal_dialog(self.screen, self.font, "About", about_text, ["OK"])

    def save_game(self):
        """Save the current game to a file"""
        filename = save_file_dialog()
        if not filename:
            return
        try:
            if save_game(filename, self.move_history):
                self.dirty = False
                logging.debug(f"Game saved successfully to {filename}")
            else:
                show_modal_dialog(self.screen, self.font, "Error", 
                                "Failed to save game file", ["OK"])
                logging.error("Failed to save game file")
        except Exception as e:
            show_modal_dialog(self.screen, self.font, "Error", 
                            f"Error saving game: {str(e)}", ["OK"])
            logging.error(f"Error saving game: {e}")

    def load_game(self):
        """Load a game from a file"""
        filename = open_file_dialog()
        if not filename:
            return
        try:
            with open(filename, "r") as f:
                lines = f.read().splitlines()
            # Reset game
            self.new_game()
            # Parse and replay moves
            turns = {}
            for line in lines:
                if line.startswith("Turn"):
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
                    self.move_history.append(line)
            
            # Replay moves in order
            for t in sorted(turns.keys()):
                if "R" in turns[t]:
                    for move_str in turns[t]["R"]:
                        move = parse_move(move_str)
                        if move:
                            self.board = apply_move(self.board, move)
                if "B" in turns[t]:
                    for move_str in turns[t]["B"]:
                        move = parse_move(move_str)
                        if move:
                            self.board = apply_move(self.board, move)
            logging.debug("Game loaded and moves replayed from file.")
        except Exception as e:
            logging.error(f"Error loading game: {e}")

    def finish_half_turn(self, player, move_str):
        """Record a move for the current player's half-turn"""
        if player == RED_PIECE:
            self.current_red_moves.append(move_str)
        else:
            self.current_black_moves.append(move_str)

    def complete_turn(self):
        """Aggregate the current half-turn moves into two history entries with the same turn number"""
        self.turn_number += 1
        red_entry = f"Turn {self.turn_number} R: " + " | ".join(self.current_red_moves) if self.current_red_moves else f"Turn {self.turn_number} R: --"
        black_entry = f"Turn {self.turn_number} B: " + " | ".join(self.current_black_moves) if self.current_black_moves else f"Turn {self.turn_number} B: --"
        self.move_history.append(red_entry)
        self.move_history.append(black_entry)
        logging.debug(f"Completed turn {self.turn_number}: {red_entry} || {black_entry}")
        self.current_red_moves.clear()
        self.current_black_moves.clear()

    def switch_turn(self):
        """Switch the current player"""
        logging.debug(f"[switch_turn] Switching turn from {self.current_player}")
        self.current_player = BLACK_PIECE if self.current_player == RED_PIECE else RED_PIECE
        logging.debug(f"[switch_turn] Turn switched to {self.current_player}")
        
        # Update game state
        if self.check_game_over():
            self.status = "COMPLETED"  # Set status to COMPLETED if game is over
        else:
            self.selected_piece = None
            self.valid_moves = []
            logging.debug(f"[switch_turn] Switched turn. Now it's {'RED' if self.current_player == RED_PIECE else 'BLACK'}'s turn.")

    def handle_board_click(self, pos):
        """Handle mouse clicks on the game board"""
        if self.status != "ACTIVE":
            return
        
        boardR = board_rect()
        # Calculate cell position
        cell_w = boardR.width // 8
        cell_h = boardR.height // 8
        # Calculate board coordinates
        col = (pos[0] - boardR.x) // cell_w
        row = (pos[1] - boardR.y) // cell_h
        
        # Validate the calculated position
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        logging.debug(f"Cell clicked: ({row}, {col})")
        logging.debug(f"Current player: {self.current_player}")
        logging.debug(f"Board state at clicked position: {self.board[row][col]}")

        # If a piece is already selected
        if self.selected_piece:
            move = (self.selected_piece, (row, col))
            possible = get_possible_moves(self.board, self.selected_piece[0], self.selected_piece[1], self.must_capture)
            
            if move in possible:
                # Apply the move
                self.board = apply_move(self.board, move, self.current_player)
                move_str = f"({self.selected_piece[0]},{self.selected_piece[1]})->({row},{col})"
                self.finish_half_turn(self.current_player, move_str)
                
                # Check for additional captures
                if abs(row - self.selected_piece[0]) == 2:
                    further = get_capturing_moves_from(self.board, row, col)
                    if further:
                        self.multi_hop_message = True
                        self.selected_piece = (row, col)
                        self.valid_moves = further
                        logging.debug("Extra hops available")
                        return
                
                # Clear selection and switch turns
                self.selected_piece = None
                self.valid_moves = []
                self.multi_hop_message = False
                self.switch_turn()
                
                # If it's AI's turn, make the move
                if self.mode == "1P" and self.current_player == BLACK_PIECE:
                    self.ai_move()
            else:
                # If clicking on own piece, select it instead
                if self.board[row][col].lower() == self.current_player:
                    self.selected_piece = (row, col)
                    self.valid_moves = get_possible_moves(self.board, row, col, self.must_capture)
                else:
                    # Invalid move, clear selection
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Select piece if it belongs to current player
            if self.board[row][col].lower() == self.current_player:
                self.selected_piece = (row, col)
                self.valid_moves = get_possible_moves(self.board, row, col, self.must_capture)
                logging.debug(f"Selected piece at ({row}, {col})")
                logging.debug(f"Valid moves: {self.valid_moves}")

    def check_game_over(self):
        """Check if the game is over due to no moves or no pieces"""
        if self.status != "ACTIVE":
            return False

        # Count pieces
        red_count = sum(row.count(RED_PIECE) + row.count(RED_KING) for row in self.board)
        black_count = sum(row.count(BLACK_PIECE) + row.count(BLACK_KING) for row in self.board)
        
        # Check for no pieces
        if red_count == 0 or black_count == 0:
            winner = "Black" if red_count == 0 else "Red"
            logging.debug(f"Game over: {winner} wins - opponent has no pieces left")
            self.status = "COMPLETED"  # Update status
            res = show_modal_dialog(self.screen, self.font, "Game Over",
                                  f"{winner} wins! Play again?", ["Yes", "No"])
            if res == "Yes":
                self.new_game()
            else:
                pygame.quit()
                sys.exit()
            return True

        # Check for no moves
        moves = get_all_moves(self.board, self.current_player, self.must_capture)
        if not moves:
            winner = "Black" if self.current_player == RED_PIECE else "Red"
            logging.debug(f"Game over: {winner} wins - {self.current_player} has no moves")
            self.status = "COMPLETED"  # Update status
            res = show_modal_dialog(self.screen, self.font, "Game Over",
                                  f"{winner} wins! Play again?", ["Yes", "No"])
            if res == "Yes":
                self.new_game()
            else:
                pygame.quit()
                sys.exit()
            return True
        
        return False

    def cleanup(self):
        """Cleanup resources"""
        try:
            pygame.quit()
        except Exception:
            pass

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()









