"""
civic_engine/ticket_manager.py
--------------------------------
Agent Tool #4: Ticket Lifecycle Manager.

Creates, retrieves, and updates civic complaint tickets in a
thread-safe in-memory store. Simulates the AMC Central Redressal
Gateway with realistic ticket IDs and SLA timelines.

Design:
  - Uses an OrderedDict as a bounded in-memory database.
  - Ticket IDs follow AMC format: AMC-{YEAR}-{DEPT_CODE}-{SEQ}.
  - Thread-safe via a threading.Lock for concurrent request safety.
  - Automatically generates realistic timeline entries.
  - Max 10,000 tickets — oldest evicted when full (LRU).
"""

import logging
import threading
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict

from app.models.complaint_models import (
    TicketRecord,
    TicketStatus,
    ImageAnalysisResult,
    WardLookupResult,
    DepartmentAssignment,
)

logger = logging.getLogger(__name__)

# ── In-memory ticket store (bounded OrderedDict) ─────────────────────────────
_MAX_TICKETS = 10_000
_ticket_store: OrderedDict[str, TicketRecord] = OrderedDict()
_ticket_lock = threading.Lock()
_ticket_counter: Dict[str, int] = {}

# IST timezone offset (+5:30)
_IST = timezone(timedelta(hours=5, minutes=30))


def _generate_ticket_id(department_id: str) -> str:
    """Generate a unique AMC-format ticket ID.

    Format: AMC-{YEAR}-{DEPT_CODE}-{SEQUENCE}
    Example: AMC-2025-RD-00042
    """
    dept_code_map = {
        "ROADS_NW": "RD",
        "WATER_SW": "WS",
        "SOLID_WASTE": "SW",
        "ELECTRICAL": "EL",
    }
    code = dept_code_map.get(department_id, "GN")
    year = datetime.now(_IST).year

    key = f"{year}-{code}"
    with _ticket_lock:
        _ticket_counter[key] = _ticket_counter.get(key, 0) + 1
        seq = _ticket_counter[key]

    return f"AMC-{year}-{code}-{seq:05d}"


def _build_timeline(
    status: TicketStatus,
    created_at: datetime,
    department_name: str,
    officer_name: str,
) -> List[dict]:
    """Build a realistic status timeline for the ticket."""
    timeline = [
        {
            "step": 1,
            "title": "Reported & AI Verified",
            "description": (
                "Citizen photograph scanned via AMC Vision-LLM. "
                "Issue classified and severity assessed automatically."
            ),
            "timestamp": created_at.isoformat(),
            "status": "completed",
        },
        {
            "step": 2,
            "title": f"Assigned to {department_name}",
            "description": (
                f"Automated jurisdiction matching assigned the incident ticket "
                f"to duty nodal engineer {officer_name}."
            ),
            "timestamp": (created_at + timedelta(minutes=1)).isoformat(),
            "status": "completed",
        },
    ]

    if status in (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED):
        timeline.append({
            "step": 3,
            "title": "Crew Dispatched",
            "description": "Quick Response Team dispatched to site.",
            "timestamp": (created_at + timedelta(hours=1)).isoformat(),
            "status": "completed" if status == TicketStatus.RESOLVED else "in_progress",
        })

    if status == TicketStatus.RESOLVED:
        timeline.append({
            "step": 4,
            "title": "Work Completed & Citizen Sign-off",
            "description": "Repair completed. Photo verification uploaded.",
            "timestamp": (created_at + timedelta(hours=4)).isoformat(),
            "status": "completed",
        })
    else:
        timeline.append({
            "step": 3 if len(timeline) == 2 else 4,
            "title": "Crew Dispatch & Repair",
            "description": "Awaiting crew dispatch to incident site.",
            "timestamp": "",
            "status": "pending",
        })

    return timeline


def create_ticket(
    citizen_name: str,
    phone: str,
    area_or_address: str,
    description: str,
    image_analysis: ImageAnalysisResult,
    ward_lookup: WardLookupResult,
    department: DepartmentAssignment,
) -> TicketRecord:
    """Agent Tool: Create a new civic complaint ticket.

    Args:
        citizen_name: Name of the reporting citizen.
        phone: Contact phone number.
        area_or_address: Location of the incident.
        description: Free-text description.
        image_analysis: Output from vision analyzer.
        ward_lookup: Output from ward resolver.
        department: Output from department router.

    Returns:
        TicketRecord with full ticket details and tracking ID.
    """
    ticket_id = _generate_ticket_id(department.department_id)
    now = datetime.now(_IST)
    resolution_eta = now + timedelta(hours=department.sla_hours)

    status = TicketStatus.ASSIGNED
    timeline = _build_timeline(
        status, now, department.department_name, ward_lookup.officer_name,
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        citizen_name=citizen_name,
        phone=phone,
        area_or_address=area_or_address,
        description=description,
        issue_type=image_analysis.detected_class.value,
        severity=image_analysis.severity,
        severity_label=image_analysis.severity_label,
        urgency=department.urgency.value,
        ward_id=ward_lookup.ward_id,
        ward_name=ward_lookup.ward_name,
        zone_name=ward_lookup.zone_name,
        department_id=department.department_id,
        department_name=department.department_name,
        sla_hours=department.sla_hours,
        officer_name=ward_lookup.officer_name,
        officer_phone=ward_lookup.officer_phone,
        status=status,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        resolution_eta=resolution_eta.isoformat(),
        timeline=timeline,
    )

    # Store with LRU eviction
    with _ticket_lock:
        if len(_ticket_store) >= _MAX_TICKETS:
            _ticket_store.popitem(last=False)
        _ticket_store[ticket_id] = ticket

    logger.info("Ticket created: %s for %s", ticket_id, area_or_address)
    return ticket


def get_ticket(ticket_id: str) -> Optional[TicketRecord]:
    """Agent Tool: Retrieve a ticket by its tracking ID.

    Args:
        ticket_id: The AMC tracking token.

    Returns:
        TicketRecord if found, None otherwise.
    """
    with _ticket_lock:
        return _ticket_store.get(ticket_id)


def get_all_tickets() -> List[TicketRecord]:
    """Return all tickets in the store (newest first)."""
    with _ticket_lock:
        return list(reversed(_ticket_store.values()))


def update_ticket_status(
    ticket_id: str,
    new_status: TicketStatus,
) -> Optional[TicketRecord]:
    """Update a ticket's status and refresh the timeline.

    Args:
        ticket_id: The AMC tracking token.
        new_status: New lifecycle status.

    Returns:
        Updated TicketRecord if found, None otherwise.
    """
    with _ticket_lock:
        ticket = _ticket_store.get(ticket_id)
        if ticket is None:
            return None

        now = datetime.now(_IST)
        updated = ticket.model_copy(update={
            "status": new_status,
            "updated_at": now.isoformat(),
            "timeline": _build_timeline(
                new_status,
                datetime.fromisoformat(ticket.created_at),
                ticket.department_name,
                ticket.officer_name,
            ),
        })
        _ticket_store[ticket_id] = updated

    logger.info("Ticket %s updated to %s", ticket_id, new_status.value)
    return updated


def clear_store() -> None:
    """Reset the ticket store — used in tests to prevent cross-contamination."""
    with _ticket_lock:
        _ticket_store.clear()
        _ticket_counter.clear()
