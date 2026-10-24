"""
tests/test_integration.py
---------------------------
End-to-end integration tests for the full complaint lifecycle:
  1. File a complaint → get ticket ID
  2. Track the ticket → verify status
  3. File multiple types → verify department routing
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestFullComplaintLifecycle:
    _headers = {"X-Forwarded-For": "10.0.0.1"}

    def test_file_then_track(self):
        """File a complaint and then track it — full lifecycle."""
        # Step 1: File complaint
        payload = {
            "citizen_name": "Integration Test User",
            "phone": "9825099999",
            "area_or_address": "Pakwan Cross Road, Bodakdev",
            "description": "Integration test pothole",
            "issue_type": "pothole",
        }
        file_resp = client.post("/complaint/file", json=payload, headers=self._headers)
        assert file_resp.status_code == 200
        file_data = file_resp.json()

        ticket_id = file_data["ticket_id"]
        assert ticket_id.startswith("AMC-")
        assert "-RD-" in ticket_id  # Roads department code

        # Step 2: Track complaint
        track_resp = client.post(
            "/status/track",
            json={"ticket_id": ticket_id},
            headers=self._headers,
        )
        assert track_resp.status_code == 200
        track_data = track_resp.json()

        assert track_data["ticket"]["ticket_id"] == ticket_id
        assert track_data["ticket"]["status"] == "assigned"
        assert track_data["ticket"]["ward_name"] == "Bodakdev"
        assert track_data["ticket"]["department_name"] == "Roads & Buildings"

    def test_multiple_complaint_types(self):
        """File different complaint types and verify routing."""
        cases = [
            ("pothole", "Bodakdev", "Roads & Buildings"),
            ("garbage_dump", "Kankaria, Maninagar", "Solid Waste & Health"),
            ("water_logging", "C.G. Road, Navrangpura", "Water & Sewerage"),
            ("streetlight_off", "Thaltej Cross Road", "Streetlight & Electrical"),
        ]

        for issue_type, area, expected_dept in cases:
            payload = {
                "citizen_name": "Test",
                "phone": "9825012345",
                "area_or_address": area,
                "issue_type": issue_type,
            }
            resp = client.post("/complaint/file", json=payload, headers=self._headers)
            data = resp.json()
            assert data["department"]["department_name"] == expected_dept, \
                f"{issue_type} should route to {expected_dept}"

    def test_agent_trace_complete(self):
        """Verify the agent trace covers all 4 tool calls."""
        payload = {
            "citizen_name": "Trace Test",
            "phone": "9825012345",
            "area_or_address": "SG Highway",
            "issue_type": "pothole",
        }
        data = client.post("/complaint/file", json=payload, headers=self._headers).json()
        trace = data["agent_trace"]

        assert len(trace) == 4
        assert trace[0]["tool"] == "amc.vision.classify_hazard"
        assert trace[1]["tool"] == "amc.gis.resolve_ward_polygon"
        assert trace[2]["tool"] == "amc.dispatch.assign_ticket"
        assert trace[3]["tool"] == "amc.ticket.create"

        for step in trace:
            assert step["status"] == "SUCCESS"
            assert step["latency_ms"] >= 0

    def test_ward_directory_then_file(self):
        """Verify wards from directory can be used to file complaints."""
        # Get wards
        wards = client.get("/directory/wards").json()
        assert wards["total_wards"] > 0

        # File for first ward
        first_ward = wards["wards"][0]
        payload = {
            "citizen_name": "Directory Test",
            "phone": "9825012345",
            "area_or_address": first_ward["ward_name"],
            "issue_type": "pothole",
        }
        resp = client.post("/complaint/file", json=payload, headers=self._headers)
        assert resp.status_code == 200

    def test_health_during_operations(self):
        """Health endpoint remains responsive during operations."""
        # File a complaint
        payload = {
            "citizen_name": "Health Test",
            "phone": "9825012345",
            "area_or_address": "SG Highway",
            "issue_type": "pothole",
        }
        client.post("/complaint/file", json=payload, headers=self._headers)

        # Health should still work
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
