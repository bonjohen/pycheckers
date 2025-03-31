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


def get_possible_moves(board, row, col):
    """Returns a list of legal moves for the piece at (row, col)."""
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

    # Normal moves
    for dr, dc in directions:
        new_r, new_c = row + dr, col + dc
        if 0 <= new_r < 8 and 0 <= new_c < 8 and board[new_r][new_c] == EMPTY:
            moves.append(((row, col), (new_r, new_c)))

    # Capture moves
    capture_moves = get_capturing_moves_from(board, row, col)
    return moves + capture_moves

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
    else:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        mid_r, mid_c = row + dr, col + dc
        end_r, end_c = row + 2 * dr, col + 2 * dc
        if (0 <= mid_r < 8 and 0 <= mid_c < 8 and 0 <= end_r < 8 and 0 <= end_c < 8):
            if board[mid_r][mid_c] in opponent(piece) and board[end_r][end_c] == EMPTY:
                moves.append(((row, col), (end_r, end_c)))
    return moves

def get_all_moves(board, player):
    """Returns all legal moves for the given player."""
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c].lower() == player:
                moves.extend(get_possible_moves(board, r, c))
    return moves

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

