# Chess Game

A GUI-based chess game for two players, built with Python and PyQt5.  
The game supports saving and reviewing previous games using CSV files and a SQLite database.

---

## Features

- Local 2-player chess game
- Save game progress and moves automatically in CSV files
- Load and review past games from a list
- Full-screen chessboard with interactive piece selection
- Visual highlights for active pieces and possible moves
- Track game state and move history
- Surrender or end the game at any time
- Supports pawn promotion and castling
- Side table displays moves in standard chess notation

---

## Usage

Run the game by executing the main program file.

### Main Menu

- **Play Chess (2-player):** Start a new game
- **Select a Game:** Load a previously saved game
- **Close Game:** Exit the program

### Starting a New Game

- Enter a name for the game (4–40 characters)  
  (if the name already exists, a new unique name will be assigned)
- The chessboard will appear in full screen
- Click on a piece to select it, then click the destination square to make a move
- Moves are automatically tracked and displayed in the side table

### Viewing Past Games

- Select a saved game from the list
- View moves and board positions step by step
- Option to delete a game from the database and CSV files

### Ending a Game

- Players can surrender at any time
- The game is automatically saved in CSV and recorded in the database

---

## Project Structure

- main.py — Main program entry point
- chess.py — Chess game logic and rules
- viewing.py — GUI dialogs and menus using PyQt5
- img/chess/ — Images for chess pieces
- data.db — SQLite database for storing game information
- CSV files — Saved games with move history

---

## Requirements

- Python 3.7+
- PyQt5
- chess (Python library)
- SQLite3

---

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)
