"""
Feedback Service
Service layer for feedback database operations and business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

from app.models.feedback import Feedback, FeedbackType
from app.models.alert import Alert
from app.schemas.feedback import FeedbackCreate


class FeedbackService:
    """Service for feedback database operations."""
    
    @staticmethod
    def create_feedback(
        db: Session,
        feedback_data: FeedbackCreate
    ) -> Feedback:
        """
        Create a new feedback entry.
        
        Args:
            db: Database session
            feedback_data: Feedback creation data
            
        Returns:
            Created Feedback object
            
        Raises:
            ValueError: If alert not found
        """
        # Verify alert exists
        alert = db.query(Alert).filter(Alert.id == feedback_data.alert_id).first()
        if not alert:
            raise ValueError(f"Alert with ID {feedback_data.alert_id} not found")
        
        # Create feedback
        feedback = Feedback(
            alert_id=feedback_data.alert_id,
            feedback_type=feedback_data.feedback_type,
            comments=feedback_data.comments,
            admin_user=feedback_data.admin_user,
            created_at=datetime.utcnow()
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return feedback
    
    @staticmethod
    def get_feedback_by_id(db: Session, feedback_id: int) -> Optional[Feedback]:
        """
        Get a specific feedback by ID.
        
        Args:
            db: Database session
            feedback_id: Feedback ID
            
        Returns:
            Feedback object or None if not found
        """
        return db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    @staticmethod
    def get_feedback_by_alert_id(
        db: Session,
        alert_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Feedback], int]:
        """
        Get all feedback for a specific alert.
        
        Args:
            db: Database session
            alert_id: Alert ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of feedback, total count)
        """
        query = db.query(Feedback).filter(Feedback.alert_id == alert_id)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting (newest first)
        query = query.order_by(desc(Feedback.created_at))
        
        # Apply pagination
        feedback_list = query.offset(skip).limit(limit).all()
        
        return feedback_list, total_count
    
    @staticmethod
    def get_all_feedback(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        feedback_type: Optional[FeedbackType] = None,
        alert_id: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Feedback], int]:
        """
        Get all feedback with optional filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            feedback_type: Filter by feedback type
            alert_id: Filter by alert ID
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Tuple of (list of feedback, total count)
        """
        query = db.query(Feedback)
        
        # Apply filters
        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)
        if alert_id:
            query = query.filter(Feedback.alert_id == alert_id)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if hasattr(Feedback, sort_by):
            sort_column = getattr(Feedback, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # Default sorting
            query = query.order_by(desc(Feedback.created_at))
        
        # Apply pagination
        feedback_list = query.offset(skip).limit(limit).all()
        
        return feedback_list, total_count
    
    @staticmethod
    def get_feedback_stats(db: Session) -> dict:
        """
        Get feedback statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with feedback statistics
        """
        total_feedback = db.query(Feedback).count()
        false_positives = db.query(Feedback).filter(
            Feedback.feedback_type == FeedbackType.FALSE_POSITIVE
        ).count()
        true_positives = db.query(Feedback).filter(
            Feedback.feedback_type == FeedbackType.TRUE_POSITIVE
        ).count()
        informative = db.query(Feedback).filter(
            Feedback.feedback_type == FeedbackType.INFORMATIVE
        ).count()
        other = db.query(Feedback).filter(
            Feedback.feedback_type == FeedbackType.OTHER
        ).count()
        
        return {
            "total": total_feedback,
            "false_positives": false_positives,
            "true_positives": true_positives,
            "informative": informative,
            "other": other,
            "false_positive_rate": round(
                false_positives / total_feedback * 100 
                if total_feedback > 0 else 0, 2
            ),
            "true_positive_rate": round(
                true_positives / total_feedback * 100 
                if total_feedback > 0 else 0, 2
            )
        }

