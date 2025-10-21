import React, { useState } from 'react';
import {
  Button,
  Box,
  VStack,
  HStack,
  Text,
  useBreakpointValue,
  Collapse,
  IconButton
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon, DownloadIcon } from '@chakra-ui/icons';

interface MobileExportDropdownProps {
  onExportActivities: (format: string) => void;
  onExportAllData: (format: string) => void;
  isLoading: boolean;
}

const MobileExportDropdown: React.FC<MobileExportDropdownProps> = ({
  onExportActivities,
  onExportAllData,
  isLoading
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const isMobile = useBreakpointValue({ base: true, md: false });

  if (!isMobile) {
    return null; // Let the parent handle desktop
  }

  return (
    <Box position="relative">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        isLoading={isLoading}
        loadingText="Exporting..."
        size="xs"
        colorScheme="blue"
        variant="outline"
        minW="80px"
        rightIcon={isOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
      >
        <DownloadIcon mr={1} />
        Export
      </Button>
      
      <Collapse in={isOpen} animateOpacity>
        <Box
          position="absolute"
          top="100%"
          right={0}
          mt={1}
          bg="white"
          border="1px solid"
          borderColor="gray.200"
          borderRadius="md"
          boxShadow="lg"
          zIndex={9999}
          minW="200px"
        >
          <VStack spacing={0} align="stretch">
            <Text fontSize="xs" fontWeight="bold" p={2} bg="gray.50" borderBottom="1px solid" borderColor="gray.200">
              Export Options
            </Text>
            
            <VStack spacing={0} align="stretch">
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportActivities('csv');
                  setIsOpen(false);
                }}
                _hover={{ bg: "blue.50" }}
              >
                Export Activities (CSV)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportActivities('json');
                  setIsOpen(false);
                }}
                _hover={{ bg: "blue.50" }}
              >
                Export Activities (JSON)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportAllData('csv');
                  setIsOpen(false);
                }}
                _hover={{ bg: "blue.50" }}
              >
                Export All Data (CSV)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportAllData('json');
                  setIsOpen(false);
                }}
                _hover={{ bg: "blue.50" }}
              >
                Export All Data (JSON)
              </Button>
            </VStack>
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
};

export default MobileExportDropdown;
