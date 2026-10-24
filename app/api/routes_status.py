"""
api/routes_status.py
---------------------
Ticket status lookup and tracking endpoints.

Handles:
  1. POST /status/track — Look up a ticket by tracking ID.
  2. GET  /status/all  — List all tickets (newest first).
"""

import time
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.middleware.rate_limiter import status_rate_limit
from app.models.complaint_models import StatusRequest, StatusResponse, TicketRecord
from app.civic_engine.ticket_manager import get_ticket, get_all_tickets

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status")


@router.post(
    "/track",
    response_model=StatusResponse,
    summary="Track a civic complaint by ID",
    dependencies=[Depends(status_rate_limit)],
)
async def track_complaint(request: StatusRequest) -> StatusResponse:
    """Look up the current status of a civic complaint.

    Returns the full ticket record with timeline, ward assignment,
    department details, and SLA clock status.
    """
    t0 = time.monotonic()
    ticket = get_ticket(request.ticket_id)
    t1 = time.monotonic()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket '{request.ticket_id}' not found. Please check the ID and try again.",
        )

    agent_trace = [
        {
            "step": 1,
            "tool": "amc.ticket.lookup",
            "description": "Ticket Store Query",
            "latency_ms": round((t1 - t0) * 1000),
            "status": "SUCCESS",
            "result": {
                "ticket_id": ticket.ticket_id,
                "current_status": ticket.status.value,
            },
        },
    ]

    return StatusResponse(ticket=ticket, agent_trace=agent_trace)


@router.get(
    "/all",
    response_model=list[TicketRecord],
    summary="List all civic complaints",
    dependencies=[Depends(status_rate_limit)],
)
async def list_all_tickets() -> list[TicketRecord]:
    """Return all tickets in the store, newest first.

    Used by the operations dashboard for a complete view of
    all complaints across wards and departments.
    """
    return get_all_tickets()
