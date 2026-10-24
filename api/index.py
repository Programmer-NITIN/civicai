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
except Exception as exc1:
    try:
        from api.app.main import app  # noqa: E402
    except Exception as exc2:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse, HTMLResponse
        app = FastAPI(title="AMC CivicAI Emergency Fallback")

        @app.get("/health")
        async def health():
            return JSONResponse({"status": "healthy", "mode": "fallback", "error": f"{exc1} | {exc2}"})

        @app.get("/{rest_of_path:path}")
        async def fallback_all(rest_of_path: str):
            for path in ("public/index.html", "frontend/index.html", "index.html", str(api_dir / "index.html")):
                if os.path.exists(path):
                    return HTMLResponse(content=Path(path).read_text(encoding="utf-8"))
            return JSONResponse({"status": "diagnostic", "error1": str(exc1), "error2": str(exc2)})
