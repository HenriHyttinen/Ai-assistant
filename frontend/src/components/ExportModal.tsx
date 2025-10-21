import React from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  Text,
  useBreakpointValue,
  useDisclosure
} from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

interface ExportModalProps {
  onExportActivities: (format: string) => void;
  onExportAllData: (format: string) => void;
  isLoading: boolean;
}

const ExportModal: React.FC<ExportModalProps> = ({
  onExportActivities,
  onExportAllData,
  isLoading
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  if (!isMobile) {
    return null; // Let the parent handle desktop
  }

  return (
    <>
      <Button
        onClick={onOpen}
        isLoading={isLoading}
        loadingText="Exporting..."
        size="xs"
        colorScheme="blue"
        variant="outline"
        minW="80px"
      >
        <DownloadIcon mr={1} />
        Export
      </Button>

      <Modal isOpen={isOpen} onClose={onClose} size="sm" isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader fontSize="md">Export Data</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Choose what to export:
              </Text>
              
              <VStack spacing={3} align="stretch">
                <Text fontSize="sm" fontWeight="bold" color="blue.600">
                  Activities Only
                </Text>
                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      onExportActivities('csv');
                      onClose();
                    }}
                    flex={1}
                    colorScheme="blue"
                  >
                    CSV
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      onExportActivities('json');
                      onClose();
                    }}
                    flex={1}
                    colorScheme="blue"
                  >
                    JSON
                  </Button>
                </HStack>
              </VStack>

              <VStack spacing={3} align="stretch">
                <Text fontSize="sm" fontWeight="bold" color="green.600">
                  All Health Data
                </Text>
                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      onExportAllData('csv');
                      onClose();
                    }}
                    flex={1}
                    colorScheme="green"
                  >
                    CSV
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      onExportAllData('json');
                      onClose();
                    }}
                    flex={1}
                    colorScheme="green"
                  >
                    JSON
                  </Button>
                </HStack>
              </VStack>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default ExportModal;
