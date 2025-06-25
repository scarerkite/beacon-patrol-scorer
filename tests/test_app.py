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


