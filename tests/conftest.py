"""
conftest.py
-----------
Shared test configuration, fixtures, and helpers for the CivicAI test suite.

Design:
- Provides pre-configured test client for API integration tests.
- Resets rate limiter state between test modules to prevent cross-contamination.
- Resets ticket store between tests for isolation.
- Centralizes common test data so test files stay DRY and consistent.
- Registers custom markers for selective test execution.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.rate_limiter import (
    complaint_rate_limit,
    status_rate_limit,
    upload_rate_limit,
)
from app.civic_engine.ticket_manager import clear_store


# ── Client Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client() -> TestClient:
    """Shared test client for the entire session."""
    return TestClient(app)


# ── Rate Limiter & Store Reset ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_state():
    """Resets all rate limiter stores and ticket store between tests."""
    complaint_rate_limit.store.clear()
    status_rate_limit.store.clear()
    upload_rate_limit.store.clear()
    clear_store()
    yield
    complaint_rate_limit.store.clear()
    status_rate_limit.store.clear()
    upload_rate_limit.store.clear()
    clear_store()


# ── Shared Test Data ─────────────────────────────────────────────────────────

@pytest.fixture()
def valid_complaint() -> dict:
    """Returns a valid complaint payload for filing tests."""
    return {
        "citizen_name": "Test Citizen",
        "phone": "9825012345",
        "area_or_address": "Pakwan Cross Road, SG Highway, Bodakdev",
        "description": "Deep pothole near service lane",
        "issue_type": "pothole",
    }


@pytest.fixture()
def valid_garbage_complaint() -> dict:
    """Returns a valid garbage complaint payload."""
    return {
        "citizen_name": "Amit Patel",
        "phone": "8765432109",
        "area_or_address": "Kankaria Lake Gate, Maninagar",
        "description": "Large garbage dump near residential area",
        "issue_type": "garbage_dump",
    }


@pytest.fixture()
def nav_headers() -> dict[str, str]:
    """Returns headers with a unique forwarded IP for rate-limiter isolation."""
    return {"X-Forwarded-For": "10.203.0.1"}
