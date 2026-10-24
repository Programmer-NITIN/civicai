"""
tests/test_ticket_manager.py
------------------------------
Tests for the ticket lifecycle manager (Agent Tool #4).
Validates ticket creation, retrieval, status updates, and store boundaries.
"""

from app.civic_engine.ticket_manager import (
    create_ticket, get_ticket, get_all_tickets,
    update_ticket_status, clear_store,
)
from app.civic_engine.vision_analyzer import analyze_image
from app.civic_engine.ward_resolver import resolve_ward
from app.civic_engine.department_router import assign_department
from app.models.complaint_models import TicketStatus, IssueType


def _create_test_ticket(issue_type=IssueType.POTHOLE, area="SG Highway, Bodakdev"):
    """Helper to create a ticket through the full agent pipeline."""
    image = analyze_image("test.jpg", issue_type_override=issue_type)
    ward = resolve_ward(area)
    dept = assign_department(issue_type)
    return create_ticket(
        citizen_name="Test User",
        phone="9825012345",
        area_or_address=area,
        description="Test complaint",
        image_analysis=image,
        ward_lookup=ward,
        department=dept,
    )


class TestTicketCreation:
    def test_creates_ticket(self):
        ticket = _create_test_ticket()
        assert ticket.ticket_id.startswith("AMC-")

    def test_ticket_has_assigned_status(self):
        ticket = _create_test_ticket()
        assert ticket.status == TicketStatus.ASSIGNED

    def test_ticket_has_citizen_data(self):
        ticket = _create_test_ticket()
        assert ticket.citizen_name == "Test User"
        assert ticket.phone == "9825012345"

    def test_ticket_has_ward(self):
        ticket = _create_test_ticket()
        assert ticket.ward_id == "W08"
        assert ticket.ward_name == "Bodakdev"

    def test_ticket_has_department(self):
        ticket = _create_test_ticket()
        assert ticket.department_name == "Roads & Buildings"

    def test_ticket_has_timestamps(self):
        ticket = _create_test_ticket()
        assert ticket.created_at is not None
        assert ticket.updated_at is not None
        assert ticket.resolution_eta is not None

    def test_ticket_has_timeline(self):
        ticket = _create_test_ticket()
        assert len(ticket.timeline) >= 2

    def test_sequential_ticket_ids(self):
        t1 = _create_test_ticket()
        t2 = _create_test_ticket()
        assert t1.ticket_id != t2.ticket_id

    def test_department_code_in_id(self):
        ticket = _create_test_ticket(issue_type=IssueType.GARBAGE_DUMP,
                                      area="Kankaria, Maninagar")
        assert "-SW-" in ticket.ticket_id

    def test_water_department_code(self):
        ticket = _create_test_ticket(issue_type=IssueType.WATER_LOGGING,
                                      area="C.G. Road, Navrangpura")
        assert "-WS-" in ticket.ticket_id

    def test_electrical_department_code(self):
        ticket = _create_test_ticket(issue_type=IssueType.STREETLIGHT_OFF,
                                      area="Thaltej")
        assert "-EL-" in ticket.ticket_id


class TestTicketRetrieval:
    def test_get_existing_ticket(self):
        ticket = _create_test_ticket()
        found = get_ticket(ticket.ticket_id)
        assert found is not None
        assert found.ticket_id == ticket.ticket_id

    def test_get_nonexistent_ticket(self):
        assert get_ticket("AMC-9999-XX-99999") is None

    def test_get_all_tickets_empty(self):
        tickets = get_all_tickets()
        assert isinstance(tickets, list)

    def test_get_all_tickets_has_items(self):
        _create_test_ticket()
        _create_test_ticket()
        tickets = get_all_tickets()
        assert len(tickets) >= 2

    def test_newest_first_ordering(self):
        t1 = _create_test_ticket()
        t2 = _create_test_ticket()
        tickets = get_all_tickets()
        assert tickets[0].ticket_id == t2.ticket_id


class TestTicketStatusUpdate:
    def test_update_to_in_progress(self):
        ticket = _create_test_ticket()
        updated = update_ticket_status(ticket.ticket_id, TicketStatus.IN_PROGRESS)
        assert updated is not None
        assert updated.status == TicketStatus.IN_PROGRESS

    def test_update_to_resolved(self):
        ticket = _create_test_ticket()
        updated = update_ticket_status(ticket.ticket_id, TicketStatus.RESOLVED)
        assert updated is not None
        assert updated.status == TicketStatus.RESOLVED

    def test_update_refreshes_timeline(self):
        ticket = _create_test_ticket()
        updated = update_ticket_status(ticket.ticket_id, TicketStatus.RESOLVED)
        assert len(updated.timeline) > len(ticket.timeline)

    def test_update_nonexistent_returns_none(self):
        result = update_ticket_status("AMC-9999-XX-99999", TicketStatus.RESOLVED)
        assert result is None

    def test_update_changes_updated_at(self):
        ticket = _create_test_ticket()
        updated = update_ticket_status(ticket.ticket_id, TicketStatus.IN_PROGRESS)
        assert updated.updated_at >= ticket.updated_at


class TestStoreBoundaries:
    def test_clear_store(self):
        _create_test_ticket()
        assert len(get_all_tickets()) > 0
        clear_store()
        assert len(get_all_tickets()) == 0
