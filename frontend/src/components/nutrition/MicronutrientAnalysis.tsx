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
  Heading,
  Badge,
  Progress,
  useToast,
  SimpleGrid,
  Icon,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
  Collapse,
  useDisclosure,
} from '@chakra-ui/react';
import { 
  FiCheckCircle, 
  FiAlertTriangle,
  FiInfo,
  FiChevronDown,
  FiChevronUp,
  FiHeart,
  FiZap,
  FiShield,
  FiTarget
} from 'react-icons/fi';

interface MicronutrientAnalysisProps {
  userId?: string;
  onUpdate?: () => void;
}

interface MicronutrientData {
  period: {
    start_date: string;
    end_date: string;
    days_analyzed: number;
  };
  totals: Record<string, number>;
  daily_averages: Record<string, number>;
  deficiencies: Array<{
    nutrient: string;
    current_intake: number;
    recommended: number;
    deficiency_percentage: number;
    severity: 'mild' | 'moderate' | 'severe';
  }>;
  excesses: Array<{
    nutrient: string;
    current_intake: number;
    recommended: number;
    excess_percentage: number;
  }>;
  recommendations: Array<{
    type: 'deficiency' | 'excess' | 'optimization';
    nutrient: string;
    message: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  diversity_score: number;
  food_suggestions: Array<{
    nutrient: string;
    foods: Array<{
      name: string;
      content: number;
      unit: string;
    }>;
  }>;
}

const MicronutrientAnalysis: React.FC<MicronutrientAnalysisProps> = () => {
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<MicronutrientData | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month'>('week');
  const [expandedNutrients, setExpandedNutrients] = useState<Set<string>>(new Set());
  const { isOpen: showDetails, onToggle: toggleDetails } = useDisclosure();
  
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Micronutrient categories and their display names
  const micronutrientCategories = {
    vitamins: {
      title: 'Vitamins',
      icon: FiZap,
      nutrients: ['vitamin_d', 'vitamin_b12', 'vitamin_c', 'vitamin_a', 'vitamin_e', 'vitamin_k', 'thiamine', 'riboflavin', 'niacin', 'folate'],
      color: 'blue'
    },
    minerals: {
      title: 'Minerals',
      icon: FiShield,
      nutrients: ['calcium', 'iron', 'magnesium', 'zinc', 'selenium', 'potassium', 'phosphorus'],
      color: 'green'
    },
    fatty_acids: {
      title: 'Fatty Acids',
      icon: FiHeart,
      nutrients: ['omega_3', 'omega_6'],
      color: 'purple'
    }
  };

  const nutrientDisplayNames: Record<string, string> = {
    vitamin_d: 'Vitamin D',
    vitamin_b12: 'Vitamin B12',
    vitamin_c: 'Vitamin C',
    vitamin_a: 'Vitamin A',
    vitamin_e: 'Vitamin E',
    vitamin_k: 'Vitamin K',
    thiamine: 'Thiamine (B1)',
    riboflavin: 'Riboflavin (B2)',
    niacin: 'Niacin (B3)',
    folate: 'Folate (B9)',
    calcium: 'Calcium',
    iron: 'Iron',
    magnesium: 'Magnesium',
    zinc: 'Zinc',
    selenium: 'Selenium',
    potassium: 'Potassium',
    phosphorus: 'Phosphorus',
    omega_3: 'Omega-3',
    omega_6: 'Omega-6'
  };

  const nutrientUnits: Record<string, string> = {
    vitamin_d: 'IU',
    vitamin_b12: 'mcg',
    vitamin_c: 'mg',
    vitamin_a: 'IU',
    vitamin_e: 'mg',
    vitamin_k: 'mcg',
    thiamine: 'mg',
    riboflavin: 'mg',
    niacin: 'mg',
    folate: 'mcg',
    calcium: 'mg',
    iron: 'mg',
    magnesium: 'mg',
    zinc: 'mg',
    selenium: 'mcg',
    potassium: 'mg',
    phosphorus: 'mg',
    omega_3: 'g',
    omega_6: 'g'
  };

  const loadMicronutrientAnalysis = async () => {
    setLoading(true);
    try {
      // This would call the actual API endpoint
      // const response = await fetch(`/api/micronutrients/analysis?period=${selectedPeriod}`);
      // const data = await response.json();
      
      // Mock data for demonstration
      const mockData: MicronutrientData = {
        period: {
          start_date: '2024-01-01',
          end_date: '2024-01-07',
          days_analyzed: 7
        },
        totals: {
          vitamin_d: 2100,
          vitamin_b12: 8.4,
          iron: 45,
          calcium: 2100,
          vitamin_c: 315,
          magnesium: 1260,
          zinc: 28,
          omega_3: 4.2
        },
        daily_averages: {
          vitamin_d: 300,
          vitamin_b12: 1.2,
          iron: 6.4,
          calcium: 300,
          vitamin_c: 45,
          magnesium: 180,
          zinc: 4,
          omega_3: 0.6
        },
        deficiencies: [
          {
            nutrient: 'vitamin_d',
            current_intake: 300,
            recommended: 600,
            deficiency_percentage: 50,
            severity: 'moderate'
          },
          {
            nutrient: 'iron',
            current_intake: 6.4,
            recommended: 18,
            deficiency_percentage: 64,
            severity: 'severe'
          }
        ],
        excesses: [
          {
            nutrient: 'vitamin_c',
            current_intake: 45,
            recommended: 90,
            excess_percentage: -50
          }
        ],
        recommendations: [
          {
            type: 'deficiency',
            nutrient: 'vitamin_d',
            message: 'Consider adding more fatty fish, fortified dairy, or sunlight exposure',
            priority: 'high'
          },
          {
            type: 'deficiency',
            nutrient: 'iron',
            message: 'Include more lean meats, spinach, and legumes in your diet',
            priority: 'high'
          }
        ],
        diversity_score: 75,
        food_suggestions: [
          {
            nutrient: 'vitamin_d',
            foods: [
              { name: 'Salmon', content: 988, unit: 'IU' },
              { name: 'Fortified Milk', content: 120, unit: 'IU' },
              { name: 'Egg Yolks', content: 37, unit: 'IU' }
            ]
          },
          {
            nutrient: 'iron',
            foods: [
              { name: 'Lean Beef', content: 2.9, unit: 'mg' },
              { name: 'Spinach', content: 2.7, unit: 'mg' },
              { name: 'Lentils', content: 3.3, unit: 'mg' }
            ]
          }
        ]
      };
      
      setAnalysisData(mockData);
    } catch (error) {
      console.error('Error loading micronutrient analysis:', error);
      toast({
        title: 'Error',
        description: 'Failed to load micronutrient analysis',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMicronutrientAnalysis();
  }, [selectedPeriod]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'mild': return 'yellow';
      case 'moderate': return 'orange';
      case 'severe': return 'red';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'green';
    if (percentage >= 75) return 'blue';
    if (percentage >= 50) return 'yellow';
    return 'red';
  };

  const toggleNutrientExpansion = (nutrient: string) => {
    const newExpanded = new Set(expandedNutrients);
    if (newExpanded.has(nutrient)) {
      newExpanded.delete(nutrient);
    } else {
      newExpanded.add(nutrient);
    }
    setExpandedNutrients(newExpanded);
  };

  if (loading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading micronutrient analysis...</Text>
      </Box>
    );
  }

  if (!analysisData) {
    return (
      <Alert status="info" borderRadius="lg">
        <AlertIcon />
        <Box>
          <Text fontWeight="semibold">No micronutrient data available</Text>
          <Text>Start logging your meals to see micronutrient analysis!</Text>
        </Box>
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <Box>
        <Heading size="lg" mb={2}>Micronutrient Analysis</Heading>
        <Text color="gray.600">
          Comprehensive analysis of your vitamin and mineral intake over {analysisData.period.days_analyzed} days
        </Text>
      </Box>

      {/* Period Selector */}
      <HStack spacing={4}>
        <Text fontWeight="semibold">Analysis Period:</Text>
        <Button
          size="sm"
          colorScheme={selectedPeriod === 'week' ? 'blue' : 'gray'}
          variant={selectedPeriod === 'week' ? 'solid' : 'outline'}
          onClick={() => setSelectedPeriod('week')}
        >
          Last Week
        </Button>
        <Button
          size="sm"
          colorScheme={selectedPeriod === 'month' ? 'blue' : 'gray'}
          variant={selectedPeriod === 'month' ? 'solid' : 'outline'}
          onClick={() => setSelectedPeriod('month')}
        >
          Last Month
        </Button>
      </HStack>

      {/* Diversity Score */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardBody>
          <HStack justify="space-between" align="center">
            <VStack align="start" spacing={1}>
              <Text fontWeight="semibold" fontSize="lg">Nutritional Diversity Score</Text>
              <Text color="gray.600" fontSize="sm">
                How well you're covering all essential micronutrients
              </Text>
            </VStack>
            <VStack align="end" spacing={1}>
              <Text fontSize="3xl" fontWeight="bold" color="blue.500">
                {analysisData.diversity_score}%
              </Text>
              <Progress
                value={analysisData.diversity_score}
                colorScheme="blue"
                size="lg"
                width="100px"
              />
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      {/* Deficiencies and Excesses Summary */}
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md" color="red.500">
              <Icon as={FiAlertTriangle} mr={2} />
              Deficiencies
            </Heading>
          </CardHeader>
          <CardBody>
            {analysisData.deficiencies.length > 0 ? (
              <VStack spacing={3} align="stretch">
                {analysisData.deficiencies.map((deficiency, index) => (
                  <Box key={index} p={3} bg="red.50" borderRadius="md" border="1px" borderColor="red.200">
                    <HStack justify="space-between" mb={2}>
                      <Text fontWeight="semibold">{nutrientDisplayNames[deficiency.nutrient]}</Text>
                      <Badge colorScheme={getSeverityColor(deficiency.severity)}>
                        {deficiency.severity}
                      </Badge>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {deficiency.current_intake.toFixed(1)} / {deficiency.recommended} {nutrientUnits[deficiency.nutrient]}
                    </Text>
                    <Progress
                      value={(deficiency.current_intake / deficiency.recommended) * 100}
                      colorScheme="red"
                      size="sm"
                      mt={2}
                    />
                  </Box>
                ))}
              </VStack>
            ) : (
              <Text color="green.600" fontWeight="semibold">
                <Icon as={FiCheckCircle} mr={2} />
                No significant deficiencies detected!
              </Text>
            )}
          </CardBody>
        </Card>

        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md" color="orange.500">
              <Icon as={FiInfo} mr={2} />
              Excesses
            </Heading>
          </CardHeader>
          <CardBody>
            {analysisData.excesses.length > 0 ? (
              <VStack spacing={3} align="stretch">
                {analysisData.excesses.map((excess, index) => (
                  <Box key={index} p={3} bg="orange.50" borderRadius="md" border="1px" borderColor="orange.200">
                    <Text fontWeight="semibold">{nutrientDisplayNames[excess.nutrient]}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {excess.current_intake.toFixed(1)} / {excess.recommended} {nutrientUnits[excess.nutrient]}
                    </Text>
                    <Text fontSize="xs" color="orange.600">
                      {Math.abs(excess.excess_percentage).toFixed(0)}% over recommended
                    </Text>
                  </Box>
                ))}
              </VStack>
            ) : (
              <Text color="green.600" fontWeight="semibold">
                <Icon as={FiCheckCircle} mr={2} />
                No significant excesses detected!
              </Text>
            )}
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Detailed Micronutrient Breakdown */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Detailed Breakdown</Heading>
            <Button size="sm" onClick={toggleDetails}>
              {showDetails ? <FiChevronUp /> : <FiChevronDown />}
              {showDetails ? 'Hide Details' : 'Show Details'}
            </Button>
          </HStack>
        </CardHeader>
        <Collapse in={showDetails}>
          <CardBody>
            <Tabs>
              <TabList>
                {Object.entries(micronutrientCategories).map(([key, category]) => (
                  <Tab key={key}>
                    <Icon as={category.icon} mr={2} />
                    {category.title}
                  </Tab>
                ))}
              </TabList>
              <TabPanels>
                {Object.entries(micronutrientCategories).map(([key, category]) => (
                  <TabPanel key={key}>
                    <VStack spacing={4} align="stretch">
                      {category.nutrients.map((nutrient) => {
                        const current = analysisData.daily_averages[nutrient] || 0;
                        const recommended = 100; // This would come from the API
                        const percentage = (current / recommended) * 100;
                        const isExpanded = expandedNutrients.has(nutrient);
                        
                        return (
                          <Box key={nutrient} p={4} bg="gray.50" borderRadius="md">
                            <HStack justify="space-between" mb={2}>
                              <Text fontWeight="semibold">{nutrientDisplayNames[nutrient]}</Text>
                              <HStack spacing={2}>
                                <Text fontSize="sm" color="gray.600">
                                  {current.toFixed(1)} / {recommended} {nutrientUnits[nutrient]}
                                </Text>
                                <Button
                                  size="xs"
                                  variant="ghost"
                                  onClick={() => toggleNutrientExpansion(nutrient)}
                                >
                                  {isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                                </Button>
                              </HStack>
                            </HStack>
                            <Progress
                              value={Math.min(percentage, 100)}
                              colorScheme={getProgressColor(percentage)}
                              size="sm"
                            />
                            <Text fontSize="xs" color="gray.500" mt={1}>
                              {percentage.toFixed(0)}% of recommended daily intake
                            </Text>
                            
                            {isExpanded && (
                              <Box mt={3} p={3} bg="white" borderRadius="md" border="1px" borderColor="gray.200">
                                <Text fontSize="sm" color="gray.600">
                                  {nutrient === 'vitamin_d' && 'Essential for bone health and immune function. Get from sunlight, fatty fish, and fortified foods.'}
                                  {nutrient === 'iron' && 'Critical for oxygen transport. Found in lean meats, spinach, and legumes.'}
                                  {nutrient === 'calcium' && 'Important for bone and teeth health. Sources include dairy, leafy greens, and fortified foods.'}
                                  {!['vitamin_d', 'iron', 'calcium'].includes(nutrient) && 'Essential micronutrient for optimal health and bodily functions.'}
                                </Text>
                              </Box>
                            )}
                          </Box>
                        );
                      })}
                    </VStack>
                  </TabPanel>
                ))}
              </TabPanels>
            </Tabs>
          </CardBody>
        </Collapse>
      </Card>

      {/* Recommendations */}
      {analysisData.recommendations.length > 0 && (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">
              <Icon as={FiTarget} mr={2} />
              Recommendations
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              {analysisData.recommendations.map((rec, index) => (
                <Box key={index} p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{nutrientDisplayNames[rec.nutrient]}</Text>
                    <Badge colorScheme={getPriorityColor(rec.priority)}>
                      {rec.priority} priority
                    </Badge>
                  </HStack>
                  <Text fontSize="sm">{rec.message}</Text>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Food Suggestions */}
      {analysisData.food_suggestions.length > 0 && (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">
              <Icon as={FiHeart} mr={2} />
              Food Suggestions
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {analysisData.food_suggestions.map((suggestion, index) => (
                <Box key={index}>
                  <Text fontWeight="semibold" mb={2}>
                    High in {nutrientDisplayNames[suggestion.nutrient]}:
                  </Text>
                  <SimpleGrid columns={{ base: 1, md: 3 }} spacing={2}>
                    {suggestion.foods.map((food, foodIndex) => (
                      <Box key={foodIndex} p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
                        <Text fontWeight="medium">{food.name}</Text>
                        <Text fontSize="sm" color="gray.600">
                          {food.content} {food.unit} per 100g
                        </Text>
                      </Box>
                    ))}
                  </SimpleGrid>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
};

export default MicronutrientAnalysis;
