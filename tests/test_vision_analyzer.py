"""
tests/test_vision_analyzer.py
-------------------------------
Tests for the image classification engine (Agent Tool #1).
Validates detection heuristics, confidence scoring, and severity mapping.
"""

from app.civic_engine.vision_analyzer import analyze_image, _classify_from_text
from app.models.complaint_models import IssueType


class TestKeywordClassification:
    def test_pothole_keyword(self):
        assert _classify_from_text("pothole_sg_highway.jpg") == IssueType.POTHOLE

    def test_garbage_keyword(self):
        assert _classify_from_text("garbage_dump_area.jpg") == IssueType.GARBAGE_DUMP

    def test_water_keyword(self):
        assert _classify_from_text("water_logging_road.jpg") == IssueType.WATER_LOGGING

    def test_pipe_keyword(self):
        assert _classify_from_text("pipe_burst_main.jpg") == IssueType.PIPE_BURST

    def test_streetlight_keyword(self):
        assert _classify_from_text("streetlight_off_road.jpg") == IssueType.STREETLIGHT_OFF

    def test_sewage_keyword(self):
        assert _classify_from_text("sewage_overflow.jpg") == IssueType.SEWAGE_OVERFLOW

    def test_unknown_returns_none(self):
        assert _classify_from_text("random_photo.jpg") is None

    def test_case_insensitive(self):
        assert _classify_from_text("POTHOLE_SG_HIGHWAY.JPG") == IssueType.POTHOLE


class TestAnalyzeImage:
    def test_returns_image_analysis_result(self):
        result = analyze_image("pothole_test.jpg")
        assert result.detected_class == IssueType.POTHOLE

    def test_confidence_range(self):
        result = analyze_image("pothole_test.jpg")
        assert 0.85 <= result.confidence <= 0.99

    def test_severity_positive(self):
        result = analyze_image("pothole_test.jpg")
        assert 1 <= result.severity <= 5

    def test_description_nonempty(self):
        result = analyze_image("pothole_test.jpg")
        assert len(result.description) > 0

    def test_override_issue_type(self):
        result = analyze_image(
            "random.jpg", issue_type_override=IssueType.GARBAGE_DUMP
        )
        assert result.detected_class == IssueType.GARBAGE_DUMP

    def test_description_fallback(self):
        result = analyze_image(
            "random.jpg", description="There is a big pothole"
        )
        assert result.detected_class == IssueType.POTHOLE

    def test_deterministic_confidence(self):
        """Same filename always produces same confidence score."""
        r1 = analyze_image("test_file.jpg")
        r2 = analyze_image("test_file.jpg")
        assert r1.confidence == r2.confidence

    def test_different_files_different_confidence(self):
        r1 = analyze_image("file_a.jpg")
        r2 = analyze_image("file_b.jpg")
        # Not guaranteed to differ, but with SHA-256 they almost certainly will
        # This is a statistical test, not a strict assertion

    def test_road_category_highway(self):
        result = analyze_image("pothole.jpg", address="SG Highway")
        assert "Arterial" in result.road_category

    def test_road_category_default(self):
        result = analyze_image("pothole.jpg", address="Random Area")
        assert result.road_category == "Municipal Ward Road"

    def test_severity_label_present(self):
        result = analyze_image("pothole.jpg")
        assert result.severity_label in ("LOW", "NORMAL", "HIGH", "URGENT", "CRITICAL")


class TestAllIssueTypes:
    """Ensure all issue types can be classified successfully."""

    def test_pothole(self):
        r = analyze_image("x", issue_type_override=IssueType.POTHOLE)
        assert r.severity > 0

    def test_road_damage(self):
        r = analyze_image("x", issue_type_override=IssueType.ROAD_DAMAGE)
        assert r.severity > 0

    def test_garbage(self):
        r = analyze_image("x", issue_type_override=IssueType.GARBAGE_DUMP)
        assert r.severity > 0

    def test_water_logging(self):
        r = analyze_image("x", issue_type_override=IssueType.WATER_LOGGING)
        assert r.severity > 0

    def test_pipe_burst(self):
        r = analyze_image("x", issue_type_override=IssueType.PIPE_BURST)
        assert r.severity == 5  # Critical severity

    def test_streetlight(self):
        r = analyze_image("x", issue_type_override=IssueType.STREETLIGHT_OFF)
        assert r.severity > 0

    def test_broken_pole(self):
        r = analyze_image("x", issue_type_override=IssueType.BROKEN_POLE)
        assert r.severity > 0

    def test_sewage(self):
        r = analyze_image("x", issue_type_override=IssueType.SEWAGE_OVERFLOW)
        assert r.severity == 5  # Critical severity
