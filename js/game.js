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

// Make engine move
async function makeEngineMove() {
    // Only make move if it's engine's turn
    if ((game.turn() === 'w' && playerColor === 'w') ||
        (game.turn() === 'b' && playerColor === 'b')) {
        return;
    }

    updateEngineStatus(true);
    try {
        // Generate all possible positions for each legal move
        const positions = generatePositions(game, 3); // depth = 3

        const response = await fetch(`${API_URL}/api/get-move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                positions: positions,
                depth: 3
            })
        });
        
        const { move, score, nodes } = await response.json();
        
        if (move) {
            game.move(move);
            board.position(game.fen());
            updateStatus();
            console.log(`Evaluated ${nodes} positions, best move score: ${score}`);
        }

    } catch (error) {
        console.error('Error in engine move:', error);
        // Fallback to random move if evaluation fails
        var moves = game.moves();
        if (moves.length > 0) {
            const randomMove = moves[Math.floor(Math.random() * moves.length)];
            game.move(randomMove);
            board.position(game.fen());
            updateStatus();
        }
    } finally {
        updateEngineStatus(false);
    }
}

function generatePositions(game, depth) {
    if (depth === 0) {
        return [{
            move: '',
            fen: game.fen()
        }];
    }

    const positions = [];
    const moves = game.moves({ verbose: true });

    for (const move of moves) {
        // Make the move
        game.move(move);
        
        // Store the position
        positions.push({
            move: move.from + move.to + (move.promotion || ''),
            fen: game.fen()
        });

        if (depth > 1 && !game.game_over()) {
            // Recursively get positions for subsequent moves
            const childPositions = generatePositions(game, depth - 1);
            positions.push(...childPositions);
        }

        // Undo the move
        game.undo();
    }

    return positions;
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