import os
from config import Config
from core.detector import detect_file_type

def validate_file(filepath):
    """
    Validates a file's security profile.
    Checks:
        1. File existence and size (must not be empty, must be within MAX_CONTENT_LENGTH).
        2. Extension (must be supported).
        3. Double check MIME and extensions correspond.
    Returns:
        (is_valid, error_message)
    """
    norm_path = os.path.abspath(filepath)
    if '..' in filepath or not os.path.exists(norm_path):
        return False, "Invalid or unauthorized file path."

    if not os.path.exists(filepath):
        return False, "File does not exist."
        
    size = os.path.getsize(filepath)
    if size == 0:
        return False, "File is empty."
        
    if size > Config.MAX_CONTENT_LENGTH:
        return False, f"File size exceeds the limit of {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB."
        
    ext, mime_type, category = detect_file_type(filepath)
    
    dangerous_extensions = {'exe', 'bat', 'cmd', 'sh', 'php', 'py', 'js', 'vbs', 'scr', 'dll', 'so', 'dylib'}
    if ext in dangerous_extensions or ext not in Config.SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file format: .{ext}"
        
    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)
            
        if ext in ['jpg', 'jpeg']:
            if not header.startswith(b'\xff\xd8\xff'):
                return False, "Invalid JPEG file signature."
        elif ext == 'png':
            if not header.startswith(b'\x89PNG\r\n\x1a\n'):
                return False, "Invalid PNG file signature."
        elif ext == 'pdf':
            if not header.startswith(b'%PDF'):
                return False, "Invalid PDF file signature."
        elif ext in ['docx', 'xlsx', 'pptx', 'odt', 'ods', 'odp']:
            if not header.startswith(b'PK\x03\x04'):
                return False, "Invalid Document archive signature."
        elif ext == 'webp':
            if not (header.startswith(b'RIFF') and b'WEBP' in header[8:12]):
                return False, "Invalid WebP signature."
    except Exception as e:
        return False, f"Security check failed: {str(e)}"
        
    return True, None
