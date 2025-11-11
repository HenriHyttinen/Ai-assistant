"""
Pydantic schemas for assistant API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|assistant)$")


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    conversation_id: str
    role: str
    content: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    function_results: Optional[List[Dict[str, Any]]] = None
    token_count: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: str
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    stream: bool = False  # For future streaming support


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: MessageResponse
    user_message: Optional[MessageResponse] = None  # User message that was sent
    conversation_id: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    token_usage: Optional[Dict[str, int]] = None


class FunctionCallRequest(BaseModel):
    """Schema for function call request."""
    name: str
    arguments: Dict[str, Any]


class FunctionCallResponse(BaseModel):
    """Schema for function call response."""
    name: str
    result: Any
    error: Optional[str] = None

