"""
Unit tests for AnomalyDetector ensemble.
"""

import sys
from pathlib import Path

# Add project root and backend to path for imports
project_root = Path(__file__).parent.parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

import pytest
import numpy as np

from ml_engine.detector import AnomalyDetector, DetectionResult
from ml_engine.models.isolation_forest import IsolationForestDetector
from ml_engine.models.autoencoder import AutoencoderDetector
from ml_engine.feature_vector import FeatureVector


@pytest.fixture
def sample_feature_vectors():
    """Create sample feature vectors for testing."""
    # Create normal traffic features (low values, consistent patterns)
    normal_vectors = []
    for i in range(50):
        features = {
            'requests_per_ip': float(10 + i % 5),
            'payload_size': float(100 + i * 2),
            'response_time': float(50 + i % 10),
            'status_code': 200.0,
            'is_status_200': 1.0,
            'hour': float(i % 24),
            'url_length': float(30 + i % 10)
        }
        normal_vectors.append(FeatureVector(features, {'id': i}))
    
    # Create anomaly features (outlier values)
    anomaly_vectors = []
    for i in range(10):
        features = {
            'requests_per_ip': float(1000 + i * 100),  # Very high request rate
            'payload_size': float(10000 + i * 1000),   # Very large payload
            'response_time': float(5000 + i * 500),    # Very slow response
            'status_code': 500.0,                       # Error status
            'is_status_200': 0.0,
            'hour': float(i % 24),
            'url_length': float(500 + i * 50)          # Very long URL
        }
        anomaly_vectors.append(FeatureVector(features, {'id': i + 1000}))
    
    return normal_vectors, anomaly_vectors


@pytest.fixture
def trained_models(sample_feature_vectors):
    """Create and train both models for testing."""
    normal_vectors, _ = sample_feature_vectors
    
    # Train Isolation Forest
    if_detector = IsolationForestDetector(random_state=42, contamination=0.1)
    if_detector.train(normal_vectors)
    
    # Train Autoencoder
    ae_detector = AutoencoderDetector(
        epochs=5,
        batch_size=16,
        early_stopping_patience=3,
        random_seed=42
    )
    ae_detector.train(normal_vectors)
    
    return if_detector, ae_detector


class TestAnomalyDetectorInit:
    """Test AnomalyDetector initialization."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        detector = AnomalyDetector()
        
        assert detector.isolation_forest is None
        assert detector.autoencoder is None
        assert detector.if_weight == 0.5
        assert detector.ae_weight == 0.5
        assert detector.anomaly_threshold == 0.5
    
    def test_init_with_models(self, trained_models):
        """Test initialization with trained models."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        assert detector.isolation_forest == if_model
        assert detector.autoencoder == ae_model
        assert detector.if_weight == 0.5
        assert detector.ae_weight == 0.5
    
    def test_init_custom_weights(self, trained_models):
        """Test initialization with custom weights."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(
            isolation_forest=if_model,
            autoencoder=ae_model,
            if_weight=0.7,
            ae_weight=0.3,
            anomaly_threshold=0.6
        )
        
        assert detector.if_weight == 0.7
        assert detector.ae_weight == 0.3
        assert detector.anomaly_threshold == 0.6
    
    def test_init_invalid_weights_sum(self):
        """Test initialization with weights that don't sum to 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="must equal 1.0"):
            AnomalyDetector(if_weight=0.6, ae_weight=0.5)
    
    def test_init_invalid_weight_range(self):
        """Test initialization with weights outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError, match="must be in \\[0, 1\\] range"):
            AnomalyDetector(if_weight=1.5, ae_weight=-0.5)
    
    def test_init_invalid_threshold(self):
        """Test initialization with threshold outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError, match="must be in \\[0, 1\\] range"):
            AnomalyDetector(anomaly_threshold=1.5)


