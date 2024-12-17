// Initialize the chess game
var game = new Chess();
var $status = $('#status');
var $gameOver = $('#game-over');
var playerColor = 'w';
var $engineStatus = $('#engine-status');
const API_URL = 'http://localhost:5001';
// Configure the board with piece theme
var config = {
    position: 'start',
    draggable: true,
    orientation: 'white',
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
    onDrop: handleMove
};

// Initialize the board with the config
var board = Chessboard('board', config);

// Handle piece movement
function handleMove(source, target) {
    // Only allow moves if it's player's turn
    if ((game.turn() === 'w' && playerColor === 'b') ||
        (game.turn() === 'b' && playerColor === 'w')) {
        return 'snapback';
    }

    // Try to make the move
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // Always promote to queen for simplicity
    });

    // If illegal move, snap back
    if (move === null) return 'snapback';

    updateStatus();

    // After player moves, call your engine
    if (!game.game_over()) {
        window.setTimeout(makeEngineMove, 250);
    }
}

// Update game status
function updateStatus() {
    removeHighlights();
    
    let status = '';
    let moveColor = game.turn() === 'b' ? 'Black' : 'White';

    // Checkmate?
    if (game.in_checkmate()) {
        status = `Game over, ${moveColor} is in checkmate.`;
        showGameOver(`${moveColor} is in checkmate!`);
    }
    // Draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position';
        showGameOver('Game drawn!');
    }
    // Game still on
    else {
        status = `${moveColor} to move`;
        // Check?
        if (game.in_check()) {
            status += `, ${moveColor} is in check`;
            highlightCheck();
        }
    }

    $status.html(status);
}

// Highlight king in check
function highlightCheck() {
    removeHighlights();
    
    // Find the king
    const color = game.turn();
    const pieces = game.board();
    let kingPosition = null;

    for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
            const piece = pieces[i][j];
            if (piece && piece.type === 'k' && piece.color === color) {
                kingPosition = {row: i, col: j};
                break;
            }
        }
        if (kingPosition) break;
    }

    if (kingPosition) {
        const square = String.fromCharCode(97 + kingPosition.col) + (8 - kingPosition.row);
        $(`#board .square-${square}`).addClass('in-check');
    }
}

// Remove all highlights
function removeHighlights() {
    $('#board .square-55d63').removeClass('in-check');
}

// Show game over overlay
function showGameOver(message) {
    $gameOver.html(`
        <h2>${message}</h2>
        <p>Click "Play Again" to start a new game</p>
    `).fadeIn();
}

// Add this function
function updateEngineStatus(isThinking) {
    if (isThinking) {
        $engineStatus.html('Engine is thinking...').show();
    } else {
        $engineStatus.hide();
    }
}
class ChessEngineInterface {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.isThinking = false;
    }
    
    async makeMove(game, depth = 3) {
        if (this.isThinking) return null;
        
        try {
            this.isThinking = true;
            const positions = this._generatePositions(game, depth);
            
            console.log('Generated positions:', positions); // Debug log
            
            const response = await fetch(`${this.apiUrl}/api/get-move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ positions, depth })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', response.status, errorText);
                throw new Error(`Engine API error: ${errorText}`);
            }
            
            const result = await response.json();
            console.log('Received result:', result);
            
            if (!result.move) throw new Error('No move returned');
            
            return result;
            
        } catch (error) {
            console.error('Engine error:', error);
            return this._makeRandomMove(game);
        } finally {
            this.isThinking = false;
        }
    }
    
    _generatePositions(game, depth) {
        const positions = [];
        
        try {
            const moves = game.moves({ verbose: true });
            console.log(`Generating positions for ${moves.length} possible moves`);
            
            for (const move of moves) {
                game.move(move);
                
                const position = {
                    move: move.from + move.to + (move.promotion || ''),
                    fen: game.fen()
                };
                positions.push(position);
                
                game.undo();
            }
            
            console.log(`Generated ${positions.length} positions`);
            return positions;
            
        } catch (error) {
            console.error('Error generating positions:', error);
            return positions;
        }
    }

    _makeRandomMove(game) {
        const moves = game.moves();
        if (moves.length === 0) return null;
        
        const move = moves[Math.floor(Math.random() * moves.length)];
        return { move, score: 0, nodes: 1 };
    }
}

// Usage in your game code
const engine = new ChessEngineInterface(API_URL);

async function makeEngineMove() {
    // Debug logging
    console.log('Turn:', game.turn(), 'Player Color:', playerColor);
    
    if ((game.turn() === 'w' && playerColor === 'w') ||
        (game.turn() === 'b' && playerColor === 'b')) {
        console.log('Not engine turn, returning');
        return;
    }

    updateEngineStatus(true);
    
    try {
        const result = await engine.makeMove(game, 3);
        console.log('Engine returned move:', result);
        
        if (result && result.move) {
            // Convert the move string to an object
            const move = {
                from: result.move.substring(0, 2),
                to: result.move.substring(2, 4),
                promotion: result.move.length > 4 ? result.move.substring(4, 5) : undefined
            };
            
            console.log('Attempting move:', move);
            
            // Try to make the move
            const madeMove = game.move(move);
            console.log('Move result:', madeMove);
            
            if (madeMove) {
                board.position(game.fen());
                updateStatus();
                console.log(`Engine moved: ${result.move}, evaluated ${result.nodes} positions, score: ${result.score}`);
            } else {
                console.error('Invalid move:', move);
            }
        }
    } catch (error) {
        console.error('Error making engine move:', error);
    } finally {
        updateEngineStatus(false);
    }
}

// Start new game
function startNewGame() {
    game.reset();
    board.start();
    $gameOver.fadeOut();
    
    // If playing as black, make engine move first
    if (playerColor === 'b') {
        makeEngineMove();
    }
    
    updateStatus();
}

// Color selection handlers
$('#playAsWhite').on('click', function() {
    playerColor = 'w';
    board.orientation('white');
    $('.color-btn').removeClass('active');
    $(this).addClass('active');
    startNewGame();
});

$('#playAsBlack').on('click', function() {
    playerColor = 'b';
    board.orientation('black');
    $('.color-btn').removeClass('active');
    $(this).addClass('active');
    startNewGame();
});

// Play Again button handler
$('#playAgain').on('click', startNewGame);

// Make the board responsive
$(window).resize(board.resize);

// Initialize status
updateStatus();