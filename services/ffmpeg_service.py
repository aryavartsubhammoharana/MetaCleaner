import os
import shutil
import subprocess

class FFmpegService:
    @staticmethod
    def is_available():
        """
        Checks if ffmpeg is available on the system PATH.
        """
        return shutil.which('ffmpeg') is not None

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans video metadata using FFmpeg stream copy.
        ffmpeg -y -i input_path -map_metadata -1 -c copy output_path
        """
        if not FFmpegService.is_available():
            return False
            
        try:
            # -y overwrites output file
            # -map_metadata -1 strips all metadata
            # -c copy performs stream copy (no transcoding, ultra fast)
            cmd = ['ffmpeg', '-y', '-i', input_path, '-map_metadata', '-1', '-c', 'copy', output_path]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            print(f"FFmpeg video cleaning failed: {e}")
            return False
