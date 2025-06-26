import pytest
import io
from PIL import Image

@pytest.fixture
def blue_dominant_image():
    """Create an image with Beacon Patrol-style light blue"""
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
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

@pytest.fixture
def beacon_patrol_style_image():
    """Create an image with blue water and white land (should pass)"""
    img = Image.new("RGB", (800, 600), color=(135, 206, 235))
    pixels = img.load()
    for x in range(200, 400):
        for y in range(100, 300):
            pixels[x, y] = (255, 255, 255)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes