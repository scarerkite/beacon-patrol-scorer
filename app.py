from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16 MB max file size

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file selected", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Basic image validation
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                
                # Basic validation - reasonable size for a board photo
                if width < 200 or height < 200:
                    return "Image too small - please upload a clearer photo", 400
                
                if width > 4000 or height > 4000:
                    return "Image too large - please upload a smaller file", 400
                
                # Simple scoring based on image properties (placeholder)
                score = min(50, (width * height) // 10000)  # Bigger images = higher scores
                
                return f"Valid board image! Size: {width}x{height}px. Your score: {score}"
                
        except Exception as e:
            return f"Error: Not a valid image file", 400

if __name__ == "__main__":
    app.run(debug=True)