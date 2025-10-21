from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models.user import User
from models.consent import DataConsent
from schemas.consent import DataConsent as DataConsentSchema, ConsentResponse, ConsentUpdate
from auth.supabase_auth import get_current_user_supabase as get_current_user

router = APIRouter(prefix="/consent", tags=["data consent"])

@router.post("/give", response_model=ConsentResponse)
async def give_consent(
    consent_data: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User gives consent for data usage."""
    
    # Check if consent already exists
    existing_consent = db.query(DataConsent).filter(
        DataConsent.user_id == current_user.id
    ).first()
    
    if existing_consent:
        # Update existing consent
        existing_consent.consent_given = consent_data.consent_given
        existing_consent.consent_date = datetime.utcnow()
        existing_consent.data_collection = consent_data.data_usage_consent.data_collection
        existing_consent.data_processing = consent_data.data_usage_consent.data_processing
        existing_consent.data_sharing = consent_data.data_usage_consent.data_sharing
        existing_consent.ai_insights = consent_data.data_usage_consent.ai_insights
        existing_consent.email_notifications = consent_data.data_usage_consent.email_notifications
        existing_consent.analytics_tracking = consent_data.data_usage_consent.analytics_tracking
        existing_consent.health_metrics = consent_data.data_usage_consent.health_metrics
        existing_consent.activity_data = consent_data.data_usage_consent.activity_data
        existing_consent.personal_info = consent_data.data_usage_consent.personal_info
        existing_consent.usage_patterns = consent_data.data_usage_consent.usage_patterns
        
        db.commit()
        db.refresh(existing_consent)
        consent = existing_consent
    else:
        # Create new consent
        consent = DataConsent(
            user_id=current_user.id,
            consent_given=consent_data.consent_given,
            consent_date=datetime.utcnow(),
            data_collection=consent_data.data_usage_consent.data_collection,
            data_processing=consent_data.data_usage_consent.data_processing,
            data_sharing=consent_data.data_usage_consent.data_sharing,
            ai_insights=consent_data.data_usage_consent.ai_insights,
            email_notifications=consent_data.data_usage_consent.email_notifications,
            analytics_tracking=consent_data.data_usage_consent.analytics_tracking,
            health_metrics=consent_data.data_usage_consent.health_metrics,
            activity_data=consent_data.data_usage_consent.activity_data,
            personal_info=consent_data.data_usage_consent.personal_info,
            usage_patterns=consent_data.data_usage_consent.usage_patterns
        )
        
        db.add(consent)
        db.commit()
        db.refresh(consent)
    
    return ConsentResponse(
        user_id=current_user.id,
        consent_given=consent.consent_given,
        consent_date=consent.consent_date.isoformat(),
        data_usage_consent=DataConsentSchema(
            data_collection=consent.data_collection,
            data_processing=consent.data_processing,
            data_sharing=consent.data_sharing,
            ai_insights=consent.ai_insights,
            email_notifications=consent.email_notifications,
            analytics_tracking=consent.analytics_tracking,
            health_metrics=consent.health_metrics,
            activity_data=consent.activity_data,
            personal_info=consent.personal_info,
            usage_patterns=consent.usage_patterns
        ),
        privacy_policy_version=consent.privacy_policy_version
    )

@router.get("/status", response_model=ConsentResponse)
async def get_consent_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current consent status for user."""
    
    consent = db.query(DataConsent).filter(
        DataConsent.user_id == current_user.id
    ).first()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No consent data found. Please provide consent first."
        )
    
    return ConsentResponse(
        user_id=current_user.id,
        consent_given=consent.consent_given,
        consent_date=consent.consent_date.isoformat(),
        data_usage_consent=DataConsentSchema(
            data_collection=consent.data_collection,
            data_processing=consent.data_processing,
            data_sharing=consent.data_sharing,
            ai_insights=consent.ai_insights,
            email_notifications=consent.email_notifications,
            analytics_tracking=consent.analytics_tracking,
            health_metrics=consent.health_metrics,
            activity_data=consent.activity_data,
            personal_info=consent.personal_info,
            usage_patterns=consent.usage_patterns
        ),
        privacy_policy_version=consent.privacy_policy_version
    )

@router.delete("/withdraw")
async def withdraw_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User withdraws consent for data usage."""
    
    consent = db.query(DataConsent).filter(
        DataConsent.user_id == current_user.id
    ).first()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No consent data found"
        )
    
    # Update consent to withdrawn
    consent.consent_given = False
    consent.consent_date = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Consent withdrawn successfully"}

