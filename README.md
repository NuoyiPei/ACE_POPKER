# ACE Poker - Texas Hold'em AI Trainer

A professional Texas Hold'em poker simulator designed to help players train against AI opponents and practice Game Theory Optimal (GTO) strategies.

## Features

- Complete Texas Hold'em Game Flow
  - Pre-flop, flop, turn, and river betting rounds
  - Blinds and position-based play
  - Full hand evaluation and showdown

- Advanced AI Opponents
  - GTO-based decision making
  - Position-aware strategy
  - Learning from historical hands
  - Multi-position simulation
  - Machine Learning integration
    - Random Forest for action prediction
    - Feature-based decision making
    - Automatic strategy adaptation

- Real-time Analysis
  - Monte Carlo win probability calculation
  - Pot odds analysis
  - Expected Value (EV) computation
  - Implied odds calculation
  - GTO action recommendations

- Hand Review System
  - Detailed hand history
  - Action-by-action analysis
  - Position-based strategy review
  - Learning recommendations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ACE_Poker.git
cd ACE_Poker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface
```bash
python main_cli.py
```

### Game Rules
- Starting stack: $1000 per player
- Small blind: $10
- Big blind: $20
- Standard Texas Hold'em rules apply

## Project Structure

```
ACE_Poker/
├── main_cli.py        # Command-line interface
├── gui.py             # Graphical UI (in development)
├── cards.py           # Card system and definitions
├── game.py            # Core game logic
├── montecarlo.py      # Win probability simulations
├── ai.py              # AI strategy implementation
├── handrecord.py      # Hand history records
├── ml/                # Machine Learning module
│   ├── features.py    # Feature extraction
│   ├── trainer.py     # Model training
│   └── model.pkl      # Trained model
├── utils.py           # Utility functions
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation
```

## Development Roadmap

### Phase 1: Core Game (Completed)
- [x] Basic game logic
- [x] Card system
- [x] Hand evaluation
- [x] Command-line interface

### Phase 2: AI Enhancement (In Progress)
- [x] Monte Carlo simulation
- [x] GTO strategy implementation
- [x] Position-based play
- [x] Machine Learning integration
- [ ] Advanced hand reading
- [ ] Range analysis

### Phase 3: UI/UX (Planned)
- [ ] Graphical interface
- [ ] Hand history visualization
- [ ] Real-time statistics
- [ ] Interactive tutorials

### Phase 4: Analytics (Planned)
- [ ] Session statistics
- [ ] Leak detection
- [ ] Performance tracking
- [ ] Custom reports

## Contributing

We welcome contributions! Please feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Share your ideas for improvements
- Help with documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by professional poker training tools
- Built with Python 3.8+
- Uses Monte Carlo simulation for probability calculations

## Support

For support, please:
- Open an issue on GitHub
- Join our Discord community
- Contact the maintainers

---

Made with ❤️ by PEI & YANG