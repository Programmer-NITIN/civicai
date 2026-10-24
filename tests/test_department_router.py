"""
tests/test_department_router.py
---------------------------------
Tests for the department SLA routing engine (Agent Tool #3).
Validates issue-to-department mapping, SLA values, and urgency levels.
"""

from app.civic_engine.department_router import assign_department
from app.models.complaint_models import IssueType, UrgencyLevel


class TestDepartmentAssignment:
    def test_pothole_routes_to_roads(self):
        result = assign_department(IssueType.POTHOLE)
        assert result.department_name == "Roads & Buildings"

    def test_road_damage_routes_to_roads(self):
        result = assign_department(IssueType.ROAD_DAMAGE)
        assert result.department_name == "Roads & Buildings"

    def test_garbage_routes_to_solid_waste(self):
        result = assign_department(IssueType.GARBAGE_DUMP)
        assert result.department_name == "Solid Waste & Health"

    def test_water_logging_routes_to_water(self):
        result = assign_department(IssueType.WATER_LOGGING)
        assert result.department_name == "Water & Sewerage"

    def test_pipe_burst_routes_to_water(self):
        result = assign_department(IssueType.PIPE_BURST)
        assert result.department_name == "Water & Sewerage"

    def test_streetlight_routes_to_electrical(self):
        result = assign_department(IssueType.STREETLIGHT_OFF)
        assert result.department_name == "Streetlight & Electrical"

    def test_broken_pole_routes_to_electrical(self):
        result = assign_department(IssueType.BROKEN_POLE)
        assert result.department_name == "Streetlight & Electrical"

    def test_sewage_routes_to_water(self):
        result = assign_department(IssueType.SEWAGE_OVERFLOW)
        assert result.department_name == "Water & Sewerage"


class TestSLAValues:
    def test_pothole_sla_24h(self):
        result = assign_department(IssueType.POTHOLE)
        assert result.sla_hours == 24

    def test_garbage_sla_12h(self):
        result = assign_department(IssueType.GARBAGE_DUMP)
        assert result.sla_hours == 12

    def test_pipe_burst_sla_6h(self):
        result = assign_department(IssueType.PIPE_BURST)
        assert result.sla_hours == 6

    def test_sewage_sla_6h(self):
        result = assign_department(IssueType.SEWAGE_OVERFLOW)
        assert result.sla_hours == 6

    def test_streetlight_sla_24h(self):
        result = assign_department(IssueType.STREETLIGHT_OFF)
        assert result.sla_hours == 24


class TestUrgencyLevels:
    def test_pothole_urgent(self):
        result = assign_department(IssueType.POTHOLE)
        assert result.urgency == UrgencyLevel.URGENT

    def test_pipe_burst_critical(self):
        result = assign_department(IssueType.PIPE_BURST)
        assert result.urgency == UrgencyLevel.CRITICAL

    def test_streetlight_normal(self):
        result = assign_department(IssueType.STREETLIGHT_OFF)
        assert result.urgency == UrgencyLevel.NORMAL

    def test_garbage_high(self):
        result = assign_department(IssueType.GARBAGE_DUMP)
        assert result.urgency == UrgencyLevel.HIGH


class TestResultStructure:
    def test_has_nodal_officer(self):
        result = assign_department(IssueType.POTHOLE)
        assert len(result.nodal_officer) > 0

    def test_has_helpline(self):
        result = assign_department(IssueType.POTHOLE)
        assert len(result.helpline) > 0

    def test_has_division(self):
        result = assign_department(IssueType.POTHOLE)
        assert len(result.division) > 0

    def test_has_repair_unit(self):
        result = assign_department(IssueType.POTHOLE)
        assert len(result.repair_unit) > 0

    def test_has_department_id(self):
        result = assign_department(IssueType.POTHOLE)
        assert result.department_id == "ROADS_NW"
