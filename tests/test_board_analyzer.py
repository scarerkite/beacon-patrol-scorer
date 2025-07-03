import pytest
import tempfile
import io
from PIL import Image
from board_analyzer import analyze_complete_board, _is_valid_image_size

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
def small_image():
    """Create a small image (should fail size check)"""
    img = Image.new("RGB", (100, 100), color=(135, 206, 235))
    return img

@pytest.fixture
def large_image():
    """Create a large image (should fail size check)"""
    img = Image.new("RGB", (5000, 5000), color=(135, 206, 235))
    return img

@pytest.fixture
def valid_blue_image():
    """Create a valid blue image"""
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))
    return img

@pytest.fixture
def beacon_patrol_image():
    """Use actual beacon patrol board photo"""
    with open("test_images/valid_boards/7_tiles_blue.jpg", "rb") as f:
        img_bytes = io.BytesIO(f.read())
        img_bytes.seek(0)
        return img_bytes
    
@pytest.fixture
def mixed_grayscale_image():
    """Create an image that's half gray, half black (should fail)"""
    img = Image.new("RGB", (800, 600), color=(128, 128, 128))
    pixels = img.load()
    for x in range(400, 800):
        for y in range(600):
            pixels[x, y] = (0, 0, 0)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

# Test the complete analysis function
def test_analyze_complete_board_fails_on_small_image(small_image):
    """Test that small images fail at size check"""
    result = analyze_complete_board(small_image)
    
    assert result['is_valid'] == False
    assert result['failed_at'] == 'size_check'
    assert 'too small' in result['errors'][0].lower()

def test_analyze_complete_board_fails_on_large_image(large_image):
    """Test that large images fail at size check"""
    result = analyze_complete_board(large_image)
    
    assert result['is_valid'] == False
    assert result['failed_at'] == 'size_check'
    assert 'too large' in result['errors'][0].lower()

def test_analyze_complete_board_fails_on_wrong_colors(red_dominant_image):
    """Test that non-blue images fail at color check"""
    result = analyze_complete_board(red_dominant_image)
    
    assert result['is_valid'] == False
    assert result['failed_at'] == 'color_check'
    assert 'does not look like a Beacon Patrol game' in result['errors'][0]

def test_analyze_complete_board_fails_on_grayscale_image(mixed_grayscale_image):
    """Test that grayscale images fail at color check"""
    result = analyze_complete_board(mixed_grayscale_image)
    
    assert result['is_valid'] == False
    assert result['failed_at'] == 'color_check'
    assert 'does not look like a Beacon Patrol game' in result['errors'][0]

def test_analyze_complete_board_succeeds_with_valid_image(valid_blue_image):
    """Test that valid blue images pass all basic checks"""
    result = analyze_complete_board(valid_blue_image)
    
    assert result['is_valid'] == True
    assert result['score'] == 42  # Placeholder score
    assert result['rank'] == 'Sailors'  # Placeholder rank
    assert result['errors'] == []
    assert result['details']['passed_all_checks'] == True

def test_analyze_complete_board_succeeds_with_beacon_patrol_image(beacon_patrol_image):
    """Test that blue/white mixed images pass validation"""
    result = analyze_complete_board(beacon_patrol_image)
    
    assert result['is_valid'] == True
    assert result['score'] == 42
    assert result['rank'] == 'Sailors'

def test_analyze_complete_board_returns_consistent_structure():
    """Test that function always returns expected structure"""
    # Test with invalid input
    result = analyze_complete_board("nonexistent_file.jpg")
    
    required_keys = ['is_valid', 'errors']
    for key in required_keys:
        assert key in result
    
    # Valid result should have additional keys
    valid_image = Image.new("RGB", (800, 600), color=(135, 206, 235))
    result = analyze_complete_board(valid_image)
    
    if result['is_valid']:
        assert 'score' in result
        assert 'rank' in result
        assert 'details' in result

# Test individual helper functions
def test_is_valid_image_size():
    """Test size validation function"""
    small_img = Image.new("RGB", (100, 100), color="blue")
    large_img = Image.new("RGB", (5000, 5000), color="blue")
    valid_img = Image.new("RGB", (800, 600), color="blue")
    
    assert _is_valid_image_size(small_img) == False
    assert _is_valid_image_size(large_img) == False
    assert _is_valid_image_size(valid_img) == True