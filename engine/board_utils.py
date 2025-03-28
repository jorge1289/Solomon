from .constants import (
    PIECES, PHASE_WEIGHTS, BitboardPieces, Square, KNIGHT_ATTACKS, KING_ATTACKS, 
    PAWN_ATTACKS_WHITE, PAWN_ATTACKS_BLACK, NORTH, SOUTH, EAST, WEST, NORTH_EAST,
    NORTH_WEST, SOUTH_EAST, SOUTH_WEST
    )

from typing import List, Dict, Tuple, Optional


# bitboard operations
def set_bit(bitboard: int, square: int) -> int:
    """Set a bit at the specified square."""
    return bitboard | (1 << square)

def clear_bit(bitboard: int, square: int) -> int:
    """Clear a bit at the specified square."""
    return bitboard & ~(1 << square)

def get_bit(bitboard: int, square: int) -> bool:
    """Check if a bit is set at the specified square."""
    return (bitboard & (1 << square)) != 0

def count_bits(bitboard: int) -> int:
    """Count the number of set bits (1s) in a bitboard."""
    return bin(bitboard).count('1')

def lsb(bitboard: int) -> int:
    """Get the index of the least significant bit."""
    if bitboard == 0:
        return -1
    return (bitboard & -bitboard).bit_length() - 1

def print_bitboard(bitboard: int) -> None:
    """Print a visual representation of a bitboard."""
    for r in range(7, -1, -1):
        row = ""
        for c in range(8):
            square = r * 8 + c
            row += "1 " if get_bit(bitboard, square) else ". "
        print(row)
    print()


def parse_fen_to_bitboards(fen: str) -> Tuple[BitboardPieces, dict]:
    """Parse a FEN string to bitboard representation and game state."""
    pieces = BitboardPieces()
    game_state = {
        'side_to_move': 'w',
        'castling_rights': '',
        'en_passant': None,
        'halfmove_clock': 0,
        'fullmove_number': 1
    }
    
    # Split FEN components
    fen_parts = fen.split(' ')
    board_part = fen_parts[0]
    
    # Parse side to move
    if len(fen_parts) > 1:
        game_state['side_to_move'] = fen_parts[1]
    
    # Parse castling rights
    if len(fen_parts) > 2:
        game_state['castling_rights'] = fen_parts[2]
    
    # Parse en passant target square
    if len(fen_parts) > 3 and fen_parts[3] != '-':
        game_state['en_passant'] = algebraic_to_index(fen_parts[3])
    
    # Parse halfmove and fullmove clocks
    if len(fen_parts) > 4:
        game_state['halfmove_clock'] = int(fen_parts[4])
    if len(fen_parts) > 5:
        game_state['fullmove_number'] = int(fen_parts[5])

    # Parse board part to bitboards
    square = 56  # Start at a8 (top-left)
    
    for c in board_part:
        if c == '/':
            square -= 16  # Move down one row and back to the a-file
        elif c.isdigit():
            square += int(c)  # Skip empty squares
        else:
            # Set the appropriate piece bitboard
            if c == 'P': pieces.W_PAWNS = set_bit(pieces.W_PAWNS, square)
            elif c == 'N': pieces.W_KNIGHTS = set_bit(pieces.W_KNIGHTS, square)
            elif c == 'B': pieces.W_BISHOPS = set_bit(pieces.W_BISHOPS, square)
            elif c == 'R': pieces.W_ROOKS = set_bit(pieces.W_ROOKS, square)
            elif c == 'Q': pieces.W_QUEENS = set_bit(pieces.W_QUEENS, square)
            elif c == 'K': pieces.W_KING = set_bit(pieces.W_KING, square)
            elif c == 'p': pieces.B_PAWNS = set_bit(pieces.B_PAWNS, square)
            elif c == 'n': pieces.B_KNIGHTS = set_bit(pieces.B_KNIGHTS, square)
            elif c == 'b': pieces.B_BISHOPS = set_bit(pieces.B_BISHOPS, square)
            elif c == 'r': pieces.B_ROOKS = set_bit(pieces.B_ROOKS, square)
            elif c == 'q': pieces.B_QUEENS = set_bit(pieces.B_QUEENS, square)
            elif c == 'k': pieces.B_KING = set_bit(pieces.B_KING, square)
            square += 1

    # Calculate combined bitboards
    pieces.W_PIECES = (pieces.W_PAWNS | pieces.W_KNIGHTS | pieces.W_BISHOPS | 
                       pieces.W_ROOKS | pieces.W_QUEENS | pieces.W_KING)
    pieces.B_PIECES = (pieces.B_PAWNS | pieces.B_KNIGHTS | pieces.B_BISHOPS | 
                       pieces.B_ROOKS | pieces.B_QUEENS | pieces.B_KING)
    pieces.ALL_PIECES = pieces.W_PIECES | pieces.B_PIECES
    
    return pieces, game_state

