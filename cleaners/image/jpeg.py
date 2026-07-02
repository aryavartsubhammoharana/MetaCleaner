from cleaners.image.jpg import clean as jpg_clean

def clean(input_path, output_path):
    """
    Cleans JPEG metadata. Alias for JPG cleaner.
    """
    return jpg_clean(input_path, output_path)
