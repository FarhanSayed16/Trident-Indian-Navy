import requests
import traceback

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TRAFFIC_ENDPOINT = f"{BASE_URL}{API_PREFIX}/traffic"
ALERTS_ENDPOINT = f"{BASE_URL}{API_PREFIX}/alerts"
TIMEOUT = 30

# Added 'url' field to match required payload fields as per API error
EXAMPLE_TRAFFIC_LOG = {
    "src_ip": "192.168.1.10",
    "dst_ip": "10.0.0.5",
    "method": "GET",
    "endpoint": "/api/v1/test-endpoint",
    "url": "http://localhost:8000/api/v1/test-endpoint",  # Added required field
    "response_time_ms": 120,
    "payload_size": 512,
    "user_agent": "Mozilla/5.0 (compatible; TestClient/1.0)",
    "status_code": 200,
    "timestamp": "2024-01-15T12:34:56Z"
}

def test_get_api_v1_alerts_id_get_alert_details():
    headers = {
        "Content-Type": "application/json"
    }
    alert_id = None
    traffic_id = None

    try:
        # Step 1: Create a traffic log to trigger alert generation
        resp_traffic = requests.post(
            TRAFFIC_ENDPOINT,
            json=EXAMPLE_TRAFFIC_LOG,
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp_traffic.status_code in (200,201), f"Failed to create traffic log: {resp_traffic.status_code} {resp_traffic.text}"
        traffic_data = resp_traffic.json()
        assert isinstance(traffic_data, dict), "Traffic creation response is not a dict"
        # traffic log ID might be returned for cross-reference
        traffic_id = traffic_data.get("id")

        # Step 2: Fetch alerts list to find alert related to created traffic (may need retry for real alert creation delay)
        params = {
            "src_ip": EXAMPLE_TRAFFIC_LOG["src_ip"],
            "endpoint": EXAMPLE_TRAFFIC_LOG["endpoint"]
        }
        # We'll do limited retries waiting for the alert to appear (simulate near real-time detection)
        import time
        alert_list = None
        for attempt in range(5):
            resp_alerts = requests.get(ALERTS_ENDPOINT, params=params, headers=headers, timeout=TIMEOUT)
            if resp_alerts.status_code != 200:
                raise AssertionError(f"Failed to list alerts: {resp_alerts.status_code} {resp_alerts.text}")
            alerts_data = resp_alerts.json()
            if isinstance(alerts_data, dict) and "alerts" in alerts_data and alerts_data["alerts"]:
                alert_list = alerts_data["alerts"]
                break
            time.sleep(1)  # wait and retry
        assert alert_list is not None and len(alert_list) > 0, "No alerts found related to the created traffic log"

        # Pick the first alert's ID for details fetching
        alert = alert_list[0]
        alert_id = alert.get("id")
        assert alert_id is not None, "Alert ID is missing from alerts list"

        # Step 3: Get alert details by alert ID
        resp_detail = requests.get(f"{ALERTS_ENDPOINT}/{alert_id}", headers=headers, timeout=TIMEOUT)
        assert resp_detail.status_code == 200, f"Failed to get alert details: {resp_detail.status_code} {resp_detail.text}"
        detail_data = resp_detail.json()
        assert isinstance(detail_data, dict), "Alert detail response is not a dict"
        
        # Validate response fields: risk score, timestamp, related traffic log
        # Risk score: int or float 0-100
        risk_score = detail_data.get("risk_score")
        assert risk_score is not None, "risk_score missing in alert detail"
        assert isinstance(risk_score, (int, float)), "risk_score should be a number"
        assert 0 <= risk_score <= 100, f"risk_score out of expected range 0-100: {risk_score}"

        # Timestamp: ISO8601 string parse check
        timestamp = detail_data.get("timestamp")
        assert timestamp is not None, "timestamp missing in alert detail"
        from dateutil.parser import parse as date_parse
        try:
            parsed_ts = date_parse(timestamp)
        except Exception as e:
            raise AssertionError(f"timestamp field not in valid ISO8601 format: {timestamp}") from e

        # Related traffic log: should be present with key fields
        related_traffic = detail_data.get("traffic_log")
        assert related_traffic is not None, "related traffic_log missing in alert detail"
        assert isinstance(related_traffic, dict), "traffic_log field should be a dict"
        # Validate some key fields in related traffic log
        for key in ["src_ip", "method", "response_time_ms", "payload_size", "timestamp"]:
            assert key in related_traffic, f"traffic_log missing expected field: {key}"
        # Optional: Match src_ip and endpoint with original traffic log input to confirm relation
        assert related_traffic.get("src_ip") == EXAMPLE_TRAFFIC_LOG["src_ip"], "src_ip in traffic_log does not match original"
        assert related_traffic.get("method") == EXAMPLE_TRAFFIC_LOG["method"], "method in traffic_log does not match original"
        
    except Exception:
        traceback.print_exc()
        raise
    finally:
        # Cleanup: If traffic log or alert deletion endpoints exist, delete created resources here
        # Currently no delete endpoints provided for alerts or traffic in PRD; if available, add cleanup code here
        pass

test_get_api_v1_alerts_id_get_alert_details()
