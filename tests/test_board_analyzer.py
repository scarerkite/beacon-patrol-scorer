import pytest
import tempfile
import io
from PIL import Image
from app import app
from board_analyzer import analyze_board_colors, identify_blue_tiles
import cv2
import numpy as np
import os

@pytest.fixture
def green_dominant_image():
    """Create an image that's mostly green (should fail)"""
    img = Image.new("RGB", (800, 600), color=(34, 139, 34))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def red_dominant_image():
    """Create an image that's mostly red (should fail)"""
    img = Image.new("RGB", (800, 600), color=(245, 66, 66))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def simple_game_image():
    image_path = "test_images/valid_boards/simple_game1.png"
    return image_path

def test_predominantly_blue_image_is_valid_board(blue_dominant_image):
    """Test result from a predominantly blue image"""
    response = analyze_board_colors(blue_dominant_image)
    assert response == True

def test_beacon_patrol_style_image_is_valid_board(beacon_patrol_style_image):
    """Test that a blue/white mixed image is recognized as valid"""
    response = analyze_board_colors(beacon_patrol_style_image)
    assert response == True

def test_invalid_colors_mostly_green(green_dominant_image):
    """Test result from a predominantly green image"""
    response = analyze_board_colors(green_dominant_image)
    assert response == False

def test_invalid_colors_mostly_red(red_dominant_image):
    """Test result from a predominantly red image"""
    response = analyze_board_colors(red_dominant_image)
    assert response == False

def test_mixed_grayscale_image_is_not_valid_board(mixed_grayscale_image):
    """Test that a mixed gray/black image is not recognized as a valid board"""
    response = analyze_board_colors(mixed_grayscale_image)
    assert response == False

def test_analyze_board_colors_accepts_pil_image():
    """Test that analyze_board_colors can handle PIL Image objects directly"""
    # Create a PIL Image (not BytesIO)
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))  # Blue
    
    # Pass PIL Image directly
    result = analyze_board_colors(img)
    
    assert result == True

def test_identify_blue_tiles_finds_correct_number(simple_game_image):
    contours = identify_blue_tiles(simple_game_image)
    assert len(contours) == 7, f"Expected 7 tiles, found {len(contours)}"

# def test_identify_blue_tiles_with_different_image(different_game_image):
#     """Test with a different board layout - adjust expected count as needed"""
#     if os.path.exists(different_game_image):
#         contours = identify_blue_tiles(different_game_image)
#         # You'll need to count the tiles in your second test image
#         assert len(contours) > 0, "Should find at least some tiles"
#         assert len(contours) < 20, "Shouldn't find an unrealistic number of tiles"
#     else:
#         pytest.skip("Second test image not available")

def test_identify_blue_tiles_handles_missing_file():
    """Test that function handles non-existent files gracefully"""
    with pytest.raises(FileNotFoundError):
        identify_blue_tiles("non_existent_file.jpg")

def test_identify_blue_tiles_returns_list():
    """Test that function returns a list of contours"""
    contours = identify_blue_tiles("test_images/valid_boards/simple_game1.png")
    assert isinstance(contours, list), "Should return a list of contours"
    assert all(hasattr(contour, 'shape') for contour in contours), "Each item should be a contour array"