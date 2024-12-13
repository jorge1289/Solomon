"""
Chess position evaluation using PeSTO's Evaluation Function
Adapted to work with FEN strings from chess.js
Credit: Based on Pawel Koziol's implementation in TSCP
"""

from .constants import (
    PIECES, PIECE_VALUES_MG, PIECE_VALUES_EG,
    MG_PAWN_TABLE, MG_KNIGHT_TABLE, CHECKMATE_SCORE
)
from .board_utils import parse_fen, get_game_phase, get_square_index, mirror_square

class ChessEvaluator:

    def __init__(self):
        self.nodes_evaluated = 0
    
    def evaluate_fen(self, fen):
        """
        Evaluates a chess position from FEN string.
        Returns score in centipawns (positive for white advantage).
        """
        # Parse board state from FEN
        board = parse_fen(fen)
        
        # Get game phase
        phase = get_game_phase(board)
        
        # Calculate middlegame and endgame scores
        mg_score = 0
        eg_score = 0
        
        for square, piece in enumerate(board):
            if not piece:
                continue
                
            piece_type = PIECES[piece]
            is_white = piece.isupper()
            
            # Get square for piece-square tables
            ps_square = square if is_white else mirror_square(square)
            
            # Get piece values
            mg_value = PIECE_VALUES_MG[piece_type]
            eg_value = PIECE_VALUES_EG[piece_type]
            
            # Add piece-square table bonus
            if piece.upper() == 'P':
                mg_value += MG_PAWN_TABLE[ps_square]
                # Add EG_PAWN_TABLE value
            elif piece.upper() == 'N':
                mg_value += MG_KNIGHT_TABLE[ps_square]
                # Add EG_KNIGHT_TABLE value
            # Add other piece types...
            
            # Add to respective scores
            if is_white:
                mg_score += mg_value
                eg_score += eg_value
            else:
                mg_score -= mg_value
                eg_score -= eg_value
        
        # Interpolate between middlegame and endgame scores
        final_score = ((mg_score * phase) + (eg_score * (256 - phase))) // 256
        
        return final_score

    def get_best_move(self, positions, depth=3):
        """
        Find best move from current position.
        legal_moves should be array of moves in UCI format from chess.js
        """
        self.nodes_evaluated = 0
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # White maximizes, Black minimizes
        is_white = positions[0]['fen'].split(' ')[1] == 'w'
        best_score = float('-inf') if is_white else float('inf')
        
        # First level of search
        for position in positions:
            score = self.minimax(position['fen'], depth - 1, alpha, beta, not is_white)
            
            if is_white and score > best_score:
                best_score = score
                best_move = position['move']
                alpha = max(alpha, score)
            elif not is_white and score < best_score:
                best_score = score
                best_move = position['move']
                beta = min(beta, score)
        
        return {
            'move': best_move,
            'score': best_score,
            'nodes': self.nodes_evaluated
        }
    
    def minimax(self, fen, depth, alpha, beta, maximizing):
        """
        Minimax implementation with alpha-beta pruning.
        Uses position evaluations for leaf nodes.
        """
        self.nodes_evaluated += 1
        
        # Base case: leaf node
        if depth == 0:
            return self.evaluate_position(fen)
            
        # We'll receive the possible moves and resulting positions from the frontend
        return self.evaluate_position(fen)  # For non-leaf nodes, use current position for now

# Add Flask endpoint to receive FEN and return evaluation
from flask import Flask, request, jsonify

app = Flask(__name__)
evaluator = ChessEvaluator()

@app.route('/api/get-move', methods=['POST'])
def get_move():
    try:
        data = request.json
        if not data or 'positions' not in data:
            return jsonify({'error': 'Missing positions data'}), 400
            
        positions = data['positions']
        depth = data.get('depth', 3)
        
        result = evaluator.get_best_move(positions, depth)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500