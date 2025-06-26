# test_arrow_detector.py (following your style)

import pytest
import tempfile
import io
import os
import cv2
import numpy as np
from PIL import Image
from arrow_detection import detect_arrow_orientations, validate_board_arrows

@pytest.fixture 
def nonexistent_image_path():
    """Path to an image that doesn't exist"""
    return "definitely_does_not_exist.jpg"

def test_detect_arrow_orientations_returns_correct_tuple_format():
    """Test that detect_arrow_orientations returns the expected format"""
    # Test with nonexistent file to avoid dependencies
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations("fake_file.jpg")
    
    assert isinstance(correct_count, int)
    assert isinstance(incorrect_count, int)
    assert annotated_image is None 

def test_detect_arrow_orientations_handles_missing_file(nonexistent_image_path):
    """Test that function handles non-existent files gracefully"""
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations(nonexistent_image_path)
    
    assert correct_count == 0
    assert incorrect_count == 0
    assert annotated_image is None

def test_validate_board_arrows_handles_missing_file(nonexistent_image_path):
    """Test that validation handles non-existent files gracefully"""
    is_valid, message, correct_count, incorrect_count, annotated_image = validate_board_arrows(nonexistent_image_path)
    
    assert is_valid == False
    assert "Could not load image" in message
    assert correct_count == 0
    assert incorrect_count == 0
    assert annotated_image is None

def test_7_tile_board_has_7_correct_arrows():
    """Test that the 7-tile board image detects exactly 7 correct arrows"""
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations("test_images/valid_boards/7_tiles_blue.jpg")
    
    assert correct_count == 7
    assert incorrect_count == 0
    assert annotated_image is not None

def test_14_tile_board_has_14_correct_arrows():
    """Test that the 14-tile board image detects exactly 14 correct arrows"""
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations("test_images/valid_boards/14_tiles.jpg")
    
    assert correct_count == 14
    assert incorrect_count == 0
    assert annotated_image is not None

def test_5_tile_board_has_2_correct_arrows_3_incorrect_arrows():
    """Test that the 5-tile board image detects exactly 2 correct arrows and 3 incorrect"""
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations("test_images/invalid_boards/5_tiles_3_arrows_wrong.jpg")
    
    assert correct_count == 2
    assert incorrect_count == 3
    assert annotated_image is not None

def test_15_tile_board_has_13_correct_arrows_2_incorrect_arrows():
    """Test that the 15-tile board image detects exactly 13 correct arrows and 2 incorrect"""
    correct_count, incorrect_count, annotated_image = detect_arrow_orientations("test_images/invalid_boards/15_tiles_2_arrows_wrong.jpg")
    
    assert correct_count == 13
    assert incorrect_count == 2
    assert annotated_image is not None

def test_validate_board_arrows_returns_valid_for_correct_arrows():
    """Test that validate_board_arrows returns True for boards with all correct arrows"""
    is_valid, message, correct_count, incorrect_count, annotated_image = validate_board_arrows("test_images/valid_boards/7_tiles_blue.jpg")
    
    assert is_valid == True
    assert "Valid board" in message
    assert "All 7 arrows pointing correctly" in message
    assert correct_count == 7
    assert incorrect_count == 0
    assert annotated_image is not None

def test_validate_board_arrows_returns_invalid_for_wrong_arrows():
    """Test that validate_board_arrows returns False for boards with incorrect arrows"""
    is_valid, message, correct_count, incorrect_count, annotated_image = validate_board_arrows("test_images/invalid_boards/5_tiles_3_arrows_wrong.jpg")
    
    assert is_valid == False
    assert "Invalid board" in message
    assert "3 arrows pointing wrong direction" in message
    assert correct_count == 2
    assert incorrect_count == 3
    assert annotated_image is not None