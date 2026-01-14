"""
Recommendation Service
Service layer for recommendation database operations and business logic.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime

from app.models.recommendation import Recommendation, RecommendationStatus, RuleType
from app.models.alert import Alert
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate


class RecommendationService:
    """Service for recommendation database operations."""
    
    @staticmethod
    def create_recommendation(
        db: Session,
        recommendation_data: RecommendationCreate,
        estimated_impact: Optional[Dict[str, Any]] = None
    ) -> Recommendation:
        """
        Create a new recommendation.
        
        Args:
            db: Database session
            recommendation_data: Recommendation creation data
            estimated_impact: Optional impact estimation results
            
        Returns:
            Created Recommendation object
            
        Raises:
            ValueError: If alert_id doesn't exist
        """
        # Verify alert exists
        alert = db.query(Alert).filter(Alert.id == recommendation_data.alert_id).first()
        if not alert:
            raise ValueError(f"Alert with ID {recommendation_data.alert_id} not found")
        
        # Convert estimated_impact to JSON-compatible format if provided
        impact_json = None
        if estimated_impact:
            impact_json = estimated_impact
        
        # Create recommendation
        recommendation = Recommendation(
            alert_id=recommendation_data.alert_id,
            rule_type=recommendation_data.rule_type,
            rule_config=recommendation_data.rule_config,
            rule_content=recommendation_data.rule_content,
            rule_content_modsec=recommendation_data.rule_content_modsec,
            confidence=recommendation_data.confidence,
            estimated_impact=impact_json,
            status=recommendation_data.status,
        )
        
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    @staticmethod
    def get_recommendation(db: Session, recommendation_id: int) -> Optional[Recommendation]:
        """Get a recommendation by ID."""
        return db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    
    @staticmethod
    def list_recommendations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[RecommendationStatus] = None,
        rule_type: Optional[RuleType] = None,
        alert_id: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Recommendation], int]:
        """
        List recommendations with filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            rule_type: Filter by rule type
            alert_id: Filter by alert ID
            sort_by: Field to sort by (created_at, confidence, etc.)
            sort_order: Sort order (asc or desc)
            
        Returns:
            Tuple of (list of recommendations, total count)
        """
        query = db.query(Recommendation)
        
        # Apply filters
        if status:
            query = query.filter(Recommendation.status == status)
        if rule_type:
            query = query.filter(Recommendation.rule_type == rule_type)
        if alert_id:
            query = query.filter(Recommendation.alert_id == alert_id)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        sort_column = getattr(Recommendation, sort_by, Recommendation.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        recommendations = query.offset(skip).limit(limit).all()
        
        return recommendations, total_count
    
    @staticmethod
    def approve_recommendation(
        db: Session,
        recommendation_id: int,
        approved_by: str
    ) -> Recommendation:
        """
        Approve a recommendation.
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation to approve
            approved_by: Username of approver
            
        Returns:
            Updated Recommendation object
            
        Raises:
            ValueError: If recommendation not found or already processed
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise ValueError(f"Recommendation with ID {recommendation_id} not found")
        
        if recommendation.status != RecommendationStatus.PENDING:
            raise ValueError(
                f"Recommendation {recommendation_id} is already {recommendation.status.value}, "
                f"cannot approve"
            )
        
        # Update recommendation
        recommendation.status = RecommendationStatus.APPROVED
        recommendation.approved_by = approved_by
        recommendation.approved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    @staticmethod
    def reject_recommendation(
        db: Session,
        recommendation_id: int,
        approved_by: str,
        rejection_reason: str
    ) -> Recommendation:
        """
        Reject a recommendation.
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation to reject
            approved_by: Username of rejector
            rejection_reason: Reason for rejection
            
        Returns:
            Updated Recommendation object
            
        Raises:
            ValueError: If recommendation not found or already processed
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise ValueError(f"Recommendation with ID {recommendation_id} not found")
        
        if recommendation.status != RecommendationStatus.PENDING:
            raise ValueError(
                f"Recommendation {recommendation_id} is already {recommendation.status.value}, "
                f"cannot reject"
            )
        
        # Update recommendation
        recommendation.status = RecommendationStatus.REJECTED
        recommendation.approved_by = approved_by
        recommendation.approved_at = datetime.utcnow()
        recommendation.rejection_reason = rejection_reason
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    @staticmethod
    def mark_deployed(
        db: Session,
        recommendation_id: int
    ) -> Recommendation:
        """
        Mark a recommendation as deployed.
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation to mark as deployed
            
        Returns:
            Updated Recommendation object
            
        Raises:
            ValueError: If recommendation not found
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            raise ValueError(f"Recommendation with ID {recommendation_id} not found")
        
        # Update recommendation
        recommendation.status = RecommendationStatus.DEPLOYED
        recommendation.deployed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    @staticmethod
    def delete_recommendation(db: Session, recommendation_id: int) -> bool:
        """
        Delete a recommendation.
        
        Args:
            db: Database session
            recommendation_id: ID of recommendation to delete
            
        Returns:
            True if deleted, False if not found
        """
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if not recommendation:
            return False
        
        db.delete(recommendation)
        db.commit()
        
        return True

