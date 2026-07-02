import os
import time
from config import Config

def format_size(size_in_bytes):
    """
    Converts bytes to a human-readable string (KB, MB, GB).
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def cleanup_old_temp_files(max_age_seconds=900):
    """
    Cleans up any upload or cleaned temporary files that are older than
    max_age_seconds (default 15 minutes). This covers cases where files
    were uploaded but never processed or downloaded.
    """
    now = time.time()
    folders = [Config.UPLOAD_FOLDER, Config.CLEANED_FOLDER]
    
    count = 0
    for folder in folders:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            # Skip folders
            if os.path.isdir(filepath):
                continue
                
            try:
                # Check creation/modification time
                mtime = os.path.getmtime(filepath)
                if now - mtime > max_age_seconds:
                    os.remove(filepath)
                    count += 1
            except Exception as e:
                print(f"Periodic Cleanup error on {filepath}: {e}")
                
    if count > 0:
        print(f"Periodic Cleanup: Pruned {count} stale temporary files.")
    return count
