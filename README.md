# Solomon

# Chess Engine Project

A chess engine implementation using chess.js and chessboard.js. This project aims to create a chess AI that can play against human players.

## 🚀 Features

- Interactive chess board interface
- Legal move validation
- Position evaluation engine
- Responsive design
- Python Flask backend for chess engine calculations
- Move analysis and scoring

## 📋 Prerequisites

### Frontend Dependencies (CDN-hosted):
- chess.js
- chessboard.js
- jQuery

### Backend Dependencies:
- Python 3.7+
- Flask
- Flask-CORS

## 🎮 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/jorge1289/Solomon
   cd Solomon
   ```

2. Set up the Python environment:
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate

   # Install dependencies
   pip install flask flask-cors
   ```

3. Start the Flask server:
   ```bash
   # Make sure you're in the project root directory
   python app.py
   ```
   The engine will run on `http://localhost:5001`

4. Start the frontend server:
   Using Python:
   ```bash
   python -m http.server
   ```
   Then visit `http://localhost:8000`

   If you have Node.js installed:
   ```bash
   npm install -g serve
   serve
   ```
   Open your browser to the URL it provides


=======
      Install a simple server: npm install -g serve
      Navigate to your project folder
      Run: serve
      Open your browser to the URL it provides

## 🏗️ Project Structure

```
Solomon/
├── app.py              # Flask server
├── engine/
│   ├── __init__.py
│   ├── evaluation.py   # Chess position evaluation
│   ├── constants.py    # Chess piece values and tables
│   └── board_utils.py  # Board manipulation utilities
├── static/
│   ├── js/
│   │   ├── game.js    # Game logic
│   └── css/
│       └── style.css
└── index.html
```

## 🛠️ Development Roadmap

- [x] Basic board setup and move validation
- [x] Flask backend integration
- [x] Position evaluation function
- [x] Minimax algorithm implementation
- [ ] Alpha-beta pruning optimization
- [ ] Opening book integration
- [ ] Endgame tablebase integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project makes use of the following open-source libraries:

- [chess.js](https://github.com/jhlywa/chess.js) - Chess logic implementation
- [chessboard.js](https://chessboardjs.com/) - Chessboard UI
- [jQuery](https://jquery.com/) - Required by chessboard.js
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Flask-CORS](https://flask-cors.readthedocs.io/) - Cross-Origin Resource Sharing for Flask

## 📧 Contact


Jorge Emanuel Nunez - [jorge1289@berkeley.edu](mailto:jorge1289@berkeley.edu)

Project Link: [https://github.com/jorge1289/Solomon](https://github.com/jorge1289/Solomon)

