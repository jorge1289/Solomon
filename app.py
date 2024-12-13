from flask import Flask, request, jsonify
from flask_cors import CORS  # We need this for cross-origin requests
import os
from engine.evaluation import ChessEvaluator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the chess evaluator
evaluator = ChessEvaluator()

@app.route('/api/evaluate', methods=['POST'])
def evaluate_position():
    try:
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5001))
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Makes the server externally visible
        port=port,
        debug=True  # Set to False in production
    )