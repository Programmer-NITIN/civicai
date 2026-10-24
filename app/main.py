"""
main.py
-------
FastAPI application factory for CivicAI.

Responsibilities:
  - Creates the FastAPI instance with conditional documentation.
  - Registers all API routers under appropriate prefixes.
  - Installs security middleware (CSP, HSTS, X-Frame-Options).
  - Configures CORS based on environment (wildcard in debug, strict in prod).
  - Mounts the static frontend for SPA serving.
  - Provides a startup/shutdown lifecycle hook.
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api import routes_health, routes_complaint, routes_status, routes_wards

logger = logging.getLogger(__name__)


# ── Lifecycle ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup and shutdown hooks for the application."""
    logger.info(
        "CivicAI starting — version=%s debug=%s vision=%s",
        settings.app_version,
        settings.debug,
        "mock" if not settings.gemini_api_key else "live",
    )
    yield
    logger.info("CivicAI shutting down")


# ── App creation ─────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AMC CivicAI — Autonomous Civic Complaint Agent with image analysis, "
        "ward routing, and ticket lifecycle management."
    ),
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    lifespan=lifespan,
)


# ── Security headers middleware ──────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Injects production security headers on every response.

    Headers:
    - Content-Security-Policy: restricts resource origins.
    - X-Content-Type-Options: prevents MIME sniffing.
    - X-Frame-Options: prevents clickjacking.
    - Referrer-Policy: limits referrer leakage.
    - Strict-Transport-Security: enforces HTTPS in production.
    """
    start = time.monotonic()
    response: Response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(self), payment=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https://*.googleapis.com https://*.googleusercontent.com https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://*.arcgisonline.com https://server.arcgisonline.com https://*.google.com https://mt0.google.com https://mt1.google.com https://mt2.google.com https://mt3.google.com; "
        "connect-src 'self' https://*.googleapis.com https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://*.arcgisonline.com https://server.arcgisonline.com https://*.google.com https://mt0.google.com https://mt1.google.com https://mt2.google.com https://mt3.google.com; "
        "frame-ancestors 'none'"
    )

    if not settings.debug:
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )

    # Request logging
    latency_ms = (time.monotonic() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method, request.url.path, response.status_code, latency_ms,
    )

    return response


# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(routes_health.router, tags=["Health"])
app.include_router(routes_complaint.router, tags=["Complaint Filing"])
app.include_router(routes_status.router, tags=["Ticket Tracking"])
app.include_router(routes_wards.router, tags=["Ward & Department Directory"])


import os
from fastapi.responses import FileResponse, HTMLResponse

# ── Root index handler (Ensures Vercel function serves index if rewritten to root) ─
@app.get("/", include_in_schema=False)
async def serve_root():
    for cand in ("public/index.html", "frontend/index.html", "index.html"):
        if os.path.exists(cand):
            return FileResponse(cand)
    return HTMLResponse("<h1>AMC CivicAI</h1><p>API operational.</p>")


# ── Static mounts ────────────────────────────────────────────────────────────
for sub in ("css", "js", "assets"):
    target = f"frontend/{sub}" if os.path.isdir(f"frontend/{sub}") else sub
    if os.path.isdir(target):
        try:
            app.mount(f"/{sub}", StaticFiles(directory=target), name=sub)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

try:
    frontend_dir = "public" if os.path.isdir("public") else "frontend"
    app.mount("/static", StaticFiles(directory=frontend_dir, html=True), name="static")
except Exception:  # pylint: disable=broad-exception-caught
    logger.warning("Frontend directory not found — API-only mode.")