def algebraic_to_index(algebraic: str) -> int:
    """Convert algebraic notation (e.g. 'e4') to board index (0-63)."""
    file = ord(algebraic[0]) - ord('a')
    rank = 8 - int(algebraic[1])
    return rank * 8 + file

def index_to_algebraic(index: int) -> str:
    """Convert board index (0-63) to algebraic notation (e.g. 'e4')."""
    file = chr(index % 8 + ord('a'))
    rank = 8 - (index // 8)
    return f"{file}{rank}"

def initialize_attack_tables():
    """Initialize pre-calculated attack tables"""
    # knight attack patterns
    knight_dirs = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

    for sq in range(64):
        row, col = sq // 8, sq % 8
        # knight attacks
        for dr, dc in knight_dirs:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and  0 <= c < 8:
                target_sq = r * 8 + c
                KNIGHT_ATTACKS[sq] = set_bit(KNIGHT_ATTACKS[sq], target_sq)
    
    # king attacks
    king_dirs = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
    for dr, dc in king_dirs:
        r, c = r + dr, c + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target_sq = r * 8 + c
            KING_ATTACKS[sq] = set_bit(KING_ATTACKS[sq], target_sq)
    
    # pawn attacks
    if col > 0: # can attack left
        if row < 7: # White pawn can attack up-left
            PAWN_ATTACKS_WHITE[sq] = set_bit(PAWN_ATTACKS_WHITE[sq], sq + NORTH_WEST)
        if row > 0: # black pawn can attack down-left
            PAWN_ATTACKS_BLACK[sq] = set_bit(PAWN_ATTACKS_BLACK[sq], sq + SOUTH_WEST)
    
    if col < 7: # can attack right
        if row < 7: # white pawn can atack up-right
            PAWN_ATTACKS_WHITE[sq] = set_bit(PAWN_ATTACKS_WHITE[sq], sq + NORTH_EAST)
        if row > 0:
            PAWN_ATTACKS_BLACK[sq] = set_bit(PAWN_ATTACKS_BLACK[sq], sq + SOUTH_EAST)

def generate_knight_moves(knights: int, own_pieces: int) -> list:
    """generate all knkight moves"""
    moves = [] # (from_sq, to_sq)
    piece = knights
    while piece:
        from_sq = lsb(piece)
        piece = clear_bit(piece, from_sq)

        # get all possible target sqaures
        targets = KNIGHT_ATTACKS[from_sq]  & ~own_pieces

        # for each set bit in targets, create a move
        targets_copy = targets
        while targets_copy:
            to_sq = lsb(targets_copy)
            targets_copy = clear_bit(targets_copy, to_sq)
            moves.append((from_sq, to_sq))
    
    return moves

def generate_pawn_moves(pawns: int, all_pieces: int, enemy_pieces: int, is_white: bool) -> list:
    """Generate all pawn moves including captures and promotions"""
    moves = []
    piece = pawns

    # Direction of pawn movement depends on the color
    forward = NORTH if is_white else SOUTH
    double_forward = forward * 2

    # Starting rank for double-move
    start_rank = 1 if is_white else 6

    while piece:
        from_sq = lsb(piece)
        piece = clear_bit(piece, from_sq)
        
        # Single push
        to_sq = from_sq + forward
        if 0 <= to_sq < 64 and not get_bit(all_pieces, to_sq):
            moves.append((from_sq, to_sq))
            
            # Double push from starting rank
            if from_sq // 8 == start_rank:
                to_sq_double = from_sq + double_forward
                if 0 <= to_sq_double < 64 and not get_bit(all_pieces, to_sq_double):
                    moves.append((from_sq, to_sq_double))
        
        # Captures
        attack_board = (PAWN_ATTACKS_WHITE[from_sq] if is_white else PAWN_ATTACKS_BLACK[from_sq]) & enemy_pieces
        targets = attack_board
        while targets:
            to_sq = lsb(targets)
            targets = clear_bit(targets, to_sq)
            moves.append((from_sq, to_sq))
    
    return moves

def get_bishop_attacks(square: int, occupied: int) -> int:
    """Get all possible bishop attacks from a square."""
    attacks = 0
    row, col = square // 8, square % 8
    
    # Northeast ray
    r, c = row - 1, col + 1
    while r >= 0 and c < 8:
        target_sq = r * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
        r -= 1
        c += 1
    
    # Northwest ray
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0:
        target_sq = r * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
        r -= 1
        c -= 1
    
    # Southeast ray
    r, c = row + 1, col + 1
    while r < 8 and c < 8:
        target_sq = r * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
        r += 1
        c += 1
    
    # Southwest ray
    r, c = row + 1, col - 1
    while r < 8 and c >= 0:
        target_sq = r * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
        r += 1
        c -= 1
    
    return attacks

def get_rook_attacks(square: int, occupied: int) -> int:
    """Get all possible rook attacks from a square."""
    attacks = 0
    row, col = square // 8, square % 8
    
    # North ray
    for r in range(row - 1, -1, -1):
        target_sq = r * 8 + col
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
    
    # South ray
    for r in range(row + 1, 8):
        target_sq = r * 8 + col
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
    
    # East ray
    for c in range(col + 1, 8):
        target_sq = row * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
    
    # West ray
    for c in range(col - 1, -1, -1):
        target_sq = row * 8 + c
        attacks = set_bit(attacks, target_sq)
        if get_bit(occupied, target_sq):
            break
    
    return attacks

def get_queen_attacks(square: int, occupied: int) -> int:
    """Get all possible queen attacks from a square."""
    # Queens move like bishops and rooks combined
    return get_bishop_attacks(square, occupied) | get_rook_attacks(square, occupied)

def generate_bishop_moves(bishops: int, own_pieces: int, all_pieces: int) -> list:
    """Generate all bishop moves."""
    moves = []
    piece = bishops
    
    while piece:
        from_sq = lsb(piece)
        piece = clear_bit(piece, from_sq)
        
        # Get attack squares for this bishop
        attacks = get_bishop_attacks(from_sq, all_pieces) & ~own_pieces
        
        # For each set bit in attacks, create a move
        attack_copy = attacks
        while attack_copy:
            to_sq = lsb(attack_copy)
            attack_copy = clear_bit(attack_copy, to_sq)
            moves.append((from_sq, to_sq))
    
    return moves

def generate_rook_moves(rooks: int, own_pieces: int, all_pieces: int) -> list:
    """Generate all rook moves."""
    moves = []
    piece = rooks
    
    while piece:
        from_sq = lsb(piece)
        piece = clear_bit(piece, from_sq)
        
        # Get attack squares for this rook
        attacks = get_rook_attacks(from_sq, all_pieces) & ~own_pieces
        
        # For each set bit in attacks, create a move
        attack_copy = attacks
        while attack_copy:
            to_sq = lsb(attack_copy)
            attack_copy = clear_bit(attack_copy, to_sq)
            moves.append((from_sq, to_sq))
    
    return moves

def generate_queen_moves(queens: int, own_pieces: int, all_pieces: int) -> list:
    """Generate all queen moves."""
    moves = []
    piece = queens
    
    while piece:
        from_sq = lsb(piece)
        piece = clear_bit(piece, from_sq)
        
        # Get attack squares for this queen
        attacks = get_queen_attacks(from_sq, all_pieces) & ~own_pieces
        
        # For each set bit in attacks, create a move
        attack_copy = attacks
        while attack_copy:
            to_sq = lsb(attack_copy)
            attack_copy = clear_bit(attack_copy, to_sq)
            moves.append((from_sq, to_sq))
    
    return moves

def generate_king_moves(king: int, own_pieces: int) -> list:
    """Generate king moves."""
    moves = []
    
    if king == 0:
        return moves
    
    from_sq = lsb(king)  # There is only one king
    
    # Get attack squares for the king
    attacks = KING_ATTACKS[from_sq] & ~own_pieces
    
    # For each set bit in attacks, create a move
    attack_copy = attacks
    while attack_copy:
        to_sq = lsb(attack_copy)
        attack_copy = clear_bit(attack_copy, to_sq)
        moves.append((from_sq, to_sq))
    
    return moves

def is_square_attacked(square: int, pieces: BitboardPieces, by_white: bool) -> bool:
    """Check if a square is under attack."""
    # Check for pawn attacks
    if by_white:
        # White pawns attack down-left and down-right
        if (square % 8 > 0 and get_bit(pieces.W_PAWNS, square - 9)) or \
           (square % 8 < 7 and get_bit(pieces.W_PAWNS, square - 7)):
            return True
    else:
        # Black pawns attack up-left and up-right
        if (square % 8 > 0 and get_bit(pieces.B_PAWNS, square + 7)) or \
           (square % 8 < 7 and get_bit(pieces.B_PAWNS, square + 9)):
            return True
    
    # Check for knight attacks
    attackers = pieces.W_KNIGHTS if by_white else pieces.B_KNIGHTS
    if KNIGHT_ATTACKS[square] & attackers:
        return True
    
    # Check for king attacks
    king = pieces.W_KING if by_white else pieces.B_KING
    if KING_ATTACKS[square] & king:
        return True
    
    # Check for sliding piece attacks (bishop, rook, queen)
    bishop_attacks = get_bishop_attacks(square, pieces.ALL_PIECES)
    rook_attacks = get_rook_attacks(square, pieces.ALL_PIECES)
    
    if by_white:
        if bishop_attacks & (pieces.W_BISHOPS | pieces.W_QUEENS):
            return True
        if rook_attacks & (pieces.W_ROOKS | pieces.W_QUEENS):
            return True
    else:
        if bishop_attacks & (pieces.B_BISHOPS | pieces.B_QUEENS):
            return True
        if rook_attacks & (pieces.B_ROOKS | pieces.B_QUEENS):
            return True
    
    return False

def is_in_check(pieces: BitboardPieces, white_to_move: bool) -> bool:
    """Check if the side to move is in check."""
    # Find the king square
    king = pieces.W_KING if white_to_move else pieces.B_KING
    king_square = lsb(king)
    
    # Check if the king is under attack by the opponent
    return is_square_attacked(king_square, pieces, not white_to_move)

def mirror_square(square: int) -> int:
    """Mirror a square vertically for black piece evaluation."""
    return square ^ 56  # XOR with 56 (7 * 8) flips the board

def generate_castling_moves(pieces: BitboardPieces, castling_rights: str, is_white: bool) -> list:
    """Generate castling moves if they are legal."""
    moves = []
    
    # Skip if the king is in check
    if is_in_check(pieces, is_white):
        return moves
    
    if is_white:
        # Kingside castling for white
        if 'K' in castling_rights:
            # Check if squares between king and rook are empty
            if (not get_bit(pieces.ALL_PIECES, Square.F1) and 
                not get_bit(pieces.ALL_PIECES, Square.G1)):
                # Check if king passes through or lands on attacked square
                if (not is_square_attacked(Square.F1, pieces, False) and 
                    not is_square_attacked(Square.G1, pieces, False)):
                    moves.append((Square.E1, Square.G1))
        
        # Queenside castling for white
        if 'Q' in castling_rights:
            # Check if squares between king and rook are empty
            if (not get_bit(pieces.ALL_PIECES, Square.D1) and 
                not get_bit(pieces.ALL_PIECES, Square.C1) and
                not get_bit(pieces.ALL_PIECES, Square.B1)):
                # Check if king passes through or lands on attacked square
                if (not is_square_attacked(Square.D1, pieces, False) and 
                    not is_square_attacked(Square.C1, pieces, False)):
                    moves.append((Square.E1, Square.C1))
    else:
        # Kingside castling for black
        if 'k' in castling_rights:
            # Check if squares between king and rook are empty
            if (not get_bit(pieces.ALL_PIECES, Square.F8) and 
                not get_bit(pieces.ALL_PIECES, Square.G8)):
                # Check if king passes through or lands on attacked square
                if (not is_square_attacked(Square.F8, pieces, True) and 
                    not is_square_attacked(Square.G8, pieces, True)):
                    moves.append((Square.E8, Square.G8))
        
        # Queenside castling for black
        if 'q' in castling_rights:
            # Check if squares between king and rook are empty
            if (not get_bit(pieces.ALL_PIECES, Square.D8) and 
                not get_bit(pieces.ALL_PIECES, Square.C8) and
                not get_bit(pieces.ALL_PIECES, Square.B8)):
                # Check if king passes through or lands on attacked square
                if (not is_square_attacked(Square.D8, pieces, True) and 
                    not is_square_attacked(Square.C8, pieces, True)):
                    moves.append((Square.E8, Square.C8))
    
    return moves

def generate_en_passant_moves(pieces: BitboardPieces, en_passant_square: int, is_white: bool) -> list:
    """Generate en passant capture moves."""
    moves = []
    
    if en_passant_square is None:
        return moves
    
    if is_white:
        # Check if there are white pawns that can capture en passant
        # En passant capturing pawns must be on rank 5 (indices 32-39)
        # and adjacent to the target pawn
        if en_passant_square // 8 == 2:  # Target square on rank 3
            # Check for white pawn to the left of the captured pawn
            left_square = en_passant_square + 7
            if left_square % 8 != 7 and get_bit(pieces.W_PAWNS, left_square):
                moves.append((left_square, en_passant_square))
            
            # Check for white pawn to the right of the captured pawn
            right_square = en_passant_square + 9
            if right_square % 8 != 0 and get_bit(pieces.W_PAWNS, right_square):
                moves.append((right_square, en_passant_square))
    else:
        # Check if there are black pawns that can capture en passant
        # En passant capturing pawns must be on rank 4 (indices 24-31)
        # and adjacent to the target pawn
        if en_passant_square // 8 == 5:  # Target square on rank 6
            # Check for black pawn to the left of the captured pawn
            left_square = en_passant_square - 9
            if left_square % 8 != 7 and get_bit(pieces.B_PAWNS, left_square):
                moves.append((left_square, en_passant_square))
            
            # Check for black pawn to the right of the captured pawn
            right_square = en_passant_square - 7
            if right_square % 8 != 0 and get_bit(pieces.B_PAWNS, right_square):
                moves.append((right_square, en_passant_square))
    
    return moves