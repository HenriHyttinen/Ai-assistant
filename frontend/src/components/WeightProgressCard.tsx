import {
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  VStack,
  HStack,
  Progress,
  Badge,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useBreakpointValue,
} from '@chakra-ui/react';
import { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { healthProfile } from '../services/api';

interface WeightProgressCardProps {
  currentWeight: number;
  targetWeight: number;
  weightTrend: number[];
  weightTrendTimestamps?: string[];
  measurementSystem: 'metric' | 'imperial';
  fitnessGoal?: string;
}

const WeightProgressCard = ({ 
  currentWeight, 
  targetWeight, 
  weightTrend,
  weightTrendTimestamps = [],
  measurementSystem,
  fitnessGoal
}: WeightProgressCardProps) => {
  const { language } = useApp();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isTrendOpen, onOpen: onTrendOpen, onClose: onTrendClose } = useDisclosure();
  const toast = useToast();
  const [newWeight, setNewWeight] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mobile-responsive values
  const isMobile = useBreakpointValue({ base: true, md: false });
  const chartHeight = useBreakpointValue({ base: 200, md: 250, lg: 300 });
  const fontSize = useBreakpointValue({ base: 10, md: 12, lg: 14 });
  const gridColumns = useBreakpointValue({ base: 1, md: 2, lg: 3 });

  // Calculate progress
  const weightDifference = currentWeight - targetWeight;
  
  // Determine if gaining or losing weight based on fitness goal
  const isGainingWeight = fitnessGoal?.toLowerCase().includes('muscle') || 
                          fitnessGoal?.toLowerCase().includes('gain') || 
                          fitnessGoal?.toLowerCase().includes('bulk') ||
                          (currentWeight < targetWeight && !fitnessGoal?.toLowerCase().includes('lose'));
  const isLosingWeight = fitnessGoal?.toLowerCase().includes('lose') || 
                        fitnessGoal?.toLowerCase().includes('weight loss') ||
                        (currentWeight > targetWeight && !fitnessGoal?.toLowerCase().includes('muscle') && !fitnessGoal?.toLowerCase().includes('gain'));
  
  // Progress calculation based on goal type
  const getProgressPercentage = () => {
    if (!targetWeight || !currentWeight) return 0;
    
    if (isGainingWeight) {
      // For weight gain: progress is how much we've gained towards the target
      if (weightTrend.length > 0) {
        // Use historical data if available
        const startingWeight = Math.min(...weightTrend); // Use lowest weight as starting point
        const totalToGain = targetWeight - startingWeight;
        const gainedSoFar = currentWeight - startingWeight;
        return totalToGain > 0 ? Math.max(0, Math.min(100, (gainedSoFar / totalToGain) * 100)) : 0;
      } else {
        // No historical data: calculate progress based on current vs target
        const totalToGain = targetWeight - currentWeight;
        if (totalToGain <= 0) return 100; // Already at or above target
        return 0; // Start at 0% and build up as user logs weight
      }
    } else if (isLosingWeight) {
      // For weight loss: progress is how much we've lost towards the target
      if (weightTrend.length > 0) {
        // Use historical data if available
        const startingWeight = Math.max(...weightTrend); // Use highest weight as starting point
        const totalToLose = startingWeight - targetWeight;
        const lostSoFar = startingWeight - currentWeight;
        return totalToLose > 0 ? Math.max(0, Math.min(100, (lostSoFar / totalToLose) * 100)) : 0;
      } else {
        // No historical data: calculate progress based on current vs target
        const totalToLose = currentWeight - targetWeight;
        if (totalToLose <= 0) return 100; // Already at or below target
        return 0; // Start at 0% and build up as user logs weight
      }
    }
    return 0;
  };
  
  const progressPercentage = getProgressPercentage();
  
  // Milestone tracking and encouraging messages
  const getMilestoneMessage = () => {
    const percentage = Math.round(progressPercentage);
    
    if (percentage >= 100) {
      return "🎉 Congratulations! You've reached your goal!";
    } else if (percentage >= 90) {
      return `🔥 Amazing! You're ${percentage}% there! Just ${100 - percentage}% to go!`;
    } else if (percentage >= 75) {
      return `💪 Great job! You're ${percentage}% done! Keep pushing!`;
    } else if (percentage >= 50) {
      return `🎯 Excellent progress! You're halfway there at ${percentage}%!`;
    } else if (percentage >= 25) {
      return `⭐ Good start! You're ${percentage}% of the way to your goal!`;
    } else if (percentage >= 10) {
      return `🚀 You're getting started! ${percentage}% complete, ${100 - percentage}% to go!`;
    } else if (percentage > 0) {
      return `🌱 Every step counts! You're ${percentage}% on your way!`;
    } else {
      return "💫 Ready to start your journey? Log your weight to begin tracking!";
    }
  };
  
  // Calculate trend based on goal direction
  const getTrend = () => {
    if (weightTrend.length < 2) {
      // If we have current weight and target, we can still determine if we're on track
      if (isGainingWeight && currentWeight < targetWeight) return 'up';    // On track to gain
      if (isLosingWeight && currentWeight > targetWeight) return 'up';     // On track to lose
      return 'stable';
    }
    
    const recent = weightTrend.slice(-3);
    const trend = recent[recent.length - 1] - recent[0];
    
    // For weight gain goals: positive trend (gaining weight) is good
    if (isGainingWeight) {
      if (trend > 0.5) return 'up';    // Gaining weight = good progress
      if (trend < -0.5) return 'down';  // Losing weight = concerning
      return 'stable';
    } 
    // For weight loss goals: negative trend (losing weight) is good
    else if (isLosingWeight) {
      if (trend < -0.5) return 'up';    // Losing weight = good progress
      if (trend > 0.5) return 'down';   // Gaining weight = concerning
      return 'stable';
    }
    return 'stable';
  };

  const trend = getTrend();
  
  // Color logic based on goal type
  const getTrendColor = () => {
    if (isGainingWeight) {
      // For weight gain goals: up is good (green), down is bad (red)
      return trend === 'up' ? 'green' : trend === 'down' ? 'red' : 'gray';
    } else if (isLosingWeight) {
      // For weight loss goals: up (good progress) is green, down (bad progress) is red
      return trend === 'up' ? 'green' : trend === 'down' ? 'red' : 'gray';
    }
    return 'gray';
  };
  
  const trendColor = getTrendColor();
  
  // Get appropriate trend text based on goal type
  const getTrendText = () => {
    if (isGainingWeight) {
      // For weight gain goals
      if (trend === 'up') {
        return '🎯 GAINING WEIGHT';
      } else if (trend === 'down') {
        return '⚠️ LOSING WEIGHT';
      } else {
        return '📊 STABLE';
      }
    } else if (isLosingWeight) {
      // For weight loss goals
      if (trend === 'up') {
        return '🎯 LOSING WEIGHT';
      } else if (trend === 'down') {
        return '⚠️ GAINING WEIGHT';
      } else {
        return '📊 STABLE';
      }
    }
    return '📊 STABLE';
  };

  // Debug logging removed to prevent console spam

  const handleSubmit = async () => {
    if (!newWeight || isNaN(Number(newWeight))) {
      toast({
        title: 'Invalid Weight',
        description: 'Please enter a valid weight value',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSubmitting(true);
    try {
      // Update the health profile with the new weight
      await healthProfile.updateProfile({ weight: Number(newWeight) });
      
      toast({
        title: 'Weight Logged!',
        description: 'Your weight has been successfully recorded',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      setNewWeight('');
      onClose();
      window.location.reload(); // Refresh to show new data
    } catch (error) {
      console.error('Error logging weight:', error);
      toast({
        title: 'Error',
        description: 'Failed to log weight',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProgressMessage = () => {
    const unit = measurementSystem === 'metric' ? 'kg' : 'lbs';
    const amount = Math.abs(weightDifference).toFixed(1);
    
    if (isGainingWeight) {
      return `You're ${amount}${unit} away from your goal!`;
    } else if (isLosingWeight) {
      return `You're ${amount}${unit} away from your goal!`;
    }
    return `You're ${amount}${unit} away from your goal!`;
  };


  return (
    <>
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">{t('weightProgress' as any, language)}</Heading>
            <Button size="sm" colorScheme="blue" onClick={onOpen}>
              {t('logWeight' as any, language)}
            </Button>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            {/* Current Weight Display */}
            <Box textAlign="center" py={4} bg="blue.50" borderRadius="md">
              <Text fontSize="3xl" fontWeight="bold" color="blue.600">
                {currentWeight.toFixed(1)} {measurementSystem === 'metric' ? 'kg' : 'lbs'}
              </Text>
              <Text color="gray.600" fontSize="sm">
                {t('currentWeight' as any, language)}
              </Text>
              <Badge colorScheme={trendColor} mt={2} textTransform="none">
                {getTrendText()}
              </Badge>
            </Box>

            {/* Progress Bar */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" color="gray.600">
                  {getProgressMessage()}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  {targetWeight.toFixed(1)} {measurementSystem === 'metric' ? 'kg' : 'lbs'} {t('goal' as any, language)}
                </Text>
              </HStack>
              <Progress 
                value={progressPercentage} 
                colorScheme={isGainingWeight ? 'green' : isLosingWeight ? 'green' : 'blue'}
                size="lg"
                borderRadius="md"
              />
            </Box>

            {/* Milestone Message */}
            <Box p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
              <Text color="green.800" fontSize="sm" textAlign="center" fontWeight="medium">
                {getMilestoneMessage()}
              </Text>
            </Box>

            {/* Quick Stats */}
            <HStack justify="space-around" py={2}>
              <VStack spacing={1}>
                <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                  {weightTrend.length}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  {t('entries' as any, language)}
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="2xl" fontWeight="bold" color="green.600">
                  {Math.abs(weightDifference).toFixed(1)}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  {measurementSystem === 'metric' ? 'kg' : 'lbs'} {t('toGo' as any, language)}
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text 
                  fontSize="2xl" 
                  fontWeight="bold" 
                  color="purple.600" 
                  cursor="pointer" 
                  title={t('trendTooltip' as any, language)}
                  onClick={onTrendOpen}
                  _hover={{ transform: 'scale(1.1)' }}
                  transition="transform 0.2s"
                >
                  {trend === 'down' ? '📉' : trend === 'up' ? '📈' : '📊'}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  {t('graphs' as any, language)}
                </Text>
              </VStack>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Weight Logging Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('logYourWeight' as any, language)}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>{t('weight' as any, language)} ({measurementSystem === 'metric' ? 'kg' : 'lbs'})</FormLabel>
              <Input
                type="number"
                step="0.1"
                placeholder={t('enterCurrentWeight' as any, language).replace('{unit}', measurementSystem === 'metric' ? 'kg' : 'lbs')}
                value={newWeight}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewWeight(e.target.value)}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t('cancel' as any, language)}
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              {t('logWeight' as any, language)}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Weight Analytics Modal */}
      <Modal isOpen={isTrendOpen} onClose={onTrendClose} size={isMobile ? "sm" : "xl"}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('graphs' as any, language)}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              {/* Analytics Overview */}
              <SimpleGrid columns={gridColumns} spacing={4}>
                <Stat textAlign="center">
                  <StatLabel>{t('currentWeight' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl" color="blue.600">
                    {currentWeight.toFixed(1)}
                  </StatNumber>
                  <StatHelpText>{measurementSystem === 'metric' ? 'kg' : 'lbs'}</StatHelpText>
                </Stat>
                <Stat textAlign="center">
                  <StatLabel>{t('targetWeight' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl" color="green.600">
                    {targetWeight.toFixed(1)}
                  </StatNumber>
                  <StatHelpText>{measurementSystem === 'metric' ? 'kg' : 'lbs'}</StatHelpText>
                </Stat>
                <Stat textAlign="center">
                  <StatLabel>{t('progress' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl" color="purple.600">
                    {Math.abs(weightDifference).toFixed(1)}
                  </StatNumber>
                  <StatHelpText>
                    <StatArrow type={isLosingWeight ? 'decrease' : 'increase'} />
                    {t('toGo' as any, language)}
                  </StatHelpText>
                </Stat>
              </SimpleGrid>

              {/* Weight Trend Chart */}
              {weightTrend.length > 0 && (
                <Box>
                  <Text fontSize="lg" fontWeight="bold" mb={4}>
                    {t('weightTrendChart' as any, language)}
                  </Text>
                  <Box p={isMobile ? 2 : 4} bg="white" borderRadius="md" border="1px" borderColor="gray.200" height={`${chartHeight}px`}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={weightTrend.slice(-10).map((weight, index) => {
                        const recentTimestamps = weightTrendTimestamps.slice(-10);
                        const timestamp = recentTimestamps[index] || 
                                        new Date(Date.now() - (weightTrend.length - 1 - index) * 24 * 60 * 60 * 1000).toISOString();
                        return {
                          date: new Date(timestamp).toLocaleDateString(),
                          weight: weight,
                          target: targetWeight
                        };
                      })}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#718096"
                          fontSize={fontSize}
                          angle={isMobile ? -45 : 0}
                          textAnchor={isMobile ? "end" : "middle"}
                          height={isMobile ? 60 : 40}
                          tickFormatter={(tickItem: any, index: number) => {
                            // Get all data points to determine unique dates
                            const data = weightTrend.slice(-10).map((weight, i) => {
                                const recentTimestamps = weightTrendTimestamps.slice(-10);
                                const ts = recentTimestamps[i] || new Date(Date.now() - (weightTrend.length - 1 - i) * 24 * 60 * 60 * 1000).toISOString();
                                return { date: new Date(ts).toLocaleDateString(), weight: weight };
                            });
                            
                            // Count occurrences of each date
                            const dateCounts: { [key: string]: number } = {};
                            data.forEach(item => {
                                dateCounts[item.date] = (dateCounts[item.date] || 0) + 1;
                            });
                            
                            // If this date appears multiple times, add a counter
                            if (dateCounts[tickItem] > 1) {
                                const dateIndex = data.slice(0, index + 1).filter(item => item.date === tickItem).length;
                                return `${tickItem} (${dateIndex})`;
                            }
                            
                            return tickItem;
                          }}
                        />
                        <YAxis 
                          stroke="#718096"
                          fontSize={fontSize}
                          domain={['dataMin - 2', 'dataMax + 2']}
                          width={isMobile ? 50 : 60}
                        />
                        <Tooltip 
                          formatter={(value: any, name: any) => [
                            `${value} ${measurementSystem === 'metric' ? 'kg' : 'lbs'}`, 
                            name === 'weight' ? t('currentWeight' as any, language) : t('targetWeight' as any, language)
                          ]}
                          labelFormatter={(label: any) => `${t('date' as any, language)}: ${label}`}
                          contentStyle={{
                            backgroundColor: '#f7fafc',
                            border: '1px solid #e2e8f0',
                            borderRadius: '6px',
                            fontSize: fontSize
                          }}
                          labelStyle={{
                            fontSize: fontSize,
                            fontWeight: 'bold'
                          }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="weight" 
                          stroke="#3182ce" 
                          strokeWidth={isMobile ? 2 : 3}
                          dot={{ fill: '#3182ce', strokeWidth: 2, r: isMobile ? 3 : 4 }}
                          name="weight"
                        />
                        {targetWeight > 0 && (
                          <Line 
                            type="monotone" 
                            dataKey="target" 
                            stroke="#38a169" 
                            strokeWidth={isMobile ? 1 : 2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="target"
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>
              )}

              {/* Insights & Recommendations */}
              <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                <Text fontSize="md" fontWeight="bold" color="blue.800" mb={3}>
                  {t('insights' as any, language)}
                </Text>
                <VStack spacing={2} align="stretch">
                  {trend === 'down' && isLosingWeight && (
                    <Text fontSize="sm" color="green.700">🎉 {t('greatProgressKeepGoing' as any, language)}</Text>
                  )}
                  {trend === 'up' && isLosingWeight && (
                    <Text fontSize="sm" color="orange.700">💪 {t('weightFluctuatesStayConsistent' as any, language)}</Text>
                  )}
                  {trend === 'stable' && (
                    <Text fontSize="sm" color="blue.700">📊 {t('weightStableMaintainConsistency' as any, language)}</Text>
                  )}
                  <Text fontSize="sm" color="gray.700">📝 {t('logWeightRegularly' as any, language)}</Text>
                  <Text fontSize="sm" color="gray.700">🎯 {t('setRealisticGoals' as any, language)}</Text>
                </VStack>
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={onTrendClose}>
              {t('close' as any, language)}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default WeightProgressCard;
