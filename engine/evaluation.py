# evaluation.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from .constants import (
    BitboardPieces, PIECE_VALUES_MG, PIECE_VALUES_EG,
    MG_PAWN_TABLE, EG_PAWN_TABLE, MG_KNIGHT_TABLE, 
    EG_KNIGHT_TABLE, MG_BISHOP_TABLE, EG_BISHOP_TABLE,
    MG_ROOK_TABLE, EG_ROOK_TABLE, MG_QUEEN_TABLE, 
    EG_QUEEN_TABLE, MG_KING_TABLE, EG_KING_TABLE,
    CHECKMATE_SCORE, PIECES
)
from . import board_utils
import random

# Global variable for node counting
nodes_evaluated = 0

class ChessEvaluator:
    def __init__(self):
        self.transposition_table = {}
        self.position_history = {}  # Store all positions seen
        self.move_history = []      # Store recent moves
        self.MAX_HISTORY = 10       # Keep track of last 10 moves
    
    def get_best_move(self, fen: str, depth: int) -> dict:
        """Evaluate a position directly from FEN and find the best move."""
        global nodes_evaluated
        nodes_evaluated = 0
        self.transposition_table.clear()
        
        try:
            # Parse FEN to bitboards
            pieces, game_state = board_utils.parse_fen_to_bitboards(fen)
            is_white = game_state['side_to_move'] == 'w'
            print(f"Side to move: {game_state['side_to_move']}") # debugging
            
            # Generate all legal moves for the current position
            all_moves = generate_all_moves(pieces, game_state)
            print(f"Generated {len(all_moves)} moves for {'white' if is_white else 'black'}")
            for i, move in enumerate(all_moves[:5]):  # Print first 5 moves
                from_sq, to_sq = move
                from_alg = board_utils.square_to_algebraic(from_sq)
                to_alg = board_utils.square_to_algebraic(to_sq)
                print(f"  Move {i}: {from_alg}{to_alg}")
            
            if not all_moves:
                # No legal moves available
                return {'move': None, 'score': 0, 'nodes': 0}
            
            # Order moves for better alpha-beta pruning
            ordered_moves = order_moves(all_moves, pieces, game_state)
            
            # Filter moves to ensure they're coming from the correct side's pieces
            valid_moves = []
            for move in ordered_moves:
                from_sq, to_sq = move
                
                # Check if the move is from the correct side's piece
                if is_white:
                    is_correct_side = (
                        board_utils.get_bit(pieces.W_PAWNS, from_sq) or
                        board_utils.get_bit(pieces.W_KNIGHTS, from_sq) or
                        board_utils.get_bit(pieces.W_BISHOPS, from_sq) or
                        board_utils.get_bit(pieces.W_ROOKS, from_sq) or
                        board_utils.get_bit(pieces.W_QUEENS, from_sq) or
                        board_utils.get_bit(pieces.W_KING, from_sq)
                    )
                else:
                    is_correct_side = (
                        board_utils.get_bit(pieces.B_PAWNS, from_sq) or
                        board_utils.get_bit(pieces.B_KNIGHTS, from_sq) or
                        board_utils.get_bit(pieces.B_BISHOPS, from_sq) or
                        board_utils.get_bit(pieces.B_ROOKS, from_sq) or
                        board_utils.get_bit(pieces.B_QUEENS, from_sq) or
                        board_utils.get_bit(pieces.B_KING, from_sq)
                    )
                
                if is_correct_side:
                    valid_moves.append(move)
                else:
                    print(f"  WARNING: Filtering out move {board_utils.square_to_algebraic(from_sq)}{board_utils.square_to_algebraic(to_sq)} - not from correct side")
            
            if not valid_moves:
                print("ERROR: No valid moves for the correct side after filtering!")
                return {'move': None, 'score': 0, 'nodes': 0}
            
            print(f"Filtered to {len(valid_moves)} valid moves for {'white' if is_white else 'black'}")
            
            best_move = None
            best_score = float('-inf') if is_white else float('inf')
            
            # Iterative deepening - start from depth 1 and increase
            max_depth = min(depth, 10)  # Limit max depth for performance
            for current_depth in range(1, max_depth + 1):
                print(f"Searching at depth {current_depth}...")
                
                # For each move, make it and evaluate the position
                for move in valid_moves:
                    from_sq, to_sq = move
                    move_str = board_utils.square_to_algebraic(from_sq) + board_utils.square_to_algebraic(to_sq)
                    
                    # Make move and get new position
                    new_pieces, new_game_state = make_move(pieces, move, game_state)
                    
                    # Evaluate with minimax
                    # The minimax evaluation gives us the score from the perspective of the player who just moved
                    # So we're evaluating how good the position is for our opponent
                    score = minimax(
                        new_pieces, 
                        new_game_state, 
                        current_depth - 1, 
                        float('-inf'), 
                        float('inf'), 
                        not is_white,  # Opponent's turn after our move
                        self  # Pass the evaluator instance
                    )
                    
                    # Since the score is from the perspective of the opponent,
                    # we need to negate it to get our perspective
                    score = -score
                    
                    # Update best move based on the current player
                    if ((is_white and score > best_score) or 
                        (not is_white and score < best_score) or
                        best_move is None):
                        best_score = score
                        best_move = move
                        print(f"New best move: {move_str} with score {score}")
                
                # Early termination if we found a mate
                if abs(best_score) > CHECKMATE_SCORE - 1000:
                    break
            
            # Convert move to string format (e.g., "e2e4")
            if best_move:
                from_sq, to_sq = best_move
                move_str = board_utils.square_to_algebraic(from_sq) + board_utils.square_to_algebraic(to_sq)
                
                # Debug to make sure the move is for the correct side
                print(f"Side to move: {game_state['side_to_move']}, Selected best move: {move_str}")
                print(f"best_move after minmax: {best_move}")
                
                # Store move in history
                self._update_move_history(move_str)
                
                return {
                    'move': move_str,
                    'score': best_score,
                    'nodes': nodes_evaluated
                }
            else:
                return {'move': None, 'score': 0, 'nodes': nodes_evaluated}
                
        except Exception as e:
            print(f"Error in get_best_move: {e}")
            import traceback
            traceback.print_exc()
            # Return a fallback
            return {'move': None, 'score': 0, 'nodes': 0}
    
    # def get_best_move(self, positions: List[dict], depth: int) -> dict:
    #     """Find best move using bitboard-based engine with iterative deepening."""
    #     global nodes_evaluated
    #     nodes_evaluated = 0
    #     self.transposition_table.clear()
        
    #     try:
    #         # Check if we have valid positions
    #         if not positions:
    #             return {'move': None, 'score': 0, 'nodes': 0}
                
    #         # Parse the FEN from the first position to determine side to move
    #         starting_fen = positions[0]['fen']
    #         is_white = starting_fen.split(' ')[1] == 'w'
            
    #         best_move = None
    #         best_score = float('-inf') if is_white else float('inf')
            
    #         # Store position evaluation results
    #         position_scores = {}
            
    #         # Iterative deepening - start from depth 1 and increase
    #         # This helps improve move ordering and alpha-beta pruning effectiveness
    #         max_depth = min(depth, 10)  # Limit max depth for performance
    #         for current_depth in range(1, max_depth + 1):
    #             print(f"Searching at depth {current_depth}...")
                
    #             # Sort positions by previous iteration scores (if available)
    #             if current_depth > 1 and position_scores:
    #                 if is_white:
    #                     # White wants to maximize score
    #                     sorted_positions = sorted(positions, 
    #                                               key=lambda pos: position_scores.get(pos['move'], float('-inf')),
    #                                               reverse=True)
    #                 else:
    #                     # Black wants to minimize score
    #                     sorted_positions = sorted(positions, 
    #                                               key=lambda pos: position_scores.get(pos['move'], float('inf')))
    #             else:
    #                 sorted_positions = positions
                
    #             # Reset scores for this iteration
    #             position_scores = {}
                
    #             # Convert each position to bitboards and evaluate using minimax
    #             for position in sorted_positions:
    #                 # Parse FEN to bitboards
    #                 pieces, game_state = board_utils.parse_fen_to_bitboards(position['fen'])
                    
    #                 # Evaluate with minimax (opponent's perspective since move is already made)
    #                 score = minimax(
    #                     pieces, 
    #                     game_state, 
    #                     current_depth - 1, 
    #                     float('-inf'), 
    #                     float('inf'), 
    #                     not is_white,
    #                     self  # Pass the evaluator instance
    #                 )
                    
    #                 # Store score for this position
    #                 position_scores[position['move']] = score
                    
    #                 # Update best move based on side to move
    #                 if ((is_white and score > best_score) or 
    #                     (not is_white and score < best_score) or
    #                     best_move is None):
    #                     best_score = score
    #                     best_move = position['move']
                
    #             # Early termination if we found a mate
    #             if abs(best_score) > CHECKMATE_SCORE - 1000:
    #                 break
                    
    #             # Time check (add a reasonable time check later for tournament play)
            
    #         # If we have a valid move, return it
    #         if best_move:
    #             # Store move in history
    #             self._update_move_history(best_move)
                
    #             return {
    #                 'move': best_move,
    #                 'score': best_score,
    #                 'nodes': nodes_evaluated
    #             }
    #         else:
    #             return {'move': None, 'score': 0, 'nodes': nodes_evaluated}
                
    #     except Exception as e:
    #         print(f"Error in get_best_move: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         # Return a fallback move
    #         return {'move': positions[0]['move'] if positions else None, 'score': 0, 'nodes': 0}
    
    def _update_move_history(self, move: str):
        """Update the history of moves played."""
        self.move_history.append(move)
        if len(self.move_history) > self.MAX_HISTORY:
            self.move_history.pop(0)

