import mimetypes
import os

# Additional custom MIME types mapping if not present in the system registry
MIME_MAP = {
    '.heic': 'image/heic',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.webp': 'image/webp',
}

def detect_file_type(filepath):
    """
    Detects the file extension and MIME type of a given file.
    Returns:
        (extension, mime_type, category)
        Where category is one of 'image', 'document', 'audio', 'video', or 'unknown'.
    """
    _, ext = os.path.splitext(filepath.lower())
    
    # Try custom mapping first
    mime_type = MIME_MAP.get(ext)
    
    if not mime_type:
        # Fall back to standard mimetypes library
        mime_type, _ = mimetypes.guess_type(filepath)
    
    if not mime_type:
        mime_type = 'application/octet-stream'
        
    category = 'unknown'
    if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.webp', '.heic']:
        category = 'image'
    elif ext in ['.pdf', '.docx', '.xlsx', '.pptx']:
        category = 'document'
    elif ext in ['.mp3']:
        category = 'audio'
    elif ext in ['.mp4', '.mov', '.avi']:
        category = 'video'
        
    return ext.lstrip('.'), mime_type, category
