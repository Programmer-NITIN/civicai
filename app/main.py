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
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https://*.googleapis.com; "
        "connect-src 'self' https://*.googleapis.com; "
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


# ── Static frontend ─────────────────────────────────────────────────────────
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception:  # pylint: disable=broad-exception-caught
    logger.warning("Frontend directory not found — API-only mode.")
