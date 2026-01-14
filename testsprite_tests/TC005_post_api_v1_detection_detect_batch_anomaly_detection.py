import requests
import os
import json
import time

BASE_URL = "http://localhost:8000"
API_BATCH_DETECT_ENDPOINT = "/api/v1/detection/detect/batch"
TEST_FILES_DIR = "testsprite_tests"
TIMEOUT = 30

def test_post_api_v1_detection_detect_batch_anomaly_detection():
    """
    Test the POST /api/v1/detection/detect/batch endpoint for batch anomaly detection
    on multiple traffic logs, verifying detection results and performance under load.
    """

    # Load batch traffic log test payload(s) from the testsprite_tests directory
    # Each file contains a list of traffic logs matching the API schema field names
    batch_payload = []
    try:
        # read all json test files in the test directory
        for filename in os.listdir(TEST_FILES_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(TEST_FILES_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # data expected to be a list of traffic logs or a single log
                    if isinstance(data, list):
                        batch_payload.extend(data)
                    elif isinstance(data, dict):
                        batch_payload.append(data)
        if not batch_payload:
            raise RuntimeError("No test data found in testsprite_tests directory")

        url = BASE_URL + API_BATCH_DETECT_ENDPOINT
        headers = {"Content-Type": "application/json"}

        start_time = time.time()
        response = requests.post(url, json=batch_payload, headers=headers, timeout=TIMEOUT)
        elapsed_time = time.time() - start_time

        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        result = response.json()

        # The response format expectation:
        # The result should be a list with entries corresponding to input traffic logs
        assert isinstance(result, list), "Response JSON is not a list"
        assert len(result) == len(batch_payload), \
            "Response count does not match batch payload count"

        # Validate each detection result in the response list
        for detection in result:
            # Each detection should contain anomaly detection fields such as:
            # risk_score (int 0-100), is_anomaly (bool), explanation (str or dict)
            assert isinstance(detection, dict), "Detection result is not a dict"
            assert "risk_score" in detection, "risk_score missing in detection result"
            assert 0 <= detection["risk_score"] <= 100, "risk_score out of range 0-100"
            assert "is_anomaly" in detection, "is_anomaly missing in detection result"
            assert isinstance(detection["is_anomaly"], bool), "is_anomaly not a boolean"
            assert "explanation" in detection, "explanation missing in detection result"
            # explanation can be string or dict, ensure non-empty
            explanation = detection["explanation"]
            assert explanation is not None
            if isinstance(explanation, str):
                assert len(explanation.strip()) > 0, "explanation string is empty"
            elif isinstance(explanation, dict):
                assert explanation, "explanation dict is empty"
            else:
                raise AssertionError("explanation is neither str nor dict")

        # Assert that performance requirement is met: latency under 1 second per 1 log approx
        # This is a batch, so allow some scaling, here we check if total time < len(batch)*1s
        assert elapsed_time <= max(1, len(batch_payload)), \
            f"Detection latency high: {elapsed_time:.2f}s for batch size {len(batch_payload)}"

    except Exception as e:
        raise e

test_post_api_v1_detection_detect_batch_anomaly_detection()