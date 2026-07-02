from services.office_service import OfficeService
from services.exiftool_service import ExifToolService

def clean(input_path, output_path):
    """
    Cleans XLSX metadata.
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    return OfficeService.clean_metadata(input_path, output_path)
