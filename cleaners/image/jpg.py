from services.exif_service import ExifService
from services.exiftool_service import ExifToolService

def clean(input_path, output_path):
    """
    Cleans JPG/JPEG metadata using Pillow ExifService, or ExifTool if available.
    """
    # 1. Try ExifTool first for highest precision (strips all marker metadata)
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    # 2. Fall back to Pillow ExifService
    return ExifService.clean_metadata(input_path, output_path)
