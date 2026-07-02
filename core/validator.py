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
    if not os.path.exists(filepath):
        return False, "File does not exist."
        
    size = os.path.getsize(filepath)
    if size == 0:
        return False, "File is empty."
        
    if size > Config.MAX_CONTENT_LENGTH:
        return False, f"File size exceeds the limit of {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB."
        
    ext, mime_type, category = detect_file_type(filepath)
    
    if ext not in Config.SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file format: .{ext}"
        
    # Prevent malicious uploads disguised with wrong extensions
    # (e.g. executable/script named as .png)
    # Check headers for common formats
    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)
            
        if ext in ['jpg', 'jpeg']:
            # JPEG magic numbers: FF D8 FF
            if not header.startswith(b'\xff\xd8\xff'):
                return False, "Invalid JPEG file signature."
        elif ext == 'png':
            # PNG magic numbers: 89 50 4E 47 0D 0A 1A 0A
            if not header.startswith(b'\x89PNG\r\n\x1a\n'):
                return False, "Invalid PNG file signature."
        elif ext == 'pdf':
            # PDF magic number: %PDF-
            if not header.startswith(b'%PDF'):
                return False, "Invalid PDF file signature."
        elif ext in ['docx', 'xlsx', 'pptx']:
            # Office Open XML files are ZIP containers starting with PK\x03\x04
            if not header.startswith(b'PK\x03\x04'):
                return False, "Invalid Office Document signature."
        elif ext == 'webp':
            # RIFF .... WEBP
            if not (header.startswith(b'RIFF') and b'WEBP' in header[8:12]):
                return False, "Invalid WebP signature."
    except Exception as e:
        return False, f"Security check failed: {str(e)}"
        
    return True, None
