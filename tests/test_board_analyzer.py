import pytest
import tempfile
import io
from PIL import Image
from app import app
from board_analyzer import analyze_board_colors
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
def simple_game_image_path():
    image_path = "test_images/valid_boards/7_tiles_blue.jpg"
    return image_path

@pytest.fixture
def game_image_path():
    image_path = "test_images/valid_boards/14_tiles.jpg"
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

