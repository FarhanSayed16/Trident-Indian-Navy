"""
Pydantic schemas for TRIDENT backend.
Request and response models for API validation.
"""

# Traffic Log Schemas
from app.schemas.traffic import (
    TrafficLogBase,
    TrafficLogCreate,
    TrafficLogResponse,
    TrafficLogSummary,
    TrafficLogBatchCreate,
    HTTPMethod,
)

# Alert Schemas
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    AlertSummary,
    AlertDetail,
    AlertStatus,
    AlertSeverity,
)

# Recommendation Schemas
from app.schemas.recommendation import (
    RecommendationBase,
    RecommendationCreate,
    RecommendationResponse,
    RecommendationUpdate,
    RecommendationSummary,
    RecommendationApproval,
    RecommendationRejection,
    RecommendationStatus,
    RuleType,
    ImpactEstimation,
)

# Baseline Schemas
from app.schemas.baseline import (
    BaselineStatsBase,
    BaselineStatsResponse,
    BaselineSummary,
    BaselineUpdateRequest,
    BaselineUpdateResponse,
    BaselineListResponse,
    ConceptDriftResult,
    AdaptiveThresholdResult,
)

__all__ = [
    # Traffic Log
    "TrafficLogBase",
    "TrafficLogCreate",
    "TrafficLogResponse",
    "TrafficLogSummary",
    "TrafficLogBatchCreate",
    "HTTPMethod",
    # Alert
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "AlertUpdate",
    "AlertSummary",
    "AlertDetail",
    "AlertStatus",
    "AlertSeverity",
    # Recommendation
    "RecommendationBase",
    "RecommendationCreate",
    "RecommendationResponse",
    "RecommendationUpdate",
    "RecommendationSummary",
    "RecommendationApproval",
    "RecommendationRejection",
    "RecommendationStatus",
    "RuleType",
    "ImpactEstimation",
    # Baseline
    "BaselineStatsBase",
    "BaselineStatsResponse",
    "BaselineSummary",
    "BaselineUpdateRequest",
    "BaselineUpdateResponse",
    "BaselineListResponse",
    "ConceptDriftResult",
    "AdaptiveThresholdResult",
]
