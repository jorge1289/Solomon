from .constants import PIECES, PHASE_WEIGHTS

def parse_fen(fen):
    """Parse FEN string and return board representation"""
    board = []
    fen_board = fen.split(' ')[0]  # Get board part of FEN
    
    for row in fen_board.split('/'):
        board_row = []
        for char in row:
            if char.isdigit():
                board_row.extend([''] * int(char))
            else:
                board_row.append(char)
        board.extend(board_row)
    
    return board

def get_game_phase(board):
    """Calculate game phase based on remaining material"""
    phase = 24  # Starting phase value (maximum)
    
    for piece in board:
        if piece.upper() in PHASE_WEIGHTS:
            phase -= PHASE_WEIGHTS[piece.upper()]
    
    # Convert to 256 scale
    phase = (phase * 256 + 12) // 24
    return max(0, min(256, phase))

def get_square_index(file, rank):
    """Convert file (0-7) and rank (0-7) to square index (0-63)"""
    return rank * 8 + file

def mirror_square(square):
    """Mirror square vertically (for black pieces)"""
    return square ^ 56  # XOR with 56 flips the rank