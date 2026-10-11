import mimetypes
import os

MIME_MAP = {
    '.heic': 'image/heic',
    '.svg': 'image/svg+xml',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.odt': 'application/vnd.oasis.opendocument.text',
    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
    '.odp': 'application/vnd.oasis.opendocument.presentation',
    '.rtf': 'application/rtf',
    '.md': 'text/markdown',
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.flac': 'audio/flac',
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/mp4',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.mkv': 'video/x-matroska',
    '.webp': 'image/webp',
}

def detect_file_type(filepath):
    """
    Detects the file extension and MIME type of a given file.
    Returns:
        (extension, mime_type, category)
        Where category is one of 'image', 'document', 'text', 'audio', 'video', or 'unknown'.
    """
    _, ext = os.path.splitext(filepath.lower())
    
    mime_type = MIME_MAP.get(ext)
    
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filepath)
    
    if not mime_type:
        mime_type = 'application/octet-stream'
        
    category = 'unknown'
    if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.webp', '.heic', '.svg']:
        category = 'image'
    elif ext in ['.pdf', '.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp', '.rtf']:
        category = 'document'
    elif ext in ['.txt', '.md', '.csv', '.json', '.xml']:
        category = 'text'
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
        category = 'audio'
    elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
        category = 'video'
        
    return ext.lstrip('.'), mime_type, category
