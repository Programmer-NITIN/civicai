"""
api/index.py
------------
Serverless entry point for Vercel deployment.
Exposes the FastAPI instance from app.main.
"""

import sys
from pathlib import Path

# Add api directory and root directory to sys.path
api_dir = Path(__file__).resolve().parent
root_dir = api_dir.parent

for p in (str(api_dir), str(root_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app
except Exception:
    from api.app.main import app  # noqa: E402
