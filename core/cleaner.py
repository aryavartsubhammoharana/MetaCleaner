import os
from core.detector import detect_file_type

# Import cleaner modules
from cleaners.image.jpg import clean as clean_jpg
from cleaners.image.jpeg import clean as clean_jpeg
from cleaners.image.png import clean as clean_png
from cleaners.image.webp import clean as clean_webp
from cleaners.image.tiff import clean as clean_tiff
from cleaners.image.heic import clean as clean_heic

from cleaners.documents.pdf import clean as clean_pdf
from cleaners.documents.docx import clean as clean_docx
from cleaners.documents.xlsx import clean as clean_xlsx
from cleaners.documents.pptx import clean as clean_pptx

from cleaners.media.audio import clean as clean_audio
from cleaners.media.video import clean as clean_video

from cleaners.generic import clean_generic

# Map extensions to their cleaning functions
CLEANERS_MAP = {
    'jpg': clean_jpg,
    'jpeg': clean_jpeg,
    'png': clean_png,
    'webp': clean_webp,
    'tiff': clean_tiff,
    'heic': clean_heic,
    
    'pdf': clean_pdf,
    'docx': clean_docx,
    'xlsx': clean_xlsx,
    'pptx': clean_pptx,
    
    'mp3': clean_audio,
    'mp4': clean_video,
    'mov': clean_video,
    'avi': clean_video
}

def clean_file_metadata(input_path, output_path):
    """
    Routes the file to the correct cleaner based on its extension.
    Returns:
        (success, error_message)
    """
    ext, _, _ = detect_file_type(input_path)
    
    cleaner_func = CLEANERS_MAP.get(ext)
    
    if not cleaner_func:
        # Fallback to generic cleaner
        print(f"No specific cleaner for .{ext}. Routing to generic cleaner.")
        success = clean_generic(input_path, output_path)
        if success:
            return True, None
        return False, "Failed to clean metadata using generic fallback cleaner."
        
    try:
        success = cleaner_func(input_path, output_path)
        if success:
            return True, None
        return False, "Cleaning function returned failure status."
    except Exception as e:
        print(f"Exception during cleaner routing for .{ext}: {e}")
        return False, str(e)
