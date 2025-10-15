// @ts-nocheck
import {
  Box,
  Button,
  Text,
  VStack,
  HStack,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Code,
  Divider,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { useState } from 'react';
import { FaCode, FaCopy, FaCheck } from 'react-icons/fa';

interface DevHelperProps {
  title: string;
  links: Array<{
    label: string;
    url: string;
    description?: string;
  }>;
  isOpen: boolean;
  onClose: () => void;
}

const DevHelper: React.FC<DevHelperProps> = ({ title, links, isOpen, onClose }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack>
            <FaCode />
            <Text>Development Helper - {title}</Text>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack spacing={4} align="stretch">
            <Alert status="info">
              <AlertIcon />
              <Text fontSize="sm">
                For testing purposes, use the links below instead of checking email.
              </Text>
            </Alert>

            {links.map((link, index) => (
              <Box key={index} p={4} border="1px" borderColor="gray.200" borderRadius="md">
                <VStack spacing={3} align="stretch">
                  <HStack justify="space-between">
                    <Text fontWeight="bold" color="blue.600">
                      {link.label}
                    </Text>
                    <IconButton
                      aria-label="Copy link"
                      icon={copiedIndex === index ? <FaCheck /> : <FaCopy />}
                      size="sm"
                      colorScheme={copiedIndex === index ? "green" : "blue"}
                      onClick={() => copyToClipboard(link.url, index)}
                    />
                  </HStack>
                  
                  {link.description && (
                    <Text fontSize="sm" color="gray.600">
                      {link.description}
                    </Text>
                  )}
                  
                  <Code p={2} fontSize="xs" wordBreak="break-all">
                    {link.url}
                  </Code>
                  
                  <Button
                    as="a"
                    href={link.url}
                    target="_blank"
                    colorScheme="blue"
                    size="sm"
                    width="full"
                  >
                    Open Link
                  </Button>
                </VStack>
              </Box>
            ))}

            <Divider />
            
            <Text fontSize="sm" color="gray.500" textAlign="center">
              These links are only shown in development mode for testing purposes.
            </Text>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default DevHelper;
