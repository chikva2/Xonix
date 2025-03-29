# Xonix Game

A Python implementation of the classic Xonix arcade game, featuring both classic and modern visual styles, and multiple difficulty levels.

![Xonix Game Screenshot](https://github.com/yourusername/xonix-game/raw/main/screenshots/xonix_preview.png)

## About the Game

Xonix is a classic arcade game where players control a character that can move across different surfaces. The objective is to claim territory by drawing lines through unclaimed areas and returning to already claimed territory. Players must avoid enemies while doing so, as collisions will cost lives.

### Game Features:

- **Multiple Game Modes**:
  - **Classic View**: Retro geometric shapes with simple colors
  - **Modern View**: Enhanced visuals with character sprites
- **Difficulty Options**:
  - **Small Mode**: Easier gameplay with a smaller grid
  - **Big Mode**: More challenging gameplay with a larger grid
- **Progressive Challenge**:
  - Increasing difficulty with each level
  - More enemies appear as you advance
- **Scoring System**:
  - Points for each area you claim
  - Track your high scores between games

## Installation

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/xonix-game.git
   cd xonix-game
   ```

2. Install required dependencies:
   ```bash
   pip install pygame
   ```

3. Launch the game:
   ```bash
   python xonix_main_menu.py
   ```

## How to Play

1. **Controls**:
   - Use arrow keys to move your character
   - Draw lines by moving into unclaimed territory
   - Return to claimed territory to fill the enclosed area

2. **Objective**:
   - Fill at least 75% of the screen to advance to the next level
   - Avoid enemies and your own trail
   - Complete as many levels as possible before running out of lives

3. **Scoring**:
   - Points are awarded based on the area you fill
   - Completing levels grants bonus points
   - The faster you fill areas, the higher your score

## Game Files

- **xonix_main_menu.py**: Game launcher with configuration options
- **xonix_gui.py**: GUI implementation and game rendering
- **xonix_logic.py**: Core game mechanics and logic

## Customization

To add custom sprites for the modern view, place the following image files in the game directory:
- `rabbit.png`: Player character
- `crocodile.png`: Water enemy
- `wolf.png`: Land enemy
- `water.png`: Water background
- `sand.png`: Filled area texture

The game will automatically detect and use these images if they're present.

## Development

This game was developed using Pygame, a cross-platform set of Python modules designed for writing video games. The architecture follows a separation of concerns:

- **Logic**: Game state, collision detection, and scoring
- **GUI**: Rendering, animations, and visual effects
- **Main Menu**: Configuration and game launching

## Contributing

Contributions are welcome! If you'd like to improve the game, please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Xonix game concept by Ilan Rav and Dani Katz
- Pygame community for their excellent documentation and examples
