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

    def get_best_move(self, fen, legal_moves, depth=3):
        """
        Find best move from current position.
        legal_moves should be array of moves in UCI format from chess.js
        """
        best_move = None
        best_score = float('-inf')
        
        for move in legal_moves:
            # Here you would need to:
            # 1. Apply move to get new FEN
            # 2. Evaluate new position
            # 3. Use minimax/alpha-beta
            # 4. Keep track of best move
            pass
            
        return best_move

# Add Flask endpoint to receive FEN and return evaluation
from flask import Flask, request, jsonify

app = Flask(__name__)
evaluator = ChessEvaluator()

@app.route('/api/evaluate', methods=['POST'])
def evaluate_position():
    data = request.json
    fen = data['fen']
    score = evaluator.evaluate_fen(fen)
    return jsonify({'score': score})

if __name__ == '__main__':
    app.run(debug=True)