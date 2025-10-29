import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  useToast,
  Spinner,
  Divider,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Grid,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription
} from '@chakra-ui/react';
import { FiGitBranch, FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi';
import { format } from 'date-fns';

interface VersionComparison {
  version1: {
    id: string;
    version: string;
    created_at: string;
    meal_count: number;
    total_calories: number;
    total_protein: number;
  };
  version2: {
    id: string;
    version: string;
    created_at: string;
    meal_count: number;
    total_calories: number;
    total_protein: number;
  };
  differences: {
    calorie_difference: number;
    protein_difference: number;
    meal_count_difference: number;
  };
}

interface MealPlanVersionComparisonProps {
  mealPlanId: string;
  version1Id?: string;
  version2Id?: string;
}

const MealPlanVersionComparison: React.FC<MealPlanVersionComparisonProps> = ({
  mealPlanId,
  version1Id,
  version2Id
}) => {
  const [comparison, setComparison] = useState<VersionComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    if (version1Id && version2Id) {
      fetchComparison();
    }
  }, [version1Id, version2Id]);

  const fetchComparison = async () => {
    if (!version1Id || !version2Id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `/api/meal-plans/${mealPlanId}/versions/compare?version1_id=${version1Id}&version2_id=${version2Id}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setComparison(data);
        onOpen();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch comparison');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch comparison');
      toast({
        title: 'Error',
        description: 'Failed to fetch version comparison',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (value: number) => {
    if (value > 0) return <FiTrendingUp color="green" />;
    if (value < 0) return <FiTrendingDown color="red" />;
    return <FiMinus color="gray" />;
  };

  const getTrendColor = (value: number) => {
    if (value > 0) return 'green';
    if (value < 0) return 'red';
    return 'gray';
  };

  const formatDifference = (value: number, unit: string = '') => {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}${unit}`;
  };

  if (loading) {
    return (
      <Box textAlign="center" py={4}>
        <Spinner size="sm" />
        <Text mt={2} fontSize="sm">Comparing versions...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertTitle>Comparison Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!comparison) {
    return null;
  }

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <FiGitBranch />
              <Text>Version Comparison</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              {/* Version Headers */}
              <Grid templateColumns="1fr 1fr" gap={4}>
                <Card>
                  <CardHeader pb={2}>
                    <HStack justify="space-between">
                      <Text fontWeight="bold">Version {comparison.version1.version}</Text>
                      <Badge colorScheme="blue">Older</Badge>
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={2} align="stretch">
                      <Text fontSize="sm" color="gray.600">
                        {format(new Date(comparison.version1.created_at), 'MMM dd, yyyy HH:mm')}
                      </Text>
                      <HStack spacing={4}>
                        <Stat size="sm">
                          <StatLabel>Meals</StatLabel>
                          <StatNumber>{comparison.version1.meal_count}</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Calories</StatLabel>
                          <StatNumber>{Math.round(comparison.version1.total_calories)}</StatNumber>
                          <StatHelpText>kcal</StatHelpText>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Protein</StatLabel>
                          <StatNumber>{Math.round(comparison.version1.total_protein)}</StatNumber>
                          <StatHelpText>g</StatHelpText>
                        </Stat>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader pb={2}>
                    <HStack justify="space-between">
                      <Text fontWeight="bold">Version {comparison.version2.version}</Text>
                      <Badge colorScheme="green">Newer</Badge>
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={2} align="stretch">
                      <Text fontSize="sm" color="gray.600">
                        {format(new Date(comparison.version2.created_at), 'MMM dd, yyyy HH:mm')}
                      </Text>
                      <HStack spacing={4}>
                        <Stat size="sm">
                          <StatLabel>Meals</StatLabel>
                          <StatNumber>{comparison.version2.meal_count}</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Calories</StatLabel>
                          <StatNumber>{Math.round(comparison.version2.total_calories)}</StatNumber>
                          <StatHelpText>kcal</StatHelpText>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Protein</StatLabel>
                          <StatNumber>{Math.round(comparison.version2.total_protein)}</StatNumber>
                          <StatHelpText>g</StatHelpText>
                        </Stat>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              </Grid>

              <Divider />

              {/* Differences */}
              <Box>
                <Text fontWeight="bold" mb={4}>Changes</Text>
                <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                  <Card>
                    <CardBody textAlign="center">
                      <VStack spacing={2}>
                        {getTrendIcon(comparison.differences.calorie_difference)}
                        <Text fontSize="sm" color="gray.600">Calories</Text>
                        <Text 
                          fontWeight="bold" 
                          color={`${getTrendColor(comparison.differences.calorie_difference)}.500`}
                        >
                          {formatDifference(comparison.differences.calorie_difference, ' kcal')}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card>
                    <CardBody textAlign="center">
                      <VStack spacing={2}>
                        {getTrendIcon(comparison.differences.protein_difference)}
                        <Text fontSize="sm" color="gray.600">Protein</Text>
                        <Text 
                          fontWeight="bold" 
                          color={`${getTrendColor(comparison.differences.protein_difference)}.500`}
                        >
                          {formatDifference(comparison.differences.protein_difference, ' g')}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card>
                    <CardBody textAlign="center">
                      <VStack spacing={2}>
                        {getTrendIcon(comparison.differences.meal_count_difference)}
                        <Text fontSize="sm" color="gray.600">Meals</Text>
                        <Text 
                          fontWeight="bold" 
                          color={`${getTrendColor(comparison.differences.meal_count_difference)}.500`}
                        >
                          {formatDifference(comparison.differences.meal_count_difference)}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                </Grid>
              </Box>

              {/* Summary */}
              <Alert status="info">
                <AlertIcon />
                <Box>
                  <AlertTitle>Summary</AlertTitle>
                  <AlertDescription>
                    {comparison.differences.calorie_difference > 0 
                      ? `Version ${comparison.version2.version} has ${Math.round(comparison.differences.calorie_difference)} more calories`
                      : comparison.differences.calorie_difference < 0
                      ? `Version ${comparison.version2.version} has ${Math.round(Math.abs(comparison.differences.calorie_difference))} fewer calories`
                      : 'Both versions have the same calorie content'
                    }
                    {comparison.differences.meal_count_difference !== 0 && (
                      <span>
                        {comparison.differences.meal_count_difference > 0 
                          ? ` and ${comparison.differences.meal_count_difference} more meals`
                          : ` and ${Math.abs(comparison.differences.meal_count_difference)} fewer meals`
                        }
                      </span>
                    )}
                    .
                  </AlertDescription>
                </Box>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default MealPlanVersionComparison;
