import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.constants import BitboardPieces, Square
from engine import board_utils
from engine.evaluation import generate_all_moves

class TestMoveGeneration(unittest.TestCase):
    def setup(self):
        #board_utils.initialize_attack_tables() NOTE: attack tables initialized when module is loaded
        pass

    def test_attack_tables_initialization(self):
        """Test that attack tables are initialized correctly"""
        # Knight attacks from center of board (d4)
        knight_attacks = board_utils.KNIGHT_ATTACKS[27]  # d4
        expected_targets = {
            10, 12,  # b2, c2
            17, 21,  # b3, f3
            33, 37,  # b5, f5
            42, 44   # b6, c6
        }
        
        for target in expected_targets:
            self.assertTrue(board_utils.get_bit(knight_attacks, target),
                            f"Knight at d4 should attack {board_utils.square_to_algebraic(target)}")
        
        # King attacks from e1
        king_attacks = board_utils.KING_ATTACKS[4]  # e1
        expected_targets = {3, 5, 11, 12, 13}  # d1, f1, d2, e2, f2
        
        for target in expected_targets:
            self.assertTrue(board_utils.get_bit(king_attacks, target),
                            f"King at e1 should attack {board_utils.square_to_algebraic(target)}")
        
        # Pawn attacks
        # White pawn at e2 (12) can attack d3 and f3
        white_pawn_attacks = board_utils.PAWN_ATTACKS_WHITE[12]
        self.assertTrue(board_utils.get_bit(white_pawn_attacks, 19))  # d3
        self.assertTrue(board_utils.get_bit(white_pawn_attacks, 21))  # f3
        
        # Black pawn at e7 (52) can attack d6 and f6
        black_pawn_attacks = board_utils.PAWN_ATTACKS_BLACK[52]
        self.assertTrue(board_utils.get_bit(black_pawn_attacks, 43))  # d6
        self.assertTrue(board_utils.get_bit(black_pawn_attacks, 45))  # f6

    def test_pawn_move_generation(self):
        """Test pawn move generation"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white pawn moves
        white_pawn_moves = board_utils.generate_pawn_moves(
            pieces.W_PAWNS, pieces.ALL_PIECES, pieces.B_PIECES, True)
        
        # Should have 8 single moves and 8 double moves
        self.assertEqual(len(white_pawn_moves), 16)
        
        # Check specific pawn moves
        e2_e3 = (12, 20)  # e2-e3
        e2_e4 = (12, 28)  # e2-e4
        self.assertIn(e2_e3, white_pawn_moves)
        self.assertIn(e2_e4, white_pawn_moves)
        
        # Test black pawn moves
        game_state['side_to_move'] = 'b'
        black_pawn_moves = board_utils.generate_pawn_moves(
            pieces.B_PAWNS, pieces.ALL_PIECES, pieces.W_PIECES, False)
        
        # Should have 8 single moves and 8 double moves
        self.assertEqual(len(black_pawn_moves), 16)
        
        # Check specific pawn moves
        e7_e6 = (52, 44)  # e7-e6
        e7_e5 = (52, 36)  # e7-e5
        self.assertIn(e7_e6, black_pawn_moves)
        self.assertIn(e7_e5, black_pawn_moves)
        
        # Test pawn captures
        # Set up a position with captures
        fen = "rnbqkbnr/ppp1p1pp/8/3p1p2/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        white_pawn_moves = board_utils.generate_pawn_moves(
            pieces.W_PAWNS, pieces.ALL_PIECES, pieces.B_PIECES, True)
        
        # e4 pawn can capture d5 and f5
        e4_d5 = (28, 35)  # e4-d5
        e4_f5 = (28, 37)  # e4-f5
        self.assertIn(e4_d5, white_pawn_moves)
        self.assertIn(e4_f5, white_pawn_moves)

    def test_knight_move_generation(self):
        """Test knight move generation"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white knight moves
        white_knight_moves = board_utils.generate_knight_moves(
            pieces.W_KNIGHTS, pieces.W_PIECES)
        
        # Each knight has 2 possible moves in the starting position
        self.assertEqual(len(white_knight_moves), 4)
        
        # b1 knight can move to a3 and c3
        b1_a3 = (1, 16)  # b1-a3
        b1_c3 = (1, 18)  # b1-c3
        self.assertIn(b1_a3, white_knight_moves)
        self.assertIn(b1_c3, white_knight_moves)
        
        # g1 knight can move to f3 and h3
        g1_f3 = (6, 21)  # g1-f3
        g1_h3 = (6, 23)  # g1-h3
        self.assertIn(g1_f3, white_knight_moves)
        self.assertIn(g1_h3, white_knight_moves)
        
        # Test black knight moves
        black_knight_moves = board_utils.generate_knight_moves(
            pieces.B_KNIGHTS, pieces.B_PIECES)
        
        # Each knight has 2 possible moves in the starting position
        self.assertEqual(len(black_knight_moves), 4)
        
        # b8 knight can move to a6 and c6
        b8_a6 = (57, 40)  # b8-a6
        b8_c6 = (57, 42)  # b8-c6
        self.assertIn(b8_a6, black_knight_moves)
        self.assertIn(b8_c6, black_knight_moves)

    def test_bishop_move_generation(self):
        """Test bishop move generation"""
        # Position with bishops that can move
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white bishop moves
        white_bishop_moves = board_utils.generate_bishop_moves(
            pieces.W_BISHOPS, pieces.W_PIECES, pieces.ALL_PIECES)
        
        # The bishop at f1 can move to e2, d3, c4, b5, a6, g2, h3
        f1 = 5  # f1 square
        expected_targets = {
            13,  # e2
            19,  # d3
            26,  # c4
            33,  # b5
            40,  # a6
            14,  # g2
            23   # h3
        }
        
        for target in expected_targets:
            self.assertIn((f1, target), white_bishop_moves, 
                          f"Bishop should be able to move from f1 to {board_utils.square_to_algebraic(target)}")
        
        # Total number of moves should be the sum of expected targets
        self.assertEqual(len(white_bishop_moves), len(expected_targets))

    def test_rook_move_generation(self):
        """Test rook move generation"""
        # Position with rooks that can move
        fen = "rnbqkbnr/1ppppppp/p7/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white rook moves
        white_rook_moves = board_utils.generate_rook_moves(
            pieces.W_ROOKS, pieces.W_PIECES, pieces.ALL_PIECES)
        
        # The rook at a1 can move to a2, a3, a4, a5, a6, a7, b1, c1, d1
        a1 = 0  # a1 square
        expected_a1_targets = {
            8, 16, 24, 32, 40, 48,  # a2-a7
            1, 2, 3                # b1, c1, d1
        }
        
        for target in expected_a1_targets:
            self.assertIn((a1, target), white_rook_moves, 
                          f"Rook should be able to move from a1 to {board_utils.square_to_algebraic(target)}")
        
        # The rook at h1 can move to h2, h3, h4, h5, h6, h7, g1, f1
        h1 = 7  # h1 square
        expected_h1_targets = {
            15, 23, 31, 39, 47, 55,  # h2-h7
            6, 5                    # g1, f1
        }
        
        for target in expected_h1_targets:
            self.assertIn((h1, target), white_rook_moves, 
                          f"Rook should be able to move from h1 to {board_utils.square_to_algebraic(target)}")
        
        # Total number of moves should be the sum of expected targets
        self.assertEqual(len(white_rook_moves), len(expected_a1_targets) + len(expected_h1_targets))

    def test_queen_move_generation(self):
        """Test queen move generation"""
        # Position with queen that can move
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white queen moves
        white_queen_moves = board_utils.generate_queen_moves(
            pieces.W_QUEENS, pieces.W_PIECES, pieces.ALL_PIECES)
        
        # The queen at d1 should be able to move to d2, d3, e2
        d1 = 3  # d1 square
        expected_targets = {
            11,  # d2
            19,  # d3
            12   # e2
        }
        
        for target in expected_targets:
            self.assertIn((d1, target), white_queen_moves, 
                          f"Queen should be able to move from d1 to {board_utils.square_to_algebraic(target)}")
        
        # Total number of moves should be the sum of expected targets
        self.assertEqual(len(white_queen_moves), len(expected_targets))

    def test_king_move_generation(self):
        """Test king move generation"""
        # Position with king that can move
        fen = "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQK2R w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white king moves
        white_king_moves = board_utils.generate_king_moves(
            pieces.W_KING, pieces.W_PIECES)
        
        # The king at e1 should be able to move to e2, d2, f1, f2
        e1 = 4  # e1 square
        expected_targets = {
            12,  # e2
            11,  # d2
            5,   # f1
            13   # f2
        }
        
        for target in expected_targets:
            self.assertIn((e1, target), white_king_moves, 
                          f"King should be able to move from e1 to {board_utils.square_to_algebraic(target)}")
        
        # Total number of moves should be the sum of expected targets
        self.assertEqual(len(white_king_moves), len(expected_targets))

    def test_castling_move_generation(self):
        """Test castling move generation"""
        # Position with king that can castle kingside
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white kingside castling
        white_castling_moves = board_utils.generate_castling_moves(
            pieces, game_state['castling_rights'], True)
        
        # The king should be able to castle kingside (e1-g1)
        e1_g1 = (4, 6)  # e1-g1
        self.assertIn(e1_g1, white_castling_moves)
        
        # Position with king that can castle queenside as well
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Test white castling in both directions
        white_castling_moves = board_utils.generate_castling_moves(
            pieces, game_state['castling_rights'], True)
        
        # The king should be able to castle kingside (e1-g1) and queenside (e1-c1)
        e1_g1 = (4, 6)  # e1-g1
        e1_c1 = (4, 2)  # e1-c1
        self.assertIn(e1_g1, white_castling_moves)
        self.assertIn(e1_c1, white_castling_moves)
        
        # Test black castling
        fen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        black_castling_moves = board_utils.generate_castling_moves(
            pieces, game_state['castling_rights'], False)
        
        # The king should be able to castle kingside (e8-g8) and queenside (e8-c8)
        e8_g8 = (60, 62)  # e8-g8
        e8_c8 = (60, 58)  # e8-c8
        self.assertIn(e8_g8, black_castling_moves)
        self.assertIn(e8_c8, black_castling_moves)

    def test_generate_all_moves_white(self):
        """Test generate_all_moves function for white"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Generate all legal moves for white
        all_moves = generate_all_moves(pieces, game_state)
        
        # In the starting position, white has 20 legal moves
        self.assertEqual(len(all_moves), 20)
        
        # Check some specific moves
        # Pawns: 16 moves (each pawn can move one or two squares forward)
        # Knights: 4 moves (b1-a3, b1-c3, g1-f3, g1-h3)
        
        # Knight moves
        b1_a3 = (1, 16)  # b1-a3
        b1_c3 = (1, 18)  # b1-c3
        g1_f3 = (6, 21)  # g1-f3
        g1_h3 = (6, 23)  # g1-h3
        
        knight_moves = [b1_a3, b1_c3, g1_f3, g1_h3]
        for move in knight_moves:
            self.assertIn(move, all_moves)
        
        # Pawn moves (check a few)
        e2_e4 = (12, 28)  # e2-e4
        d2_d4 = (11, 27)  # d2-d4
        self.assertIn(e2_e4, all_moves)
        self.assertIn(d2_d4, all_moves)

    def test_generate_all_moves_black(self):
        """Test generate_all_moves function for black"""
        # Position after 1. e4
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Generate all legal moves for black
        all_moves = generate_all_moves(pieces, game_state)
        
        # After 1. e4, black has 20 legal moves
        self.assertEqual(len(all_moves), 20)
        
        # Check some specific moves
        # Pawns: 16 moves (all pawns can move one or two squares forward)
        # Knights: 4 moves (b8-a6, b8-c6, g8-f6, g8-h6)
        
        # Knight moves
        b8_a6 = (57, 40)  # b8-a6
        b8_c6 = (57, 42)  # b8-c6
        g8_f6 = (62, 45)  # g8-f6
        g8_h6 = (62, 47)  # g8-h6
        
        knight_moves = [b8_a6, b8_c6, g8_f6, g8_h6]
        for move in knight_moves:
            self.assertIn(move, all_moves)
        
        # Pawn moves (check a few)
        e7_e5 = (52, 36)  # e7-e5
        e7_e6 = (52, 44)  # e7-e6
        self.assertIn(e7_e5, all_moves)
        self.assertIn(e7_e6, all_moves)
        
        # Make sure pawns can attack the e4 pawn
        d7_d5 = (51, 35)  # d7-d5 (pawn on e4 can be captured by d5)
        self.assertIn(d7_d5, all_moves)

    def test_is_in_check(self):
        """Test is_in_check function"""
        # Position with white king in check
        fen = "rnb1kbnr/pppp1ppp/8/4p3/4P1q1/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # White king should be in check
        self.assertTrue(board_utils.is_in_check(pieces, True))
        
        # Black king should not be in check
        self.assertFalse(board_utils.is_in_check(pieces, False))
        
        # Position with black king in check
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P2Q/8/PPPP1PPP/RNB1KBNR b KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Black king should be in check
        self.assertTrue(board_utils.is_in_check(pieces, False))
        
        # White king should not be in check
        self.assertFalse(board_utils.is_in_check(pieces, True))

    def test_make_move(self):
        """Test make_move function"""
        from engine.evaluation import make_move
        
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Make a move: e2-e4
        e2_e4 = (12, 28)
        new_pieces, new_game_state = make_move(pieces, e2_e4, game_state)
        
        # Check that the e4 square now has a white pawn
        self.assertTrue(board_utils.get_bit(new_pieces.W_PAWNS, 28))
        
        # Check that the e2 square no longer has a white pawn
        self.assertFalse(board_utils.get_bit(new_pieces.W_PAWNS, 12))
        
        # Check that the side to move has changed
        self.assertEqual(new_game_state['side_to_move'], 'b')
        
        # Check that en passant target is set (after two-square pawn move)
        self.assertEqual(new_game_state['en_passant'], 20)  # e3
        
        # Now make a black move: e7-e5
        e7_e5 = (52, 36)
        new_pieces2, new_game_state2 = make_move(new_pieces, e7_e5, new_game_state)
        
        # Check that the e5 square now has a black pawn
        self.assertTrue(board_utils.get_bit(new_pieces2.B_PAWNS, 36))
        
        # Check that the e7 square no longer has a black pawn
        self.assertFalse(board_utils.get_bit(new_pieces2.B_PAWNS, 52))
        
        # Check that the side to move has changed back to white
        self.assertEqual(new_game_state2['side_to_move'], 'w')
        
        # Check that fullmove number has increased
        self.assertEqual(new_game_state2['fullmove_number'], 2)


if __name__ == '__main__':
    unittest.main() 