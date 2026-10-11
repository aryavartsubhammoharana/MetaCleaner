import os
import re

ZERO_WIDTH_PATTERN = re.compile(r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060\ufeff]')

def clean(input_path, output_path):
    """
    Cleans text, markdown, CSV, and code files by:
    1. Stripping UTF BOM (Byte Order Marks).
    2. Stripping invisible zero-width tracking watermarks.
    3. Normalizing to clean UTF-8 encoding.
    """
    try:
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None
        for enc in encodings:
            try:
                with open(input_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if content is None:
            with open(input_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='replace')

        cleaned_content = ZERO_WIDTH_PATTERN.sub('', content)

        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned_content)

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"Error cleaning text/markdown file: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
        return False
