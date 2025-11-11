/**
 * MessageInput component - input field for sending messages.
 */
import React, { useState, KeyboardEvent } from 'react';
import {
  Box,
  Input,
  Button,
  HStack,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiSend } from 'react-icons/fi';

interface MessageInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  isLoading = false,
  placeholder = 'Ask me about your health metrics, meal plans, or nutrition...',
}) => {
  const [message, setMessage] = useState('');
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      p={4}
      bg={bgColor}
      borderTopWidth={1}
      borderColor={borderColor}
    >
      <HStack spacing={2}>
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          isDisabled={isLoading}
          size="lg"
        />
        <IconButton
          icon={<FiSend />}
          onClick={handleSend}
          isLoading={isLoading}
          isDisabled={!message.trim() || isLoading}
          colorScheme="blue"
          aria-label="Send message"
          size="lg"
        />
      </HStack>
    </Box>
  );
};

