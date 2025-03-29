# test_chess_engine.py
import sys
import os
import unittest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.evaluation import ChessEvaluator, evaluate_positions, minimax
from engine.board_utils import parse_fen_to_bitboards, square_to_algebraic

class TestChessEngine(unittest.TestCase):
    def setUp(self):
        self.evaluator = ChessEvaluator()
    
    def test_white_to_move(self):
        """Test that engine returns a valid move for white"""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        result = self.evaluator.get_best_move(fen, 3)
        
        print(f"White's move: {result['move']}")
        
        # Check that a move is returned
        self.assertIsNotNone(result['move'])
        # Check that the move is properly formatted (4 characters)
        self.assertEqual(len(result['move']), 4)
        
        # Verify the move starts from a white piece's position (rank 1-2)
        self.assertTrue(result['move'][1] in ['1', '2'], 
                        f"Move {result['move']} doesn't start from a white position")
    
    def test_black_to_move(self):
        """Test that engine returns a valid move for black"""
        # After 1.d4
        fen = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1"
        result = self.evaluator.get_best_move(fen, 3)
        
        print(f"Black's move: {result['move']}")
        
        # Check that a move is returned
        self.assertIsNotNone(result['move'])
        # Verify move length
        self.assertEqual(len(result['move']), 4)
        
        # Verify the move starts from a black piece's position (rank 7-8)
        self.assertTrue(result['move'][1] in ['7', '8'], 
                        f"Move {result['move']} doesn't start from a black position")
    
    def test_checkmate_in_one(self):
        """Test that engine finds checkmate in one move."""
        # Position where white can checkmate in one move
        fen = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4"
        result = self.evaluator.get_best_move(fen, 3)
        
        # Should find Qf7-e8 checkmate
        self.assertEqual(result['move'], 'f7e8')
    
    def test_avoid_checkmate(self):
        """Test that engine avoids immediate checkmate."""
        # Position where black must avoid checkmate
        fen = "r1bqkb1r/ppp2ppp/2n5/3PN3/2BP4/8/PPP2PPP/R1BQK1NR b KQkq - 0 1"
        result = self.evaluator.get_best_move(fen, 3)
        
        # The move should not be Kd8 or Kf8, which allow checkmate
        self.assertNotIn(result['move'], ['e8d8', 'e8f8'])
    
    def test_evaluation_function(self):
        """Test that the evaluation function gives reasonable values"""
        # Equal position
        fen_equal = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces_equal, _ = parse_fen_to_bitboards(fen_equal)
        score_equal = evaluate_positions(pieces_equal)
        
        # Score should be close to 0 for equal position
        self.assertTrue(-100 < score_equal < 100, 
                       f"Equal position evaluation should be near 0, got {score_equal}")
        
        # White is better (up a knight)
        fen_white_up = "rnbqkb1r/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
        pieces_white_up, _ = parse_fen_to_bitboards(fen_white_up)
        score_white_up = evaluate_positions(pieces_white_up)
        
        # Score should be positive and significant for white up material
        self.assertTrue(score_white_up > 300, 
                       f"White up a knight should evaluate positive, got {score_white_up}")

if __name__ == '__main__':
    unittest.main()