"""
civic_engine/vision_analyzer.py
---------------------------------
Agent Tool #1: Multimodal Vision Hazard Triage.

Classifies uploaded civic complaint images into issue categories
with severity scores. Uses a deterministic mock classifier that
simulates Gemini Vision output for zero-dependency local runs.

Design:
  - analyse_image() is the single entry point.
  - Uses filename heuristics and random-seeded confidence to produce
    realistic but deterministic mock output.
  - When GEMINI_API_KEY is set, could be extended to call real Vision API.
  - Returns an ImageAnalysisResult Pydantic model.
"""

import hashlib
import logging
from typing import Optional

from app.config import settings
from app.config_data import ISSUE_CLASSIFICATION, get_severity_label
from app.models.complaint_models import ImageAnalysisResult, IssueType

logger = logging.getLogger(__name__)

# ── Keyword → IssueType mapping for filename/description heuristics ──────────
_KEYWORD_MAP = {
    # Ordered by specificity — more specific keywords MUST come before generic
    # ones to prevent false matches (e.g. "road" matching before "streetlight").
    "pothole": IssueType.POTHOLE,
    "pot_hole": IssueType.POTHOLE,
    "asphalt": IssueType.POTHOLE,
    "waterlog": IssueType.WATER_LOGGING,
    "water_logging": IssueType.WATER_LOGGING,
    "water": IssueType.WATER_LOGGING,
    "flood": IssueType.WATER_LOGGING,
    "logging": IssueType.WATER_LOGGING,
    "pipe": IssueType.PIPE_BURST,
    "burst": IssueType.PIPE_BURST,
    "leak": IssueType.PIPE_BURST,
    "streetlight": IssueType.STREETLIGHT_OFF,
    "street_light": IssueType.STREETLIGHT_OFF,
    "lamp": IssueType.STREETLIGHT_OFF,
    "light": IssueType.STREETLIGHT_OFF,
    "sewage": IssueType.SEWAGE_OVERFLOW,
    "sewer": IssueType.SEWAGE_OVERFLOW,
    "drain": IssueType.SEWAGE_OVERFLOW,
    "garbage": IssueType.GARBAGE_DUMP,
    "waste": IssueType.GARBAGE_DUMP,
    "trash": IssueType.GARBAGE_DUMP,
    "dump": IssueType.GARBAGE_DUMP,
    "debris": IssueType.GARBAGE_DUMP,
    "pole": IssueType.BROKEN_POLE,
    "road": IssueType.ROAD_DAMAGE,
    "crack": IssueType.ROAD_DAMAGE,
}

# ── Road category classifier (based on area keywords) ────────────────────────
_ROAD_CATEGORIES = {
    "highway": "Major Arterial (TP 50)",
    "sg highway": "Major Arterial (TP 50)",
    "ring road": "Ring Road Arterial",
    "cross road": "Collector Road",
    "main road": "Collector Road",
    "service lane": "Local Service Road",
    "gali": "Internal Ward Road",
    "society": "Internal Society Road",
}


def _classify_from_text(text: str) -> Optional[IssueType]:
    """Attempt to classify issue type from filename or description text."""
    text_lower = text.lower()
    for keyword, issue_type in _KEYWORD_MAP.items():
        if keyword in text_lower:
            return issue_type
    return None


def _compute_confidence(filename: str, issue_type: str) -> float:
    """Produce a deterministic confidence score from the filename hash.

    Uses SHA-256 to ensure same file always gets same confidence,
    but different files get different-looking scores. Range: 0.85–0.99.
    """
    digest = hashlib.sha256(f"{filename}:{issue_type}".encode()).hexdigest()
    # Take first 4 hex chars → 0–65535 → normalize to 0.85–0.99
    raw = int(digest[:4], 16)
    return round(0.85 + (raw / 65535) * 0.14, 4)


def _detect_road_category(address: str) -> str:
    """Detect road category from address text."""
    address_lower = address.lower()
    for keyword, category in _ROAD_CATEGORIES.items():
        if keyword in address_lower:
            return category
    return "Municipal Ward Road"


def analyze_image(
    filename: str,
    description: str = "",
    address: str = "",
    issue_type_override: Optional[IssueType] = None,
) -> ImageAnalysisResult:
    """Agent Tool: Classify a civic complaint image.

    Args:
        filename: Original filename of the uploaded image.
        description: Optional citizen-provided description for context.
        address: Area/address string for road category detection.
        issue_type_override: Manual override if citizen specifies issue type.

    Returns:
        ImageAnalysisResult with classification, confidence, and severity.
    """
    # Priority: manual override → filename heuristic → description heuristic
    detected = issue_type_override
    if detected is None:
        detected = _classify_from_text(filename)
    if detected is None and description:
        detected = _classify_from_text(description)
    if detected is None:
        detected = IssueType.POTHOLE  # Default fallback

    # Look up classification rules
    classification = ISSUE_CLASSIFICATION.get(
        detected.value,
        ISSUE_CLASSIFICATION["pothole"],
    )

    confidence = _compute_confidence(filename, detected.value)
    road_category = _detect_road_category(address or filename)

    result = ImageAnalysisResult(
        detected_class=detected,
        confidence=confidence,
        severity=classification["severity"],
        severity_label=get_severity_label(classification["severity"]),
        description=(
            f"{classification['label']} detected with "
            f"{confidence * 100:.1f}% confidence. "
            f"Severity Level {classification['severity']}/{classification['max_severity']} "
            f"({classification['urgency']}). "
            f"Recommended repair unit: {classification['repair_unit']}."
        ),
        road_category=road_category,
    )

    logger.info(
        "Vision analysis: class=%s confidence=%.2f severity=%d",
        detected.value, confidence, classification["severity"],
    )

    return result
