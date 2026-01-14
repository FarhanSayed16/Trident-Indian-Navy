"""
Unit tests for Pydantic schemas.
Tests validation logic for traffic, alert, and recommendation schemas.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.traffic import TrafficLogCreate, TrafficLogBatchCreate, HTTPMethod
from app.schemas.alert import AlertCreate, AlertStatus, AlertSeverity
from app.schemas.recommendation import RecommendationCreate, RuleType, RecommendationStatus


class TestTrafficLogSchemas:
    """Test cases for TrafficLog schemas."""

    def test_valid_traffic_log_create(self):
        """Test creating a valid traffic log."""
        log = TrafficLogCreate(
            src_ip="192.168.1.1",
            method=HTTPMethod.GET,
            url="https://example.com/api/test",
            status_code=200,
            payload_size=1024,
            response_time_ms=150.5,
            user_agent="Mozilla/5.0",
            headers={"Content-Type": "application/json"},
            query_params={"page": "1"},
            referer="https://example.com",
            content_type="application/json"
        )
        assert log.src_ip == "192.168.1.1"
        assert log.method == HTTPMethod.GET
        assert log.status_code == 200
        assert log.payload_size == 1024

    def test_traffic_log_minimal_fields(self):
        """Test creating traffic log with only required fields."""
        log = TrafficLogCreate(
            src_ip="192.168.1.1",
            method=HTTPMethod.POST,
            url="/api/test",
            status_code=201
        )
        assert log.src_ip == "192.168.1.1"
        assert log.method == HTTPMethod.POST
        assert log.url == "/api/test"

    def test_traffic_log_invalid_ip(self):
        """Test validation fails with empty IP."""
        with pytest.raises(ValidationError):
            TrafficLogCreate(
                src_ip="",
                method=HTTPMethod.GET,
                url="/test",
                status_code=200
            )

    def test_traffic_log_invalid_status_code(self):
        """Test validation fails with invalid status code."""
        with pytest.raises(ValidationError):
            TrafficLogCreate(
                src_ip="192.168.1.1",
                method=HTTPMethod.GET,
                url="/test",
                status_code=999  # Invalid status code
            )

    def test_traffic_log_invalid_url(self):
        """Test validation fails with empty URL."""
        with pytest.raises(ValidationError):
            TrafficLogCreate(
                src_ip="192.168.1.1",
                method=HTTPMethod.GET,
                url="",  # Empty URL
                status_code=200
            )

    def test_batch_create_valid(self):
        """Test creating a valid batch of traffic logs."""
        logs = [
            TrafficLogCreate(
                src_ip="192.168.1.1",
                method=HTTPMethod.GET,
                url="/api/test1",
                status_code=200
            ),
            TrafficLogCreate(
                src_ip="192.168.1.2",
                method=HTTPMethod.POST,
                url="/api/test2",
                status_code=201
            )
        ]
        batch = TrafficLogBatchCreate(logs=logs)
        assert len(batch.logs) == 2

    def test_batch_create_empty(self):
        """Test validation fails with empty batch."""
        with pytest.raises(ValidationError):
            TrafficLogBatchCreate(logs=[])


class TestAlertSchemas:
    """Test cases for Alert schemas."""

    def test_valid_alert_create(self):
        """Test creating a valid alert."""
        alert = AlertCreate(
            traffic_log_id=1,
            anomaly_score=0.85,
            risk_score=75,
            severity=AlertSeverity.HIGH,
            reasons=["High request rate", "Unusual endpoint pattern"],
            model_version="v1.0.0",
            model_type="isolation_forest"
        )
        assert alert.traffic_log_id == 1
        assert alert.anomaly_score == 0.85
        assert alert.risk_score == 75
        assert alert.severity == AlertSeverity.HIGH
        assert len(alert.reasons) == 2

    def test_alert_invalid_anomaly_score(self):
        """Test validation fails with invalid anomaly score."""
        with pytest.raises(ValidationError):
            AlertCreate(
                traffic_log_id=1,
                anomaly_score=1.5,  # > 1.0
                risk_score=75,
                severity=AlertSeverity.HIGH,
                reasons=["Test reason"]
            )

    def test_alert_invalid_risk_score(self):
        """Test validation fails with invalid risk score."""
        with pytest.raises(ValidationError):
            AlertCreate(
                traffic_log_id=1,
                anomaly_score=0.85,
                risk_score=150,  # > 100
                severity=AlertSeverity.HIGH,
                reasons=["Test reason"]
            )

    def test_alert_empty_reasons(self):
        """Test validation fails with empty reasons."""
        with pytest.raises(ValidationError):
            AlertCreate(
                traffic_log_id=1,
                anomaly_score=0.85,
                risk_score=75,
                severity=AlertSeverity.HIGH,
                reasons=[]  # Empty reasons
            )

    def test_alert_default_status(self):
        """Test alert defaults to NEW status."""
        alert = AlertCreate(
            traffic_log_id=1,
            anomaly_score=0.85,
            risk_score=75,
            severity=AlertSeverity.HIGH,
            reasons=["Test reason"]
        )
        assert alert.status == AlertStatus.NEW


class TestRecommendationSchemas:
    """Test cases for Recommendation schemas."""

    def test_valid_recommendation_create(self):
        """Test creating a valid recommendation."""
        recommendation = RecommendationCreate(
            alert_id=1,
            rule_type=RuleType.RATE_LIMIT,
            rule_config={"limit": 100, "window": 60},
            rule_content="Limit requests to 100 per minute",
            confidence=0.9
        )
        assert recommendation.alert_id == 1
        assert recommendation.rule_type == RuleType.RATE_LIMIT
        assert recommendation.confidence == 0.9
        assert recommendation.status == RecommendationStatus.PENDING

    def test_recommendation_invalid_confidence(self):
        """Test validation fails with invalid confidence."""
        with pytest.raises(ValidationError):
            RecommendationCreate(
                alert_id=1,
                rule_type=RuleType.IP_BLOCK,
                rule_config={"ip": "192.168.1.1"},
                confidence=1.5  # > 1.0
            )

    def test_recommendation_empty_rule_config(self):
        """Test validation fails with empty rule config."""
        with pytest.raises(ValidationError):
            RecommendationCreate(
                alert_id=1,
                rule_type=RuleType.PATTERN_MATCH,
                rule_config={},  # Empty config
                confidence=0.8
            )

    def test_recommendation_default_status(self):
        """Test recommendation defaults to PENDING status."""
        recommendation = RecommendationCreate(
            alert_id=1,
            rule_type=RuleType.CHALLENGE,
            rule_config={"type": "captcha"},
            confidence=0.85
        )
        assert recommendation.status == RecommendationStatus.PENDING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

