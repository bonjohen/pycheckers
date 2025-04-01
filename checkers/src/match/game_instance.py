from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional
from src.game.pieces import EMPTY, RED_PIECE, BLACK_PIECE, RED_KING, BLACK_KING
from src.game.move_generator import get_possible_moves, apply_move

@dataclass
class Move:
    player: str
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    timestamp: datetime = datetime.now()

    def __str__(self):
        return f"({self.from_pos[0]},{self.from_pos[1]})->({self.to_pos[0]},{self.to_pos[1]})"

class GameInstance:
    def __init__(self, game_id: str, must_capture: bool = True):
        self.game_id = game_id
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        self.current_turn = RED_PIECE
        self.move_history: List[Move] = []
        self.status = "PENDING"  # PENDING, ACTIVE, COMPLETED, DRAWN
        self.must_capture = must_capture
        self._initialize_board()

    def _initialize_board(self):
        """Set up the initial board state"""
        # Place black pieces
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = BLACK_PIECE
        
        # Place red pieces
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = RED_PIECE

    def start_game(self) -> bool:
        """Start the game if it's in PENDING state"""
        if self.status != "PENDING":
            return False
        self.status = "ACTIVE"
        return True

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Attempt to make a move. Returns True if successful."""
        if not self._validate_move_input(from_pos, to_pos):
            return False
        
        if self.status != "ACTIVE":
            return False

        row, col = from_pos
        if self.board[row][col].lower() != self.current_turn:
            return False

        valid_moves = get_possible_moves(self.board, row, col, self.must_capture)
        move = (from_pos, to_pos)
        
        if move not in valid_moves:
            return False

        # Record and apply the move
        self.move_history.append(Move(
            player=self.current_turn,
            from_pos=from_pos,
            to_pos=to_pos
        ))
        
        old_piece = self.board[row][col]
        self.board = apply_move(self.board, move, self.current_turn)
        
        # End turn if king promotion occurred
        if ((old_piece == RED_PIECE and self.board[to_pos[0]][to_pos[1]] == RED_KING) or
            (old_piece == BLACK_PIECE and self.board[to_pos[0]][to_pos[1]] == BLACK_KING)):
            self._switch_turn()
            return True
        
        # Check for additional captures
        if abs(to_pos[0] - from_pos[0]) == 2:
            further_captures = get_capturing_moves_from(self.board, to_pos[0], to_pos[1])
            if not further_captures:
                self._switch_turn()
        else:
            self._switch_turn()
        
        self.check_game_over()
        return True

    def get_valid_moves(self, pos: Tuple[int, int]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get valid moves for a piece at the given position"""
        if self.status != "ACTIVE":
            return []
        
        row, col = pos
        if not (0 <= row < 8 and 0 <= col < 8):
            return []
        
        if self.board[row][col].lower() != self.current_turn:
            return []
            
        return get_possible_moves(self.board, row, col, self.must_capture)

    def check_game_over(self) -> bool:
        """Check if the game is over and update status accordingly"""
        if self.status != "ACTIVE":
            return False

        # Count pieces
        red_count = sum(row.count(RED_PIECE) + row.count(RED_KING) for row in self.board)
        black_count = sum(row.count(BLACK_PIECE) + row.count(BLACK_KING) for row in self.board)

        if red_count == 0:
            self.status = "COMPLETED"
            self.winner = BLACK_PIECE
            return True
        elif black_count == 0:
            self.status = "COMPLETED"
            self.winner = RED_PIECE
            return True

        # Check for available moves
        current_pieces = RED_PIECE if self.current_turn == RED_PIECE else BLACK_PIECE
        for row in range(8):
            for col in range(8):
                if self.board[row][col].lower() == current_pieces:
                    if get_possible_moves(self.board, row, col):
                        return False

        # No moves available - game is drawn
        self.status = "DRAWN"
        return True

    def _switch_turn(self):
        """Switch the current turn"""
        self.current_turn = BLACK_PIECE if self.current_turn == RED_PIECE else RED_PIECE

    def get_state(self):
        """Get the current game state"""
        return {
            "game_id": self.game_id,
            "board": self.board,
            "current_turn": self.current_turn,
            "status": self.status,
            "moves": [str(move) for move in self.move_history]
        }

    def _validate_move_input(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Validate move input coordinates"""
        for pos in (from_pos, to_pos):
            if not isinstance(pos, tuple) or len(pos) != 2:
                return False
            row, col = pos
            if not (isinstance(row, int) and isinstance(col, int)):
                return False
            if not (0 <= row < 8 and 0 <= col < 8):
                return False
        return True