def get_game_phase(pieces: BitboardPieces) -> int:
    """Calculate game phase for interpolating between middlegame and endgame scores."""
    # Count pieces for phase calculation
    pawn_count = board_utils.count_bits(pieces.W_PAWNS | pieces.B_PAWNS)
    knight_count = board_utils.count_bits(pieces.W_KNIGHTS | pieces.B_KNIGHTS)
    bishop_count = board_utils.count_bits(pieces.W_BISHOPS | pieces.B_BISHOPS)
    rook_count = board_utils.count_bits(pieces.W_ROOKS | pieces.B_ROOKS)
    queen_count = board_utils.count_bits(pieces.W_QUEENS | pieces.B_QUEENS)
    
    # Calculate phase points based on piece counts
    # Typically: pawns=0, knights/bishops=1, rooks=2, queens=4
    phase = knight_count + bishop_count + 2 * rook_count + 4 * queen_count
    
    # Scale phase to a value between 0 and 256
    # 24 is the total phase value at the start of the game
    # 0 would be the endgame, 24 would be the opening
    phase = (phase * 256 + 12) // 24
    
    # Ensure the phase stays within bounds
    if phase > 256:
        phase = 256
    
    return phase


def evaluate_positions(pieces: BitboardPieces) -> int:
    """Evaluate a position using bitboards with PeSTO's evaluation function."""
    mg_score = eg_score = 0
    
    # Define piece mappings
    piece_mappings = [
        (pieces.W_PAWNS, 'P', True),
        (pieces.W_KNIGHTS, 'N', True),
        (pieces.W_BISHOPS, 'B', True),
        (pieces.W_ROOKS, 'R', True),
        (pieces.W_QUEENS, 'Q', True),
        (pieces.W_KING, 'K', True),
        (pieces.B_PAWNS, 'p', False),
        (pieces.B_KNIGHTS, 'n', False),
        (pieces.B_BISHOPS, 'b', False),
        (pieces.B_ROOKS, 'r', False),
        (pieces.B_QUEENS, 'q', False),
        (pieces.B_KING, 'k', False)
    ]
    
    # Calculate scores for all pieces
    for bitboard, piece_type, is_white in piece_mappings:
        piece_mg, piece_eg = get_piece_scores(bitboard, piece_type, is_white)
        mg_score += piece_mg
        eg_score += piece_eg

    # Calculate game phase and interpolate
    phase = get_game_phase(pieces)
    
    # Final score is from white's perspective
    final_score = ((mg_score * phase) + (eg_score * (256 - phase))) // 256
    
    return final_score


