import requests
import json
import os

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
ALERTS_ENDPOINT = f"{BASE_URL}{API_PREFIX}/alerts"
TRAFFIC_ENDPOINT = f"{BASE_URL}{API_PREFIX}/traffic"
DETECTION_ENDPOINT = f"{BASE_URL}{API_PREFIX}/detection/detect"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_get_api_v1_alerts_list_alerts():
    # Step 1: Ingest one traffic log to generate related alert eventually
    # Load sample corrected traffic log from testsprite_tests directory
    traffic_log_path = os.path.join("testsprite_tests", "sample_traffic_log.json")
    with open(traffic_log_path, 'r', encoding='utf-8') as f:
        traffic_log = json.load(f)

    alert_id = None
    try:
        # Create single traffic log
        resp = requests.post(TRAFFIC_ENDPOINT, headers=HEADERS, json=traffic_log, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Traffic log creation failed with status {resp.status_code}"
        traffic_created = resp.json()
        assert "id" in traffic_created, "Response missing traffic log id"
        traffic_id = traffic_created["id"]

        # Perform anomaly detection on this traffic log to generate alert
        detection_payload = {"traffic_log_id": traffic_id}
        resp = requests.post(DETECTION_ENDPOINT, headers=HEADERS, json=detection_payload, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Detection failed with status {resp.status_code}"
        detection_result = resp.json()
        assert "alert_id" in detection_result, "Detection response missing alert_id"
        alert_id = detection_result["alert_id"]

        # Step 2: GET /api/v1/alerts to retrieve list of alerts with filtering and pagination
        params = {
            "page": 1,
            "size": 10,
            "sort": "timestamp,desc",  # Assuming sorting supported
            "filter[alert_id]": alert_id  # Assuming filter param, fallback if not supported is to get all alerts then check.
        }
        resp = requests.get(ALERTS_ENDPOINT, headers=HEADERS, params=params, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Get alerts failed with status {resp.status_code}"
        alerts_data = resp.json()

        # Validate general structure and pagination keys
        assert "alerts" in alerts_data, "Response missing 'alerts' key"
        assert isinstance(alerts_data["alerts"], list), "'alerts' should be a list"
        # Optional pagination metadata validation if included
        if "pagination" in alerts_data:
            pagination = alerts_data["pagination"]
            assert "page" in pagination and "size" in pagination and "total" in pagination, "Pagination metadata incomplete"
            assert pagination["page"] >= 1, "Invalid pagination page"
            assert pagination["size"] > 0, "Invalid pagination size"
            assert pagination["total"] >= 0, "Invalid pagination total"

        alerts_list = alerts_data["alerts"]
        # Ensure at least one alert is returned, ideally the alert we generated
        assert len(alerts_list) > 0, "No alerts returned"

        # Find our alert by alert_id in returned list
        matching_alerts = [a for a in alerts_list if a.get("id") == alert_id]
        assert len(matching_alerts) == 1, "Generated alert not found in alerts list"
        alert = matching_alerts[0]

        # Validate expected alert metadata fields and data types
        expected_fields = {
            "id": str,
            "timestamp": str,
            "src_ip": str,
            "dest_ip": str,
            "method": str,
            "endpoint": str,
            "response_time_ms": (int, float),
            "payload_size": int,
            "risk_score": (int, float),
            "risk_tier": str,
            "explanation_present": bool
        }

        for field, ftype in expected_fields.items():
            assert field in alert, f"Alert missing expected field '{field}'"
            val = alert[field]
            if isinstance(ftype, tuple):
                assert any(isinstance(val, t) for t in ftype), f"Field '{field}' expected type {ftype} but got {type(val)}"
            else:
                assert isinstance(val, ftype), f"Field '{field}' expected type {ftype} but got {type(val)}"

        # Additional consistency checks
        # timestamp format ISO8601 check (basic)
        import re
        iso8601_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$"
        assert re.match(iso8601_regex, alert["timestamp"]), "Timestamp not in ISO8601 format"

        # risk_score between 0-100
        assert 0 <= alert["risk_score"] <= 100, "risk_score out of range 0-100"

        # risk_tier should be one of expected categories (example: "low","medium","high","critical")
        allowed_tiers = {"low","medium","high","critical"}
        assert alert["risk_tier"].lower() in allowed_tiers, f"risk_tier value unexpected: {alert['risk_tier']}"

    finally:
        # Cleanup: if alert was created, optionally delete alert if API allows (not specified)
        # No delete alert endpoint defined in PRD, so skip

        # Cleanup created traffic log
        if 'traffic_id' in locals():
            try:
                requests.delete(f"{TRAFFIC_ENDPOINT}/{traffic_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass

test_get_api_v1_alerts_list_alerts()