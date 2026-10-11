import os
import shutil
import mutagen
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3

class MutagenService:
    @staticmethod
    def read_metadata(filepath):
        """
        Reads metadata tags from audio (MP3) and video/audio containers (MP4, M4A, etc.).
        """
        metadata = {}
        try:
            audio = mutagen.File(filepath)
            if audio is None:
                return metadata
                
            if isinstance(audio, MP3) or getattr(audio, 'tags', None) is not None:
                tags = audio.tags
                if tags:
                    id3_mapping = {
                        'TIT2': 'Title',
                        'TPE1': 'Artist',
                        'TALB': 'Album',
                        'TDRC': 'Date Created/Year',
                        'TCON': 'Genre',
                        'COMM': 'Comments',
                        'TCOM': 'Composer',
                        'TRCK': 'Track Number'
                    }
                    for key, display in id3_mapping.items():
                        for tag_name in tags.keys():
                            if tag_name.startswith(key):
                                val = tags[tag_name]
                                if hasattr(val, 'text') and val.text:
                                    metadata[display] = str(val.text[0])
                                elif hasattr(val, 'url'):
                                    metadata[display] = str(val.url)
                                else:
                                    metadata[display] = str(val)
                                break
                                
            if isinstance(audio, MP4):
                mp4_mapping = {
                    '\xa9nam': 'Title',
                    '\xa9ART': 'Artist',
                    '\xa9alb': 'Album',
                    '\xa9day': 'Date Created/Year',
                    '\xa9gen': 'Genre',
                    '\xa9cmt': 'Comments',
                    '\xa9wrt': 'Composer',
                    'trkn': 'Track Number'
                }
                for key, display in mp4_mapping.items():
                    if key in audio:
                        val = audio[key]
                        if isinstance(val, list) and val:
                            metadata[display] = str(val[0])
                        else:
                            metadata[display] = str(val)
                            
            if not metadata and hasattr(audio, 'keys'):
                generic_mapping = {
                    'title': 'Title',
                    'artist': 'Artist',
                    'album': 'Album',
                    'date': 'Date Created/Year',
                    'genre': 'Genre',
                    'comment': 'Comments',
                    'composer': 'Composer'
                }
                for key, display in generic_mapping.items():
                    if key in audio:
                        val = audio[key]
                        if isinstance(val, list) and val:
                            metadata[display] = str(val[0])
                        else:
                            metadata[display] = str(val)
        except Exception as e:
            print(f"Error reading Mutagen metadata: {e}")
            
        return metadata

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans all metadata tags from MP3, MP4, and other audio/video containers.
        Copies the file to output path, then wipes tags.
        """
        try:
            shutil.copyfile(input_path, output_path)
            
            audio = mutagen.File(output_path)
            if audio is not None:
                audio.delete()
                audio.save()
            return True
        except Exception as e:
            print(f"Error cleaning Mutagen metadata: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False
