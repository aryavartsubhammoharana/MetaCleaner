from services.ffmpeg_service import FFmpegService
from services.exiftool_service import ExifToolService
from services.mutagen_service import MutagenService
import shutil
import os

def clean(input_path, output_path):
    """
    Cleans video (MP4, MOV, AVI) metadata.
    Pipeline:
      1. Try FFmpeg (safest stream-copy, strips all container metadata)
      2. Try ExifTool (strips all EXIF/XMP tags)
      3. Try Mutagen (MP4 files only, deletes core tags)
      4. Fallback: Safe copy
    """
    # 1. FFmpeg is the golden standard for video containers.
    if FFmpegService.is_available():
        if FFmpegService.clean_metadata(input_path, output_path):
            return True
            
    # 2. ExifTool is secondary
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    # 3. Mutagen is tertiary (handles MP4 metadata in-place)
    _, ext = os.path.splitext(input_path.lower())
    if ext == '.mp4':
        if MutagenService.clean_metadata(input_path, output_path):
            return True
            
    # 4. Fallback safe copy
    try:
        shutil.copyfile(input_path, output_path)
        return True
    except Exception as e:
        print(f"Video cleaning fallback copy failed: {e}")
        return False
