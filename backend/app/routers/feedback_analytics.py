"""
Feedback Analytics Router
API endpoints for feedback analytics and integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.feedback_analytics import (
    FeedbackStatsResponse,
    FPRateOverTimeResponse,
    FeedbackTrendsResponse,
    BaselineAdjustmentResponse,
)
from app.services.feedback_analytics_service import FeedbackAnalyticsService
from app.services.feedback_integration_service import FeedbackIntegrationService

router = APIRouter()


@router.get(
    "/feedback-analytics/stats",
    response_model=FeedbackStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feedback statistics",
    description="Get overall feedback statistics with optional date filtering.",
    tags=["feedback-analytics"],
)
async def get_feedback_stats(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
):
    """
    Get overall feedback statistics.
    
    Returns total feedback, false positives, true positives, and rates.
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        stats = FeedbackAnalyticsService.get_feedback_stats(
            db=db,
            start_date=start,
            end_date=end
        )
        
        return FeedbackStatsResponse(**stats)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback statistics: {str(e)}"
        )


@router.get(
    "/feedback-analytics/fp-rate-over-time",
    response_model=list[FPRateOverTimeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get false positive rate over time",
    description="Get false positive rate trends over time.",
    tags=["feedback-analytics"],
)
async def get_fp_rate_over_time(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    interval: str = Query("day", pattern="^(day|week|hour)$", description="Time interval"),
    db: Session = Depends(get_db),
):
    """
    Get false positive rate over time.
    
    Returns false positive rate trends for the specified period.
    """
    try:
        data = FeedbackAnalyticsService.get_false_positive_rate_over_time(
            db=db,
            days=days,
            interval=interval
        )
        
        return [FPRateOverTimeResponse(**item) for item in data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FP rate over time: {str(e)}"
        )


@router.get(
    "/feedback-analytics/trends",
    response_model=FeedbackTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feedback trends",
    description="Get feedback trends over time with daily breakdown.",
    tags=["feedback-analytics"],
)
async def get_feedback_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """
    Get feedback trends over time.
    
    Returns daily feedback counts and trends.
    """
    try:
        trends = FeedbackAnalyticsService.get_feedback_trends(
            db=db,
            days=days
        )
        
        return FeedbackTrendsResponse(**trends)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback trends: {str(e)}"
        )


@router.get(
    "/feedback-analytics/by-severity",
    status_code=status.HTTP_200_OK,
    summary="Get feedback by alert severity",
    description="Get feedback statistics grouped by alert severity.",
    tags=["feedback-analytics"],
)
async def get_feedback_by_severity(
    db: Session = Depends(get_db),
):
    """
    Get feedback statistics grouped by alert severity.
    
    Returns feedback counts and rates for each severity level.
    """
    try:
        stats = FeedbackAnalyticsService.get_feedback_by_alert_severity(db=db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback by severity: {str(e)}"
        )


@router.get(
    "/feedback-analytics/top-fp-patterns",
    status_code=status.HTTP_200_OK,
    summary="Get top false positive patterns",
    description="Get top patterns that result in false positives.",
    tags=["feedback-analytics"],
)
async def get_top_fp_patterns(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of patterns to return"),
    db: Session = Depends(get_db),
):
    """
    Get top patterns that result in false positives.
    
    Returns alerts/IPs/URLs that frequently generate false positives.
    """
    try:
        patterns = FeedbackAnalyticsService.get_top_false_positive_patterns(
            db=db,
            limit=limit
        )
        return patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving top FP patterns: {str(e)}"
        )


@router.post(
    "/feedback-analytics/adjust-baselines",
    response_model=BaselineAdjustmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Adjust baselines with feedback",
    description="Adjust baselines based on false positive feedback.",
    tags=["feedback-analytics"],
)
async def adjust_baselines_with_feedback(
    src_ip: Optional[str] = Query(None, description="Source IP address (optional)"),
    url: Optional[str] = Query(None, description="Endpoint URL (optional)"),
    window_seconds: int = Query(3600, ge=60, description="Time window in seconds"),
    db: Session = Depends(get_db),
):
    """
    Adjust baselines based on false positive feedback.
    
    This endpoint updates baselines for IPs/URLs that have received
    false positive feedback, helping to reduce future false positives.
    """
    try:
        service = FeedbackIntegrationService(db=db)
        result = service.adjust_baselines_with_feedback(
            src_ip=src_ip,
            url=url,
            window_seconds=window_seconds
        )
        
        return BaselineAdjustmentResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adjusting baselines: {str(e)}"
        )

