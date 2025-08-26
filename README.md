# Beacon Patrol Board Scorer

An automated computer vision application that analyzes photos of completed [Beacon Patrol](https://beaconpatrol.com/) board games and calculates scores according to the official rules.

## Overview

Beacon Patrol is a cooperative tile-laying game where players explore ocean waters by placing tiles adjacent to their ships. At the end of the game, players score points for "explored" tiles (those surrounded on all four sides), with bonus points for lighthouses and buoys.

This application automates the end-game scoring process using:
- **Computer vision** to analyze board photos and detect game elements
- **Template matching** to identify orientation arrows and scored objects (lighthouses/buoys)
- **Grid estimation** to determine tile positions and find fully surrounded tiles
- **Web interface** for easy photo upload and result display

## Features

### ✅ Currently Working
- **Web interface** with drag-and-drop photo upload
- **Board validation** - rejects photos that aren't Beacon Patrol boards
- **Arrow orientation detection** - identifies incorrectly rotated tiles
- **Tile boundary detection** using arrow positions as reference points
- **Object recognition** - distinguishes between lighthouses (3 pts), buoys (2 pts), and empty water (1 pt)
- **Automatic scoring** with official rank calculation
- **Visual feedback** - annotated images showing detected tiles and objects

### 🚧 In Development
- **Complex board handling** - improving accuracy on larger, more intricate layouts
- **Enhanced arrow detection** - reducing false positives on boards with 15+ tiles
- **Scoring refinements** - debugging edge cases in object detection

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
*Note: Developed and tested on macOS. Should work on other platforms but not tested.*

1. Clone the repository:
   ```bash
   git clone https://github.com/scarerkite/beacon-patrol-scorer.git
   cd beacon-patrol-scorer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify installation:
   ```bash
   pytest tests/ -v
   ```

## Usage

### Running the Web Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000` (you can also try `http://localhost:5000`)

#### Photo Requirements
For best results, ensure your photos have:
- **All orientation arrows pointing the same direction** (preferably up)
- **Good lighting** with minimal shadows
- **Clear tile boundaries** - avoid blurry or angled shots
- **Complete board visibility** - all tiles should be in frame

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_app.py -v
```

### Debugging Tools
The project includes debugging utilities for development:

```bash
# Debug the complete scoring pipeline
python debug_scoring.py

# Visualize tile boundary detection
python tile_analyzer.py

# Test arrow detection on specific images
python arrow_detection.py
```

Some debugging functions can generate annotated images showing detected features - check for output files in the project directory.

## Architecture

### Key Components

- **`app.py`** - Flask web application and main entry point
- **`board_analyzer.py`** - Main analysis pipeline coordinating all validation steps
- **`arrow_detection.py`** - Template matching for orientation arrow validation
- **`tile_analyzer.py`** - Tile boundary detection and adjacency analysis
- **`scored_objects_detector.py`** - Object recognition and final score calculation
- **`debug_scoring.py`** - Development debugging utilities

### Analysis Pipeline

1. **Basic Validation** - Image size and color analysis
2. **Arrow Detection** - Template matching to find and validate tile orientations
3. **Tile Grid Estimation** - Use arrow positions to calculate tile boundaries
4. **Adjacency Analysis** - Determine which tiles are fully surrounded
5. **Object Recognition** - Identify lighthouses, buoys, and empty tiles using template matching and color analysis
6. **Score Calculation** - Apply official Beacon Patrol scoring rules

### Technical Approach

- **OpenCV** for image processing and computer vision operations
- **Template matching** with multiple templates to handle different tile appearances
- **Color space analysis** (HSV) to distinguish water from land tiles
- **Geometric algorithms** for tile adjacency detection
- **Flask** web framework with drag-and-drop file upload

## Development Process

You can read about the development journey in my blog series:

- [Building a Beacon Patrol Scorer pt. 1: Basic setup with flask](https://sarahcknight.co.uk/posts/beacon-patrol-scorer-part1/) - Basic web application and image validation
- [Building a Beacon Patrol Scorer pt. 2: Identifying tile orientation with Computer Vision](https://sarahcknight.co.uk/posts/beacon-patrol-scorer-part2/) - Initial tile boundary detection attempts  

More to come!

## Current Limitations

- **Complex boards**: Accuracy may decrease on very large or intricate tile arrangements
- **Base game only**: Expansion tiles (windmills, piers) not supported
- **Photo quality dependent**: Requires good lighting and clear tile visibility
- **Arrow detection**: May produce false positives on boards with 15+ tiles

## Testing

The project includes tests covering:
- Image processing pipeline
- Arrow detection accuracy
- Tile boundary calculations
- Object recognition
- End-to-end scoring validation

Test images are organized in `test_images/valid_boards/` with boards of varying complexity.

## License

This is a personal portfolio project. Please contact me regarding usage rights.

## Acknowledgments

- **Beacon Patrol** is designed by Torben Ratzlaff and published by Pandasaurus Games
- Built as a learning project to explore computer vision and Python development
