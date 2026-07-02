from core.detector import detect_file_type
from services.exif_service import ExifService
from services.pdf_service import PdfService
from services.office_service import OfficeService
from services.mutagen_service import MutagenService
from services.exiftool_service import ExifToolService

def read_file_metadata(filepath):
    """
    Detects the file type and routes it to the correct service to read metadata.
    Attempts to read metadata via pure-Python services, and merges/falls back
    to ExifTool if available.
    """
    ext, mime_type, category = detect_file_type(filepath)
    
    metadata = {}
    
    # 1. Use specific services based on categories
    if category == 'image':
        metadata = ExifService.read_metadata(filepath)
    elif category == 'document':
        if ext == 'pdf':
            metadata = PdfService.read_metadata(filepath)
        elif ext in ['docx', 'xlsx', 'pptx']:
            metadata = OfficeService.read_metadata(filepath)
    elif category in ['audio', 'video']:
        # MP3 and MP4 tags
        metadata = MutagenService.read_metadata(filepath)
        
    # 2. Merge with ExifTool if available (it can enrich metadata or be a fallback)
    if ExifToolService.is_available():
        tool_meta = ExifToolService.read_metadata(filepath)
        # Update/fill missing fields, or merge
        for key, val in tool_meta.items():
            if key not in metadata or not metadata[key]:
                metadata[key] = val
                
    return metadata
