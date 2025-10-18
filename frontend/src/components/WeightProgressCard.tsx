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
} from '@chakra-ui/react';
import { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface WeightProgressCardProps {
  currentWeight: number;
  targetWeight: number;
  weightTrend: number[];
  measurementSystem: 'metric' | 'imperial';
}

const WeightProgressCard = ({ 
  currentWeight, 
  targetWeight, 
  weightTrend, 
  measurementSystem 
}: WeightProgressCardProps) => {
  const { language } = useApp();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isTrendOpen, onOpen: onTrendOpen, onClose: onTrendClose } = useDisclosure();
  const toast = useToast();
  const [newWeight, setNewWeight] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Calculate progress
  const weightDifference = currentWeight - targetWeight;
  const progressPercentage = Math.max(0, Math.min(100, (weightDifference / Math.abs(weightDifference + targetWeight)) * 100));
  
  // Determine if gaining or losing weight
  const isLosingWeight = currentWeight > targetWeight;
  
  // Calculate trend
  const getTrend = () => {
    if (weightTrend.length < 2) return 'stable';
    const recent = weightTrend.slice(-3);
    const trend = recent[recent.length - 1] - recent[0];
    if (trend > 0.5) return 'up';
    if (trend < -0.5) return 'down';
    return 'stable';
  };

  const trend = getTrend();
  const trendColor = trend === 'up' ? 'red' : trend === 'down' ? 'green' : 'gray';

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
      // Here you would call the API to add weight entry
      // await analytics.addWeightEntry(Number(newWeight));
      
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
    return t('weightProgressMessage' as any, language).replace('{amount}', Math.abs(weightDifference).toFixed(1)).replace('{unit}', unit);
  };

  const getMotivationalMessage = () => {
    if (trend === 'down' && isLosingWeight) {
      return t('greatProgressMovingRight' as any, language);
    } else if (trend === 'up' && isLosingWeight) {
      return t('dontWorryWeightFluctuates' as any, language);
    } else if (trend === 'stable') {
      return t('weightStableKeepGoodWork' as any, language);
    }
    return t('everyStepCounts' as any, language);
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
              <Badge colorScheme={trendColor} mt={2}>
                {trend === 'up' ? t('trendingUp' as any, language) : trend === 'down' ? t('trendingDown' as any, language) : t('stable' as any, language)}
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
                colorScheme={isLosingWeight ? 'green' : 'blue'}
                size="lg"
                borderRadius="md"
              />
            </Box>

            {/* Motivational Message */}
            <Box p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
              <Text color="green.800" fontSize="sm" textAlign="center">
                {getMotivationalMessage()}
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
      <Modal isOpen={isTrendOpen} onClose={onTrendClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('graphs' as any, language)}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              {/* Analytics Overview */}
              <SimpleGrid columns={3} spacing={4}>
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
                  <Box p={4} bg="white" borderRadius="md" border="1px" borderColor="gray.200" height="300px">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={weightTrend.slice(-10).map((weight, index) => ({
                        entry: index + 1,
                        weight: weight,
                        target: targetWeight
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis 
                          dataKey="entry" 
                          stroke="#718096"
                          fontSize={12}
                        />
                        <YAxis 
                          stroke="#718096"
                          fontSize={12}
                          domain={['dataMin - 2', 'dataMax + 2']}
                        />
                        <Tooltip 
                          formatter={(value: any, name: any) => [
                            `${value} ${measurementSystem === 'metric' ? 'kg' : 'lbs'}`, 
                            name === 'weight' ? t('currentWeight' as any, language) : t('targetWeight' as any, language)
                          ]}
                          labelFormatter={(label: any) => `${t('entry' as any, language)} ${label}`}
                          contentStyle={{
                            backgroundColor: '#f7fafc',
                            border: '1px solid #e2e8f0',
                            borderRadius: '6px'
                          }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="weight" 
                          stroke="#3182ce" 
                          strokeWidth={3}
                          dot={{ fill: '#3182ce', strokeWidth: 2, r: 4 }}
                          name="weight"
                        />
                        {targetWeight > 0 && (
                          <Line 
                            type="monotone" 
                            dataKey="target" 
                            stroke="#38a169" 
                            strokeWidth={2}
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
