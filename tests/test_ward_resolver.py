"""
tests/test_ward_resolver.py
-----------------------------
Tests for the GIS ward boundary resolution engine (Agent Tool #2).
Validates area-name matching, GPS resolution, and fallback behavior.
"""

from app.civic_engine.ward_resolver import resolve_ward, _find_by_area_name, _find_by_gps


class TestAreaNameResolution:
    def test_exact_landmark_match(self):
        assert _find_by_area_name("SG Highway") == "W08"

    def test_case_insensitive_match(self):
        assert _find_by_area_name("sg highway") == "W08"

    def test_substring_match(self):
        assert _find_by_area_name("Near SG Highway Bodakdev") == "W08"

    def test_navrangpura_match(self):
        assert _find_by_area_name("C.G. Road, Navrangpura") == "W12"

    def test_maninagar_match(self):
        assert _find_by_area_name("Kankaria Lake, Maninagar") == "W24"

    def test_thaltej_match(self):
        assert _find_by_area_name("Thaltej Cross Road") == "W09"

    def test_satellite_match(self):
        assert _find_by_area_name("Satellite Road") == "W15"

    def test_vastral_match(self):
        assert _find_by_area_name("Vastral") == "W30"

    def test_chandkheda_match(self):
        assert _find_by_area_name("Motera Stadium, Chandkheda") == "W42"

    def test_dariapur_match(self):
        assert _find_by_area_name("Relief Road, Old City") == "W03"

    def test_unknown_returns_none(self):
        assert _find_by_area_name("Completely Unknown Location XYZ") is None

    def test_ward_name_direct_match(self):
        assert _find_by_area_name("Bodakdev") == "W08"


class TestGPSResolution:
    def test_bodakdev_coordinates(self):
        assert _find_by_gps(23.0487, 72.5074) == "W08"

    def test_navrangpura_coordinates(self):
        assert _find_by_gps(23.0350, 72.5610) == "W12"

    def test_maninagar_coordinates(self):
        assert _find_by_gps(23.0070, 72.6040) == "W24"

    def test_vastral_coordinates(self):
        ward = _find_by_gps(22.9930, 72.6480)
        assert ward == "W30"


class TestResolveWard:
    def test_area_name_resolution(self):
        result = resolve_ward("Pakwan Cross Road, Bodakdev")
        assert result.ward_id == "W08"
        assert result.ward_name == "Bodakdev"
        assert result.zone_name == "North West Zone"
        assert result.resolution_method == "area_name_match"

    def test_gps_fallback(self):
        result = resolve_ward("Unknown Area XYZ", latitude=23.0487, longitude=72.5074)
        assert result.ward_id == "W08"
        assert result.resolution_method == "gps_nearest"

    def test_default_fallback(self):
        result = resolve_ward("Completely Unknown Location")
        assert result.ward_id == "W08"  # Default ward
        assert result.resolution_method == "default_fallback"

    def test_result_has_officer(self):
        result = resolve_ward("SG Highway, Bodakdev")
        assert result.officer_name == "R. V. Patel"
        assert len(result.officer_phone) > 0

    def test_result_has_pincode(self):
        result = resolve_ward("SG Highway, Bodakdev")
        assert result.pincode == "380054"

    def test_result_has_designation(self):
        result = resolve_ward("Bodakdev")
        assert len(result.officer_designation) > 0
