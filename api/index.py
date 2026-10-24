import os
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
    try:
        from api.app.main import app  # noqa: E402
    except Exception:
        import traceback
        err = traceback.format_exc()
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        app = FastAPI(title="AMC CivicAI")

        @app.get("/health")
        async def health_diag():
            return JSONResponse({"status": "startup_traceback", "trace": err})

        @app.get("/{rest_of_path:path}")
        async def catch_all(rest_of_path: str):
            return JSONResponse({"status": "startup_traceback", "trace": err})
