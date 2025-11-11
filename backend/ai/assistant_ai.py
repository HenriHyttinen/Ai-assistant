"""
Main AI assistant logic.
Handles OpenAI integration, function calling, and response generation.
"""
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import get_settings
import logging
import json

logger = logging.getLogger(__name__)


class AssistantAI:
    """AI assistant for conversational interactions."""
    
    def __init__(self, function_registry):
        """
        Initialize AI assistant.
        
        Args:
            function_registry: Function registry instance
        """
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.function_registry = function_registry
        self.default_model = settings.default_model if hasattr(settings, 'default_model') else "gpt-3.5-turbo"
        self.fallback_model = settings.fallback_model if hasattr(settings, 'fallback_model') else "gpt-3.5-turbo"
        self.temperature = settings.temperature if hasattr(settings, 'temperature') else 0.7
        self.top_p = settings.top_p if hasattr(settings, 'top_p') else 1.0
        self.max_tokens = settings.max_tokens if hasattr(settings, 'max_tokens') else 2000
    
    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        use_functions: bool = True,
        _retry_count: int = 0,
        allow_tool_messages: bool = False
    ) -> Dict[str, Any]:
        """
        Call OpenAI API.
        
        Args:
            messages: Conversation messages
            functions: Function definitions
            model: Model to use (defaults to default_model)
            use_functions: Whether to use function calling
            _retry_count: Internal retry counter to prevent infinite recursion
        
        Returns:
            OpenAI response
        """
        model = model or self.default_model
        
        # Prevent infinite recursion
        if _retry_count > 1:
            logger.error(f"Maximum retry attempts reached. Last error was with model: {model}")
            raise Exception(f"OpenAI API call failed after {_retry_count} attempts")
        
        # CRITICAL: Filter out tool messages from conversation history
        # BUT: Allow tool messages if they're part of the current turn (after function execution)
        # Tool messages in the current turn contain function results that the AI needs to see
        if not allow_tool_messages:
            # Filter out ALL tool messages (from conversation history)
            original_count = len(messages)
            filtered_messages = []
            for i, msg in enumerate(messages):
                msg_role = msg.get("role")
                if msg_role == "tool":
                    logger.warning(f"Filtering out tool message at index {i} from conversation history")
                    logger.warning(f"  Tool message content: {str(msg.get('content', ''))[:100]}")
                    continue
                filtered_messages.append(msg)
            
            if len(filtered_messages) != original_count:
                removed = original_count - len(filtered_messages)
                logger.info(f"Removed {removed} tool message(s) from conversation history")
                messages = filtered_messages
        else:
            # Allow tool messages - they're part of the current turn with function results
            logger.info(f"Allowing tool messages in current turn (function results needed)")
            tool_count = sum(1 for msg in messages if msg.get("role") == "tool")
            if tool_count > 0:
                logger.info(f"Found {tool_count} tool message(s) with function results - these will be sent to OpenAI")
        
        # Log what we're actually sending
        logger.error(f"_call_openai: Sending {len(messages)} messages to OpenAI")
        for i, msg in enumerate(messages):
            logger.error(f"  [{i}] role={msg.get('role')}, has_tool_calls={bool(msg.get('tool_calls'))}")
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens
        }
        
        if use_functions and functions:
            kwargs["tools"] = [{"type": "function", "function": func} for func in functions]
            kwargs["tool_choice"] = "auto"
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            
            return {
                "content": message.content,
                "function_calls": message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else None,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            error_str = str(e)
            logger.error(f"OpenAI API error: {error_str}")
            
            # Only retry with fallback model if it's a model-specific error and we haven't already tried fallback
            if model == self.default_model and self.fallback_model and _retry_count == 0:
                # Check if error is related to message format (don't retry for these)
                if "tool" in error_str.lower() or "message" in error_str.lower() or "invalid" in error_str.lower():
                    logger.error("Message format error detected. Not retrying with fallback model.")
                    raise
                logger.info(f"Trying fallback model: {self.fallback_model}")
                return self._call_openai(messages, functions, self.fallback_model, use_functions, _retry_count + 1)
            raise
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        system_prompt: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response to user message.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
            system_prompt: System prompt
            user_name: User's name for personalization
        
        Returns:
            Response dictionary with content, function_calls, token_usage
        """
        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]
        
        # Log conversation history before filtering
        logger.info(f"Conversation history before filtering: {len(conversation_history)} messages")
        for i, msg in enumerate(conversation_history[-10:]):
            logger.info(f"  History[{i}]: role={msg.get('role')}, has_tool_calls={bool(msg.get('tool_calls'))}, content_preview={str(msg.get('content', ''))[:50]}")
        
        # Process conversation history and filter out ALL tool messages
        # Tool messages are not needed in conversation history - the assistant already has function results
        # Including them causes issues with OpenAI's API validation
        filtered_history = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            msg_role = msg.get("role", "user")
            
            # Skip all tool messages from conversation history
            # They're not needed for context and cause validation errors
            if msg_role == "tool":
                logger.error(f"CRITICAL: Found tool message in conversation_history! Skipping: {msg.get('content', '')[:50]}")
                continue
            
            # Also skip any messages with tool_calls - they've already been executed
            if msg.get("tool_calls"):
                logger.warning(f"Skipping message with tool_calls from history: {msg.get('content', '')[:50]}")
                # Create a clean version without tool_calls
                clean_msg = {
                    "role": msg_role,
                    "content": msg.get("content", "")
                }
                filtered_history.append(clean_msg)
            else:
                # Add non-tool messages
                filtered_history.append(msg)
        
        # Add filtered conversation history to messages
        # Don't include tool_calls in history - they've already been executed
        # Including them causes validation errors with OpenAI's API
        for msg in filtered_history:
            msg_dict = {
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            }
            
            # Don't include tool_calls in history messages
            # Tool calls have already been executed and results are in the content
            # Including tool_calls causes OpenAI to expect tool messages, which causes errors
            
            messages.append(msg_dict)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Final validation: remove ALL tool messages from history
        # Tool messages should only be added during the current conversation turn, not from history
        validated_messages = []
        for i, msg in enumerate(messages):
            msg_role = msg.get("role")
            if msg_role == "tool":
                # Skip ALL tool messages from history - they're not needed
                logger.warning(f"Skipping tool message at index {i} from conversation history")
                continue
            else:
                validated_messages.append(msg)
        
        messages = validated_messages
        
        # Log final message structure for debugging
        logger.info(f"Final messages structure: {[{'role': m.get('role'), 'has_tool_calls': bool(m.get('tool_calls'))} for m in messages]}")
        
        # Final safety check: remove ALL tool messages before sending to OpenAI
        # Tool messages should only be added during the current conversation turn, not from history
        original_count = len(messages)
        messages = [m for m in messages if m.get("role") != "tool"]
        removed_count = original_count - len(messages)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} tool message(s) from messages array before sending to OpenAI")
        
        # Log detailed message structure before sending (use ERROR level to ensure it shows)
        logger.error(f"Messages being sent to OpenAI ({len(messages)} messages):")
        for i, msg in enumerate(messages):
            logger.error(f"  [{i}] role={msg.get('role')}, has_tool_calls={bool(msg.get('tool_calls'))}, content_preview={str(msg.get('content', ''))[:50]}")
        
        # CRITICAL: Final check - remove ALL tool messages before sending
        # This is the last line of defense
        original_messages = messages.copy()
        messages = [m for m in messages if m.get("role") != "tool"]
        
        if len(messages) != len(original_messages):
            removed = len(original_messages) - len(messages)
            logger.error(f"CRITICAL: Removed {removed} tool message(s) in final check!")
            for i, msg in enumerate(original_messages):
                if msg.get("role") == "tool":
                    logger.error(f"  Removed tool message at index {i}: {str(msg.get('content', ''))[:50]}")
        
        # Double-check: ensure no tool messages remain
        tool_messages = [i for i, m in enumerate(messages) if m.get("role") == "tool"]
        if tool_messages:
            logger.error(f"CRITICAL: Found tool messages at indices {tool_messages} after final filtering!")
            # Force remove them
            messages = [m for m in messages if m.get("role") != "tool"]
            logger.error(f"Force removed tool messages, new count: {len(messages)}")
        
        # Get function definitions
        functions = self.function_registry.get_function_definitions()
        
        # Call OpenAI
        response = self._call_openai(messages, functions, use_functions=True)
        
        # Handle function calls if any
        function_calls = []
        function_results = []
        
        if response.get("function_calls"):
            # CRITICAL: We need to add the assistant message with tool_calls to the messages array
            # BEFORE adding tool messages, because tool messages must immediately follow assistant messages with tool_calls
            assistant_message_with_tool_calls = {
                "role": "assistant",
                "content": response.get("content") or "",
                "tool_calls": [
                    {
                        "id": tool_call.id if hasattr(tool_call, 'id') else f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments if isinstance(tool_call.function.arguments, str) else json.dumps(tool_call.function.arguments)
                        }
                    }
                    for i, tool_call in enumerate(response["function_calls"])
                ]
            }
            messages.append(assistant_message_with_tool_calls)
            logger.info(f"Added assistant message with {len(response['function_calls'])} tool_calls")
            
            for tool_call in response["function_calls"]:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                
                try:
                    # Call function
                    result = await self.function_registry.call_function(
                        function_name,
                        function_args
                    )
                    
                    # Store full tool_call info including id for proper reconstruction
                    tool_call_id = tool_call.id if hasattr(tool_call, 'id') else f"call_{len(function_calls)}"
                    function_calls.append({
                        "id": tool_call_id,
                        "name": function_name,
                        "arguments": function_args
                    })
                    function_results.append({
                        "name": function_name,
                        "result": result
                    })
                    
                    # Add function result to messages
                    # Log the function result for debugging
                    logger.info(f"Function {function_name} returned result: {json.dumps(result)[:200]}...")
                    
                    # Format result to make it clear this is current data
                    if isinstance(result, dict):
                        result_str = json.dumps(result, indent=2)
                    else:
                        result_str = json.dumps(result) if not isinstance(result, str) else result
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id if hasattr(tool_call, 'id') else None,
                        "content": result_str
                    })
                    
                    logger.info(f"Added tool message with result for function {function_name}")
                    
                except Exception as e:
                    logger.error(f"Error calling function {function_name}: {str(e)}")
                    function_results.append({
                        "name": function_name,
                        "error": str(e)
                    })
            
            # Get final response after function calls
            # Log the messages being sent for final response (including tool messages)
            logger.info(f"Getting final response after function calls. Messages count: {len(messages)}")
            for i, msg in enumerate(messages):
                if msg.get("role") == "tool":
                    logger.info(f"  Tool message [{i}]: {str(msg.get('content', ''))[:200]}...")
                elif msg.get("role") == "assistant" and msg.get("tool_calls"):
                    logger.info(f"  Assistant message [{i}] with {len(msg.get('tool_calls', []))} tool_calls")
                else:
                    logger.info(f"  Message [{i}]: role={msg.get('role')}, content_preview={str(msg.get('content', ''))[:50]}")
            
            # CRITICAL: When calling OpenAI after function execution, we MUST include tool messages
            # Tool messages contain the function results that the AI needs to generate the response
            # Only filter tool messages from conversation history, not from current turn
            response = self._call_openai(messages, functions, use_functions=False, allow_tool_messages=True)
        
        return {
            "content": response.get("content", ""),
            "function_calls": function_calls,
            "function_results": function_results,
            "token_usage": response.get("usage", {}),
            "model": response.get("model", self.default_model)
        }

