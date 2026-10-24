"""
tests/test_api.py
------------------
Integration tests for all API endpoints.
Validates request/response contracts, status codes, and payload structure.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=True)

_VALID_COMPLAINT = {
    "citizen_name": "Test User",
    "phone": "9825012345",
    "area_or_address": "Pakwan Cross Road, SG Highway, Bodakdev",
    "description": "Test pothole complaint",
    "issue_type": "pothole",
}


class TestHealthEndpoint:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_has_status(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_has_version(self):
        data = client.get("/health").json()
        assert "version" in data

    def test_health_has_subsystems(self):
        data = client.get("/health").json()
        assert "subsystems" in data
        assert "vision_ai" in data["subsystems"]
        assert "ticket_store" in data["subsystems"]

    def test_health_subsystem_types(self):
        data = client.get("/health").json()
        assert data["subsystems"]["vision_ai"] in ("mock", "live")
        assert data["subsystems"]["ticket_store"] == "in_memory"


class TestComplaintFiling:
    _headers = {"X-Forwarded-For": "192.168.10.1"}

    def test_file_complaint_returns_200(self):
        resp = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        )
        assert resp.status_code == 200

    def test_file_complaint_returns_ticket_id(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert "ticket_id" in data
        assert data["ticket_id"].startswith("AMC-")

    def test_file_complaint_returns_agent_trace(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert "agent_trace" in data
        assert len(data["agent_trace"]) == 4

    def test_agent_trace_has_latencies(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        for step in data["agent_trace"]:
            assert "latency_ms" in step
            assert "status" in step
            assert step["status"] == "SUCCESS"

    def test_file_complaint_returns_image_analysis(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert data["image_analysis"]["detected_class"] == "pothole"
        assert 0 <= data["image_analysis"]["confidence"] <= 1

    def test_file_complaint_returns_ward(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert data["ward_lookup"]["ward_name"] == "Bodakdev"
        assert data["ward_lookup"]["zone_name"] == "North West Zone"

    def test_file_complaint_returns_department(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert data["department"]["department_name"] == "Roads & Buildings"

    def test_file_garbage_complaint(self):
        payload = {**_VALID_COMPLAINT, "issue_type": "garbage_dump",
                   "area_or_address": "Kankaria Lake, Maninagar"}
        data = client.post(
            "/complaint/file", json=payload, headers=self._headers
        ).json()
        assert data["image_analysis"]["detected_class"] == "garbage_dump"
        assert data["department"]["department_name"] == "Solid Waste & Health"

    def test_file_water_complaint(self):
        payload = {**_VALID_COMPLAINT, "issue_type": "water_logging",
                   "area_or_address": "C.G. Road, Navrangpura"}
        data = client.post(
            "/complaint/file", json=payload, headers=self._headers
        ).json()
        assert data["department"]["department_name"] == "Water & Sewerage"

    def test_file_streetlight_complaint(self):
        payload = {**_VALID_COMPLAINT, "issue_type": "streetlight_off",
                   "area_or_address": "Thaltej Cross Road"}
        data = client.post(
            "/complaint/file", json=payload, headers=self._headers
        ).json()
        assert data["department"]["department_name"] == "Streetlight & Electrical"

    def test_sla_hours_returned(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert data["sla_hours"] > 0

    def test_created_at_present(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        assert "created_at" in data
        assert "resolution_eta" in data


class TestStatusTracking:
    _headers = {"X-Forwarded-For": "192.168.20.1"}

    def test_track_existing_ticket(self):
        # First create a ticket
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        ticket_id = data["ticket_id"]

        # Then track it
        resp = client.post(
            "/status/track",
            json={"ticket_id": ticket_id},
            headers=self._headers,
        )
        assert resp.status_code == 200
        assert resp.json()["ticket"]["ticket_id"] == ticket_id

    def test_track_nonexistent_ticket(self):
        resp = client.post(
            "/status/track",
            json={"ticket_id": "AMC-9999-XX-99999"},
            headers={"X-Forwarded-For": "192.168.20.2"},
        )
        assert resp.status_code == 404

    def test_track_returns_timeline(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        ticket_id = data["ticket_id"]

        status = client.post(
            "/status/track",
            json={"ticket_id": ticket_id},
            headers=self._headers,
        ).json()
        assert len(status["ticket"]["timeline"]) >= 2

    def test_list_all_tickets(self):
        # Create two tickets
        client.post("/complaint/file", json=_VALID_COMPLAINT, headers=self._headers)
        client.post("/complaint/file", json=_VALID_COMPLAINT, headers=self._headers)

        resp = client.get("/status/all", headers=self._headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_track_returns_agent_trace(self):
        data = client.post(
            "/complaint/file", json=_VALID_COMPLAINT, headers=self._headers
        ).json()
        status = client.post(
            "/status/track",
            json={"ticket_id": data["ticket_id"]},
            headers=self._headers,
        ).json()
        assert "agent_trace" in status
        assert len(status["agent_trace"]) >= 1


class TestDirectoryEndpoints:
    def test_list_wards(self):
        resp = client.get("/directory/wards")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_wards"] > 0
        assert len(data["wards"]) > 0

    def test_list_departments(self):
        resp = client.get("/directory/departments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_departments"] > 0

    def test_get_ward_by_id(self):
        resp = client.get("/directory/wards/W08")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ward_name"] == "Bodakdev"

    def test_get_invalid_ward(self):
        resp = client.get("/directory/wards/INVALID")
        data = resp.json()
        assert "error" in data

    def test_get_department_by_id(self):
        resp = client.get("/directory/departments/ROADS_NW")
        assert resp.status_code == 200
        data = resp.json()
        assert data["department_name"] == "Roads & Buildings"

    def test_get_invalid_department(self):
        resp = client.get("/directory/departments/INVALID")
        data = resp.json()
        assert "error" in data

    def test_ward_has_landmarks(self):
        resp = client.get("/directory/wards/W08")
        data = resp.json()
        assert "landmarks" in data
        assert len(data["landmarks"]) > 0

    def test_department_has_sla(self):
        resp = client.get("/directory/departments/ROADS_NW")
        data = resp.json()
        assert "sla_hours" in data
        assert data["sla_hours"] > 0
