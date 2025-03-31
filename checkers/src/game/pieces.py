# No imports needed

# Piece definitions
EMPTY       = ' '
RED_PIECE   = 'r'
RED_KING    = 'R'
BLACK_PIECE = 'b'
BLACK_KING  = 'B'

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