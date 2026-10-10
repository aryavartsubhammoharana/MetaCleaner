import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'metacleaner-secret-key-3d-glow')
    
    # Workspace root directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    import tempfile
    is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    if is_serverless:
        TEMP_DIR = os.path.join(tempfile.gettempdir(), 'metacleaner')
    else:
        TEMP_DIR = os.path.join(BASE_DIR, 'temp')
        
    UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'uploads')
    CLEANED_FOLDER = os.path.join(TEMP_DIR, 'cleaned')
    
    # Ensure temporary folders exist safely
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(CLEANED_FOLDER, exist_ok=True)
    except Exception as e:
        print(f"Directory initialization warning: {e}")
    
    # Limits: 25MB Max Upload Size
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    
    # Allowed formats categories
    SUPPORTED_EXTENSIONS = {
        # Images
        'jpg', 'jpeg', 'png', 'tiff', 'webp', 'heic',
        # Documents
        'pdf', 'docx', 'xlsx', 'pptx',
        # Media
        'mp3', 'mp4', 'mov', 'avi'
    }
