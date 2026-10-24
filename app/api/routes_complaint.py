"""
api/routes_complaint.py
-------------------------
Complaint filing endpoints — the core agent pipeline.

Handles:
  1. POST /complaint/file — File a new civic complaint (with optional photo).
  2. POST /complaint/file-with-image — File with image upload.

The filing pipeline executes four agent tool calls in sequence:
  Tool 1: vision_analyzer.analyze_image()
  Tool 2: ward_resolver.resolve_ward()
  Tool 3: department_router.assign_department()
  Tool 4: ticket_manager.create_ticket()

Each tool call is timed and its latency is included in the response
for full agent transparency (matching the "Live Agent Tool Inspector" UI).
"""

import time
import logging
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException

from app.middleware.rate_limiter import complaint_rate_limit, upload_rate_limit
from app.models.complaint_models import (
    ComplaintRequest,
    ComplaintResponse,
    IssueType,
)
from app.civic_engine.vision_analyzer import analyze_image
from app.civic_engine.ward_resolver import resolve_ward
from app.civic_engine.department_router import assign_department
from app.civic_engine.ticket_manager import create_ticket
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/complaint")


def _run_agent_pipeline(
    citizen_name: str,
    phone: str,
    area_or_address: str,
    description: str,
    filename: str,
    latitude: Optional[float],
    longitude: Optional[float],
    issue_type_override: Optional[IssueType],
) -> ComplaintResponse:
    """Execute the four-step agent tool chain with latency tracking.

    Each tool call is timed independently and its latency is recorded
    in the agent_trace for full transparency.
    """
    agent_trace = []
    pipeline_start = time.monotonic()

    # ── Tool 1: Image Analysis ───────────────────────────────────────────
    t0 = time.monotonic()
    image_result = analyze_image(
        filename=filename,
        description=description,
        address=area_or_address,
        issue_type_override=issue_type_override,
    )
    t1 = time.monotonic()
    agent_trace.append({
        "step": 1,
        "tool": "amc.vision.classify_hazard",
        "description": "Multimodal Vision Hazard Triage",
        "latency_ms": round((t1 - t0) * 1000),
        "status": "SUCCESS",
        "result": {
            "detected_class": image_result.detected_class.value,
            "confidence": image_result.confidence,
            "severity": image_result.severity,
            "severity_label": image_result.severity_label,
        },
    })

    # ── Tool 2: Ward Resolution ──────────────────────────────────────────
    t0 = time.monotonic()
    ward_result = resolve_ward(
        area_or_address=area_or_address,
        latitude=latitude,
        longitude=longitude,
    )
    t1 = time.monotonic()
    agent_trace.append({
        "step": 2,
        "tool": "amc.gis.resolve_ward_polygon",
        "description": "Spatial GIS Boundary Resolution",
        "latency_ms": round((t1 - t0) * 1000),
        "status": "SUCCESS",
        "result": {
            "ward_id": ward_result.ward_id,
            "ward_name": ward_result.ward_name,
            "zone_name": ward_result.zone_name,
            "resolution_method": ward_result.resolution_method,
        },
    })

    # ── Tool 3: Department Routing ───────────────────────────────────────
    t0 = time.monotonic()
    dept_result = assign_department(image_result.detected_class)
    t1 = time.monotonic()
    agent_trace.append({
        "step": 3,
        "tool": "amc.dispatch.assign_ticket",
        "description": "Department Officer SLA Routing",
        "latency_ms": round((t1 - t0) * 1000),
        "status": "SUCCESS",
        "result": {
            "department_name": dept_result.department_name,
            "sla_hours": dept_result.sla_hours,
            "urgency": dept_result.urgency.value,
            "officer": dept_result.nodal_officer,
        },
    })

    # ── Tool 4: Ticket Creation ──────────────────────────────────────────
    t0 = time.monotonic()
    ticket = create_ticket(
        citizen_name=citizen_name,
        phone=phone,
        area_or_address=area_or_address,
        description=description,
        image_analysis=image_result,
        ward_lookup=ward_result,
        department=dept_result,
    )
    t1 = time.monotonic()
    agent_trace.append({
        "step": 4,
        "tool": "amc.ticket.create",
        "description": "Omnichannel Citizen Dispatch",
        "latency_ms": round((t1 - t0) * 1000),
        "status": "SUCCESS",
        "result": {
            "ticket_id": ticket.ticket_id,
            "status": ticket.status.value,
        },
    })

    total_ms = round((time.monotonic() - pipeline_start) * 1000)
    logger.info("Agent pipeline completed in %dms: %s", total_ms, ticket.ticket_id)

    return ComplaintResponse(
        ticket_id=ticket.ticket_id,
        status=ticket.status.value,
        message=(
            f"Your complaint has been registered successfully. "
            f"Tracking ID: {ticket.ticket_id}. "
            f"Assigned to {dept_result.department_name} — "
            f"SLA: {dept_result.sla_hours} hours ({dept_result.urgency.value})."
        ),
        image_analysis=image_result,
        ward_lookup=ward_result,
        department=dept_result,
        sla_hours=dept_result.sla_hours,
        created_at=ticket.created_at,
        resolution_eta=ticket.resolution_eta,
        agent_trace=agent_trace,
    )


@router.post(
    "/file",
    response_model=ComplaintResponse,
    summary="File a civic complaint (JSON body)",
    dependencies=[Depends(complaint_rate_limit)],
)
async def file_complaint(request: ComplaintRequest) -> ComplaintResponse:
    """File a civic complaint using form data (no photo upload).

    Requires citizen_name, phone, and area_or_address. Optionally accepts
    an issue_type override if no image is being analyzed.
    """
    return _run_agent_pipeline(
        citizen_name=request.citizen_name,
        phone=request.phone,
        area_or_address=request.area_or_address,
        description=request.description,
        filename=request.issue_type.value if request.issue_type else "unknown_issue",
        latitude=request.latitude,
        longitude=request.longitude,
        issue_type_override=request.issue_type,
    )


@router.post(
    "/file-with-image",
    response_model=ComplaintResponse,
    summary="File a civic complaint with photo upload",
    dependencies=[Depends(upload_rate_limit)],
)
async def file_complaint_with_image(
    citizen_name: str = Form(
        ..., min_length=1, max_length=100,
        description="Full name of the reporting citizen",
    ),
    phone: str = Form(
        ..., min_length=10, max_length=15,
        description="Contact phone number",
    ),
    area_or_address: str = Form(
        ..., min_length=2, max_length=200,
        description="Area name, landmark, or address",
    ),
    description: str = Form(
        default="", max_length=1000,
        description="Optional description of the issue",
    ),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
    image: UploadFile = File(..., description="Photo of the civic issue"),
) -> ComplaintResponse:
    """File a civic complaint with an attached photo.

    The image filename is used for heuristic classification.
    Validates file type and size before processing.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if image.content_type and image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid file type: {image.content_type}. "
                f"Allowed: {', '.join(allowed_types)}"
            ),
        )

    # Validate file size (read content to check)
    content = await image.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    filename = image.filename or "uploaded_image.jpg"

    return _run_agent_pipeline(
        citizen_name=citizen_name,
        phone=phone,
        area_or_address=area_or_address,
        description=description,
        filename=filename,
        latitude=latitude,
        longitude=longitude,
        issue_type_override=None,  # Let vision classifier determine from filename
    )
