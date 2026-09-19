import sys
import os

# Configure paths so backend modules can be imported smoothly
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(frontend_dir, "backend")
parent_backend_dir = os.path.join(os.path.dirname(frontend_dir), "backend")

for p in [backend_dir, parent_backend_dir, current_dir, frontend_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from app.main import app
