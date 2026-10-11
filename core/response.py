import os
import time
from flask import jsonify, Response

def json_response(success=True, message="", data=None, status_code=200):
    """
    Creates a standard JSON response.
    """
    response = {
        "success": success,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def send_cleaned_file(cleaned_path, original_path, filename, mimetype):
    """
    Streams the cleaned file to the client and automatically deletes the
    cleaned and original files once the download is complete.
    """
    def generate():
        try:
            with open(cleaned_path, 'rb') as f:
                while True:
                    chunk = f.read(65536)  # 64KB chunks
                    if not chunk:
                        break
                    yield chunk
        finally:
            for path in [cleaned_path, original_path]:
                if path and os.path.exists(path):
                    for attempt in range(3):
                        try:
                            os.remove(path)
                            print(f"Privacy Cleanup: Successfully deleted temp file {path}")
                            break
                        except Exception as e:
                            time.sleep(0.05)

    response = Response(generate(), mimetype=mimetype)
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
