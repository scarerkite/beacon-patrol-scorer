import pytest
import tempfile
import io
from PIL import Image
from app import app
from board_analyzer import analyze_board_colors

@pytest.fixture
def blue_dominant_image():
    """Create an image that's mostly blue (like Beacon Patrol water)"""
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

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
def mixed_grayscale_image():
    """Create an image that's half gray, half black (should fail)"""
    img = Image.new("RGB", (800, 600), color=(128, 128, 128))  # Start with gray
    
    # Paint the right half black
    pixels = img.load()
    for x in range(400, 800):  # Right half
        for y in range(600):
            pixels[x, y] = (0, 0, 0)  # Black
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def beacon_patrol_style_image():
    """Create an image with blue water and white land (should pass)"""
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))  # Blue water
    
    # Add some white land areas  
    pixels = img.load()
    for x in range(200, 400):  # Middle section
        for y in range(100, 300):  # Top area
            pixels[x, y] = (255, 255, 255)  # White land
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

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