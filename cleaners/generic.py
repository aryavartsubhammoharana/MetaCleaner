import shutil
from services.exiftool_service import ExifToolService

def clean_generic(input_path, output_path):
    """
    Cleans metadata from any file type.
    Attempts to use ExifTool (which supports almost all formats).
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    print("Generic clean: ExifTool not available to clean generic file type.")
    return False
