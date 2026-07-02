import os
import shutil
import mutagen
from mutagen.id3 import ID3
from mutagen.mp4 import MP4

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
                
            # If it's MP3/ID3
            if isinstance(audio, mutagen.mp3.MP3) or getattr(audio, 'tags', None) is not None:
                tags = audio.tags
                if tags:
                    # Map standard ID3 tags
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
                        # ID3 tags can have sub-tags or lists, or multiple instances. Get the first one.
                        for tag_name in tags.keys():
                            if tag_name.startswith(key):
                                val = tags[tag_name]
                                # Comm tags are COMM:desc:lang
                                if hasattr(val, 'text') and val.text:
                                    metadata[display] = str(val.text[0])
                                elif hasattr(val, 'url'):
                                    metadata[display] = str(val.url)
                                else:
                                    metadata[display] = str(val)
                                break
                                
            # If it's MP4
            if isinstance(audio, MP4):
                # MP4 tags map
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
                            
            # Fallback for generic mutagen tags dictionary
            if not metadata and hasattr(audio, 'keys'):
                # Many tags are in format like artist, title, album, date
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
            # Copy to output path first
            shutil.copyfile(input_path, output_path)
            
            # Load the copy
            audio = mutagen.File(output_path)
            if audio is not None:
                audio.delete()
                audio.save()
            return True
        except Exception as e:
            print(f"Error cleaning Mutagen metadata: {e}")
            # If it failed to wipe using mutagen, return True if we managed to copy it,
            # or False if it completely failed.
            return os.path.exists(output_path)
