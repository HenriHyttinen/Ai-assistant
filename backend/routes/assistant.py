"""
API routes for AI assistant.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from schemas.assistant import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse
)
from services.conversation_service import ConversationService
from models.conversation import Conversation, Message
from utils.security import SecurityValidator
import logging

logger = logging.getLogger(__name__)

security_validator = SecurityValidator()

router = APIRouter(tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """
    Send a message to the AI assistant and get a response.
    
    Args:
        request: Chat request with message and optional conversation_id
        current_user: Current authenticated user
        db: Database session
        http_request: FastAPI request object (injected)
    
    Returns:
        Chat response with assistant message
    """
    try:
        user_id = str(current_user.id)
        
        # Get token from request headers for API client
        # Extract from Authorization header if available
        auth_token = ""
        if http_request:
            auth_header = http_request.headers.get("Authorization", "")
            if auth_header and auth_header.startswith("Bearer "):
                auth_token = auth_header[7:]  # Remove "Bearer " prefix
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication"
            )
        
        # Create conversation service
        conversation_service = ConversationService(db, auth_token)
        
        # Process message
        response = await conversation_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of conversations
    """
    try:
        user_id = str(current_user.id)
        
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
        
        result = []
        for conv in conversations:
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            result.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": message_count
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of messages
    """
    try:
        user_id = str(current_user.id)
        
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify data ownership
        if not security_validator.verify_data_ownership(str(user_id), str(conversation.user_id), "conversation"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to conversation"
            )
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                function_calls=msg.function_calls,
                function_results=msg.function_results,
                token_count=msg.token_count,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting messages: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        db: Database session
    """
    try:
        user_id = str(current_user.id)
        
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify data ownership
        if not security_validator.verify_data_ownership(str(user_id), str(conversation.user_id), "conversation"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to conversation"
            )
        
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )

