/**
 * Assistant page - main page for AI assistant.
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Button,
  useColorModeValue,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  List,
  ListItem,
  Text,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react';
import { FiMenu, FiPlus, FiTrash2 } from 'react-icons/fi';
import { ChatInterface } from '../components/assistant/ChatInterface';
import type { Conversation } from '../services/assistantService';
import { assistantService } from '../services/assistantService';

export const Assistant: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const convs = await assistantService.getConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(undefined);
    // Force reload conversations to ensure UI is updated
    loadConversations();
    onClose();
  };

  const handleSelectConversation = (conversationId: string) => {
    setCurrentConversationId(conversationId);
    onClose();
  };

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await assistantService.deleteConversation(conversationId);
      if (currentConversationId === conversationId) {
        setCurrentConversationId(undefined);
      }
      loadConversations();
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleConversationChange = (conversationId: string) => {
    setCurrentConversationId(conversationId);
    loadConversations();
  };

  return (
    <Box
      position="relative"
      h="calc(100vh - 60px - 64px)"
      minH="calc(100vh - 60px - 64px)"
      maxH="calc(100vh - 60px - 64px)"
      w="100%"
      p={0}
      m={0}
      overflow="hidden"
    >
      <HStack spacing={0} h="100%" align="stretch">
        {/* Sidebar - Conversations List */}
        <Box
          w="300px"
          h="100%"
          borderRightWidth={1}
          borderColor={borderColor}
          bg={bgColor}
          display={{ base: 'none', md: 'block' }}
          overflowY="auto"
        >
          <VStack align="stretch" p={4} spacing={4}>
            <HStack justify="space-between">
              <Heading size="md">Conversations</Heading>
              <Button
                leftIcon={<FiPlus />}
                size="sm"
                colorScheme="blue"
                onClick={handleNewConversation}
              >
                New
              </Button>
            </HStack>
            <List spacing={2}>
              {conversations.map((conv) => (
                <ListItem key={conv.id}>
                  <Button
                    w="100%"
                    justifyContent="flex-start"
                    variant={currentConversationId === conv.id ? 'solid' : 'ghost'}
                    onClick={() => handleSelectConversation(conv.id)}
                    rightIcon={
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          icon={<FiTrash2 />}
                          size="xs"
                          variant="ghost"
                          onClick={(e) => e.stopPropagation()}
                        />
                        <MenuList>
                          <MenuItem
                            icon={<FiTrash2 />}
                            onClick={(e) => handleDeleteConversation(conv.id, e)}
                          >
                            Delete
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    }
                  >
                    <Text isTruncated>{conv.title || 'New Conversation'}</Text>
                  </Button>
                </ListItem>
              ))}
            </List>
          </VStack>
        </Box>

        {/* Mobile Menu Button */}
        <Box
          position="absolute"
          top={4}
          left={4}
          display={{ base: 'block', md: 'none' }}
          zIndex={10}
        >
          <IconButton
            icon={<FiMenu />}
            onClick={onOpen}
            aria-label="Open conversations"
          />
        </Box>

        {/* Mobile Drawer */}
        <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
          <DrawerOverlay />
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>Conversations</DrawerHeader>
            <DrawerBody>
              <VStack align="stretch" spacing={4}>
                <Button
                  leftIcon={<FiPlus />}
                  colorScheme="blue"
                  onClick={handleNewConversation}
                >
                  New Conversation
                </Button>
                <List spacing={2}>
                  {conversations.map((conv) => (
                    <ListItem key={conv.id}>
                      <Button
                        w="100%"
                        justifyContent="flex-start"
                        variant={currentConversationId === conv.id ? 'solid' : 'ghost'}
                        onClick={() => handleSelectConversation(conv.id)}
                      >
                        {conv.title || 'New Conversation'}
                      </Button>
                    </ListItem>
                  ))}
                </List>
              </VStack>
            </DrawerBody>
          </DrawerContent>
        </Drawer>

        {/* Chat Interface */}
        <Box flex={1} h="100%" overflow="hidden">
          <ChatInterface
            conversationId={currentConversationId}
            onConversationChange={handleConversationChange}
          />
        </Box>
      </HStack>
    </Box>
  );
};

export default Assistant;

