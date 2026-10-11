import os
from pypdf import PdfReader, PdfWriter

class PdfService:
    @staticmethod
    def read_metadata(filepath):
        """
        Reads metadata from a PDF file.
        """
        metadata = {}
        try:
            reader = PdfReader(filepath)
            info = reader.metadata
            if info:
                keys_map = {
                    '/Title': 'Title',
                    '/Author': 'Author',
                    '/Subject': 'Subject',
                    '/Creator': 'Creator',
                    '/Producer': 'Producer',
                    '/CreationDate': 'Date Created',
                    '/ModDate': 'Date Modified',
                    '/Keywords': 'Keywords'
                }
                for key, display in keys_map.items():
                    if key in info and info[key]:
                        val = info[key]
                        if isinstance(val, bytes):
                            val = val.decode('utf-8', errors='ignore')
                        metadata[display] = str(val)
        except Exception as e:
            print(f"Error reading PDF metadata: {e}")
            
        return metadata

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans all metadata from a PDF file by copying pages to a new writer and setting empty metadata.
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
                
            writer.add_metadata({})
            
            try:
                if hasattr(writer, 'root_object') and '/Metadata' in writer.root_object:
                    del writer.root_object['/Metadata']
            except Exception:
                pass
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            print(f"Error cleaning PDF metadata: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False
