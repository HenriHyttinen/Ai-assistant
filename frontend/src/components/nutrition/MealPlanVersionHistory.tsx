import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Badge,
  Card,
  CardBody,
  Divider,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useToast,
  Spinner,
  IconButton,
  Tooltip,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText
} from '@chakra-ui/react';
import { FiClock, FiRotateCcw, FiTrash2, FiEye, FiGitBranch } from 'react-icons/fi';
import { format } from 'date-fns';

interface MealPlanVersion {
  id: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  action?: string;
  description?: string;
  meal_count: number;
  total_calories: number;
}

interface MealPlanVersionHistoryProps {
  mealPlanId: string;
  onVersionRestored?: (newPlanId: string) => void;
}

const MealPlanVersionHistory: React.FC<MealPlanVersionHistoryProps> = ({
  mealPlanId,
  onVersionRestored
}) => {
  const [versions, setVersions] = useState<MealPlanVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoring, setRestoring] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<MealPlanVersion | null>(null);
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { 
    isOpen: isDeleteOpen, 
    onOpen: onDeleteOpen, 
    onClose: onDeleteClose 
  } = useDisclosure();
  
  const toast = useToast();
  const cancelRef = React.useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (mealPlanId) {
      fetchVersions();
    }
  }, [mealPlanId]);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();

      console.log('🔐 Session token:', session?.access_token ? 'Present' : 'Missing');
      console.log('🔐 Token preview:', session?.access_token?.substring(0, 20) + '...');
      console.log('🔐 Full session:', session);

      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlanId}/versions`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions || []);
      } else {
        throw new Error('Failed to fetch versions');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch meal plan versions',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const restoreVersion = async (versionId: string) => {
    setRestoring(versionId);
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();

      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/restore/${versionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: 'Meal plan version restored successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Refresh versions
        await fetchVersions();
        
        // Notify parent component
        if (onVersionRestored) {
          onVersionRestored(data.new_meal_plan_id);
        }
      } else {
        throw new Error('Failed to restore version');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to restore meal plan version',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setRestoring(null);
    }
  };

  const deleteVersion = async (versionId: string) => {
    setDeleting(versionId);
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();

      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlanId}/versions/${versionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });
      
      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Meal plan version deleted successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Refresh versions
        await fetchVersions();
      } else {
        throw new Error('Failed to delete version');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete meal plan version',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setDeleting(null);
      onDeleteClose();
    }
  };

  const getActionColor = (action?: string) => {
    switch (action) {
      case 'regenerate_plan':
        return 'blue';
      case 'regenerate_meal':
        return 'green';
      case 'reorder_meals':
        return 'purple';
      case 'add_custom_meal':
        return 'orange';
      case 'adjust_portions':
        return 'teal';
      case 'restore_version':
        return 'pink';
      default:
        return 'gray';
    }
  };

  const getActionLabel = (action?: string) => {
    switch (action) {
      case 'regenerate_plan':
        return 'Plan Regenerated';
      case 'regenerate_meal':
        return 'Meal Regenerated';
      case 'reorder_meals':
        return 'Meals Reordered';
      case 'add_custom_meal':
        return 'Custom Meal Added';
      case 'adjust_portions':
        return 'Portions Adjusted';
      case 'restore_version':
        return 'Version Restored';
      default:
        return 'Created';
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="lg" />
        <Text mt={4}>Loading version history...</Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        {versions.length === 0 ? (
          <Card>
            <CardBody textAlign="center" py={8}>
              <Text color="gray.500">No version history available</Text>
            </CardBody>
          </Card>
        ) : (
          versions.map((version) => (
            <Card key={version.id} variant={version.is_active ? 'outline' : 'elevated'}>
              <CardBody>
                <Flex justify="space-between" align="start">
                  <VStack align="start" spacing={2} flex={1}>
                    <HStack>
                      <Badge 
                        colorScheme={version.is_active ? 'green' : 'gray'}
                        variant={version.is_active ? 'solid' : 'subtle'}
                      >
                        {version.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <Badge colorScheme={getActionColor(version.action)}>
                        {getActionLabel(version.action)}
                      </Badge>
                      <Text fontSize="sm" color="gray.500">
                        v{version.version}
                      </Text>
                    </HStack>
                    
                    <Text fontWeight="medium">
                      {version.description || 'Meal plan version'}
                    </Text>
                    
                    <HStack spacing={4} fontSize="sm" color="gray.600">
                      <HStack>
                        <FiClock />
                        <Text>
                          {format(new Date(version.created_at), 'MMM dd, yyyy HH:mm')}
                        </Text>
                      </HStack>
                      <Text>•</Text>
                      <Text>{version.meal_count} meals</Text>
                      <Text>•</Text>
                      <Text>{Math.round(version.total_calories)} calories</Text>
                    </HStack>
                  </VStack>
                  
                  <HStack spacing={2}>
                    <Tooltip label="View Details">
                      <IconButton
                        aria-label="View version details"
                        icon={<FiEye />}
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setSelectedVersion(version);
                          onOpen();
                        }}
                      />
                    </Tooltip>
                    
                    {!version.is_active && (
                      <>
                        <Tooltip label="Restore Version">
                          <IconButton
                            aria-label="Restore version"
                            icon={<FiRotateCcw />}
                            size="sm"
                            variant="ghost"
                            colorScheme="green"
                            isLoading={restoring === version.id}
                            onClick={() => restoreVersion(version.id)}
                          />
                        </Tooltip>
                        
                        <Tooltip label="Delete Version">
                          <IconButton
                            aria-label="Delete version"
                            icon={<FiTrash2 />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => {
                              setSelectedVersion(version);
                              onDeleteOpen();
                            }}
                          />
                        </Tooltip>
                      </>
                    )}
                  </HStack>
                </Flex>
              </CardBody>
            </Card>
          ))
        )}
      </VStack>

      {/* Version Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <FiGitBranch />
              <Text>Version {selectedVersion?.version} Details</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedVersion && (
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Badge colorScheme={getActionColor(selectedVersion.action)}>
                    {getActionLabel(selectedVersion.action)}
                  </Badge>
                  <Text fontSize="sm" color="gray.500">
                    {format(new Date(selectedVersion.created_at), 'MMM dd, yyyy HH:mm')}
                  </Text>
                </HStack>
                
                <Text>{selectedVersion.description}</Text>
                
                <Divider />
                
                <HStack spacing={8}>
                  <Stat>
                    <StatLabel>Meals</StatLabel>
                    <StatNumber>{selectedVersion.meal_count}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Total Calories</StatLabel>
                    <StatNumber>{Math.round(selectedVersion.total_calories)}</StatNumber>
                    <StatHelpText>kcal</StatHelpText>
                  </Stat>
                </HStack>
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            {selectedVersion && !selectedVersion.is_active && (
              <Button
                colorScheme="green"
                leftIcon={<FiRotateCcw />}
                onClick={() => {
                  restoreVersion(selectedVersion.id);
                  onClose();
                }}
                isLoading={restoring === selectedVersion.id}
              >
                Restore Version
              </Button>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Version
            </AlertDialogHeader>
            <AlertDialogBody>
              Are you sure you want to delete version {selectedVersion?.version}? 
              This action cannot be undone.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={() => selectedVersion && deleteVersion(selectedVersion.id)}
                ml={3}
                isLoading={deleting === selectedVersion?.id}
              >
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default MealPlanVersionHistory;


