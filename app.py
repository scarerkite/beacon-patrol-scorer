from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
from flask import send_from_directory

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
        return render_template("index.html", error="No file selected"), 400
    
    file = request.files["file"]
    if file.filename == "":
        return render_template("index.html", error="No file selected"), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            with Image.open(filepath) as img:
                width, height = img.size
                
                if width < 200 or height < 200:
                    return render_template("index.html", error="Image too small"), 400
                if width > 4000 or height > 4000:
                    return render_template("index.html", error="Image too large"), 400
                
                # Placeholder score and rank calculation
                score = 42
                rank = "Captain"
                
                return render_template("results.html", 
                                     filename=filename, 
                                     score=score, 
                                     rank=rank)
                
        except Exception as e:
            return render_template("index.html", error=f"Error: Not a valid image file"), 400
        
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)