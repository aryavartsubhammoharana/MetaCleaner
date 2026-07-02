from services.exif_service import ExifService
from services.exiftool_service import ExifToolService

def clean(input_path, output_path):
    """
    Cleans WebP metadata.
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    return ExifService.clean_metadata(input_path, output_path)