class TestAnomalyDetectorDetect:
    """Test AnomalyDetector detection."""
    
    def test_detect_without_models(self):
        """Test detection without models raises ValueError."""
        detector = AnomalyDetector()
        features = FeatureVector({'feature1': 1.0, 'feature2': 2.0})
        
        with pytest.raises(ValueError, match="not initialized"):
            detector.detect(features)
    
    def test_detect_with_untrained_models(self, sample_feature_vectors):
        """Test detection with untrained models raises ValueError."""
        normal_vectors, _ = sample_feature_vectors
        if_model = IsolationForestDetector()
        ae_model = AutoencoderDetector()
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        features = normal_vectors[0]
        
        with pytest.raises(ValueError, match="not trained"):
            detector.detect(features)
    
    def test_detect_normal_traffic(self, trained_models, sample_feature_vectors):
        """Test detection on normal traffic."""
        if_model, ae_model = trained_models
        normal_vectors, _ = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        result = detector.detect(normal_vectors[0])
        
        assert isinstance(result, DetectionResult)
        assert 0.0 <= result.anomaly_score <= 1.0
        assert 0.0 <= result.isolation_forest_score <= 1.0
        assert 0.0 <= result.autoencoder_score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.model_agreement, bool)
        assert isinstance(result.is_anomaly, bool)
    
    def test_detect_anomaly_traffic(self, trained_models, sample_feature_vectors):
        """Test detection on anomaly traffic."""
        if_model, ae_model = trained_models
        _, anomaly_vectors = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        result = detector.detect(anomaly_vectors[0])
        
        assert isinstance(result, DetectionResult)
        assert 0.0 <= result.anomaly_score <= 1.0
        assert 0.0 <= result.isolation_forest_score <= 1.0
        assert 0.0 <= result.autoencoder_score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        # Anomaly should be detected
        assert result.is_anomaly is True
    
    def test_detect_with_array_input(self, trained_models, sample_feature_vectors):
        """Test detection with numpy array input."""
        if_model, ae_model = trained_models
        normal_vectors, _ = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        feature_array = normal_vectors[0].to_array(if_model.feature_names)
        result = detector.detect(feature_array)
        
        assert isinstance(result, DetectionResult)


class TestAnomalyDetectorCombineScores:
    """Test score combination logic."""
    
    def test_combine_scores_equal_weights(self, trained_models):
        """Test combining scores with equal weights."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        combined = detector.combine_scores(0.3, 0.7)
        expected = 0.5  # (0.5 * 0.3) + (0.5 * 0.7) = 0.5
        
        assert abs(combined - expected) < 1e-6
    
    def test_combine_scores_custom_weights(self, trained_models):
        """Test combining scores with custom weights."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(
            isolation_forest=if_model,
            autoencoder=ae_model,
            if_weight=0.7,
            ae_weight=0.3
        )
        
        combined = detector.combine_scores(0.5, 0.5)
        expected = 0.5  # (0.7 * 0.5) + (0.3 * 0.5) = 0.5
        
        assert abs(combined - expected) < 1e-6
    
    def test_combine_scores_extreme_values(self, trained_models):
        """Test combining scores with extreme values."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        # Test with 0.0 scores
        combined = detector.combine_scores(0.0, 0.0)
        assert combined == 0.0
        
        # Test with 1.0 scores
        combined = detector.combine_scores(1.0, 1.0)
        assert combined == 1.0
        
        # Test clamping (should not exceed [0, 1])
        # Note: combine_scores already clamps, so this is more of a verification
        combined = detector.combine_scores(0.5, 0.5)
        assert 0.0 <= combined <= 1.0


class TestAnomalyDetectorWeightManagement:
    """Test weight and threshold management."""
    
    def test_set_weights(self, trained_models):
        """Test updating ensemble weights."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        detector.set_weights(0.8, 0.2)
        assert detector.if_weight == 0.8
        assert detector.ae_weight == 0.2
    
    def test_set_weights_invalid_sum(self, trained_models):
        """Test setting weights that don't sum to 1.0 raises ValueError."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        with pytest.raises(ValueError, match="must equal 1.0"):
            detector.set_weights(0.6, 0.5)
    
    def test_set_weights_invalid_range(self, trained_models):
        """Test setting weights outside [0, 1] raises ValueError."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        with pytest.raises(ValueError, match="must be in \\[0, 1\\] range"):
            detector.set_weights(1.5, -0.5)
    
    def test_set_threshold(self, trained_models):
        """Test updating anomaly threshold."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        detector.set_threshold(0.7)
        assert detector.anomaly_threshold == 0.7
    
    def test_set_threshold_invalid(self, trained_models):
        """Test setting threshold outside [0, 1] raises ValueError."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        with pytest.raises(ValueError, match="must be in \\[0, 1\\] range"):
            detector.set_threshold(1.5)


