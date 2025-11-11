"""
Conversation service - Conversation Layer logic.
Handles conversation flow, context management, and response formatting.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.conversation import Conversation, Message
from ai.assistant_ai import AssistantAI
from ai.system_prompts import get_system_prompt
from services.data_access_service import DataAccessService
from services.api_client import APIClient
from ai.function_calling import initialize_functions
from utils.security import SecurityValidator, MedicalAdviceBoundary
from utils.context_manager import ContextManager
from utils.dynamic_context import DynamicContextManager
import logging
import uuid
import json

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations."""
    
    def __init__(self, db: Session, auth_token: str):
        """
        Initialize conversation service.
        
        Args:
            db: Database session
            auth_token: Authentication token for API calls
        """
        self.db = db
        
        # Initialize data access layer
        api_client = APIClient(auth_token)
        data_access = DataAccessService(api_client)
        
        # Initialize function registry
        function_registry = initialize_functions(data_access)
        
        # Initialize AI assistant
        self.assistant = AssistantAI(function_registry)
        self.data_access = data_access
        
        # Initialize security validator
        self.security_validator = SecurityValidator()
        
        # Initialize context managers
        self.context_manager = ContextManager()
        self.dynamic_context = DynamicContextManager()
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            user_id: User ID
            message: User message
            conversation_id: Optional conversation ID
        
        Returns:
            Response dictionary
        """
        try:
            # Validate message security
            validation = self.security_validator.validate_message(message)
            if not validation["valid"]:
                raise ValueError(validation["errors"][0] if validation["errors"] else "Invalid message")
            
            # Sanitize message
            sanitized_message = self.security_validator.sanitize_input(message)
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(user_id, conversation_id)
            
            # Verify conversation ownership
            if not self.security_validator.verify_data_ownership(user_id, conversation.user_id, "conversation"):
                raise ValueError("Unauthorized access to conversation")
            
            # Get user preferences for system prompt
            user_preferences = await self._get_user_preferences()
            user_name = user_preferences.get("name", "User")
            
            # Get conversation history
            history = await self._get_conversation_history(conversation.id)
            
            # Aggressively filter out any tool messages and tool_calls
            cleaned_history = []
            for msg in history:
                msg_role = msg.get("role", "user")
                # Skip ALL tool messages
                if msg_role == "tool":
                    logger.warning(f"Found tool message in history, skipping: {msg.get('content', '')[:50]}")
                    continue
                
                # Create clean message without tool_calls
                clean_msg = {
                    "role": msg_role,
                    "content": msg.get("content", "")
                }
                
                # Remove tool_calls if present
                if msg.get("tool_calls"):
                    logger.warning(f"Found tool_calls in history message, removing: {msg.get('content', '')[:50]}")
                
                cleaned_history.append(clean_msg)
            
            history = cleaned_history
            
            # Apply dynamic context management
            if history:
                # Prioritize messages by relevance
                history = self.dynamic_context.prioritize_by_relevance(
                    history,
                    sanitized_message,
                    max_messages=10
                )
                
                # Compress if needed
                history = self.context_manager.compress_conversation(history)
            
            # Determine response detail level (concise or detailed)
            detail_level = self.dynamic_context.adjust_detail_level(sanitized_message, history)
            
            # Build system prompt with detail level guidance
            system_prompt = get_system_prompt(user_name, user_preferences, detail_level=detail_level)
            
            # Generate response
            ai_response = await self.assistant.generate_response(
                user_message=sanitized_message,
                conversation_history=history,
                system_prompt=system_prompt,
                user_name=user_name
            )
            
            # Add medical disclaimer if needed
            response_content = ai_response.get("content", "")
            response_content = MedicalAdviceBoundary.add_disclaimer_if_needed(
                sanitized_message,
                response_content
            )
            ai_response["content"] = response_content
            
            # Save user message (use sanitized version)
            user_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                role="user",
                content=sanitized_message,
                token_count=len(sanitized_message.split())  # Rough estimate
            )
            self.db.add(user_msg)
            
            # Save assistant response
            assistant_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                role="assistant",
                content=ai_response.get("content", ""),
                function_calls=ai_response.get("function_calls"),
                function_results=ai_response.get("function_results"),
                token_count=ai_response.get("token_usage", {}).get("completion_tokens", 0)
            )
            self.db.add(assistant_msg)
            
            # Update conversation
            conversation.updated_at = datetime.now()
            if not conversation.title and len(message) > 0:
                # Generate title from first message
                conversation.title = message[:50] + "..." if len(message) > 50 else message
            
            self.db.commit()
            self.db.refresh(assistant_msg)
            self.db.refresh(user_msg)
            
            return {
                "message": {
                    "id": assistant_msg.id,
                    "conversation_id": conversation.id,
                    "role": "assistant",
                    "content": assistant_msg.content,
                    "function_calls": assistant_msg.function_calls,
                    "function_results": assistant_msg.function_results,
                    "token_count": assistant_msg.token_count,
                    "created_at": assistant_msg.created_at
                },
                "user_message": {
                    "id": user_msg.id,
                    "conversation_id": conversation.id,
                    "role": "user",
                    "content": user_msg.content,
                    "token_count": user_msg.token_count,
                    "created_at": user_msg.created_at
                },
                "conversation_id": conversation.id,
                "function_calls": ai_response.get("function_calls", []),
                "token_usage": ai_response.get("token_usage", {})
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.db.rollback()
            raise
    
    async def _get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing conversation or create new one."""
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if conversation:
                return conversation
        
        # Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=None
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    async def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for context.
        Properly reconstructs tool messages from stored function_calls and function_results.
        """
        # Filter out tool messages at the database level
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role != "tool"  # Exclude tool messages at query level
        ).order_by(Message.created_at.asc()).all()
        
        history = []
        for msg in messages:
            # Double-check: skip tool messages (shouldn't be needed, but safety check)
            if msg.role == "tool":
                logger.warning(f"Found tool message in database query result, skipping: {msg.id}")
                continue
            
            # Add user or assistant message (without tool_calls)
            msg_dict = {
                "role": msg.role,
                "content": msg.content
            }
            
            # Don't include tool_calls in conversation history
            # Tool calls have already been executed and results are in the content
            # Including tool_calls causes OpenAI to expect tool messages, which causes validation errors
            
            history.append(msg_dict)
        
        return history
    
    async def _get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences for personalization."""
        try:
            preferences = await self.data_access.api_client.get_nutrition_preferences()
            return preferences
        except Exception:
            return {}

