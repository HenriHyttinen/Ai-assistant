"""
Security utilities for AI assistant.
Handles authentication verification, data ownership checks, and jailbreak protection.
"""
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates security constraints for AI assistant."""
    
    def __init__(self):
        """Initialize security validator."""
        # Jailbreak patterns
        self.jailbreak_patterns = [
            r'ignore\s+(all\s+)?(previous|above)\s+(instructions?|rules?|guidelines?)',
            r'ignore\s+all\s+previous',
            r'forget\s+(all\s+)?(previous|above)\s+(instructions?|rules?|guidelines?)',
            r'forget\s+all\s+previous',
            r'forget\s+(the\s+)?(rules?|instructions?|guidelines?)',
            r'you\s+are\s+now\s+(a|an)\s+',
            r'pretend\s+to\s+be',
            r'act\s+as\s+if',
            r'roleplay\s+as',
            r'system\s*:\s*',
            r'<\|system\|>',
            r'\[INST\]',
            r'###\s*System',
        ]
        
        # Medical advice patterns
        self.medical_patterns = [
            r'diagnos[ie]s',
            r'prescrib[ie]',
            r'treatment\s+plan',
            r'medication',
            r'dosage',
            r'symptom',
            r'condition',
            r'disease',
            r'illness',
        ]
    
    def verify_data_ownership(
        self,
        user_id: str,
        resource_user_id: str,
        resource_type: str = "data"
    ) -> bool:
        """
        Verify that user owns the resource they're trying to access.
        
        Args:
            user_id: Current user ID
            resource_user_id: Resource owner ID
            resource_type: Type of resource (for logging)
        
        Returns:
            True if user owns resource, False otherwise
        """
        if user_id != resource_user_id:
            logger.warning(
                f"Data ownership violation: User {user_id} attempted to access {resource_type} "
                f"owned by {resource_user_id}"
            )
            return False
        return True
    
    def detect_jailbreak_attempt(self, message: str) -> bool:
        """
        Detect jailbreak attempts in user message.
        
        Args:
            message: User message to check
        
        Returns:
            True if jailbreak detected, False otherwise
        """
        message_lower = message.lower()
        
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.warning(f"Jailbreak attempt detected: {pattern}")
                return True
        
        return False
    
    def detect_medical_advice_request(self, message: str) -> bool:
        """
        Detect medical advice requests in user message.
        
        Args:
            message: User message to check
        
        Returns:
            True if medical advice request detected, False otherwise
        """
        message_lower = message.lower()
        
        # Check for medical keywords
        medical_keywords = [
            'diagnose', 'diagnosis', 'prescribe', 'prescription',
            'treatment', 'medication', 'dosage', 'symptom',
            'condition', 'disease', 'illness', 'cure', 'heal'
        ]
        
        for keyword in medical_keywords:
            if keyword in message_lower:
                # Check context - if asking about their own data/metrics, it's OK
                # But direct medical questions should be flagged
                if any(word in message_lower for word in ['my', 'what is', 'tell me about']) and \
                   not any(word in message_lower for word in ['should', 'can you', 'what\'s the', 'what\'s', 'need', 'diagnose', 'prescribe', 'treatment', 'dosage', 'medication']):
                    # Asking about their own data/metrics is OK (e.g., "What is my BMI?")
                    continue
                # Otherwise, might be asking for medical advice
                logger.info(f"Potential medical advice request detected: {keyword}")
                return True
        
        return False
    
    def sanitize_input(self, message: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            message: User message to sanitize
        
        Returns:
            Sanitized message
        """
        # Remove potential script tags
        message = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potential HTML tags (keep basic formatting)
        message = re.sub(r'<[^>]+>', '', message)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r"';?\s*drop\s+table",
            r"';?\s*delete\s+from",
            r"';?\s*insert\s+into",
            r"';?\s*update\s+.*\s+set",
            r"union\s+select",
            r"or\s+1\s*=\s*1",
        ]
        for pattern in sql_patterns:
            message = re.sub(pattern, '', message, flags=re.IGNORECASE)
        
        # Remove JavaScript event handlers
        message = re.sub(r'on\w+\s*=', '', message, flags=re.IGNORECASE)
        
        # Limit message length
        max_length = 5000
        if len(message) > max_length:
            message = message[:max_length]
            logger.warning(f"Message truncated to {max_length} characters")
        
        return message.strip()
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """
        Validate user message for security issues.
        
        Args:
            message: User message to validate
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for empty message
        if not message or not message.strip():
            result["valid"] = False
            result["errors"].append("Message cannot be empty")
            return result
        
        # Check for jailbreak attempts
        if self.detect_jailbreak_attempt(message):
            result["valid"] = False
            result["errors"].append("Invalid request detected")
            return result
        
        # Check for medical advice requests
        if self.detect_medical_advice_request(message):
            result["warnings"].append("Medical advice request detected")
            # Don't block, but flag for special handling
        
        # Sanitize input
        sanitized = self.sanitize_input(message)
        if sanitized != message:
            result["warnings"].append("Message was sanitized")
        
        return result


class MedicalAdviceBoundary:
    """Handles medical advice boundaries and disclaimers."""
    
    @staticmethod
    def get_disclaimer() -> str:
        """Get medical advice disclaimer."""
        return (
            "⚠️ **Important**: I'm a wellness assistant, not a medical professional. "
            "For any health concerns, symptoms, or medical questions, please consult with "
            "a qualified healthcare provider. I can provide general wellness information "
            "and help you track your health data, but I cannot diagnose conditions or "
            "provide medical treatment recommendations."
        )
    
    @staticmethod
    def should_add_disclaimer(message: str, response: str) -> bool:
        """
        Determine if disclaimer should be added to response.
        
        Args:
            message: User message
            response: AI response
        
        Returns:
            True if disclaimer should be added
        """
        # Add disclaimer if medical terms appear in message or response
        medical_terms = [
            'diagnosis', 'diagnose', 'treatment', 'prescription', 'prescribe', 'medication',
            'symptom', 'symptoms', 'condition', 'disease', 'illness', 'diabetes', 'dosage'
        ]
        
        message_lower = message.lower()
        response_lower = response.lower()
        
        for term in medical_terms:
            if term in message_lower or term in response_lower:
                return True
        
        return False
    
    @staticmethod
    def add_disclaimer_if_needed(message: str, response: str) -> str:
        """
        Add disclaimer to response if needed.
        
        Args:
            message: User message
            response: AI response
        
        Returns:
            Response with disclaimer if needed
        """
        if MedicalAdviceBoundary.should_add_disclaimer(message, response):
            return f"{response}\n\n{MedicalAdviceBoundary.get_disclaimer()}"
        return response

