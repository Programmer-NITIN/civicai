"""
api/routes_wards.py
--------------------
Ward and department directory endpoints.

Provides read-only access to the AMC ward registry and department
directory for the frontend Ward & Department Directory page.
"""

from fastapi import APIRouter

from app.config_data import WARD_REGISTRY, DEPARTMENT_REGISTRY

router = APIRouter(prefix="/directory")


@router.get("/wards", summary="List all AMC wards")
async def list_wards() -> dict:
    """Return the full ward registry for the directory page."""
    return {
        "total_wards": len(WARD_REGISTRY),
        "wards": list(WARD_REGISTRY.values()),
    }


@router.get("/departments", summary="List all AMC departments")
async def list_departments() -> dict:
    """Return the full department registry for the directory page."""
    return {
        "total_departments": len(DEPARTMENT_REGISTRY),
        "departments": list(DEPARTMENT_REGISTRY.values()),
    }


@router.get("/wards/{ward_id}", summary="Get ward details by ID")
async def get_ward(ward_id: str) -> dict:
    """Return details for a specific ward."""
    ward = WARD_REGISTRY.get(ward_id.upper())
    if ward is None:
        return {"error": f"Ward '{ward_id}' not found"}
    return ward


@router.get("/departments/{department_id}", summary="Get department details")
async def get_department(department_id: str) -> dict:
    """Return details for a specific department."""
    dept = DEPARTMENT_REGISTRY.get(department_id.upper())
    if dept is None:
        return {"error": f"Department '{department_id}' not found"}
    return dept
