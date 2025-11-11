"""
Context window management for AI assistant.
Handles message prioritization, context compression, and token management.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Token limits (approximate)
MAX_CONTEXT_TOKENS = 8000  # Leave room for system prompt and response
AVERAGE_TOKENS_PER_MESSAGE = 50  # Rough estimate
MAX_MESSAGES_IN_CONTEXT = MAX_CONTEXT_TOKENS // AVERAGE_TOKENS_PER_MESSAGE


class ContextManager:
    """Manages conversation context and message prioritization."""
    
    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        """
        Initialize context manager.
        
        Args:
            max_tokens: Maximum tokens for context window
        """
        self.max_tokens = max_tokens
        self.avg_tokens_per_message = AVERAGE_TOKENS_PER_MESSAGE
    
    def prioritize_messages(
        self,
        messages: List[Dict[str, Any]],
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize messages for context window.
        
        Strategy:
        1. Always include the most recent messages (last 5-10)
        2. Include system/function call messages
        3. Include messages with high relevance scores
        4. Exclude older, less relevant messages if needed
        
        Args:
            messages: List of message dictionaries
            max_messages: Maximum number of messages to include
        
        Returns:
            Prioritized list of messages
        """
        if not messages:
            return []
        
        max_messages = max_messages or MAX_MESSAGES_IN_CONTEXT
        
        # If we have fewer messages than the limit, return all
        if len(messages) <= max_messages:
            return messages
        
        # Always include the most recent messages (last 10)
        recent_messages = messages[-10:]
        
        # If we still need more, include earlier messages
        if len(recent_messages) < max_messages:
            # Include messages before the recent ones
            earlier_messages = messages[:-10]
            # Take the most recent from earlier messages
            additional_needed = max_messages - len(recent_messages)
            earlier_selected = earlier_messages[-additional_needed:] if earlier_messages else []
            return earlier_selected + recent_messages
        
        # If we have too many recent messages, take the most recent
        return recent_messages[-max_messages:]
    
    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate token count for messages.
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Estimated token count
        """
        if not messages:
            return 0
        
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
        
        # Rough estimate: ~4 characters per token
        return total_chars // 4
    
    def _should_compress(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Determine if compression is needed.
        
        Args:
            messages: List of messages
        
        Returns:
            True if compression needed
        """
        estimated_tokens = self.estimate_tokens(messages)
        threshold = int(self.max_tokens * 0.8)  # 80% of max tokens
        return estimated_tokens > threshold
    
    def compress_context(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Compress context to fit within token limit.
        
        Args:
            messages: List of messages
            target_tokens: Target token count (defaults to max_tokens)
        
        Returns:
            Compressed list of messages
        """
        target_tokens = target_tokens or self.max_tokens
        
        if not messages:
            return []
        
        # Calculate tokens for each message
        message_tokens = []
        total_tokens = 0
        
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                tokens = len(content) // 4  # Rough estimate: ~4 chars per token
            else:
                tokens = 0
            message_tokens.append((msg, tokens))
            total_tokens += tokens
        
        # If we're under the limit, return all
        if total_tokens <= target_tokens:
            return messages
        
        # Start from the most recent messages and work backwards
        compressed = []
        current_tokens = 0
        
        for msg, tokens in reversed(message_tokens):
            if current_tokens + tokens <= target_tokens:
                compressed.insert(0, msg)
                current_tokens += tokens
            else:
                # Can't fit this message, stop
                break
        
        # Always include at least the most recent message
        if not compressed and messages:
            compressed = [messages[-1]]
        
        return compressed
    
    def summarize_old_messages(
        self,
        messages: List[Dict[str, Any]],
        max_recent: int = 10
    ) -> Dict[str, Any]:
        """
        Create summary of old messages for context.
        
        Args:
            messages: List of messages
            max_recent: Number of recent messages to keep in full
        
        Returns:
            Summary dictionary with recent messages and summary
        """
        if len(messages) <= max_recent:
            return {
                "recent_messages": messages,
                "summary": None
            }
        
        recent = messages[-max_recent:]
        old = messages[:-max_recent]
        
        # Create simple summary of old messages
        summary_parts = []
        for msg in old:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:100]  # First 100 chars
            summary_parts.append(f"{role}: {content}...")
        
        summary = "Previous conversation: " + " | ".join(summary_parts)
        
        return {
            "recent_messages": recent,
            "summary": summary
        }
    
    def compress_conversation(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Compress conversation by summarizing old messages.
        
        Args:
            messages: List of messages
            target_tokens: Target token count
        
        Returns:
            Compressed list of messages
        """
        target_tokens = target_tokens or self.max_tokens
        
        # If conversation is short, no compression needed
        # Calculate total tokens by summing individual message tokens
        total_tokens = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_tokens += len(content) // 4  # Rough estimate
        if total_tokens <= target_tokens:
            return messages
        
        # Use summarization for old messages
        summary_result = self.summarize_old_messages(messages)
        
        compressed = summary_result["recent_messages"]
        
        # Add summary as a system message if available
        if summary_result["summary"]:
            compressed.insert(0, {
                "role": "system",
                "content": summary_result["summary"]
            })
        
        return compressed
    
    def get_context_for_ai(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """
        Get formatted context for AI with token management.
        
        Args:
            messages: List of messages
            system_prompt: System prompt text
        
        Returns:
            Formatted messages for AI
        """
        # Estimate system prompt tokens
        system_tokens = self.estimate_tokens(system_prompt)
        
        # Calculate available tokens for messages
        available_tokens = self.max_tokens - system_tokens - 500  # Reserve for response
        
        # Compress messages to fit
        compressed = self.compress_context(messages, available_tokens)
        
        # Format for AI
        formatted = []
        for msg in compressed:
            formatted.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        return formatted

