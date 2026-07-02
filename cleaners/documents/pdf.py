from services.pdf_service import PdfService
from services.exiftool_service import ExifToolService

def clean(input_path, output_path):
    """
    Cleans PDF metadata.
    """
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    return PdfService.clean_metadata(input_path, output_path)
