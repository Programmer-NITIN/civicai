"""
civic_engine/department_router.py
-----------------------------------
Agent Tool #3: Department SLA & Field Officer Routing.

Routes a classified civic issue to the correct AMC department
with SLA timelines and field officer assignment.

Design:
  - assign_department() is the single entry point.
  - Uses ISSUE_CLASSIFICATION and DEPARTMENT_REGISTRY for deterministic routing.
  - Returns a DepartmentAssignment Pydantic model.
"""

import logging

from app.config_data import ISSUE_CLASSIFICATION, DEPARTMENT_REGISTRY
from app.models.complaint_models import (
    DepartmentAssignment,
    IssueType,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)

# Default department when issue type is unknown
_DEFAULT_DEPARTMENT_ID = "ROADS_NW"


def assign_department(issue_type: IssueType) -> DepartmentAssignment:
    """Agent Tool: Route issue to the correct AMC department.

    Args:
        issue_type: Classified issue type from vision analysis.

    Returns:
        DepartmentAssignment with department, SLA, and officer details.
    """
    # Look up issue classification rules
    classification = ISSUE_CLASSIFICATION.get(
        issue_type.value,
        ISSUE_CLASSIFICATION["pothole"],
    )

    department_id = classification["department_id"]
    department = DEPARTMENT_REGISTRY.get(
        department_id,
        DEPARTMENT_REGISTRY[_DEFAULT_DEPARTMENT_ID],
    )

    # Parse urgency level safely
    try:
        urgency = UrgencyLevel(classification["urgency"])
    except ValueError:
        urgency = UrgencyLevel.NORMAL

    result = DepartmentAssignment(
        department_id=department["department_id"],
        department_name=department["department_name"],
        division=department["division"],
        nodal_officer=department["nodal_officer"],
        helpline=department["helpline"],
        sla_hours=classification["sla_hours"],
        urgency=urgency,
        repair_unit=classification["repair_unit"],
    )

    logger.info(
        "Department assigned: %s (%s) SLA=%dh urgency=%s",
        department["department_name"],
        department["division"],
        classification["sla_hours"],
        classification["urgency"],
    )

    return result
