import os
import zipfile

BLANK_META_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
    'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" office:version="1.3">\n'
    '  <office:meta></office:meta>\n'
    '</office:document-meta>'
)

def clean(input_path, output_path):
    """
    Cleans metadata from OpenDocument files (ODT, ODS, ODP).
    Overwrites meta.xml with blank metadata and strips thumbnail previews.
    """
    if not zipfile.is_zipfile(input_path):
        return False

    try:
        with zipfile.ZipFile(input_path, 'r') as z_in:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
                for item in z_in.infolist():
                    if item.filename == 'meta.xml':
                        z_out.writestr('meta.xml', BLANK_META_XML)
                    elif item.filename.startswith('Thumbnails/'):
                        continue
                    else:
                        z_out.writestr(item, z_in.read(item.filename))
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"Error cleaning OpenDocument metadata: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
        return False
