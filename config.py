import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'metacleaner-secret-key-3d-glow')
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    import tempfile
    is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    if is_serverless:
        TEMP_DIR = os.path.join(tempfile.gettempdir(), 'metacleaner')
    else:
        TEMP_DIR = os.path.join(BASE_DIR, 'temp')
        
    UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'uploads')
    CLEANED_FOLDER = os.path.join(TEMP_DIR, 'cleaned')
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = bool(os.environ.get('VERCEL') or os.environ.get('PRODUCTION') or os.environ.get('FLASK_ENV') == 'production')
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(CLEANED_FOLDER, exist_ok=True)
        if hasattr(os, 'chmod') and os.name != 'nt':
            os.chmod(UPLOAD_FOLDER, 0o700)
            os.chmod(CLEANED_FOLDER, 0o700)
    except Exception as e:
        print(f"Directory initialization warning: {e}")
    
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    
    SUPPORTED_EXTENSIONS = {
        'jpg', 'jpeg', 'png', 'tiff', 'webp', 'heic', 'svg',
        'pdf', 'docx', 'xlsx', 'pptx', 'odt', 'ods', 'odp', 'rtf',
        'txt', 'md', 'csv', 'json', 'xml',
        'mp3', 'wav', 'flac', 'ogg', 'm4a', 'mp4', 'mov', 'avi', 'mkv'
    }
