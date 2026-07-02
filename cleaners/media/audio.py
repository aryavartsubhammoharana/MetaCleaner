from services.mutagen_service import MutagenService
from services.exiftool_service import ExifToolService

def clean(input_path, output_path):
    """
    Cleans audio (MP3) metadata.
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    return MutagenService.clean_metadata(input_path, output_path)
