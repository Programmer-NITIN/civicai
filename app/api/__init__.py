"""
api/__init__.py
----------------
Re-exports all API route modules.
"""

from app.api import routes_health  # noqa: F401
from app.api import routes_complaint  # noqa: F401
from app.api import routes_status  # noqa: F401
from app.api import routes_wards  # noqa: F401
