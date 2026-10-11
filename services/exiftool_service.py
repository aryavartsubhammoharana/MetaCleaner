import os
import shutil
import subprocess

class ExifToolService:
    @staticmethod
    def is_available():
        """
        Checks if exiftool is available on the system PATH.
        """
        return shutil.which('exiftool') is not None

    @staticmethod
    def read_metadata(filepath):
        """
        Reads metadata using exiftool CLI.
        """
        if not ExifToolService.is_available():
            return {}
            
        metadata = {}
        try:
            result = subprocess.run(
                ['exiftool', '-s', '-G', filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            tag_mappings = {
                'Title': 'Title',
                'Artist': 'Author/Artist',
                'Creator': 'Author/Creator',
                'CreateDate': 'Date Created',
                'ModifyDate': 'Date Modified',
                'DateTimeOriginal': 'Date Created (Original)',
                'Model': 'Camera Model',
                'Make': 'Device Manufacturer',
                'Software': 'Software/Firmware',
                'GPSPosition': 'GPS Location',
                'GPSLatitude': 'GPS Latitude',
                'GPSLongitude': 'GPS Longitude',
                'Subject': 'Subject',
                'Keywords': 'Keywords',
                'Comment': 'Comments'
            }

            for line in result.stdout.splitlines():
                if ':' in line:
                    part_g_tag, val = line.split(':', 1)
                    val = val.strip()
                    if ']' in part_g_tag:
                        group, tag = part_g_tag.split(']', 1)
                        tag = tag.strip()
                    else:
                        tag = part_g_tag.strip()
                        
                    if tag in tag_mappings:
                        metadata[tag_mappings[tag]] = val
        except Exception as e:
            print(f"ExifTool read failed: {e}")
            
        return metadata

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans metadata using exiftool CLI.
        exiftool -all= -overwrite_original -o output_path input_path
        """
        if not ExifToolService.is_available():
            return False
            
        try:
            if input_path != output_path:
                shutil.copyfile(input_path, output_path)
                
            subprocess.run(
                ['exiftool', '-all=', '-overwrite_original', output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            return True
        except Exception as e:
            print(f"ExifTool cleaning failed: {e}")
            return False
