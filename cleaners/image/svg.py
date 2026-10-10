import os
import re
import xml.etree.ElementTree as ET

def clean(input_path, output_path):
    """
    Cleans metadata from SVG images by removing <metadata> tags,
    XML comments, and editor namespace attributes.
    """
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            svg_content = f.read()

        # Remove XML comments
        cleaned = re.sub(r'<!--[\s\S]*?-->', '', svg_content)
        # Remove <metadata>...</metadata> blocks
        cleaned = re.sub(r'<metadata[\s\S]*?</metadata>', '', cleaned, flags=re.IGNORECASE)
        # Remove editor attributes (inkscape, sodipodi, adobe illustrator)
        cleaned = re.sub(r'\s*(?:inkscape|sodipodi):[a-zA-Z0-9_-]+="[^"]*"', '', cleaned)
        cleaned = re.sub(r'\s*xmlns:(?:inkscape|sodipodi|i)="[^"]*"', '', cleaned)

        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned.strip())

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"Error cleaning SVG metadata: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
        return False
