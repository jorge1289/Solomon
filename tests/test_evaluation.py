import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.constants import BitboardPieces, CHECKMATE_SCORE
from engine import board_utils
from engine.evaluation import (
    ChessEvaluator, 
    evaluate_positions, 
    minimax, 
    get_game_phase, 
    get_piece_scores,
    order_moves
)

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        """Set up for tests"""
        self.evaluator = ChessEvaluator()
    
    def test_get_piece_scores(self):
        """Test piece score calculation for both middlegame and endgame"""
        # Create a single white pawn at e2
        pawn_bitboard = 1 << 12  # e2
        
        # Get scores for a white pawn
        mg_score, eg_score = get_piece_scores(pawn_bitboard, 'P', True)
        
        # Scores should be positive for white
        self.assertGreater(mg_score, 0)
        self.assertGreater(eg_score, 0)
        
        # Create a single black pawn at e7
        pawn_bitboard = 1 << 52  # e7
        
        # Get scores for a black pawn
        mg_score, eg_score = get_piece_scores(pawn_bitboard, 'p', False)
        
        # Scores should be negative (from white's perspective)
        self.assertLess(mg_score, 0)
        self.assertLess(eg_score, 0)
        
        # Test with multiple pieces
        knight_bitboard = (1 << 1) | (1 << 6)  # b1 and g1
        mg_score, eg_score = get_piece_scores(knight_bitboard, 'N', True)
        
        # Scores should roughly be double the value of a single knight
        self.assertGreater(mg_score, 600)  # 2 * 337 = 674
        self.assertGreater(eg_score, 500)  # 2 * 281 = 562

    def test_evaluate_positions(self):
        """Test position evaluation in different game phases"""
        # Starting position
        fen = "rnbqkbnr/pppppppp /8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        # Evaluation should be near 0 in a balanced starting position
        score = evaluate_positions(pieces)
        self.assertTrue(-100 < score < 100, f"Starting position should be near 0, got {score}")
        
        # Position with white up a knight
        fen = "rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        score = evaluate_positions(pieces)
        self.assertGreater(score, 300, f"White up a knight should have score > 300, got {score}")
        
        # Position with black up a knight
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R1BQKBNR w KQkq - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        score = evaluate_positions(pieces)
        self.assertLess(score, -300, f"Black up a knight should have score < -300, got {score}")
    
    def test_get_game_phase(self):
        """Test game phase calculation"""
        # Starting position (opening)
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        phase = get_game_phase(pieces)
        self.assertEqual(phase, 256, f"Starting position should be phase 256, got {phase}")
        
        # Middle game (queens exchanged)
        fen = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        phase = get_game_phase(pieces)
        self.assertLess(phase, 256, "Middle game should have phase < 256")
        self.assertGreater(phase, 128, "Middle game should have phase > 128")
        
        # Endgame (only kings and pawns)
        fen = "4k3/pppppppp/8/8/8/8/PPPPPPPP/4K3 w - - 0 1"
        pieces, _ = board_utils.parse_fen_to_bitboards(fen)
        
        phase = get_game_phase(pieces)
        self.assertEqual(phase, 0, f"Endgame position should be phase 0, got {phase}")
    
    def test_order_moves(self):
        """Test move ordering for alpha-beta pruning"""
        # Position with captures available
        fen = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Generate legal moves
        from engine.evaluation import generate_all_moves
        moves = generate_all_moves(pieces, game_state)
        
        # Order the moves
        ordered_moves = order_moves(moves, pieces, game_state)
        
        # The capture move (e4xd5) should come first
        e4_d5 = (28, 35)  # e4-d5
        self.assertEqual(ordered_moves[0], e4_d5, 
                         f"Capture move e4xd5 should be first, got {board_utils.square_to_algebraic(ordered_moves[0][0])}{board_utils.square_to_algebraic(ordered_moves[0][1])}")
        
        # All captures should come before non-captures
        captures_done = False
        for move in ordered_moves:
            _, to_sq = move
            is_capture = board_utils.get_bit(pieces.ALL_PIECES, to_sq)
            
            if not is_capture and not captures_done:
                captures_done = True
            
            if is_capture and captures_done:
                self.fail("Captures should come before non-captures")
    
    def test_minimax_depth_0(self):
        """Test minimax at depth 0 (evaluation only)"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Minimax at depth 0 should return the evaluation score
        score = minimax(pieces, game_state, 0, float('-inf'), float('inf'), True, self.evaluator)
        direct_eval = evaluate_positions(pieces)
        
        self.assertEqual(score, direct_eval, 
                         f"Minimax at depth 0 should return evaluation score {direct_eval}, got {score}")
    
    def test_minimax_checkmate(self):
        """Test minimax finds checkmate"""
        # Position with checkmate in 1 for white
        fen = "rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Generate all legal moves
        from engine.evaluation import generate_all_moves
        all_moves = generate_all_moves(pieces, game_state)
        
        best_score = float('-inf')
        
        # Find the best move with minimax
        for move in all_moves:
            from engine.evaluation import make_move
            new_pieces, new_game_state = make_move(pieces, move, game_state)
            score = minimax(new_pieces, new_game_state, 1, float('-inf'), float('inf'), False, self.evaluator)
            
            if score > best_score:
                best_score = score
        
        # Best score should be checkmate
        self.assertEqual(best_score, CHECKMATE_SCORE, 
                         f"Minimax should find checkmate value {CHECKMATE_SCORE}, got {best_score}")
    
    def test_get_best_move_white(self):
        """Test get_best_move selects the best move for white"""
        # Position with a clear best move for white
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        
        # Get the best move at depth 3
        result = self.evaluator.get_best_move(fen, 3)
        
        # Should return a valid move
        self.assertIsNotNone(result['move'])
        self.assertEqual(len(result['move']), 4)  # e.g., "d2d4"
        
        # Check that the move is from a white piece position
        self.assertTrue(result['move'][1] in ['1', '2'], 
                       f"Move {result['move']} doesn't start from a white position")
    
    def test_get_best_move_black(self):
        """Test get_best_move selects the best move for black"""
        # Position with a clear best move for black
        fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1"
        
        # Get the best move at depth 3
        result = self.evaluator.get_best_move(fen, 3)
        
        # Should return a valid move
        self.assertIsNotNone(result['move'])
        self.assertEqual(len(result['move']), 4)  # e.g., "g8f6"
        
        # Check that the move is from a black piece position
        self.assertTrue(result['move'][1] in ['7', '8'], 
                       f"Move {result['move']} doesn't start from a black position")
    
    def test_transposition_table(self):
        """Test that the transposition table improves performance"""
        # Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
        
        # Clear the transposition table
        self.evaluator.transposition_table.clear()
        
        # First call to minimax should populate the table
        minimax(pieces, game_state, 2, float('-inf'), float('inf'), True, self.evaluator)
        
        # Table should have entries now
        self.assertGreater(len(self.evaluator.transposition_table), 0, 
                          "Transposition table should have entries after minimax call")


if __name__ == '__main__':
    unittest.main() 