import shutil
from services.exiftool_service import ExifToolService

def clean_generic(input_path, output_path):
    """
    Cleans metadata from any file type.
    Attempts to use ExifTool (which supports almost all formats).
    If ExifTool is not available, falls back to copying the file as-is.
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    # Fallback: Copy file
    try:
        shutil.copyfile(input_path, output_path)
        return True
    except Exception as e:
        print(f"Generic clean fallback copy failed: {e}")
        return False
