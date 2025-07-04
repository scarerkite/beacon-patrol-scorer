import pytest
import tempfile
import io
import os
import cv2
import numpy as np
from PIL import Image
from tile_analyzer import detect_scorable_tiles, _estimate_tile_size, _estimate_tile_grid, _check_tile_surrounded, _rectangles_overlap, _annotate_scorable_tiles, visualize_scorable_boundaries
from arrow_detection import get_arrow_positions

@pytest.fixture 
def nonexistent_image_path():
    """Path to an image that doesn't exist"""
    return "definitely_does_not_exist.jpg"

# Main function tests
def test_detect_scorable_tiles_handles_missing_file(nonexistent_image_path):
    """Test that function handles non-existent files gracefully"""
    tile_count, scorable_count, annotated_image, _scorable_boundaries = detect_scorable_tiles(nonexistent_image_path)
    
    assert tile_count == 0
    assert scorable_count == 0
    assert annotated_image is None

def test_7_tile_board_has_1_scorable_tile():
    """Test that the 7-tile board image detects exactly 1 scorable tile"""
    tile_count, scorable_count, annotated_image, _scorable_boundaries = detect_scorable_tiles("test_images/valid_boards/7_tiles_blue.jpg")
    
    assert tile_count == 7
    assert scorable_count == 1
    assert annotated_image is not None

def test_12_tile_board_has_2_scorable_tiles():
    """Test that the 12-tile board image detects exactly 2 scorable tiles"""
    tile_count, scorable_count, annotated_image, _scorable_boundaries = detect_scorable_tiles("test_images/valid_boards/12_tiles.jpg")
    
    assert tile_count == 12
    assert scorable_count == 2
    assert annotated_image is not None

def test_14_tile_board_has_4_scorable_tiles():
    """Test that the 14-tile board image detects exactly 4 scorable tiles"""
    tile_count, scorable_count, annotated_image, _scorable_boundaries = detect_scorable_tiles("test_images/valid_boards/14_tiles.jpg")
    
    assert tile_count == 14
    assert scorable_count == 4
    assert annotated_image is not None

# Tile size estimation tests
def test_estimate_tile_size_from_7_tile_board():
    """Test tile size estimation on the 7-tile board photo"""
    correct_positions, incorrect_positions, image = get_arrow_positions("test_images/valid_boards/7_tiles_blue.jpg")
    
    estimated_size = _estimate_tile_size(correct_positions)
    
    # Based on your actual measurements: ~218x217 pixels
    assert 210 <= estimated_size[0] <= 225  # Width tolerance
    assert 210 <= estimated_size[1] <= 225  # Height tolerance
    assert abs(estimated_size[0] - estimated_size[1]) <= 5  # Should be roughly square

def test_estimate_tile_size_from_12_tile_board():
    """Test tile size estimation on the larger 12-tile board"""
    correct_positions, _incorrect_positions, _image = get_arrow_positions("test_images/valid_boards/12_tiles.jpg")
    
    estimated_size = _estimate_tile_size(correct_positions)
    
    # Based on your actual measurements: ~270x264 pixels
    assert 260 <= estimated_size[0] <= 275  # Width tolerance
    assert 260 <= estimated_size[1] <= 275  # Height tolerance
    assert abs(estimated_size[0] - estimated_size[1]) <= 10  # Should be roughly square

def test_estimate_tile_size_from_14_tile_board():
    """Test tile size estimation on the larger 14-tile board"""
    correct_positions, _incorrect_positions, _image = get_arrow_positions("test_images/valid_boards/14_tiles.jpg")
    
    estimated_size = _estimate_tile_size(correct_positions)
    
    # Based on your actual measurements: ~249x252 pixels
    assert 240 <= estimated_size[0] <= 260  # Width tolerance
    assert 240 <= estimated_size[1] <= 260  # Height tolerance
    assert abs(estimated_size[0] - estimated_size[1]) <= 10  # Should be roughly square

def test_estimate_tile_size_handles_insufficient_arrows():
    """Test that single arrow returns None"""
    single_arrow = [(100, 100)]
    
    estimated_size = _estimate_tile_size(single_arrow)
    
    assert estimated_size is None

def test_estimate_tile_size_handles_no_arrows():
    """Test that empty arrow list returns None"""
    estimated_size = _estimate_tile_size([])
    
    assert estimated_size is None

# Tile grid estimation tests
def test_estimate_tile_grid_with_real_7_tile_board():
    """Test tile boundary generation on real photo"""
    correct_positions, incorrect_positions, image = get_arrow_positions("test_images/valid_boards/7_tiles_blue.jpg")
    tile_size = _estimate_tile_size(correct_positions)
    
    tile_boundaries = _estimate_tile_grid(correct_positions, tile_size)
    
    # Should find all 7 tiles
    assert len(tile_boundaries) == 7
    
    # Each boundary should be a tuple of 4 coordinates
    for boundary in tile_boundaries:
        assert len(boundary) == 4
        left, top, right, bottom = boundary
        assert left < right  # Valid rectangle
        assert top < bottom  # Valid rectangle

def test_estimate_tile_grid_handles_missing_data():
    """Test grid estimation with missing data"""
    # No arrows
    boundaries = _estimate_tile_grid([], (100, 100))
    assert boundaries == []
    
    # No tile size
    boundaries = _estimate_tile_grid([(100, 100)], None)
    assert boundaries == []

# Tile surrounded tests
def test_check_tile_surrounded_with_all_neighbors():
    """Test surrounded detection when tile has all 4 neighbors"""
    center_tile = (100, 100, 200, 200)  # 100x100 tile
    
    # Create 4 adjacent tiles
    all_tiles = [
        center_tile,
        (0, 100, 100, 200),    # Left neighbor
        (200, 100, 300, 200),  # Right neighbor
        (100, 0, 200, 100),    # Top neighbor
        (100, 200, 200, 300)   # Bottom neighbor
    ]
    
    assert _check_tile_surrounded(center_tile, all_tiles) == True

def test_check_tile_surrounded_with_missing_neighbors():
    """Test surrounded detection when tile is missing neighbors"""
    center_tile = (100, 100, 200, 200)
    
    # Only has 3 neighbors (missing right)
    all_tiles = [
        center_tile,
        (0, 100, 100, 200),    # Left neighbor
        (100, 0, 200, 100),    # Top neighbor
        (100, 200, 200, 300)   # Bottom neighbor
    ]
    
    assert _check_tile_surrounded(center_tile, all_tiles) == False

# Visual debugging test (optional)
# def test_visualize_boundaries():
#     """Visual test of tile boundary detection"""
#     from tile_analyzer import visualize_scorable_boundaries
    
#     # This will create debug images you can inspect
#     visualize_scorable_boundaries("test_images/valid_boards/7_tiles_blue.jpg", "debug_boundaries_7tile.jpg")
#     visualize_scorable_boundaries("test_images/valid_boards/12_tiles.jpg", "debug_boundaries_12tile.jpg")
#     visualize_scorable_boundaries("test_images/valid_boards/14_tiles.jpg", "debug_boundaries_14tile.jpg")
    
#     # Just check the files were created
#     assert os.path.exists("debug_boundaries_7tile.jpg")
#     assert os.path.exists("debug_boundaries_12tile.jpg")
#     assert os.path.exists("debug_boundaries_14tile.jpg")
