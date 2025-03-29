# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
from engine.evaluation import ChessEvaluator

app = Flask(__name__)

# Configure CORS
cors = CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins
        "methods": ["POST", "GET", "OPTIONS"],  # Allow these methods
        "allow_headers": ["Content-Type"]  # Allow these headers
    }
})

print("\n\n=== STARTING SERVER WITH NEW CODE - FEN-BASED ENGINE ===\n\n")
# Initialize the chess evaluator
evaluator = ChessEvaluator()

@app.route('/api/get-move', methods=['POST'])
def get_move():
    """Endpoint for getting the best move from a position."""
    try:
        # Log incoming request
        print(f"Received request at {request.path}")
        
        # Validate request Content-Type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        # Get and validate request data
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({'error': 'Empty request body'}), 400
            
        # Check if using the new method (FEN) or old method (positions array)
        if 'fen' in data:
            # New method: evaluate a single position
            fen = data['fen']
            if not fen:
                return jsonify({'error': 'Empty FEN position'}), 400
            
            depth = data.get('depth', 4)
            # Limit max depth to 6 for reasonable response times
            depth = min(depth, 6)
            
            print(f"Evaluating position at depth {depth}: {fen}")
            result = evaluator.get_best_move(fen, depth)
            print(f"Engine result: {result}")
            
            return jsonify(result)
        
        elif 'positions' in data:
            # Legacy method: evaluate a list of positions
            positions = data['positions']
            if not positions or not isinstance(positions, list):
                return jsonify({'error': 'Invalid positions format'}), 400
            
            # Validate each position has required fields
            for pos in positions:
                if not isinstance(pos, dict):
                    return jsonify({'error': 'Each position must be an object'}), 400
                if 'fen' not in pos:
                    return jsonify({'error': 'Missing FEN in position'}), 400
                if 'move' not in pos:
                    return jsonify({'error': 'Missing move in position'}), 400
            
            depth = data.get('depth', 4)
            # Limit max depth to 6 for reasonable response times
            depth = min(depth, 6)
            
            print(f"Processing {len(positions)} positions at depth {depth}")
            print(f"Note: Using legacy method. Consider switching to the new API.")
            result = evaluator.get_best_move(positions, depth)
            print(f"Engine result: {result}")
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Missing position data. Provide either "fen" or "positions" field.'}), 400
        
    except Exception as e:
        print("Error processing request:")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_position():
    """Endpoint for evaluating a single position."""
    try:
        print("Received request at /api/evaluate")
        data = request.json
        
        if not data or 'fen' not in data:
            return jsonify({'error': 'No FEN position provided'}), 400
            
        fen = data['fen']
        score = evaluator.evaluate_fen(fen)
        
        return jsonify({
            'score': score,
            'fen': fen
        })
        
    except Exception as e:
        print("Error in /api/evaluate:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Starting server on port {port}")
    print("CORS enabled for /api/* endpoints")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )