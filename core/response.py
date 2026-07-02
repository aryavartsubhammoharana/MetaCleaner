import os
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
            # Read the file in chunks and stream it
            with open(cleaned_path, 'rb') as f:
                while True:
                    chunk = f.read(65536)  # 64KB chunks
                    if not chunk:
                        break
                    yield chunk
        finally:
            # This block runs after the response generator has finished executing
            # (i.e. client has downloaded the file or disconnected)
            for path in [cleaned_path, original_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"Privacy Cleanup: Successfully deleted temp file {path}")
                    except Exception as e:
                        print(f"Privacy Cleanup Warning: Could not delete {path}: {e}")

    # Build the streaming response
    response = Response(generate(), mimetype=mimetype)
    # Ensure Content-Disposition headers are set properly
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
