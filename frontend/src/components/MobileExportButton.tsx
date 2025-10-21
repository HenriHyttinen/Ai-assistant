import React from 'react';
import {
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  VStack,
  Text,
  useBreakpointValue,
  HStack,
  Icon
} from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

interface MobileExportButtonProps {
  onExportActivities: (format: string) => void;
  onExportAllData: (format: string) => void;
  isLoading: boolean;
}

const MobileExportButton: React.FC<MobileExportButtonProps> = ({
  onExportActivities,
  onExportAllData,
  isLoading
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleExport = (type: string, format: string) => {
    if (type === 'activities') {
      onExportActivities(format);
    } else {
      onExportAllData(format);
    }
    onClose();
  };

  if (isMobile) {
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

        <Modal isOpen={isOpen} onClose={onClose} size="sm">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader fontSize="md">Export Data</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <VStack spacing={4} align="stretch">
                <Text fontSize="sm" color="gray.600">
                  Choose what to export:
                </Text>
                
                <VStack spacing={2} align="stretch">
                  <Text fontSize="sm" fontWeight="bold">
                    Activities Only
                  </Text>
                  <HStack spacing={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('activities', 'csv')}
                      flex={1}
                    >
                      CSV
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('activities', 'json')}
                      flex={1}
                    >
                      JSON
                    </Button>
                  </HStack>
                </VStack>

                <VStack spacing={2} align="stretch">
                  <Text fontSize="sm" fontWeight="bold">
                    All Health Data
                  </Text>
                  <HStack spacing={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('all', 'csv')}
                      flex={1}
                    >
                      CSV
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('all', 'json')}
                      flex={1}
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
  }

  // Desktop fallback - return null to use the original Menu
  return null;
};

export default MobileExportButton;
