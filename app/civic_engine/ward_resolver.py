"""
civic_engine/ward_resolver.py
-------------------------------
Agent Tool #2: GIS Ward Boundary Resolution.

Resolves a citizen-provided area name or GPS coordinates to the
correct AMC ward using the AREA_TO_WARD lookup table and
WARD_REGISTRY data.

Design:
  - resolve_ward() is the single entry point.
  - Supports two resolution methods:
    1. area_name_match: fuzzy substring matching against ward landmarks.
    2. gps_nearest: Euclidean distance to ward centroids (when coords given).
  - Returns a WardLookupResult Pydantic model.
"""

import math
import logging
from typing import Optional

from app.config_data import WARD_REGISTRY, AREA_TO_WARD
from app.models.complaint_models import WardLookupResult

logger = logging.getLogger(__name__)

# Default ward when resolution fails — Bodakdev (most common complaint area)
_DEFAULT_WARD_ID = "W08"


def _find_by_area_name(area: str) -> Optional[str]:
    """Attempt to resolve ward from area name via substring matching.

    Checks exact match first, then tries substring containment
    against all registered landmarks.
    """
    area_lower = area.lower().strip()

    # 1. Exact match in the precomputed lookup
    if area_lower in AREA_TO_WARD:
        return AREA_TO_WARD[area_lower]

    # 2. Substring match — area contains a known landmark
    for landmark, ward_id in AREA_TO_WARD.items():
        if landmark in area_lower or area_lower in landmark:
            return ward_id

    # 3. Try matching against ward names directly
    for ward_id, ward_data in WARD_REGISTRY.items():
        if ward_data["ward_name"].lower() in area_lower:
            return ward_id
        if area_lower in ward_data["ward_name"].lower():
            return ward_id

    return None


def _find_by_gps(lat: float, lng: float) -> str:
    """Resolve ward by nearest Euclidean distance to ward centroids.

    Uses simple Euclidean distance on lat/lng which is sufficient
    for intra-city resolution where curvature is negligible.
    """
    best_ward = _DEFAULT_WARD_ID
    best_distance = float("inf")

    for ward_id, ward_data in WARD_REGISTRY.items():
        coords = ward_data["coordinates"]
        distance = math.sqrt(
            (lat - coords["lat"]) ** 2 + (lng - coords["lng"]) ** 2
        )
        if distance < best_distance:
            best_distance = distance
            best_ward = ward_id

    return best_ward


def resolve_ward(
    area_or_address: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> WardLookupResult:
    """Agent Tool: Resolve area/GPS to AMC ward.

    Args:
        area_or_address: Area name, landmark, or street address.
        latitude: Optional GPS latitude.
        longitude: Optional GPS longitude.

    Returns:
        WardLookupResult with ward details and resolution method.
    """
    resolution_method = "area_name_match"
    ward_id = None

    # Try area name resolution first (most common path)
    ward_id = _find_by_area_name(area_or_address)

    # Fall back to GPS if area name didn't resolve
    if ward_id is None and latitude is not None and longitude is not None:
        ward_id = _find_by_gps(latitude, longitude)
        resolution_method = "gps_nearest"

    # Final fallback
    if ward_id is None:
        ward_id = _DEFAULT_WARD_ID
        resolution_method = "default_fallback"
        logger.warning(
            "Ward resolution failed for '%s' — using default %s",
            area_or_address, _DEFAULT_WARD_ID,
        )

    ward = WARD_REGISTRY[ward_id]

    result = WardLookupResult(
        ward_id=ward_id,
        ward_name=ward["ward_name"],
        zone_name=ward["zone_name"],
        pincode=ward["pincode"],
        officer_name=ward["officer_name"],
        officer_designation=ward["officer_designation"],
        officer_phone=ward["officer_phone"],
        resolution_method=resolution_method,
    )

    logger.info(
        "Ward resolved: %s (%s) via %s",
        ward["ward_name"], ward["zone_name"], resolution_method,
    )

    return result
