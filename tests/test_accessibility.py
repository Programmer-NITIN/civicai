"""
tests/test_accessibility.py
-----------------------------
Smoke tests for WCAG 2.1 AA compliance indicators in the HTML frontend.
"""

import os

# Read the HTML once at module load
_FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
with open(_FRONTEND_PATH, encoding="utf-8") as f:
    _HTML = f.read()


class TestSkipNavigation:
    def test_skip_link_exists(self):
        assert 'class="skip-link"' in _HTML

    def test_skip_link_targets_main(self):
        assert 'href="#main-content"' in _HTML

    def test_main_content_id_exists(self):
        assert 'id="main-content"' in _HTML


class TestAriaLiveRegions:
    def test_sr_announcer_exists(self):
        assert 'id="sr-announcer"' in _HTML
        assert 'aria-live="polite"' in _HTML

    def test_form_error_assertive(self):
        assert 'id="form-error"' in _HTML
        assert 'aria-live="assertive"' in _HTML

    def test_chat_feed_live(self):
        assert 'id="chat-feed"' in _HTML
        assert 'aria-live="polite"' in _HTML


class TestAriaLabels:
    def test_main_navigation_label(self):
        assert 'aria-label="Main Navigation"' in _HTML

    def test_main_content_label(self):
        assert 'aria-label="Civic Complaint Console"' in _HTML

    def test_evidence_upload_label(self):
        assert 'aria-label="Incident Evidence Upload"' in _HTML

    def test_pipeline_label(self):
        assert 'aria-label="Autonomous Agent Resolution Pipeline"' in _HTML

    def test_chat_dialog_role(self):
        assert 'role="dialog"' in _HTML

    def test_chat_assistant_label(self):
        assert 'aria-label="Open CivicAI Assistant"' in _HTML

    def test_chat_close_label(self):
        assert 'aria-label="Close Assistant"' in _HTML

    def test_chat_input_label(self):
        assert 'aria-label="Message the assistant"' in _HTML

    def test_image_upload_label(self):
        assert 'aria-label="Click to upload a photo of the civic issue"' in _HTML

    def test_file_input_label(self):
        assert 'aria-label="Upload photo of civic issue"' in _HTML


class TestFormAccessibility:
    def test_citizen_name_label(self):
        assert 'for="citizen-name"' in _HTML

    def test_phone_label(self):
        assert 'for="citizen-phone"' in _HTML

    def test_area_label(self):
        assert 'for="area-address"' in _HTML

    def test_description_label(self):
        assert 'for="description"' in _HTML

    def test_name_describedby(self):
        assert 'aria-describedby="name-help"' in _HTML

    def test_phone_describedby(self):
        assert 'aria-describedby="phone-help"' in _HTML

    def test_area_describedby(self):
        assert 'aria-describedby="area-help"' in _HTML

    def test_fieldset_legend_exists(self):
        assert '<legend class="sr-only">' in _HTML

    def test_chat_input_maxlength(self):
        assert 'maxlength="500"' in _HTML


class TestHeadingHierarchy:
    def test_single_h1(self):
        count = _HTML.count("<h1")
        assert count == 1, f"Expected 1 <h1>, found {count}"

    def test_h1_has_id(self):
        assert 'id="hero-title"' in _HTML


class TestSemanticsAndSEO:
    def test_lang_attribute(self):
        assert '<html lang="en">' in _HTML

    def test_meta_description(self):
        assert 'name="description"' in _HTML

    def test_title_tag(self):
        assert "<title>" in _HTML
        assert "CivicAI" in _HTML

    def test_meta_viewport(self):
        assert 'name="viewport"' in _HTML

    def test_google_fonts_loaded(self):
        assert "fonts.googleapis.com" in _HTML


class TestReducedMotionCSS:
    """Verify the CSS file includes prefers-reduced-motion support."""

    _CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "css", "style.css")

    def test_reduced_motion_media_query(self):
        with open(self._CSS_PATH, encoding="utf-8") as f:
            css = f.read()
        assert "prefers-reduced-motion" in css

    def test_focus_visible_styles(self):
        with open(self._CSS_PATH, encoding="utf-8") as f:
            css = f.read()
        assert "focus-visible" in css
