import sys
import os

# Resolve paths so that backend/app modules can be imported smoothly on Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

for path in [root_dir, backend_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import the configured FastAPI application instance
from app.main import app
