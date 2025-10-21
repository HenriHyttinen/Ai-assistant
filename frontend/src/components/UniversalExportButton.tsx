import React, { useState } from 'react';
import {
  Button,
  Box,
  VStack,
  HStack,
  Text,
  Collapse,
  useDisclosure
} from '@chakra-ui/react';
import { ChevronDownIcon, DownloadIcon } from '@chakra-ui/icons';

interface UniversalExportButtonProps {
  onExportActivities: (format: string) => void;
  onExportAllData: (format: string) => void;
  onExportWeeklySummary: (format: string) => void;
  onExportMonthlySummary: (format: string) => void;
  isLoading: boolean;
}

const UniversalExportButton: React.FC<UniversalExportButtonProps> = ({
  onExportActivities,
  onExportAllData,
  onExportWeeklySummary,
  onExportMonthlySummary,
  isLoading
}) => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <Box position="relative">
      <Button
        onClick={onToggle}
        isLoading={isLoading}
        loadingText="Exporting..."
        size="xs"
        colorScheme="blue"
        variant="outline"
        minW="80px"
        rightIcon={isOpen ? <ChevronDownIcon /> : <ChevronDownIcon />}
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
                  onToggle();
                }}
                _hover={{ bg: "blue.50" }}
                _active={{ bg: "blue.100" }}
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
                  onToggle();
                }}
                _hover={{ bg: "blue.50" }}
                _active={{ bg: "blue.100" }}
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
                  onToggle();
                }}
                _hover={{ bg: "green.50" }}
                _active={{ bg: "green.100" }}
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
                  onToggle();
                }}
                _hover={{ bg: "green.50" }}
                _active={{ bg: "green.100" }}
              >
                Export All Data (JSON)
              </Button>
              
              <Box borderTop="1px solid" borderColor="gray.200" my={1} />
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportWeeklySummary('csv');
                  onToggle();
                }}
                _hover={{ bg: "purple.50" }}
                _active={{ bg: "purple.100" }}
              >
                Export Weekly Summary (CSV)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportWeeklySummary('json');
                  onToggle();
                }}
                _hover={{ bg: "purple.50" }}
                _active={{ bg: "purple.100" }}
              >
                Export Weekly Summary (JSON)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportMonthlySummary('csv');
                  onToggle();
                }}
                _hover={{ bg: "orange.50" }}
                _active={{ bg: "orange.100" }}
              >
                Export Monthly Summary (CSV)
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                justifyContent="flex-start"
                borderRadius={0}
                onClick={() => {
                  onExportMonthlySummary('json');
                  onToggle();
                }}
                _hover={{ bg: "orange.50" }}
                _active={{ bg: "orange.100" }}
              >
                Export Monthly Summary (JSON)
              </Button>
            </VStack>
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
};

export default UniversalExportButton;
