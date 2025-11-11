"""
Dynamic context management for AI assistant.
Handles topic detection, relevance scoring, and dynamic detail adjustment.
"""
from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class DynamicContextManager:
    """Manages dynamic context based on conversation topics."""
    
    def __init__(self):
        """Initialize dynamic context manager."""
        # Topic keywords
        self.topic_keywords = {
            "health_metrics": ["bmi", "weight", "wellness", "health", "metrics", "activity"],
            "meal_planning": ["meal", "food", "recipe", "breakfast", "lunch", "dinner", "snack"],
            "nutrition": ["calories", "protein", "carbs", "fats", "nutrition", "macros"],
            "progress": ["progress", "goal", "target", "improvement", "change"],
            "recipe": ["recipe", "ingredient", "cook", "prepare", "instructions"],
        }
    
    def detect_topics(self, message: str) -> List[str]:
        """
        Detect topics in user message.
        
        Args:
            message: User message
        
        Returns:
            List of detected topics
        """
        message_lower = message.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def score_relevance(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> float:
        """
        Score relevance of conversation history to current message.
        
        Args:
            message: Current user message
            conversation_history: Previous conversation messages
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not conversation_history:
            return 0.0
        
        # Detect topics in current message
        current_topics = set(self.detect_topics(message))
        
        if not current_topics:
            # If no specific topics, give equal relevance to all
            return 0.5
        
        # Count topic matches in history
        matches = 0
        total = 0
        
        for msg in conversation_history[-10:]:  # Last 10 messages
            content = msg.get("content", "").lower()
            msg_topics = set(self.detect_topics(content))
            
            if msg_topics:
                # Calculate overlap
                overlap = len(current_topics & msg_topics) / len(current_topics | msg_topics)
                matches += overlap
                total += 1
        
        if total == 0:
            return 0.0
        
        return matches / total
    
    def prioritize_by_relevance(
        self,
        messages: List[Dict[str, Any]],
        current_message: str,
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Prioritize messages by relevance to current message.
        
        Args:
            messages: List of messages
            current_message: Current user message
            max_messages: Maximum number of messages to return
        
        Returns:
            Prioritized list of messages
        """
        if len(messages) <= max_messages:
            return messages
        
        # Score each message
        scored_messages = []
        current_topics = set(self.detect_topics(current_message))
        
        for msg in messages:
            content = msg.get("content", "")
            msg_topics = set(self.detect_topics(content))
            
            # Calculate relevance score
            if current_topics and msg_topics:
                overlap = len(current_topics & msg_topics) / len(current_topics | msg_topics)
            else:
                # Recency bonus for messages without topic match
                recency_bonus = 0.1 if len(scored_messages) < 5 else 0.0
                overlap = recency_bonus
            
            scored_messages.append((overlap, msg))
        
        # Sort by relevance (descending)
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        
        # Always include most recent message
        most_recent = messages[-1]
        selected = [most_recent]
        
        # Add top relevant messages
        for score, msg in scored_messages[:max_messages - 1]:
            if msg != most_recent:
                selected.append(msg)
        
        # Sort by original order
        selected.sort(key=lambda m: messages.index(m))
        
        return selected
    
    def adjust_detail_level(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Determine appropriate detail level for response.
        
        Args:
            message: Current user message
            conversation_history: Previous conversation messages
        
        Returns:
            Detail level: "concise" or "detailed"
        """
        message_lower = message.lower()
        
        # Check for explicit detail requests
        if any(word in message_lower for word in ["detailed", "more", "explain", "tell me about"]):
            return "detailed"
        
        if any(word in message_lower for word in ["brief", "quick", "summary", "short"]):
            return "concise"
        
        # Check conversation context
        relevance = self.score_relevance(message, conversation_history)
        
        # If high relevance, user likely wants detailed follow-up
        if relevance > 0.7:
            return "detailed"
        
        # Default to concise for new topics
        return "concise"

