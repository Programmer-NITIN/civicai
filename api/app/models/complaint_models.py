"""
models/complaint_models.py
----------------------------
Pydantic schemas for complaint request/response payloads.

Security bounds:
- citizen_name:    max 100 chars.
- area_or_address: max 200 chars — bounded to prevent log injection.
- description:     max 1000 chars — free-text field with length cap.
- phone:           max 15 chars — E.164 phone number format.
- ticket_id:       max 30 chars — bounded token for status lookups.
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class IssueType(str, Enum):
    """Detected or user-specified civic issue category."""

    POTHOLE = "pothole"
    ROAD_DAMAGE = "road_damage"
    GARBAGE_DUMP = "garbage_dump"
    WATER_LOGGING = "water_logging"
    PIPE_BURST = "pipe_burst"
    STREETLIGHT_OFF = "streetlight_off"
    BROKEN_POLE = "broken_pole"
    SEWAGE_OVERFLOW = "sewage_overflow"


class TicketStatus(str, Enum):
    """Lifecycle state of a civic complaint ticket."""

    LOGGED = "logged"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class UrgencyLevel(str, Enum):
    """Urgency classification for SLA routing."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class ImageAnalysisResult(BaseModel):
    """Output of the vision engine's image classification tool."""

    detected_class: IssueType
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Classification confidence (0.0–1.0)",
    )
    severity: int = Field(
        ..., ge=1, le=5,
        description="Hazard severity (1=minor, 5=critical)",
    )
    severity_label: str
    description: str = Field(
        ..., max_length=500,
        description="Human-readable assessment of the detected issue",
    )
    road_category: str = ""


class WardLookupResult(BaseModel):
    """Output of the GIS ward boundary resolution tool."""

    ward_id: str
    ward_name: str
    zone_name: str
    pincode: str
    officer_name: str
    officer_designation: str
    officer_phone: str
    resolution_method: str = Field(
        default="area_name_match",
        description="How the ward was resolved: gps_match, area_name_match",
    )


class DepartmentAssignment(BaseModel):
    """Output of the department SLA routing tool."""

    department_id: str
    department_name: str
    division: str
    nodal_officer: str
    helpline: str
    sla_hours: int
    urgency: UrgencyLevel
    repair_unit: str


class ComplaintRequest(BaseModel):
    """Inbound complaint filing request."""

    citizen_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the reporting citizen",
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        pattern=r"^\+?[0-9]{10,15}$",
        description="Contact phone in E.164 or 10-digit format",
    )
    area_or_address: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Area name, landmark, or street address for ward lookup",
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional free-text description of the issue",
    )
    latitude: Optional[float] = Field(
        None, ge=-90.0, le=90.0,
        description="GPS latitude from photo EXIF or device",
    )
    longitude: Optional[float] = Field(
        None, ge=-180.0, le=180.0,
        description="GPS longitude from photo EXIF or device",
    )
    issue_type: Optional[IssueType] = Field(
        None,
        description="Manual override if no photo is uploaded",
    )


class TicketRecord(BaseModel):
    """Full ticket record stored in the complaint database."""

    ticket_id: str
    citizen_name: str
    phone: str
    area_or_address: str
    description: str
    issue_type: str
    severity: int
    severity_label: str
    urgency: str
    ward_id: str
    ward_name: str
    zone_name: str
    department_id: str
    department_name: str
    sla_hours: int
    officer_name: str
    officer_phone: str
    status: TicketStatus
    created_at: str
    updated_at: str
    resolution_eta: str
    timeline: List[dict] = Field(default_factory=list)


class ComplaintResponse(BaseModel):
    """Response after filing a complaint — includes tracking token."""

    ticket_id: str
    status: str
    message: str
    image_analysis: Optional[ImageAnalysisResult] = None
    ward_lookup: Optional[WardLookupResult] = None
    department: Optional[DepartmentAssignment] = None
    sla_hours: int
    created_at: str
    resolution_eta: str
    agent_trace: List[dict] = Field(
        default_factory=list,
        description="Ordered list of agent tool calls with latencies",
    )


class StatusRequest(BaseModel):
    """Inbound request for ticket status lookup."""

    ticket_id: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="The AMC tracking token (e.g. AMC-2025-RD-88421)",
    )


class StatusResponse(BaseModel):
    """Full ticket status with timeline and tracking info."""

    ticket: TicketRecord
    agent_trace: List[dict] = Field(
        default_factory=list,
        description="Tool execution trace for this lookup",
    )
