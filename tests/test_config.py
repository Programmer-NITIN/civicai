"""
tests/test_config.py
---------------------
Tests for configuration validation and settings parsing.
"""

from app.config import Settings
from app.config_data import (
    WARD_REGISTRY, DEPARTMENT_REGISTRY, ISSUE_CLASSIFICATION,
    AREA_TO_WARD, get_severity_label,
)


class TestSettingsParsing:
    def test_debug_true_string(self):
        s = Settings(debug="true")
        assert s.debug is True

    def test_debug_false_string(self):
        s = Settings(debug="false")
        assert s.debug is False

    def test_debug_yes_string(self):
        s = Settings(debug="yes")
        assert s.debug is True

    def test_debug_1_string(self):
        s = Settings(debug="1")
        assert s.debug is True

    def test_debug_0_string(self):
        s = Settings(debug="0")
        assert s.debug is False

    def test_default_app_name(self):
        s = Settings()
        assert "CivicAI" in s.app_name

    def test_default_version(self):
        s = Settings()
        assert s.app_version == "1.0.0"

    def test_origins_list_input(self):
        s = Settings(allowed_origins_raw=["https://a.com", "https://b.com"])
        assert s.allowed_origins == ["https://a.com", "https://b.com"]


class TestWardRegistry:
    def test_registry_not_empty(self):
        assert len(WARD_REGISTRY) > 0

    def test_all_wards_have_required_fields(self):
        required = {"ward_id", "ward_name", "zone_name", "pincode",
                     "officer_name", "landmarks", "coordinates"}
        for ward_id, data in WARD_REGISTRY.items():
            for field in required:
                assert field in data, f"Ward {ward_id} missing {field}"

    def test_all_wards_have_coordinates(self):
        for ward_id, data in WARD_REGISTRY.items():
            coords = data["coordinates"]
            assert "lat" in coords and "lng" in coords

    def test_ward_ids_match_keys(self):
        for ward_id, data in WARD_REGISTRY.items():
            assert data["ward_id"] == ward_id


class TestDepartmentRegistry:
    def test_registry_not_empty(self):
        assert len(DEPARTMENT_REGISTRY) > 0

    def test_all_depts_have_required_fields(self):
        required = {"department_id", "department_name", "sla_hours",
                     "nodal_officer", "helpline", "scope"}
        for dept_id, data in DEPARTMENT_REGISTRY.items():
            for field in required:
                assert field in data, f"Dept {dept_id} missing {field}"

    def test_sla_hours_positive(self):
        for dept_id, data in DEPARTMENT_REGISTRY.items():
            assert data["sla_hours"] > 0


class TestIssueClassification:
    def test_not_empty(self):
        assert len(ISSUE_CLASSIFICATION) > 0

    def test_all_have_department(self):
        for key, data in ISSUE_CLASSIFICATION.items():
            assert data["department_id"] in DEPARTMENT_REGISTRY

    def test_severity_range(self):
        for key, data in ISSUE_CLASSIFICATION.items():
            assert 1 <= data["severity"] <= 5


class TestAreaToWardLookup:
    def test_lookup_populated(self):
        assert len(AREA_TO_WARD) > 0

    def test_all_values_are_valid_wards(self):
        for area, ward_id in AREA_TO_WARD.items():
            assert ward_id in WARD_REGISTRY


class TestSeverityLabel:
    def test_critical(self):
        assert get_severity_label(5) == "CRITICAL"

    def test_urgent(self):
        assert get_severity_label(4) == "URGENT"

    def test_high(self):
        assert get_severity_label(3) == "HIGH"

    def test_normal(self):
        assert get_severity_label(2) == "NORMAL"

    def test_low(self):
        assert get_severity_label(1) == "LOW"
