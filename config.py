import os
import hashlib
import subprocess

def _determine_version():
    app_ver = os.environ.get('APP_VERSION', '1.2.0')
    git_sha = (
        os.environ.get('VERCEL_GIT_COMMIT_SHA') or
        os.environ.get('GIT_COMMIT') or
        os.environ.get('COMMIT_REF')
    )
    if git_sha:
        return app_ver, f"{app_ver}-{git_sha[:7]}"
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        out = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=base_dir,
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        if out:
            return app_ver, f"{app_ver}-{out}"
    except Exception:
        pass
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'static')
        h = hashlib.md5()
        for root, _, files in os.walk(static_dir):
            for f in sorted(files):
                fp = os.path.join(root, f)
                h.update(f.encode())
                h.update(str(os.path.getmtime(fp)).encode())
        return app_ver, f"{app_ver}-{h.hexdigest()[:7]}"
    except Exception:
        pass
    return app_ver, app_ver

class Config:
    APP_VERSION, BUILD_ID = _determine_version()
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
