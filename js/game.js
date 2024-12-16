// Initialize the chess game
var game = new Chess();
var $status = $('#status');
var $gameOver = $('#game-over');
var playerColor = 'w';

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

/**
 * @param {string} source The source square of the move in algebraic notation
 * @param {string} target The target square of the move in algebraic notation
 * @returns {string} Returns 'snapback' if the move is illegal; otherwise, it returns `undefined`
 *
 * @description
 * Ensures only the correct player can make a move.
 * 
 * If the move is legal, it attempts to make the move and updates the game state. Otherwise,
 * it triggers a snapback, and the move is not made. 
 * 
 * After the player move, if the game isn't over, it triggers
 * the engine to make its move after a short delay.
 * 
 * @see {@link https://github.com/jhlywa/chess.js/blob/master/README.md#api} <br>
 * @see {@link https://chessboardjs.com/examples#5000}
*/
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

/**
 * @description
 * Updates the game status and displays it on the user interface.
 * 
 * This function checks the current state of the game using the `Chess.js` library
 * and updates the status message accordingly. It handles check, checkmate, draw and the player's turn circumstances
 * and displays it within a HTML element with the ID `$status`.
 * 
 * - If it is checkmate, it shows a "Game over" message and calls `showGameOver` function
 * - Else, if the game is drawn, it shows a "Game drawn!" message and calls `showGameOver` function
 * - If the game is still ongoing, it indicates which player's turn it is to move, 
 *   and highlights if the player is in check using `highlightCheck`.
 * 
 * @function
 * @returns {void} This function does not return any value; it only updates the UI directly.
 * @see {@link handleMove}()
 */
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

/**
 * @description
 * Highlights the king in check
 * 
 * This function searches the right color king's board position,
 * highlighting it appropriately only on its turn.
 * 
 * @function
 * @returns {void} This function does not return anything; it only updates the UI.
 * @see {@link updateStatus}()
 */

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

/**
 * @description
 * Removes the `in-check` king highlight accordingly to game status.
 * 
 * @function
 * @returns {void} This function does not return anything; it only updates the user interface based on game status.
 * @see {@link updateStatus}()
*/
function removeHighlights() {
    $('#board .square-55d63').removeClass('in-check');
}

/**
 * @param {string} message 
 * 
 * @description
 * Displays a message on the user interface — whether it is checkmate or a draw.
 * 
 * @see {@link updateStatus}
 */
function showGameOver(message) {
    $gameOver.html(`
        <h2>${message}</h2>
        <p>Click "Play Again" to start a new game</p>
    `).fadeIn();
}

/**
 * @description
 * Makes a move for the engine only on its turn.
 * The engine will randomly select one of the available move and apply it to the game.
 * 
 * This function checks if it is engine's turn based on the current turn and the player's color.
 * If it's the engine's turn, it selects a random move from the list of valid moves and executes it.
 * Then, it calls the `updateStatus` function, updating the board position and game status.
 * 
 * @function
 * @returns {void} This function does not return a value; it updates the user interface as a side-effect
 * @see {@link updateStatus}()
*/

function makeEngineMove() {
    // Only make move if it's engine's turn
    if ((game.turn() === 'w' && playerColor === 'w') ||
        (game.turn() === 'b' && playerColor === 'b')) {
        return;
    }

    var moves = game.moves();
    
    if (moves.length > 0) {
        var randomIdx = Math.floor(Math.random() * moves.length);
        var move = moves[randomIdx];
        game.move(move);
        board.position(game.fen());
        updateStatus();
    }
}

/**
 * @description
 * Starts a new game.
 * This function resets the board to its initial position and
 * checks the player's turn based on the user's color choice,
 * calling the `updateStatus` function to track game status.
 * 
 * @function
 * @returns This function does not return anything.
 * 
 * @see {@link showGameOver}()
 * @see {@link updateStatus}()
 * 
*/
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
    /**
    * @description
    * Set up and starts the game for user as white.
    * This function sets the player color and orientation to match the user choice (based on the button click),
    * and switches the `active` class to match the user's color choice.
    * 
    * @param {Event} onclick
    * @returns {void} 
   */

    playerColor = 'w';
    board.orientation('white');
    $('.color-btn').removeClass('active');
    $(this).addClass('active');
    startNewGame();
});


$('#playAsBlack').on('click', function() {
  /**
    * @description
    * Sets up and starts the game for user as black.
    * This function sets the player color and orientation to match the user choice (based on the button click),
    * and switches the `active` class to match the user's color choice.
    * 
    * @param {Event} onclick
    * @returns {void} 
   */
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