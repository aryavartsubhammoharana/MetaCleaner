import os
import sys

# Ensure root directory is in sys.path for serverless execution
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel WSGI entry point
# Exports the Flask application
