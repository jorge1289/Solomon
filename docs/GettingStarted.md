# Chess Game Project Documentation

This repository provides a chess game implementation using ``` chess.js ``` and ``` chessboard.js``` 
Below is a structured overview of the key functions and their usage, as if they were API endpoints.

## Table of Contents

  - [Start New Game](#StartNewGame)
  - [Handle Player Move](#HandlePlayerMove)
  - [Get Game Status](#GetGameStatus)
  - [Engine Move](#EngineMove)
  - [Highlight Check](#HighlightCheck)
  - [Remove Highlights](#RemoveHighlights)
  - [Show Game Over](#ShowGameOver)
  - [Color Selection](#ColorSelection)
  - [Resize Board](#ResizeBoard)
  - [Libraries Used](#LibrariesUsed)

# Start New Game

### Function: startNewGame()
Resets the game board and initializes a new game.
If the user selects Black, the engine makes the first move.
### Usage:
```js
startNewGame();
```

### Effect:
Resets the board to the starting position.
Updates the game status.

# Handle Player Move

### Function: handleMove(source, target)
Processes a player's move and updates the game state.
### Parameters:
source (string): Starting square of the move (e.g., "e2").
target (string): Ending square of the move (e.g., "e4").
### Usage:
```js
handleMove("e2", "e4");
```

### Effect:
Updates the board if the move is valid.
Snaps the piece back to its original position if the move is invalid.
Calls the engine's move function if applicable.

# Get Game Status

### Function: updateStatus()
Displays the current status of the game.
### Usage:
```js
updateStatus();
```

### Effect:
Indicates whose turn it is.
Notifies if the game is in check, checkmate, or drawn.

# Engine Move
### Function: makeEngineMove()
Generates a random valid move for the engine.
### Usage:
```js 
makeEngineMove();
 ```

### Effect:
Updates the board state.
Displays the new game status.

# Highlight Check
### Function: highlightCheck()
Highlights the king's square if it is in check.
### Usage:
```js
highlightCheck();
 ```

### Effect:
Visually indicates that the king is in check.

# Remove Highlights
### Function: removeHighlights()
Clears all visual highlights on the board.
### Usage:
```js
 removeHighlights();
```

### Effect:
Removes square highlights.
# Show Game Over

Function: showGameOver(message)
Displays a message when the game ends.
### Parameters:
message (string): Game outcome message (e.g., "White is in checkmate!").
### Usage:
```js
showGameOver("White is in checkmate!"); 
```

### Effect:
Shows a game-over overlay with the provided message.

# Color Selection
### Functions:
```jQuery
$('#playAsWhite').on('click', ...) 
$('#playAsBlack').on('click', ...)
 ```

Allows the player to choose their color and resets the game.
### Usage:
```jQuery
$('#playAsWhite').click();
$('#playAsBlack').click();
 ```
### Effect:
Sets the player color.
Resets the game board.

# Resize Board
### Function: $(window).resize(board.resize)
Makes the chessboard responsive to window resizing.
### Usage:
```js
$(window).resize(board.resize);
 ```
### Effect:
Dynamically adjusts the board size.

# Libraries Used
[chess.js](#chess.js): Provides game logic and move validation.
[chessboard.js](#chessboard.js): Handles board rendering and piece interaction.
All interactions occur locally in the browser, with no server-side dependencies. This structure can be adapted for server-based implementations if needed.
