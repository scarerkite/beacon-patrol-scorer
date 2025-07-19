from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
from board_analyzer import analyze_complete_board
import cv2
import tempfile

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp(prefix="beacon_patrol_")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16 MB max file size

def validate_file_content(file_path):
    """
    Validate that the file is actually a valid image by trying to open it.
    This prevents malicious files disguised as images.
    """
    try:
        with Image.open(file_path) as img:
            img.verify()  # This will raise an exception if not a valid image
            
        # Reopen for further validation (verify() can only be called once)
        with Image.open(file_path) as img:
            width, height = img.size
            
            # Additional safety checks
            if width <= 0 or height <= 0:
                return False
            if width > 10000 or height > 10000:  # Prevent memory bombs
                return False
                
        return True
        
    except Exception as e:
        print(f"File validation failed: {e}")  # Log for debugging
        return False

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
        # Check MIME type first (before saving)
        if not file.content_type.startswith('image/'):
            return render_template("index.html", error="Invalid file type"), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # ADD FILE CONTENT VALIDATION HERE
        if not validate_file_content(filepath):
            os.remove(filepath)  # Clean up the invalid file
            return render_template("index.html", error="File is corrupted or not a valid image"), 400

        try:
            with Image.open(filepath) as img:
                # Your existing analysis code...
                result = analyze_complete_board(img, filepath)

                if not result['is_valid']:
                    # Handle arrow validation errors (still has annotated_image)
                    if result.get('annotated_image') is not None:
                        annotated_filename = f"annotated_{filename}"
                        annotated_path = os.path.join(app.config["UPLOAD_FOLDER"], annotated_filename)
                        cv2.imwrite(annotated_path, result['annotated_image'])
                        return render_template("index.html", 
                                            error=result['errors'][0], 
                                            annotated_filename=annotated_filename), 400
                    
                    return render_template("index.html", error=result['errors'][0]), 400
                
                # Success! Use the annotated filename that was already saved
                annotated_filename = result.get('annotated_filename')

                if annotated_filename is None:
                    # Image generation failed, but scoring worked
                    return render_template("results.html", 
                                        filename=filename,  # Show original image
                                        score=result['score'], 
                                        rank=result['rank'],
                                        breakdown=result['breakdown'],
                                        details=result.get('details', {}))
                else:
                    # Show annotated image
                    annotated_filename = os.path.basename(annotated_filename)
                    return render_template("results.html", 
                                        filename=annotated_filename,
                                        score=result['score'], 
                                        rank=result['rank'],
                                        breakdown=result['breakdown'],
                                        details=result.get('details', {}))
                    
        except Exception as e:
            return render_template("index.html", error="Error: Not a valid image file"), 400


    
        
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)