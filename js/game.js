// Initialize the chess game
var game = new Chess();
var $status = $('#status');
var $gameOver = $('#game-over');
var playerColor = 'w';
var $engineStatus = $('#engine-status');
const API_URL = 'http://localhost:5001';
var currentGameState = game.fen();

// Configure the board with piece theme
var config = {
    position: 'start',
    draggable: true,
    orientation: 'white',
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
    onDrop: handleMove,
    onDragStart: selectedHighlight 
};

// Initialize the board with the config
var board = Chessboard('board', config);

function selectedHighlight(source, piece) {
    // Clear previous highlights
    removeHighlights();

    // Prevent highlighting for opponent's pieces
    if ((game.turn() === 'w' && piece.startsWith('b')) ||
        (game.turn() === 'b' && piece.startsWith('w'))) {
        return false;
    }
    
    // Get valid moves
    var validMoves = game.moves({ square: source, verbose: true });
    
    // Apply highlights
    validMoves.forEach((move) => {
        const $square = $(`#board .square-${move.to}`);
        $square.addClass('highlight');
        
        // Add special class for squares with pieces
        if (move.captured || game.get(move.to)) {
            $square.addClass('has-piece');
        }
    });
}

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
    $('#board .square-55d63').removeClass('highlight');
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

/**
 * @description
 * Makes a move for the engine only on its turn.
 * The engine will use the given engine.
 * 
 * This function checks if it is engine's turn based on the current turn and the player's color.
 * If it's the engine's turn, it determines the best move using an evaluation function.
 * Then, it calls the `updateStatus` function, updating the board position and game status.
 * 
 * @function
 * @returns {void} This function does not return a value; it updates the user interface as a side-effect
 * @see {@link updateStatus}()
*/
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
                showHistory();
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
    $('#history').empty();
    $gameOver.fadeOut();
    
    // If playing as black, make engine move first
    if (playerColor === 'b') {
        makeEngineMove();
    }

    updateStatus();
    showHistory();

}

// Show move history
function showHistory() {
    let autoScroll = true;
    const history = game.history();
    const $history = $('#history');
    $history.empty();

    // Show each move on the history panel
    history.forEach((move, index) => {
        const $move = $(`<div class="move">${index + 1}. ${move}</div>`);

        if (index === history.length - 1) {
            $move.addClass('current-move');
        }

        $move.on('click', function() {
            showMove(index);
        });
        
        $history.append($move);
    });

    // Scroll to the last move
    if (autoScroll) {
        const lastMove = $history.children().last()[0];
        if (lastMove) {
            lastMove.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }

}

// Change board state at specific move
function showMove(index) {
    const history = game.history({ verbose: true });
    const tempGame = new Chess();

    for (let i = 0; i <= index; i++) {
        tempGame.move(history[i]);
    }

    board.position(tempGame.fen());
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