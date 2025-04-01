from .pieces import *
from .board import apply_move
import logging

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


def get_all_capturing_moves(board, row, col, moves=None, path=None):
    """
    Recursively finds all possible capturing sequences for a piece.
    Returns a list of moves, where each move is the complete capturing sequence.
    """
    if moves is None:
        moves = []
    if path is None:
        path = [(row, col)]
        
    piece = board[row][col]
    if piece == RED_PIECE:
        directions = [(-1, -1), (-1, 1)]
    elif piece == BLACK_PIECE:
        directions = [(1, -1), (1, 1)]
    else:  # King pieces
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    found_capture = False
    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2 * dr, col + 2 * dc
        
        if (0 <= mid_r < 8 and 0 <= mid_c < 8 and 0 <= end_r < 8 and 0 <= end_c < 8):
            if board[mid_r][mid_c] in opponent(piece) and board[end_r][end_c] == EMPTY:
                found_capture = True
                # Make temporary move
                new_board = [row[:] for row in board]
                new_board[row][col] = EMPTY
                new_board[mid_r][mid_c] = EMPTY
                new_board[end_r][end_c] = piece
                
                # Recursively find more captures
                new_path = path + [(end_r, end_c)]
                further_captures = get_all_capturing_moves(new_board, end_r, end_c, moves, new_path)
                
                if not further_captures:
                    # If no more captures possible, add the current sequence
                    moves.append((path[0], new_path[-1]))

    if not found_capture and len(path) > 1:
        # Add the current sequence if it's a valid capture sequence
        moves.append((path[0], path[-1]))
        
    return moves

def get_possible_moves(board, row, col, must_capture=True):
    """Returns a list of legal moves for the piece at (row, col)."""
    moves = []
    piece = board[row][col]
    if piece == EMPTY:
        return moves

    # Determine directions based on piece type
    if piece == RED_PIECE:
        directions = [(-1, -1), (-1, 1)]  # Red moves upward
    elif piece == BLACK_PIECE:
        directions = [(1, -1), (1, 1)]    # Black moves downward
    else:  # King pieces (RED_KING or BLACK_KING)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    # First check for captures
    capture_moves = []
    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2*dr, col + 2*dc
        if (0 <= end_r < 8 and 0 <= end_c < 8 and 0 <= mid_r < 8 and 0 <= mid_c < 8):
            mid_piece = board[mid_r][mid_c]
            if mid_piece != EMPTY and is_opponent(piece, mid_piece) and board[end_r][end_c] == EMPTY:
                capture_moves.append(((row, col), (end_r, end_c)))

    # If captures are available and must_capture is True, return only captures
    if capture_moves and must_capture:
        return capture_moves

    # Add regular moves if no captures are available or must_capture is False
    for dr, dc in directions:
        new_r, new_c = row + dr, col + dc
        if 0 <= new_r < 8 and 0 <= new_c < 8 and board[new_r][new_c] == EMPTY:
            moves.append(((row, col), (new_r, new_c)))

    return capture_moves + moves if not must_capture else (capture_moves or moves)

def get_capturing_moves_from(board, row, col):
    """Returns only the capturing moves available from (row, col)."""
    moves = []
    piece = board[row][col]
    if piece == EMPTY:
        return moves

    if piece == RED_PIECE:
        directions = [(-1, -1), (-1, 1)]
    elif piece == BLACK_PIECE:
        directions = [(1, -1), (1, 1)]
    else:  # King pieces
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2 * dr, col + 2 * dc
        if (0 <= mid_r < 8 and 0 <= mid_c < 8 and 0 <= end_r < 8 and 0 <= end_c < 8):
            if board[mid_r][mid_c] in opponent(piece) and board[end_r][end_c] == EMPTY:
                moves.append(((row, col), (end_r, end_c)))
    return moves

def get_all_moves(board, player, must_capture=True):
    """Returns all possible moves for the given player"""
    all_moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != EMPTY and piece.lower() == player:
                moves = get_possible_moves(board, row, col, must_capture)
                all_moves.extend(moves)
    
    # If must_capture is True and there are capture moves, return only captures
    if must_capture:
        capture_moves = [move for move in all_moves if abs(move[1][0] - move[0][0]) == 2]
        if capture_moves:
            return capture_moves
    
    return all_moves

def apply_move(board, move, current_player):
    """
    Returns a new board with the move applied, handling captures and king promotion.
    """
    new_board = [row[:] for row in board]  # Create a deep copy of the board
    (sr, sc), (er, ec) = move  # start_row, start_col, end_row, end_col
    
    piece = new_board[sr][sc]
    
    # Validate piece ownership
    if piece.lower() != current_player:
        logging.error(f"Invalid move: Piece {piece} doesn't belong to player {current_player}")
        return board
    
    # Move the piece
    new_board[er][ec] = piece
    new_board[sr][sc] = EMPTY
    
    # Handle capture (if move distance is 2, it's a capture)
    if abs(er - sr) == 2:
        mid_r, mid_c = (sr + er) // 2, (sc + ec) // 2
        captured_piece = new_board[mid_r][mid_c]
        if captured_piece.lower() == current_player:
            logging.error(f"Invalid capture: Cannot capture own piece at ({mid_r}, {mid_c})")
            return board
        new_board[mid_r][mid_c] = EMPTY
    
    # Handle king promotion
    if piece == RED_PIECE and er == 0:
        new_board[er][ec] = RED_KING
    elif piece == BLACK_PIECE and er == 7:
        new_board[er][ec] = BLACK_KING
        
    return new_board

def opponent(piece):
    """Returns the set of opponent pieces for the given piece."""
    if piece.upper() in [RED_PIECE, RED_KING]:
        return {BLACK_PIECE, BLACK_KING}
    return {RED_PIECE, RED_KING}

def is_opponent(piece1, piece2):
    """Helper function to determine if two pieces are opponents"""
    return (piece1.lower() == RED_PIECE and piece2.lower() == BLACK_PIECE) or \
           (piece1.lower() == BLACK_PIECE and piece2.lower() == RED_PIECE)
