def minimax(pieces: BitboardPieces, game_state: dict, depth: int, alpha: int, beta: int, maximizing: bool, evaluator=None) -> int:
    """Minimax search with alpha-beta pruning using bitboards"""
    # Increment node count
    global nodes_evaluated
    nodes_evaluated += 1
    
    # Create a position key for the transposition table
    position_key = hash((
        pieces.W_PAWNS, pieces.W_KNIGHTS, pieces.W_BISHOPS, pieces.W_ROOKS, pieces.W_QUEENS, pieces.W_KING,
        pieces.B_PAWNS, pieces.B_KNIGHTS, pieces.B_BISHOPS, pieces.B_ROOKS, pieces.B_QUEENS, pieces.B_KING,
        game_state['side_to_move'], game_state['castling_rights'], game_state['en_passant']
    ))
    
    # Check if position is in transposition table
    if evaluator and position_key in evaluator.transposition_table and depth <= evaluator.transposition_table[position_key]['depth']:
        return evaluator.transposition_table[position_key]['score']
    
    # Base case - evaluate position
    if depth == 0:
        # The evaluation function returns the score from white's perspective
        # We need to adjust it based on who is to move
        score = evaluate_positions(pieces)
        # If black is to move in a maximizing node, or white is to move in a minimizing node,
        # we need to negate the score
        is_white = game_state['side_to_move'] == 'w'
        if (maximizing and not is_white) or (not maximizing and is_white):
            score = -score
            
        # Store in transposition table
        if evaluator:
            evaluator.transposition_table[position_key] = {'score': score, 'depth': depth}
        return score
    
    # Generate legal moves for the current position
    moves = generate_all_moves(pieces, game_state)
    
    # If no legal moves, check for checkmate or stalemate
    if not moves:
        if board_utils.is_in_check(pieces, game_state['side_to_move'] == 'w'):
            score = -CHECKMATE_SCORE if maximizing else CHECKMATE_SCORE
            if evaluator:
                evaluator.transposition_table[position_key] = {'score': score, 'depth': depth}
            return score
        score = 0  # Stalemate
        if evaluator:
            evaluator.transposition_table[position_key] = {'score': score, 'depth': depth}
        return score
    
    # Try to order moves for better pruning (captures first)
    ordered_moves = order_moves(moves, pieces, game_state)
    
    best_score = float('-inf') if maximizing else float('inf')
    
    for move in ordered_moves:
        # Make move
        new_pieces, new_game_state = make_move(pieces, move, game_state)
        
        # Recursive evaluation
        score = minimax(new_pieces, new_game_state, depth - 1, alpha, beta, not maximizing, evaluator)
        
        # Update best score
        if maximizing:
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
        else:
            best_score = min(best_score, score)
            beta = min(beta, best_score)
        
        # Alpha-beta pruning
        if beta <= alpha:
            break
    
    # Store in transposition table
    if evaluator:
        evaluator.transposition_table[position_key] = {'score': best_score, 'depth': depth}
    
    return best_score

