/**
 * ChatInterface component - main chat interface for AI assistant.
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertDescription,
} from '@chakra-ui/react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import type { Message } from '../../services/assistantService';
import { assistantService } from '../../services/assistantService';

interface ChatInterfaceProps {
  conversationId?: string;
  onConversationChange?: (conversationId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  onConversationChange,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const bgColor = useColorModeValue('white', 'gray.900');

  // Sync with parent conversationId prop
  useEffect(() => {
    setCurrentConversationId(conversationId);
  }, [conversationId]);

  // Load conversation messages when conversationId changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      // Clear messages when starting a new conversation
      setMessages([]);
      setError(null);
    }
  }, [currentConversationId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async (convId: string) => {
    try {
      setIsLoading(true);
      const loadedMessages = await assistantService.getConversationMessages(convId);
      setMessages(loadedMessages);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load messages');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (message: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Add user message to UI immediately (optimistic update)
      const tempUserMessage: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: currentConversationId || '',
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMessage]);

      // Send message to API
      const response = await assistantService.sendMessage({
        message,
        conversation_id: currentConversationId,
      });

      // Update conversation ID if new conversation was created
      if (response.conversation_id !== currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        if (onConversationChange) {
          onConversationChange(response.conversation_id);
        }
      }

      // Replace temp message with actual user message and add assistant response
      setMessages((prev) => {
        // Remove temp message
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id);
        
        // Add actual user message from response (if available) or keep temp
        const userMsg = response.user_message || tempUserMessage;
        
        // Add both user and assistant messages
        return [...filtered, userMsg, response.message];
      });
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => !m.id.startsWith('temp-')));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box h="100%" display="flex" flexDirection="column" bg={bgColor}>
      {error && (
        <Alert status="error" borderRadius="md" m={4}>
          <AlertIcon />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      <Box flex={1} overflowY="auto">
        <MessageList messages={messages} isLoading={isLoading && messages.length === 0} />
        <div ref={messagesEndRef} />
      </Box>
      <MessageInput onSend={handleSend} isLoading={isLoading} />
    </Box>
  );
};

