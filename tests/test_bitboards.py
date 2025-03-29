import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.constants import BitboardPieces, Square
from engine import board_utils

class TestBitboards(unittest.TestCase):
    def test_bitboard_operations(self):
        """Test basic bitboard operations (set, clear, get)"""
        # Start with empty bitboard
        bitboard = 0
        
        # Set a bit
        bitboard = board_utils.set_bit(bitboard, 8)  # Set A2
        self.assertEqual(bitboard, 1 << 8)
        
        # Set another bit
        bitboard = board_utils.set_bit(bitboard, 16)  # Set A3
        self.assertEqual(bitboard, (1 << 8) | (1 << 16))
        
        # Check if bits are set
        self.assertTrue(board_utils.get_bit(bitboard, 8))
        self.assertTrue(board_utils.get_bit(bitboard, 16))
        self.assertFalse(board_utils.get_bit(bitboard, 0))
        
        # Clear a bit
        bitboard = board_utils.clear_bit(bitboard, 8)
        self.assertFalse(board_utils.get_bit(bitboard, 8))
        self.assertTrue(board_utils.get_bit(bitboard, 16))
        
        # Check bit counting
        self.assertEqual(board_utils.count_bits(bitboard), 1)
    
    def test_lsb(self):
        """Test least significant bit detection"""
        # Test empty board
        self.assertEqual(board_utils.lsb(0), -1)
        
        # Test single bit
        self.assertEqual(board_utils.lsb(1 << 5), 5)
        
        # Test multiple bits
        bitboard = (1 << 10) | (1 << 20) | (1 << 30)
        self.assertEqual(board_utils.lsb(bitboard), 10)
    
    def test_fen_parsing(self):
        """Test parsing FEN strings to bitboards"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test pieces are in correct positions
        # White pawns should be on the 2nd rank (indexes 8-15)
        white_pawns_expected = 0
        for i in range(8, 16):
            white_pawns_expected |= (1 << i)
        self.assertEqual(pieces.W_PAWNS, white_pawns_expected)
        
        # Black pawns should be on the 7th rank (indexes 48-55)
        black_pawns_expected = 0
        for i in range(48, 56):
            black_pawns_expected |= (1 << i)
        self.assertEqual(pieces.B_PAWNS, black_pawns_expected)
        
        # Test game state
        self.assertEqual(game_state['side_to_move'], 'w')
        self.assertEqual(game_state['castling_rights'], 'KQkq')
        self.assertIsNone(game_state['en_passant'])
        self.assertEqual(game_state['halfmove_clock'], 0)
        self.assertEqual(game_state['fullmove_number'], 1)
        
        # Combined bitboards should be correct
        all_white = (pieces.W_PAWNS | pieces.W_KNIGHTS | pieces.W_BISHOPS | 
                     pieces.W_ROOKS | pieces.W_QUEENS | pieces.W_KING)
        all_black = (pieces.B_PAWNS | pieces.B_KNIGHTS | pieces.B_BISHOPS | 
                     pieces.B_ROOKS | pieces.B_QUEENS | pieces.B_KING)
        
        self.assertEqual(pieces.W_PIECES, all_white)
        self.assertEqual(pieces.B_PIECES, all_black)
        self.assertEqual(pieces.ALL_PIECES, all_white | all_black)
    
    def test_algebraic_conversions(self):
        """Test conversion between square indices and algebraic notation"""
        # Test some sample squares
        self.assertEqual(board_utils.algebraic_to_index("e4"), 28)
        self.assertEqual(board_utils.algebraic_to_index("a1"), 0)
        self.assertEqual(board_utils.algebraic_to_index("h8"), 63)
        
        # Test reverse conversion
        self.assertEqual(board_utils.index_to_algebraic(28), "e4")
        self.assertEqual(board_utils.index_to_algebraic(0), "a1")
        self.assertEqual(board_utils.index_to_algebraic(63), "h8")
        
        # Test alias function
        self.assertEqual(board_utils.square_to_algebraic(28), "e4")
    
    def test_mirror_square(self):
        """Test that squares are correctly mirrored for black pieces"""
        # Test mirroring a few squares
        self.assertEqual(board_utils.mirror_square(0), 56)  # a1 -> a8
        self.assertEqual(board_utils.mirror_square(7), 63)  # h1 -> h8
        self.assertEqual(board_utils.mirror_square(28), 28)  # e4 -> e5 (symmetric)
        self.assertEqual(board_utils.mirror_square(63), 7)   # h8 -> h1


if __name__ == '__main__':
    unittest.main() 