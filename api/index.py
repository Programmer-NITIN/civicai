"""
api/index.py
------------
Serverless entry point for Vercel deployment.
Exposes the FastAPI instance from app.main.
"""

import sys
from pathlib import Path

# Ensure the project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app  # noqa: E402