def order_moves(moves: list, pieces: BitboardPieces, game_state: dict) -> list:
    """Order moves for better alpha-beta pruning (captures first)."""
    # Simple move ordering: captures first
    captures = []
    non_captures = []
    
    for move in moves:
        from_sq, to_sq = move
        # Check if the move is a capture
        if board_utils.get_bit(pieces.ALL_PIECES, to_sq):
            captures.append(move)
        else:
            non_captures.append(move)
    
    # Return captures first, then non-captures
    return captures + non_captures

def generate_all_moves(pieces: BitboardPieces, game_state: dict) -> list:
    """Generate all legal moves for the given position."""
    moves = []
    is_white = game_state['side_to_move'] == 'w'
    
    # Determine the pieces to move based on side to move
    if is_white:
        # Generate moves for white pieces
        moves.extend(board_utils.generate_pawn_moves(
            pieces.W_PAWNS, pieces.ALL_PIECES, pieces.B_PIECES, True))
        moves.extend(board_utils.generate_knight_moves(
            pieces.W_KNIGHTS, pieces.W_PIECES))
        moves.extend(board_utils.generate_bishop_moves(
            pieces.W_BISHOPS, pieces.W_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_rook_moves(
            pieces.W_ROOKS, pieces.W_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_queen_moves(
            pieces.W_QUEENS, pieces.W_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_king_moves(
            pieces.W_KING, pieces.W_PIECES))
        # Add castling moves
        moves.extend(board_utils.generate_castling_moves(
            pieces, game_state['castling_rights'], True))
    else:
        # Generate moves for black pieces
        moves.extend(board_utils.generate_pawn_moves(
            pieces.B_PAWNS, pieces.ALL_PIECES, pieces.W_PIECES, False))
        moves.extend(board_utils.generate_knight_moves(
            pieces.B_KNIGHTS, pieces.B_PIECES))
        moves.extend(board_utils.generate_bishop_moves(
            pieces.B_BISHOPS, pieces.B_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_rook_moves(
            pieces.B_ROOKS, pieces.B_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_queen_moves(
            pieces.B_QUEENS, pieces.B_PIECES, pieces.ALL_PIECES))
        moves.extend(board_utils.generate_king_moves(
            pieces.B_KING, pieces.B_PIECES))
        # Add castling moves
        moves.extend(board_utils.generate_castling_moves(
            pieces, game_state['castling_rights'], False))
    
    # Add en passant moves
    if game_state['en_passant'] is not None:
        moves.extend(board_utils.generate_en_passant_moves(
            pieces, game_state['en_passant'], is_white))
    
    # Filter out moves that leave the king in check
    legal_moves = []
    king = pieces.W_KING if is_white else pieces.B_KING
    king_sq = board_utils.lsb(king)
    
    for move in moves:
        from_sq, to_sq = move
        is_king_move = board_utils.get_bit(king, from_sq)
        
        # Make a temporary move
        new_pieces = BitboardPieces()
        # Copy all bitboards
        new_pieces.W_PAWNS = pieces.W_PAWNS
        new_pieces.W_KNIGHTS = pieces.W_KNIGHTS
        new_pieces.W_BISHOPS = pieces.W_BISHOPS
        new_pieces.W_ROOKS = pieces.W_ROOKS
        new_pieces.W_QUEENS = pieces.W_QUEENS
        new_pieces.W_KING = pieces.W_KING
        new_pieces.B_PAWNS = pieces.B_PAWNS
        new_pieces.B_KNIGHTS = pieces.B_KNIGHTS
        new_pieces.B_BISHOPS = pieces.B_BISHOPS
        new_pieces.B_ROOKS = pieces.B_ROOKS
        new_pieces.B_QUEENS = pieces.B_QUEENS
        new_pieces.B_KING = pieces.B_KING
        
        # Update the piece bitboards for the move
        if is_white:
            if board_utils.get_bit(pieces.W_PAWNS, from_sq):
                new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, from_sq)
                new_pieces.W_PAWNS = board_utils.set_bit(new_pieces.W_PAWNS, to_sq)
            elif board_utils.get_bit(pieces.W_KNIGHTS, from_sq):
                new_pieces.W_KNIGHTS = board_utils.clear_bit(new_pieces.W_KNIGHTS, from_sq)
                new_pieces.W_KNIGHTS = board_utils.set_bit(new_pieces.W_KNIGHTS, to_sq)
            elif board_utils.get_bit(pieces.W_BISHOPS, from_sq):
                new_pieces.W_BISHOPS = board_utils.clear_bit(new_pieces.W_BISHOPS, from_sq)
                new_pieces.W_BISHOPS = board_utils.set_bit(new_pieces.W_BISHOPS, to_sq)
            elif board_utils.get_bit(pieces.W_ROOKS, from_sq):
                new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, from_sq)
                new_pieces.W_ROOKS = board_utils.set_bit(new_pieces.W_ROOKS, to_sq)
            elif board_utils.get_bit(pieces.W_QUEENS, from_sq):
                new_pieces.W_QUEENS = board_utils.clear_bit(new_pieces.W_QUEENS, from_sq)
                new_pieces.W_QUEENS = board_utils.set_bit(new_pieces.W_QUEENS, to_sq)
            elif board_utils.get_bit(pieces.W_KING, from_sq):
                new_pieces.W_KING = board_utils.clear_bit(new_pieces.W_KING, from_sq)
                new_pieces.W_KING = board_utils.set_bit(new_pieces.W_KING, to_sq)
            
            # Clear any captured black piece
            new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, to_sq)
            new_pieces.B_KNIGHTS = board_utils.clear_bit(new_pieces.B_KNIGHTS, to_sq)
            new_pieces.B_BISHOPS = board_utils.clear_bit(new_pieces.B_BISHOPS, to_sq)
            new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, to_sq)
            new_pieces.B_QUEENS = board_utils.clear_bit(new_pieces.B_QUEENS, to_sq)
        else:
            if board_utils.get_bit(pieces.B_PAWNS, from_sq):
                new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, from_sq)
                new_pieces.B_PAWNS = board_utils.set_bit(new_pieces.B_PAWNS, to_sq)
            elif board_utils.get_bit(pieces.B_KNIGHTS, from_sq):
                new_pieces.B_KNIGHTS = board_utils.clear_bit(new_pieces.B_KNIGHTS, from_sq)
                new_pieces.B_KNIGHTS = board_utils.set_bit(new_pieces.B_KNIGHTS, to_sq)
            elif board_utils.get_bit(pieces.B_BISHOPS, from_sq):
                new_pieces.B_BISHOPS = board_utils.clear_bit(new_pieces.B_BISHOPS, from_sq)
                new_pieces.B_BISHOPS = board_utils.set_bit(new_pieces.B_BISHOPS, to_sq)
            elif board_utils.get_bit(pieces.B_ROOKS, from_sq):
                new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, from_sq)
                new_pieces.B_ROOKS = board_utils.set_bit(new_pieces.B_ROOKS, to_sq)
            elif board_utils.get_bit(pieces.B_QUEENS, from_sq):
                new_pieces.B_QUEENS = board_utils.clear_bit(new_pieces.B_QUEENS, from_sq)
                new_pieces.B_QUEENS = board_utils.set_bit(new_pieces.B_QUEENS, to_sq)
            elif board_utils.get_bit(pieces.B_KING, from_sq):
                new_pieces.B_KING = board_utils.clear_bit(new_pieces.B_KING, from_sq)
                new_pieces.B_KING = board_utils.set_bit(new_pieces.B_KING, to_sq)
            
            # Clear any captured white piece
            new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, to_sq)
            new_pieces.W_KNIGHTS = board_utils.clear_bit(new_pieces.W_KNIGHTS, to_sq)
            new_pieces.W_BISHOPS = board_utils.clear_bit(new_pieces.W_BISHOPS, to_sq)
            new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, to_sq)
            new_pieces.W_QUEENS = board_utils.clear_bit(new_pieces.W_QUEENS, to_sq)
        
        # Update combined bitboards
        new_pieces.W_PIECES = (new_pieces.W_PAWNS | new_pieces.W_KNIGHTS | new_pieces.W_BISHOPS | 
                              new_pieces.W_ROOKS | new_pieces.W_QUEENS | new_pieces.W_KING)
        new_pieces.B_PIECES = (new_pieces.B_PAWNS | new_pieces.B_KNIGHTS | new_pieces.B_BISHOPS | 
                              new_pieces.B_ROOKS | new_pieces.B_QUEENS | new_pieces.B_KING)
        new_pieces.ALL_PIECES = new_pieces.W_PIECES | new_pieces.B_PIECES
        
        # If king moved, update king square
        if is_king_move:
            king_sq = to_sq
        
        # Check if king is in check after move
        if not board_utils.is_square_attacked(king_sq, new_pieces, not is_white):
            legal_moves.append(move)
    
    return legal_moves

