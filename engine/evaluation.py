# evaluation.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from .constants import (
    PIECES, PIECE_VALUES_MG, PIECE_VALUES_EG,
    MG_PAWN_TABLE, MG_KNIGHT_TABLE, MG_BISHOP_TABLE, 
    MG_ROOK_TABLE, MG_QUEEN_TABLE, MG_KING_TABLE,
    CHECKMATE_SCORE
)
from .board_utils import parse_fen, get_game_phase, mirror_square
import random

class ChessEvaluator:
    def __init__(self):
        self.nodes_evaluated = 0
        self.transposition_table = {}
        self.position_history = {}  # Store all positions seen
        self.move_history = []      # Store recent moves
        self.MAX_HISTORY = 10       # Keep track of last 10 moves
    
    def _get_piece_scores(self, piece_type: int, square: int, piece: str) -> Tuple[int, int]:
        """Get combined piece value and square table scores for middlegame/endgame."""
        mg_value = PIECE_VALUES_MG[piece_type]
        eg_value = PIECE_VALUES_EG[piece_type]
        
        piece_char = piece.upper()
        if piece_char == 'P':
            mg_value += MG_PAWN_TABLE[square]
        elif piece_char == 'N':
            mg_value += MG_KNIGHT_TABLE[square]
        elif piece_char == 'B':
            mg_value += MG_BISHOP_TABLE[square]
        elif piece_char == 'R':
            mg_value += MG_ROOK_TABLE[square]
        elif piece_char == 'Q':
            mg_value += MG_QUEEN_TABLE[square]
        elif piece_char == 'K':
            mg_value += MG_KING_TABLE[square]
            
        return (mg_value, eg_value)

    def evaluate_fen(self, fen: str) -> int:
        """Evaluates a chess position from FEN string."""
        if fen in self.transposition_table:
            score, _ = self.transposition_table[fen]
            return score
            
        board = parse_fen(fen)
        phase = get_game_phase(board)
        
        mg_score = eg_score = 0
        
        for square, piece in enumerate(board):
            if not piece:
                continue
                
            piece_type = PIECES[piece]
            is_white = piece.isupper()
            ps_square = square if is_white else mirror_square(square)
            
            scores = self._get_piece_scores(piece_type, ps_square, piece)
            factor = 1 if is_white else -1
            
            mg_score += scores[0] * factor
            eg_score += scores[1] * factor
        
        final_score = ((mg_score * phase) + (eg_score * (256 - phase))) // 256
        
        # Add randomness to break ties and avoid repetition
        final_score += random.randint(-10, 10)
        
        # Heavy penalty for repeated positions
        repetitions = self.position_history.get(fen, 0)
        if repetitions > 0:
            final_score = final_score // (2 ** repetitions)  # Exponential penalty
        
        self.transposition_table[fen] = (final_score, 0)
        return final_score

    def get_best_move(self, positions: List[dict], depth: int = 3) -> dict:
        """Find best move using iterative deepening and move diversity."""
        self.nodes_evaluated = 0
        self.transposition_table.clear()
        
        try:
            is_white = positions[0]['fen'].split(' ')[1] == 'w'
            candidates = []  # Store multiple good moves
            
            # Iterative deepening
            for current_depth in range(1, depth + 1):
                best_moves = self._find_best_moves(positions, current_depth, is_white)
                candidates = best_moves  # Keep the deepest search results
            
            # Filter out moves that lead to immediate repetition
            filtered_candidates = [
                move for move in candidates 
                if not self._leads_to_repetition(move['move'])
            ]
            
            # If all moves lead to repetition, pick the least repetitive one
            if not filtered_candidates:
                filtered_candidates = candidates
            
            # Choose from top moves with some randomness
            chosen = self._select_diverse_move(filtered_candidates)
            
            # Update move history
            self._update_move_history(chosen['move'])
            
            return {
                'move': chosen['move'],
                'score': chosen['score'],
                'nodes': self.nodes_evaluated
            }
            
        except (KeyError, IndexError) as e:
            print(f"Error processing positions: {e}")
            print(f"First position: {positions[0] if positions else 'No positions'}")
            raise

    def _find_best_moves(self, positions: List[dict], depth: int, is_white: bool) -> List[dict]:
        """Find multiple good moves."""
        moves = []
        alpha = float('-inf')
        beta = float('inf')
        
        for position in positions:
            score = self.minimax(position['fen'], depth - 1, alpha, beta, not is_white)
            moves.append({
                'move': position['move'],
                'score': score,
                'fen': position['fen']
            })
        
        # Sort moves by score
        moves.sort(key=lambda x: x['score'], reverse=is_white)
        
        # Return top 3 moves that are within 50 centipawns of the best move
        best_score = moves[0]['score']
        return [m for m in moves if abs(m['score'] - best_score) <= 50][:3]

    def _select_diverse_move(self, candidates: List[dict]) -> dict:
        """Select a move that promotes diversity."""
        if len(candidates) == 1:
            return candidates[0]
            
        # Assign weights based on move history
        weights = []
        for move in candidates:
            # Count recent occurrences of similar moves
            similar_count = sum(1 for m in self.move_history if self._moves_are_similar(m, move['move']))
            weight = 1.0 / (similar_count + 1)  # More weight to less frequent moves
            weights.append(weight)
            
        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w/total for w in weights]
            return random.choices(candidates, weights=weights, k=1)[0]
        
        return random.choice(candidates)

    def _moves_are_similar(self, move1: str, move2: str) -> bool:
        """Check if moves are similar (same piece, similar squares)."""
        if not move1 or not move2:
            return False
        return (
            move1[:2] == move2[:2] or  # Same starting square
            move1[2:] == move2[2:]     # Same ending square
        )

    def _leads_to_repetition(self, move: str) -> bool:
        """Check if a move leads to a position we've seen before."""
        return self.position_history.get(move, 0) > 0

    def _update_move_history(self, move: str):
        """Update the history of moves played."""
        self.move_history.append(move)
        if len(self.move_history) > self.MAX_HISTORY:
            self.move_history.pop(0)

    def minimax(self, fen: str, depth: int, alpha: float, beta: float, maximizing: bool) -> int:
        """Minimax with alpha-beta pruning."""
        self.nodes_evaluated += 1
        
        # Update position history
        self.position_history[fen] = self.position_history.get(fen, 0) + 1
        
        if depth == 0:
            return self.evaluate_fen(fen)
            
        return self.evaluate_fen(fen)  # Placeholder for move generation
