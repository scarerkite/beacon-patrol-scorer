import pytest
import os
import tempfile
from PIL import Image
import io
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    img = Image.new("RGB", (800, 600), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def sample_small_image():
    """Create a sample small image for testing"""
    img = Image.new("RGB", (100, 300), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def sample_large_image():
    """Create a sample large image for testing"""
    img = Image.new("RGB", (500, 4001), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def text_file():
    """Create a sample text file for testing"""
    text_content = io.BytesIO(b"Hello world, this is not an image!")
    return text_content

def test_index_page(client):
    """Test the home page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Beacon Patrol Board Scorer" in response.data

def test_upload_valid_image(client, sample_image):
    """Test uploading a valid image shows results page"""
    response = client.post("/upload", data={
        "file": (sample_image, "test.jpg")
    })
    assert response.status_code == 200
    assert b"Your Results" in response.data
    assert b"Score:" in response.data

def test_upload_no_file(client):
    """Test uploading without selecting a file returns error"""
    response = client.post("/upload", data={})
    assert response.status_code == 400
    assert b"Upload a photo of your game board" in response.data

def test_upload_small_image(client, sample_small_image):
    """Test uploading a small image returns error"""
    response = client.post("/upload", data={
        "file": (sample_small_image, "test.jpg")
    })
    assert response.status_code == 400
    assert b"Upload a photo of your game board" in response.data

def test_upload_large_image(client, sample_large_image):
    """Test uploading a large image returns error"""
    response = client.post("/upload", data={
        "file": (sample_large_image, "test.jpg")
    })
    assert response.status_code == 400
    assert b"Upload a photo of your game board" in response.data

def test_upload_non_image(client, text_file):
    """Test uploading a text file returns error"""
    response = client.post("/upload", data={
        "file": (text_file, "test.txt")
    })
    assert response.status_code == 400
    assert b"Upload a photo of your game board" in response.data

def test_upload_integration_happy_path(client, sample_image):
    """Test complete upload workflow returns expected elements"""
    response = client.post("/upload", data={
        "file": (sample_image, "test_board.jpg")
    })
    assert response.status_code == 200
    assert b"Your Results" in response.data
    assert b"42" in response.data  # placeholder score