def make_move(pieces: BitboardPieces, move: tuple, game_state: dict) -> Tuple[BitboardPieces, dict]:
    """Make a move on the bitboard and return the new state."""
    from_sq, to_sq = move
    is_white = game_state['side_to_move'] == 'w'
    print(f"Making move for {'white' if is_white else 'black'}: {board_utils.square_to_algebraic(from_sq)}{board_utils.square_to_algebraic(to_sq)}")
    
    new_pieces = BitboardPieces()
    new_game_state = game_state.copy()
    
    # Update side to move
    new_game_state['side_to_move'] = 'b' if is_white else 'w'
    
    # Reset en passant target
    new_game_state['en_passant'] = None
    
    # Increment fullmove number if black just moved
    if not is_white:
        new_game_state['fullmove_number'] += 1
    
    # Copy all bitboards
    new_pieces.W_PAWNS = pieces.W_PAWNS
    new_pieces.W_KNIGHTS = pieces.W_KNIGHTS
    new_pieces.W_BISHOPS = pieces.W_BISHOPS
    new_pieces.W_ROOKS = pieces.W_ROOKS
    new_pieces.W_QUEENS = pieces.W_QUEENS
    new_pieces.W_KING = pieces.W_KING

    new_pieces.B_PAWNS = pieces.B_PAWNS
    new_pieces.B_KNIGHTS = pieces.B_KNIGHTS
    new_pieces.B_BISHOPS = pieces.B_BISHOPS
    new_pieces.B_ROOKS = pieces.B_ROOKS
    new_pieces.B_QUEENS = pieces.B_QUEENS
    new_pieces.B_KING = pieces.B_KING
    
    # Check for captures (reset halfmove clock on capture)
    is_capture = False
    if board_utils.get_bit(pieces.ALL_PIECES, to_sq):
        is_capture = True
        new_game_state['halfmove_clock'] = 0
    
    # Find which piece is moving
    if is_white:
        # Handle white pieces
        if board_utils.get_bit(pieces.W_PAWNS, from_sq):
            # Pawn move (reset halfmove clock)
            new_game_state['halfmove_clock'] = 0
            
            # Handle pawn promotion
            if to_sq // 8 == 0:  # Reaching the 8th rank (row index 0)
                # Promote to queen by default
                new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, from_sq)
                new_pieces.W_QUEENS = board_utils.set_bit(new_pieces.W_QUEENS, to_sq)
            else:
                # Regular pawn move
                new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, from_sq)
                new_pieces.W_PAWNS = board_utils.set_bit(new_pieces.W_PAWNS, to_sq)
                
                # Check for double pawn push (set en passant target)
                if to_sq - from_sq == -16:  # Moving two squares forward (NORTH = -8 * 2)
                    new_game_state['en_passant'] = from_sq - 8
                
                # Handle en passant capture
                if game_state['en_passant'] == to_sq:
                    # Remove the captured pawn
                    new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, to_sq + 8)
            
        elif board_utils.get_bit(pieces.W_KNIGHTS, from_sq):
            new_pieces.W_KNIGHTS = board_utils.clear_bit(new_pieces.W_KNIGHTS, from_sq)
            new_pieces.W_KNIGHTS = board_utils.set_bit(new_pieces.W_KNIGHTS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.W_BISHOPS, from_sq):
            new_pieces.W_BISHOPS = board_utils.clear_bit(new_pieces.W_BISHOPS, from_sq)
            new_pieces.W_BISHOPS = board_utils.set_bit(new_pieces.W_BISHOPS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.W_ROOKS, from_sq):
            new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, from_sq)
            new_pieces.W_ROOKS = board_utils.set_bit(new_pieces.W_ROOKS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
            # Update castling rights
            if from_sq == 0:  # a1 - queenside rook
                new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('Q', '')
            elif from_sq == 7:  # h1 - kingside rook
                new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('K', '')
            
        elif board_utils.get_bit(pieces.W_QUEENS, from_sq):
            new_pieces.W_QUEENS = board_utils.clear_bit(new_pieces.W_QUEENS, from_sq)
            new_pieces.W_QUEENS = board_utils.set_bit(new_pieces.W_QUEENS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.W_KING, from_sq):
            new_pieces.W_KING = board_utils.clear_bit(new_pieces.W_KING, from_sq)
            new_pieces.W_KING = board_utils.set_bit(new_pieces.W_KING, to_sq)
            new_game_state['halfmove_clock'] += 1
            
            # Update castling rights when king moves
            new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('K', '').replace('Q', '')
            
            # Handle castling moves
            if from_sq == 4:  # e1
                if to_sq == 6:  # g1 - kingside castle
                    # Move the rook from h1 to f1
                    new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, 7)  # h1
                    new_pieces.W_ROOKS = board_utils.set_bit(new_pieces.W_ROOKS, 5)   # f1
                elif to_sq == 2:  # c1 - queenside castle
                    # Move the rook from a1 to d1
                    new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, 0)  # a1
                    new_pieces.W_ROOKS = board_utils.set_bit(new_pieces.W_ROOKS, 3)   # d1
    else:
        # Handle black pieces
        if board_utils.get_bit(pieces.B_PAWNS, from_sq):
            # Pawn move (reset halfmove clock)
            new_game_state['halfmove_clock'] = 0
            
            # Handle pawn promotion
            if to_sq // 8 == 7:  # Reaching the 1st rank (row index 7)
                # Promote to queen by default
                new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, from_sq)
                new_pieces.B_QUEENS = board_utils.set_bit(new_pieces.B_QUEENS, to_sq)
            else:
                # Regular pawn move
                new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, from_sq)
                new_pieces.B_PAWNS = board_utils.set_bit(new_pieces.B_PAWNS, to_sq)
                
                # Check for double pawn push (set en passant target)
                if to_sq - from_sq == 16:  # Moving two squares forward (SOUTH = 8 * 2)
                    new_game_state['en_passant'] = from_sq + 8
                
                # Handle en passant capture
                if game_state['en_passant'] == to_sq:
                    # Remove the captured pawn
                    new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, to_sq - 8)
                    
        elif board_utils.get_bit(pieces.B_KNIGHTS, from_sq):
            new_pieces.B_KNIGHTS = board_utils.clear_bit(new_pieces.B_KNIGHTS, from_sq)
            new_pieces.B_KNIGHTS = board_utils.set_bit(new_pieces.B_KNIGHTS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.B_BISHOPS, from_sq):
            new_pieces.B_BISHOPS = board_utils.clear_bit(new_pieces.B_BISHOPS, from_sq)
            new_pieces.B_BISHOPS = board_utils.set_bit(new_pieces.B_BISHOPS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.B_ROOKS, from_sq):
            new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, from_sq)
            new_pieces.B_ROOKS = board_utils.set_bit(new_pieces.B_ROOKS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
            # Update castling rights
            if from_sq == 56:  # a8 - queenside rook
                new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('q', '')
            elif from_sq == 63:  # h8 - kingside rook
                new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('k', '')
                
        elif board_utils.get_bit(pieces.B_QUEENS, from_sq):
            new_pieces.B_QUEENS = board_utils.clear_bit(new_pieces.B_QUEENS, from_sq)
            new_pieces.B_QUEENS = board_utils.set_bit(new_pieces.B_QUEENS, to_sq)
            new_game_state['halfmove_clock'] += 1
            
        elif board_utils.get_bit(pieces.B_KING, from_sq):
            new_pieces.B_KING = board_utils.clear_bit(new_pieces.B_KING, from_sq)
            new_pieces.B_KING = board_utils.set_bit(new_pieces.B_KING, to_sq)
            new_game_state['halfmove_clock'] += 1
            
            # Update castling rights when king moves
            new_game_state['castling_rights'] = new_game_state['castling_rights'].replace('k', '').replace('q', '')
            
            # Handle castling moves
            if from_sq == 60:  # e8
                if to_sq == 62:  # g8 - kingside castle
                    # Move the rook from h8 to f8
                    new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, 63)  # h8
                    new_pieces.B_ROOKS = board_utils.set_bit(new_pieces.B_ROOKS, 61)   # f8
                elif to_sq == 58:  # c8 - queenside castle
                    # Move the rook from a8 to d8
                    new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, 56)  # a8
                    new_pieces.B_ROOKS = board_utils.set_bit(new_pieces.B_ROOKS, 59)   # d8
    
    # Handle captures - clear any enemy piece at the target square
    if is_white:
        new_pieces.B_PAWNS = board_utils.clear_bit(new_pieces.B_PAWNS, to_sq)
        new_pieces.B_KNIGHTS = board_utils.clear_bit(new_pieces.B_KNIGHTS, to_sq)
        new_pieces.B_BISHOPS = board_utils.clear_bit(new_pieces.B_BISHOPS, to_sq)
        new_pieces.B_ROOKS = board_utils.clear_bit(new_pieces.B_ROOKS, to_sq)
        new_pieces.B_QUEENS = board_utils.clear_bit(new_pieces.B_QUEENS, to_sq)
        # Don't clear king - capturing king is illegal
    else:
        new_pieces.W_PAWNS = board_utils.clear_bit(new_pieces.W_PAWNS, to_sq)
        new_pieces.W_KNIGHTS = board_utils.clear_bit(new_pieces.W_KNIGHTS, to_sq)
        new_pieces.W_BISHOPS = board_utils.clear_bit(new_pieces.W_BISHOPS, to_sq)
        new_pieces.W_ROOKS = board_utils.clear_bit(new_pieces.W_ROOKS, to_sq)
        new_pieces.W_QUEENS = board_utils.clear_bit(new_pieces.W_QUEENS, to_sq)
        # Don't clear king - capturing king is illegal
    
    # Update combined bitboards
    new_pieces.W_PIECES = (new_pieces.W_PAWNS | new_pieces.W_KNIGHTS | new_pieces.W_BISHOPS | 
                          new_pieces.W_ROOKS | new_pieces.W_QUEENS | new_pieces.W_KING)
    new_pieces.B_PIECES = (new_pieces.B_PAWNS | new_pieces.B_KNIGHTS | new_pieces.B_BISHOPS | 
                          new_pieces.B_ROOKS | new_pieces.B_QUEENS | new_pieces.B_KING)
    new_pieces.ALL_PIECES = new_pieces.W_PIECES | new_pieces.B_PIECES
    
    return new_pieces, new_game_state

