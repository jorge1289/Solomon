// Initialize the chess game
var game = new Chess();
var $status = $('#status');
var $gameOver = $('#game-over');

// Configure the board with piece theme
var config = {
    position: 'start',
    draggable: true,
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
    onDrop: handleMove
};

// Initialize the board with the config
var board = Chessboard('board', config);

// Handle piece movement
function handleMove(source, target) {
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

// Your engine logic will go here
function makeEngineMove() {
    // This is where you'll implement your chess engine logic
    // For now, just make a random legal move
    var moves = game.moves();
    
    if (moves.length > 0) {
        var randomIdx = Math.floor(Math.random() * moves.length);
        var move = moves[randomIdx];
        game.move(move);
        board.position(game.fen());
        updateStatus();
    }
}

// Play Again button handler
$('#playAgain').on('click', function() {
    game.reset();
    board.start();
    $gameOver.fadeOut();
    updateStatus();
});

// Make the board responsive
$(window).resize(board.resize);

// Initialize status
updateStatus();