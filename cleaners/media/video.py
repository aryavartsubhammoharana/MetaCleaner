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
    if FFmpegService.is_available():
        if FFmpegService.clean_metadata(input_path, output_path):
            return True
            
    if ExifToolService.is_available():
        if ExifToolService.clean_metadata(input_path, output_path):
            return True
            
    _, ext = os.path.splitext(input_path.lower())
    if ext == '.mp4':
        if MutagenService.clean_metadata(input_path, output_path):
            return True
            
    print("Video cleaning: No available engine (FFmpeg/ExifTool/Mutagen) could clean this video.")
    return False
