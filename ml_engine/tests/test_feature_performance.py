"""
Performance tests for feature extraction.
Target: < 100ms per request for feature extraction.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import ml_engine
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from ml_engine.feature_vector import FeatureExtractor, FeatureVector
from ml_engine.feature_cache import FeatureCache
from ml_engine.feature_optimizer import FeatureOptimizer
from app.models.traffic_log import TrafficLog


class TestFeatureExtractionPerformance:
    """Performance tests for feature extraction."""
    
    def test_feature_extraction_performance_single_log(self):
        """Test that feature extraction completes in < 100ms for a single log."""
        # Create a mock log
        log = Mock(spec=TrafficLog)
        log.id = 1
        log.src_ip = "192.168.1.1"
        log.url = "/api/test"
        log.method = "GET"
        log.status_code = 200
        log.payload_size = 100
        log.response_time_ms = 50.0
        log.timestamp = datetime.utcnow()
        log.headers = {"Content-Type": "application/json", "User-Agent": "test"}
        log.user_agent = "test"
        log.referer = None
        
        # Create mock database session
        db = Mock(spec=Session)
        query_mock = Mock()
        filter_mock = Mock()
        db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []
        filter_mock.count.return_value = 0
        
        # Create feature extractor with caching
        extractor = FeatureExtractor(use_optimization=True)
        
        # Measure extraction time
        start_time = time.perf_counter()
        feature_vector = extractor.extract_features(log, db, historical_logs=[])
        end_time = time.perf_counter()
        
        extraction_time_ms = (end_time - start_time) * 1000
        
        # Verify performance target
        assert extraction_time_ms < 100, f"Feature extraction took {extraction_time_ms:.2f}ms, target is < 100ms"
        assert isinstance(feature_vector, FeatureVector)
        assert len(feature_vector.feature_dict) > 0
    
    def test_feature_extraction_with_caching_performance(self):
        """Test that cached feature extraction is faster."""
        # Create a mock log
        log = Mock(spec=TrafficLog)
        log.id = 1
        log.src_ip = "192.168.1.1"
        log.url = "/api/test"
        log.method = "GET"
        log.status_code = 200
        log.payload_size = 100
        log.response_time_ms = 50.0
        log.timestamp = datetime.utcnow()
        log.headers = {"Content-Type": "application/json"}
        log.user_agent = "test"
        log.referer = None
        
        # Create mock database session
        db = Mock(spec=Session)
        query_mock = Mock()
        filter_mock = Mock()
        db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []
        filter_mock.count.return_value = 0
        
        # Create feature extractor with caching
        cache = FeatureCache()
        extractor = FeatureExtractor(feature_cache=cache, use_optimization=True)
        
        # First extraction (no cache)
        start_time = time.perf_counter()
        feature_vector1 = extractor.extract_features(log, db, historical_logs=[])
        first_extraction_time = (time.perf_counter() - start_time) * 1000
        
        # Second extraction (with cache)
        start_time = time.perf_counter()
        feature_vector2 = extractor.extract_features(log, db, historical_logs=[])
        second_extraction_time = (time.perf_counter() - start_time) * 1000
        
        # Cached extraction should be faster (or at least not slower)
        # Both should be < 100ms
        assert first_extraction_time < 100, f"First extraction took {first_extraction_time:.2f}ms"
        assert second_extraction_time < 100, f"Cached extraction took {second_extraction_time:.2f}ms"
        assert isinstance(feature_vector1, FeatureVector)
        assert isinstance(feature_vector2, FeatureVector)
    
    def test_batch_feature_extraction_performance(self):
        """Test that batch feature extraction is efficient."""
        # Create multiple mock logs
        logs = []
        for i in range(10):
            log = Mock(spec=TrafficLog)
            log.id = i + 1
            log.src_ip = f"192.168.1.{i % 3 + 1}"  # 3 different IPs
            log.url = f"/api/test{i % 2}"  # 2 different URLs
            log.method = "GET"
            log.status_code = 200
            log.payload_size = 100 + i
            log.response_time_ms = 50.0 + i
            log.timestamp = datetime.utcnow() - timedelta(seconds=i)
            log.headers = {"Content-Type": "application/json"}
            log.user_agent = "test"
            log.referer = None
            logs.append(log)
        
        # Create mock database session
        db = Mock(spec=Session)
        query_mock = Mock()
        filter_mock = Mock()
        db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []
        filter_mock.count.return_value = 0
        
        # Create optimizer
        optimizer = FeatureOptimizer()
        
        # Measure batch extraction time
        start_time = time.perf_counter()
        rate_features = optimizer.batch_extract_rate_features(logs, db, time_window_seconds=60)
        end_time = time.perf_counter()
        
        batch_time_ms = (end_time - start_time) * 1000
        
        # Batch processing should be efficient
        # Target: < 100ms per log on average
        avg_time_per_log = batch_time_ms / len(logs)
        assert avg_time_per_log < 100, f"Average time per log: {avg_time_per_log:.2f}ms, target is < 100ms"
        assert len(rate_features) == len(logs)
    
    def test_feature_extraction_with_historical_logs_performance(self):
        """Test feature extraction with historical logs (more realistic scenario)."""
        # Create current log
        current_log = Mock(spec=TrafficLog)
        current_log.id = 100
        current_log.src_ip = "192.168.1.1"
        current_log.url = "/api/test"
        current_log.method = "GET"
        current_log.status_code = 200
        current_log.payload_size = 100
        current_log.response_time_ms = 50.0
        current_log.timestamp = datetime.utcnow()
        current_log.headers = {"Content-Type": "application/json"}
        current_log.user_agent = "test"
        current_log.referer = None
        
        # Create historical logs
        historical_logs = []
        for i in range(20):
            log = Mock(spec=TrafficLog)
            log.id = i
            log.src_ip = "192.168.1.1"
            log.url = "/api/test"
            log.method = "GET"
            log.status_code = 200
            log.payload_size = 100 + i
            log.response_time_ms = 50.0 + i
            log.timestamp = datetime.utcnow() - timedelta(seconds=20 - i)
            log.headers = {"Content-Type": "application/json"}
            log.user_agent = "test"
            log.referer = None
            historical_logs.append(log)
        
        # Create mock database session
        db = Mock(spec=Session)
        query_mock = Mock()
        filter_mock = Mock()
        db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []
        filter_mock.count.return_value = 0
        
        # Create feature extractor
        extractor = FeatureExtractor(use_optimization=True)
        
        # Measure extraction time with historical logs
        start_time = time.perf_counter()
        feature_vector = extractor.extract_features(
            current_log, db, historical_logs=historical_logs
        )
        end_time = time.perf_counter()
        
        extraction_time_ms = (end_time - start_time) * 1000
        
        # Should still be < 100ms even with historical logs
        assert extraction_time_ms < 100, f"Extraction with historical logs took {extraction_time_ms:.2f}ms, target is < 100ms"
        assert isinstance(feature_vector, FeatureVector)
        assert len(feature_vector.feature_dict) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

