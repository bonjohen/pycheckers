def evaluate_board(board):
    """
    Evaluate the board position.
    Returns a score from Black's perspective (positive is good for Black)
    """
    score = 0
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece == BLACK_PIECE:
                score += 10
            elif piece == BLACK_KING:
                score += 15
            elif piece == RED_PIECE:
                score -= 10
            elif piece == RED_KING:
                score -= 15
    return score

def minimax(board, depth, maximizing, alpha, beta, player, must_capture=True):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns (score, move)
    """
    if depth == 0:
        return evaluate_board(board), None

    current = BLACK_PIECE if maximizing else RED_PIECE
    moves = get_all_moves(board, current, must_capture)
    
    if not moves:
        logging.debug(f"[minimax] No valid moves found for player {current}")
        return -float('inf') if maximizing else float('inf'), None

    # Prioritize capture moves if must_capture is True
    capture_moves = [move for move in moves if abs(move[1][0] - move[0][0]) == 2]
    if must_capture and capture_moves:
        moves = capture_moves
        logging.debug(f"[minimax] Found {len(capture_moves)} capture moves")

    best_move = None
    if maximizing:
        max_eval = -float('inf')
        for move in moves:
            new_board = apply_move(board, move, current)
            eval, _ = minimax(new_board, depth - 1, False, alpha, beta, 
                            player, must_capture)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            new_board = apply_move(board, move, current)
            eval, _ = minimax(new_board, depth - 1, True, alpha, beta, 
                            player, must_capture)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move



