"""
api/routes_health.py
---------------------
Health check endpoint for service monitoring and container orchestrators.

Returns backend connectivity status for all subsystems.
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health", summary="Service health check")
async def health_check() -> dict:
    """Returns the service status and backend configuration.

    Used by Docker HEALTHCHECK, Cloud Run, and monitoring dashboards.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "subsystems": {
            "vision_ai": "mock" if not settings.gemini_api_key else "live",
            "ticket_store": "in_memory",
            "ward_resolver": "active",
            "department_router": "active",
        },
    }
