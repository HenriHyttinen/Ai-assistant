import React from 'react';
import {
  Box,
  HStack,
  Text,
  Icon,
  Badge,
  useColorModeValue,
  Collapse,
  Button,
  VStack,
  useBreakpointValue,
} from '@chakra-ui/react';
import { FiWifi, FiWifiOff, FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';
import { useOffline } from '../hooks/useOffline';

interface OfflineIndicatorProps {
  showDetails?: boolean;
  onRetry?: () => void;
}

const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ 
  showDetails = false, 
  onRetry 
}) => {
  const {
    isOffline,
    isSlowConnection,
    connectionType,
    getConnectionStatus,
    getConnectionMessage,
  } = useOffline();

  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const getStatusIcon = () => {
    if (isOffline) return FiWifiOff;
    if (isSlowConnection) return FiAlertTriangle;
    return FiWifi;
  };

  const getStatusColor = () => {
    if (isOffline) return 'red';
    if (isSlowConnection) return 'yellow';
    return 'green';
  };

  const getStatusText = () => {
    if (isOffline) return 'Offline';
    if (isSlowConnection) return 'Slow Connection';
    return 'Online';
  };

  const getStatusBadge = () => {
    if (isOffline) return 'Offline';
    if (isSlowConnection) return 'Slow';
    return 'Online';
  };

  // Don't show indicator if online with good connection
  if (!isOffline && !isSlowConnection) {
    return null;
  }

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={1000}
      bg={bgColor}
      borderBottom="1px"
      borderBottomColor={borderColor}
      boxShadow="sm"
    >
      <Collapse in={true}>
        <Box p={isMobile ? 2 : 3}>
          <HStack justify="space-between" align="center">
            <HStack spacing={3}>
              <Icon
                as={getStatusIcon()}
                color={`${getStatusColor()}.500`}
                boxSize={isMobile ? 4 : 5}
              />
              <VStack align="start" spacing={0}>
                <HStack spacing={2}>
                  <Text fontSize={isMobile ? 'sm' : 'md'} fontWeight="medium">
                    {getStatusText()}
                  </Text>
                  <Badge
                    colorScheme={getStatusColor()}
                    size="sm"
                    variant="subtle"
                  >
                    {getStatusBadge()}
                  </Badge>
                </HStack>
                {showDetails && (
                  <Text fontSize="xs" color={textColor}>
                    {getConnectionMessage()}
                  </Text>
                )}
              </VStack>
            </HStack>

            <HStack spacing={2}>
              {connectionType && showDetails && (
                <Text fontSize="xs" color={textColor}>
                  {connectionType}
                </Text>
              )}
              {onRetry && (
                <Button
                  size="xs"
                  variant="outline"
                  leftIcon={<Icon as={FiRefreshCw} />}
                  onClick={onRetry}
                  colorScheme={getStatusColor()}
                >
                  Retry
                </Button>
              )}
            </HStack>
          </HStack>
        </Box>
      </Collapse>
    </Box>
  );
};

export default OfflineIndicator;