def get_piece_scores(piece_bitboard: int, piece_type: str, is_white: bool) -> Tuple[int, int]:
    """Get combined piece value and square table scores for middlegame/endgame."""
    mg_score = eg_score = 0
    board = piece_bitboard
    
    # Define piece square tables mapping
    TABLES = {
        'P': (MG_PAWN_TABLE, EG_PAWN_TABLE),
        'N': (MG_KNIGHT_TABLE, EG_KNIGHT_TABLE),
        'B': (MG_BISHOP_TABLE, EG_BISHOP_TABLE),
        'R': (MG_ROOK_TABLE, EG_ROOK_TABLE),
        'Q': (MG_QUEEN_TABLE, EG_QUEEN_TABLE),
        'K': (MG_KING_TABLE, EG_KING_TABLE)
    }

    while board:
        square = board_utils.lsb(board)
        board = board_utils.clear_bit(board, square)
        
        # Mirror square for black pieces
        eval_square = square if is_white else board_utils.mirror_square(square)
        
        # Get piece values and square table bonuses
        mg_score += PIECE_VALUES_MG[PIECES[piece_type]]
        eg_score += PIECE_VALUES_EG[PIECES[piece_type]]
        
        # Get piece square table values
        mg_table, eg_table = TABLES[piece_type.upper()]
        mg_score += mg_table[eval_square]
        eg_score += eg_table[eval_square]
    
    # Negate scores for black pieces (return values from white's perspective)
    if not is_white:
        mg_score = -mg_score
        eg_score = -eg_score
    
    return mg_score, eg_score

# Initialize attack tables - call once at startup
board_utils.initialize_attack_tables()

