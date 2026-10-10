import os
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS

# Try to register HEIC support dynamically if pi-heif is installed
HEIC_SUPPORTED = False
try:
    from pi_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    print("pi-heif not installed. HEIC support will be limited.")

class ExifService:
    @staticmethod
    def get_gps_info(exif_data):
        """
        Extracts GPS coordinates if available in EXIF data.
        """
        gps_info = {}
        # Tag 34853 (0x8825) is GPSInfo
        gps_raw = exif_data.get(34853)
        if not gps_raw:
            return None
            
        # If it's a GPSInfo dictionary
        for key in gps_raw.keys():
            sub_tag = GPSTAGS.get(key, key)
            gps_info[sub_tag] = gps_raw[key]
            
        # Format latitude and longitude
        try:
            def to_degrees(value):
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)

            lat_ref = gps_info.get('GPSLatitudeRef')
            lat_val = gps_info.get('GPSLatitude')
            lon_ref = gps_info.get('GPSLongitudeRef')
            lon_val = gps_info.get('GPSLongitude')

            if lat_val and lat_ref and lon_val and lon_ref:
                lat = to_degrees(lat_val)
                if lat_ref != 'N':
                    lat = -lat
                    
                lon = to_degrees(lon_val)
                if lon_ref != 'E':
                    lon = -lon
                    
                return f"{lat:.6f}, {lon:.6f} ({lat_ref}, {lon_ref})"
        except Exception:
            pass
            
        return str(gps_info)

    @staticmethod
    def read_metadata(filepath):
        """
        Reads metadata from an image file (JPG, PNG, WebP, TIFF, HEIC).
        """
        metadata = {}
        try:
            with Image.open(filepath) as img:
                metadata['Dimensions'] = f"{img.width}x{img.height} px"
                metadata['Format'] = img.format
                
                # Read EXIF
                exif_data = img.getexif()
                if exif_data:
                    # Common keys we want to extract
                    target_tags = {
                        'Make': 'Device Manufacturer',
                        'Model': 'Camera Model',
                        'Software': 'Software/Firmware',
                        'DateTime': 'Date Created',
                        'Artist': 'Author/Artist',
                        'ImageDescription': 'Title/Description',
                        'Copyright': 'Copyright'
                    }
                    
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id)
                        if tag_name in target_tags:
                            metadata[target_tags[tag_name]] = str(value)
                            
                    # Extract GPS Info
                    gps_loc = ExifService.get_gps_info(exif_data)
                    if gps_loc:
                        metadata['GPS Location'] = gps_loc

                # Check other metadata formats (PNG/WebP text fields)
                for key, val in img.info.items():
                    if key in ['author', 'title', 'description', 'copyright', 'comment']:
                        metadata[key.capitalize()] = str(val)
        except Exception as e:
            print(f"Error reading image metadata for {filepath}: {e}")
            
        return metadata

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans image metadata by re-saving it without the EXIF headers and info chunks.
        Preserves image orientation via exif_transpose before stripping EXIF.
        """
        try:
            with Image.open(input_path) as img:
                # Transpose image based on EXIF orientation so rotation is preserved when EXIF is stripped
                transposed_img = ImageOps.exif_transpose(img)
                if transposed_img is None:
                    transposed_img = img

                # Determine save format
                save_format = img.format
                if not save_format:
                    _, ext = os.path.splitext(input_path.lower())
                    ext_map = {
                        '.jpg': 'JPEG', '.jpeg': 'JPEG',
                        '.png': 'PNG', '.webp': 'WEBP',
                        '.tif': 'TIFF', '.tiff': 'TIFF',
                        '.heic': 'HEIF'
                    }
                    save_format = ext_map.get(ext, 'PNG')

                # Handle color modes (e.g. RGBA cannot be saved as JPEG)
                if save_format.upper() == 'JPEG' and transposed_img.mode in ('RGBA', 'LA', 'P'):
                    clean_img = transposed_img.convert('RGB')
                else:
                    clean_img = transposed_img.copy()

                # Wipe embedded metadata dictionary
                clean_img.info = {}

                save_kwargs = {}
                if save_format.upper() == 'JPEG':
                    save_kwargs['quality'] = 95
                    save_kwargs['subsampling'] = 0
                    save_kwargs['exif'] = b""
                elif save_format.upper() == 'PNG':
                    save_kwargs['optimize'] = True

                clean_img.save(output_path, format=save_format, **save_kwargs)
                return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except Exception as e:
            print(f"Error cleaning image metadata: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False
