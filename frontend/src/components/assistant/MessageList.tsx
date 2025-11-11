/**
 * MessageList component - displays conversation messages.
 */
import React from 'react';
import {
  Box,
  VStack,
  Text,
  Avatar,
  HStack,
  useColorModeValue,
  Spinner,
} from '@chakra-ui/react';
import type { Message } from '../../services/assistantService';
import VisualizationChart from './VisualizationChart';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const bgUser = useColorModeValue('blue.50', 'blue.900');
  const bgAssistant = useColorModeValue('gray.50', 'gray.800');
  const textColor = useColorModeValue('gray.800', 'gray.200');

  if (isLoading && messages.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Spinner size="lg" />
      </Box>
    );
  }

  return (
    <VStack spacing={4} align="stretch" p={4}>
      {messages.map((message) => (
        <HStack
          key={message.id}
          align="flex-start"
          spacing={3}
          justify={message.role === 'user' ? 'flex-end' : 'flex-start'}
        >
          {message.role === 'assistant' && (
            <Avatar size="sm" name="AI Assistant" bg="purple.500" />
          )}
          <Box
            maxW="70%"
            p={3}
            borderRadius="lg"
            bg={message.role === 'user' ? bgUser : bgAssistant}
            color={textColor}
          >
            <Text whiteSpace="pre-wrap">{message.content}</Text>
            {message.function_calls && message.function_calls.length > 0 && (
              <Text fontSize="xs" color="gray.500" mt={2}>
                Used {message.function_calls.length} function(s)
              </Text>
            )}
            {/* Render charts from function results */}
            {message.role === 'assistant' && message.function_results && message.function_results.map((result, index) => {
              // Check if this is a chart generation result
              if (result.name === 'generate_chart' && result.result && result.result.type) {
                return (
                  <Box key={`chart-${index}`} mt={4}>
                    <VisualizationChart chartConfig={result.result} />
                  </Box>
                );
              }
              return null;
            })}
          </Box>
          {message.role === 'user' && (
            <Avatar size="sm" name="You" bg="blue.500" />
          )}
        </HStack>
      ))}
    </VStack>
  );
};

