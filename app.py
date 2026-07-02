import os
import uuid
import time
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from core.validator import validate_file
from core.detector import detect_file_type
from core.metadata_reader import read_file_metadata
from core.cleaner import clean_file_metadata
from core.response import json_response, send_cleaned_file
from core.utils import format_size, cleanup_old_temp_files

app = Flask(__name__)

# Fix for Render (Reverse Proxy) so url_for generates HTTPS links instead of HTTP
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config.from_object(Config)

# Security Hardening: Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Allow Google Fonts and inline styles for the UI
csp = {
    'default-src': ['\'self\''],
    'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://fonts.googleapis.com'],
    'font-src': ['\'self\'', 'https://fonts.gstatic.com'],
    'img-src': ['\'self\'', 'data:']
}

# Security Hardening: HTTP Headers
Talisman(app, content_security_policy=csp)

# Periodic temp folder sweep on startup
try:
    cleanup_old_temp_files(max_age_seconds=900)
except Exception as e:
    print(f"Initial cleanup failed: {e}")

@app.route('/')
def index():
    # Clean old files occasionally on root load
    try:
        cleanup_old_temp_files(max_age_seconds=900)
    except Exception:
        pass
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("20 per minute")
def upload_file():
    """
    Handles file upload, performs security checks, reads metadata,
    and returns metadata preview to client.
    """
    if 'file' not in request.files:
        return json_response(success=False, message="No file part in the request.", status_code=400)
        
    file = request.files['file']
    if file.filename == '':
        return json_response(success=False, message="No file selected.", status_code=400)
        
    # Generate unique file ID to prevent conflicts and bypass security vulnerabilities
    file_uuid = str(uuid.uuid4())
    original_name = secure_filename(file.filename)
    _, ext = os.path.splitext(original_name.lower())
    
    # Save file with unique ID
    temp_filename = f"{file_uuid}{ext}"
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    
    try:
        file.save(upload_path)
    except Exception as e:
        return json_response(success=False, message=f"Failed to save uploaded file: {str(e)}", status_code=500)
        
    # Validate file (size, extension, magic numbers)
    is_valid, err_msg = validate_file(upload_path)
    if not is_valid:
        # Delete invalid file immediately
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return json_response(success=False, message=err_msg, status_code=400)
        
    # Read metadata
    try:
        metadata = read_file_metadata(upload_path)
        file_size = os.path.getsize(upload_path)
        formatted_size = format_size(file_size)
        ext_clean, mime_type, category = detect_file_type(upload_path)
        
        # Prepare response data
        response_data = {
            "file_id": temp_filename,
            "original_name": original_name,
            "size_bytes": file_size,
            "formatted_size": formatted_size,
            "mime_type": mime_type,
            "category": category,
            "metadata": metadata
        }
        return json_response(success=True, message="File parsed successfully.", data=response_data)
    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return json_response(success=False, message=f"Failed to extract metadata: {str(e)}", status_code=500)

@app.route('/clean', methods=['POST'])
@limiter.limit("20 per minute")
def clean_file():
    """
    Cleans metadata from a previously uploaded file.
    Expects file_id in JSON payload.
    """
    data = request.get_json() or {}
    file_id = data.get('file_id')
    
    if not file_id:
        return json_response(success=False, message="Missing file_id parameter.", status_code=400)
        
    # Sanitize file_id to avoid path traversal
    file_id = secure_filename(file_id)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    
    if not os.path.exists(upload_path):
        return json_response(success=False, message="Uploaded file not found or expired.", status_code=404)
        
    cleaned_filename = f"cleaned_{file_id}"
    cleaned_path = os.path.join(app.config['CLEANED_FOLDER'], cleaned_filename)
    
    start_time = time.time()
    
    # Run cleaner
    success, err_msg = clean_file_metadata(upload_path, cleaned_path)
    
    time_taken = time.time() - start_time
    
    if not success:
        # Clean up upload file
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return json_response(success=False, message=f"Failed to clean metadata: {err_msg}", status_code=500)
        
    # Read size of cleaned file
    cleaned_size = os.path.getsize(cleaned_path)
    
    return json_response(
        success=True,
        message="Metadata successfully cleaned.",
        data={
            "file_id": file_id,
            "cleaned_file_id": cleaned_filename,
            "original_size": format_size(os.path.getsize(upload_path)),
            "cleaned_size": format_size(cleaned_size),
            "time_taken_ms": round(time_taken * 1000)
        }
    )

@app.route('/download/<file_id>')
def download_file(file_id):
    """
    Streams cleaned file and deletes both source and destination copies immediately.
    """
    file_id = secure_filename(file_id)
    
    # The cleaned file id should start with cleaned_
    if not file_id.startswith('cleaned_'):
        return "Invalid file path request.", 400
        
    cleaned_path = os.path.join(app.config['CLEANED_FOLDER'], file_id)
    
    # Original file is stored as the remainder
    original_filename = file_id.replace('cleaned_', '')
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    
    if not os.path.exists(cleaned_path):
        return "Cleaned file not found or expired.", 404
        
    # Read original filename from parameter to serve with a user-friendly name
    user_filename = request.args.get('name', 'cleaned_file')
    user_filename = secure_filename(user_filename)
    
    # Prevent empty filename or extension mismatches
    if not user_filename:
        user_filename = "cleaned_file"
        
    # Append _cleaned suffix before extension if possible
    base, ext = os.path.splitext(user_filename)
    if not base.endswith('_cleaned'):
        user_filename = f"{base}_cleaned{ext}"
        
    _, mime_type, _ = detect_file_type(cleaned_path)
    
    # Send streaming file (which deletes original and cleaned on completion)
    return send_cleaned_file(cleaned_path, original_path, user_filename, mime_type)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