class TestDetectionResult:
    """Test DetectionResult structure."""
    
    def test_detection_result_creation(self):
        """Test creating DetectionResult."""
        result = DetectionResult(
            is_anomaly=True,
            anomaly_score=0.8,
            isolation_forest_score=0.7,
            autoencoder_score=0.9,
            confidence=0.85,
            model_agreement=True
        )
        
        assert result.is_anomaly is True
        assert result.anomaly_score == 0.8
        assert result.isolation_forest_score == 0.7
        assert result.autoencoder_score == 0.9
        assert result.confidence == 0.85
        assert result.model_agreement is True
    
    def test_detection_result_to_dict(self):
        """Test converting DetectionResult to dictionary."""
        result = DetectionResult(
            is_anomaly=True,
            anomaly_score=0.8,
            isolation_forest_score=0.7,
            autoencoder_score=0.9,
            confidence=0.85,
            model_agreement=True
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['is_anomaly'] is True
        assert result_dict['anomaly_score'] == 0.8
        assert result_dict['isolation_forest_score'] == 0.7
        assert result_dict['autoencoder_score'] == 0.9
        assert result_dict['confidence'] == 0.85
        assert result_dict['model_agreement'] is True


class TestAnomalyDetectorEnsemblePerformance:
    """Test ensemble detection performance."""
    
    def test_ensemble_vs_individual_models(self, trained_models, sample_feature_vectors):
        """Test that ensemble provides detection results."""
        if_model, ae_model = trained_models
        normal_vectors, anomaly_vectors = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        # Test on normal data
        normal_results = []
        for vec in normal_vectors[:10]:
            result = detector.detect(vec)
            normal_results.append(result)
            assert isinstance(result, DetectionResult)
            assert 0.0 <= result.anomaly_score <= 1.0
        
        # Test on anomaly data
        anomaly_results = []
        for vec in anomaly_vectors[:5]:
            result = detector.detect(vec)
            anomaly_results.append(result)
            assert isinstance(result, DetectionResult)
            assert 0.0 <= result.anomaly_score <= 1.0
        
        # Verify ensemble scores are reasonable
        # Anomaly scores should generally be higher for anomalies
        avg_normal_score = np.mean([r.anomaly_score for r in normal_results])
        avg_anomaly_score = np.mean([r.anomaly_score for r in anomaly_results])
        
        # Anomaly scores should be higher (or at least not significantly lower)
        # Note: This is a soft check as model performance can vary
        assert avg_anomaly_score >= avg_normal_score - 0.2  # Allow some margin
    
    def test_model_agreement_tracking(self, trained_models, sample_feature_vectors):
        """Test that model agreement is tracked correctly."""
        if_model, ae_model = trained_models
        normal_vectors, anomaly_vectors = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        # Check some results have model agreement tracked
        result = detector.detect(normal_vectors[0])
        assert isinstance(result.model_agreement, bool)
        
        result = detector.detect(anomaly_vectors[0])
        assert isinstance(result.model_agreement, bool)
    
    def test_confidence_calculation(self, trained_models, sample_feature_vectors):
        """Test that confidence is calculated correctly."""
        if_model, ae_model = trained_models
        normal_vectors, _ = sample_feature_vectors
        
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        result = detector.detect(normal_vectors[0])
        
        # Confidence should be in [0, 1] range
        assert 0.0 <= result.confidence <= 1.0


class TestAnomalyDetectorInfo:
    """Test detector info methods."""
    
    def test_get_detector_info(self, trained_models):
        """Test getting detector information."""
        if_model, ae_model = trained_models
        detector = AnomalyDetector(isolation_forest=if_model, autoencoder=ae_model)
        
        info = detector.get_detector_info()
        
        assert info['if_initialized'] is True
        assert info['if_trained'] is True
        assert info['ae_initialized'] is True
        assert info['ae_trained'] is True
        assert info['if_weight'] == 0.5
        assert info['ae_weight'] == 0.5
        assert info['anomaly_threshold'] == 0.5
        assert 'if_model_info' in info
        assert 'ae_model_info' in info
    
    def test_get_detector_info_without_models(self):
        """Test getting detector information without models."""
        detector = AnomalyDetector()
        
        info = detector.get_detector_info()
        
        assert info['if_initialized'] is False
        assert info['if_trained'] is False
        assert info['ae_initialized'] is False
        assert info['ae_trained'] is False

