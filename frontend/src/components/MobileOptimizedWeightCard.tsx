import React from 'react';
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
  Stack,
} from '@chakra-ui/react';
import { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
import ResponsiveChart from './ResponsiveChart';
import { healthProfile } from '../services/api';

interface WeightProgressCardProps {
  currentWeight: number;
  targetWeight: number;
  weightTrend: number[];
  weightTrendTimestamps?: string[];
  measurementSystem: 'metric' | 'imperial';
  fitnessGoal?: string;
}

const MobileOptimizedWeightCard = ({ 
  currentWeight, 
  targetWeight, 
  weightTrend,
  weightTrendTimestamps = [],
  measurementSystem,
  fitnessGoal
}: WeightProgressCardProps) => {
  const { language } = useApp();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newWeight, setNewWeight] = useState('');
  const toast = useToast();

  // Responsive breakpoints
  const isMobile = useBreakpointValue({ base: true, md: false });
  const isTablet = useBreakpointValue({ base: false, md: true, lg: false });
  const isDesktop = useBreakpointValue({ base: false, lg: true });

  // Responsive grid columns
  const gridColumns = useBreakpointValue({ 
    base: 1,    // Mobile: single column
    md: 2,      // Tablet: two columns
    lg: 3       // Desktop: three columns
  });

  // Responsive chart height
  const chartHeight = useBreakpointValue({
    base: 200,  // Mobile: smaller chart
    md: 250,    // Tablet: medium chart
    lg: 300     // Desktop: larger chart
  });

  // Responsive text sizes
  const headingSize = useBreakpointValue({
    base: 'sm',
    md: 'md',
    lg: 'lg'
  });

  const textSize = useBreakpointValue({
    base: 'xs',
    md: 'sm',
    lg: 'md'
  });

  const handleWeightUpdate = async () => {
    if (!newWeight || isNaN(Number(newWeight))) {
      toast({
        title: t('error' as any, language),
        description: t('pleaseEnterValidWeight' as any, language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const weightValue = Number(newWeight);
      await healthProfile.updateProfile({ weight: weightValue });
      
      toast({
        title: t('success' as any, language),
        description: t('weightUpdatedSuccessfully' as any, language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      setNewWeight('');
      onClose();
      // Refresh the page or update state
      window.location.reload();
    } catch (error) {
      toast({
        title: t('error' as any, language),
        description: t('failedToUpdateWeight' as any, language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Calculate progress - fixed calculation
  const calculateProgress = () => {
    if (!targetWeight || !currentWeight) return 0;
    
    // For weight loss goals
    if (currentWeight > targetWeight) {
      const totalToLose = currentWeight - targetWeight;
      const lostSoFar = weightTrend.length > 0 ? Math.max(...weightTrend) - currentWeight : 0;
      return totalToLose > 0 ? Math.max(0, Math.min(100, (lostSoFar / totalToLose) * 100)) : 0;
    }
    // For weight gain goals
    else if (currentWeight < targetWeight) {
      const totalToGain = targetWeight - currentWeight;
      const gainedSoFar = weightTrend.length > 0 ? currentWeight - Math.min(...weightTrend) : 0;
      return totalToGain > 0 ? Math.max(0, Math.min(100, (gainedSoFar / totalToGain) * 100)) : 0;
    }
    // Already at target
    return 100;
  };
  
  const progress = calculateProgress();

  // Prepare chart data
  const chartData = weightTrend.slice(-10).map((weight, index) => {
    const recentTimestamps = weightTrendTimestamps.slice(-10);
    const timestamp = recentTimestamps[index] || 
                    new Date(Date.now() - (weightTrend.length - 1 - index) * 24 * 60 * 60 * 1000).toISOString();
    return {
      date: new Date(timestamp).toLocaleDateString(),
      weight: weight,
      target: targetWeight
    };
  });

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between" align="flex-start">
          <VStack align="start" spacing={1}>
            <Heading size={headingSize}>
              {t('weightProgress' as any, language)}
            </Heading>
            <Text fontSize={textSize} color="gray.600">
              {t('trackYourWeightJourney' as any, language)}
            </Text>
          </VStack>
          <Button size="sm" onClick={onOpen} colorScheme="blue" variant="outline">
            {t('updateWeight' as any, language)}
          </Button>
        </HStack>
      </CardHeader>
      
      <CardBody>
        <VStack spacing={4} align="stretch">
          {/* Progress Stats - Responsive Grid */}
          <SimpleGrid columns={gridColumns} spacing={4}>
            <Stat>
              <StatLabel fontSize={textSize}>{t('currentWeight' as any, language)}</StatLabel>
              <StatNumber fontSize={isMobile ? 'lg' : 'xl'}>
                {currentWeight} {measurementSystem === 'metric' ? 'kg' : 'lbs'}
              </StatNumber>
            </Stat>
            
            <Stat>
              <StatLabel fontSize={textSize}>{t('targetWeight' as any, language)}</StatLabel>
              <StatNumber fontSize={isMobile ? 'lg' : 'xl'}>
                {targetWeight} {measurementSystem === 'metric' ? 'kg' : 'lbs'}
              </StatNumber>
            </Stat>
            
            <Stat>
              <StatLabel fontSize={textSize}>{t('progress' as any, language)}</StatLabel>
              <StatNumber fontSize={isMobile ? 'lg' : 'xl'}>
                {progress.toFixed(1)}%
              </StatNumber>
              <StatHelpText>
                <StatArrow type={progress > 0 ? 'increase' : 'decrease'} />
                {t('towardsGoal' as any, language)}
              </StatHelpText>
            </Stat>
          </SimpleGrid>

          {/* Progress Bar */}
          <Box>
            <HStack justify="space-between" mb={2}>
              <Text fontSize={textSize} fontWeight="medium">
                {t('goalProgress' as any, language)}
              </Text>
              <Badge colorScheme={progress >= 100 ? 'green' : 'blue'} fontSize={textSize}>
                {progress.toFixed(1)}%
              </Badge>
            </HStack>
            <Progress 
              value={progress} 
              colorScheme={progress >= 100 ? 'green' : 'blue'}
              size="lg"
              borderRadius="md"
            />
          </Box>

          {/* Weight Trend Chart - Mobile Optimized */}
          {weightTrend.length > 0 && (
            <Box>
              <Text fontSize={textSize} fontWeight="bold" mb={2}>
                {t('weightTrendChart' as any, language)}
              </Text>
              <Box 
                p={isMobile ? 2 : 4} 
                bg="white" 
                borderRadius="md" 
                border="1px" 
                borderColor="gray.200"
                height={`${chartHeight}px`}
              >
                <ResponsiveChart
                  data={chartData}
                  dataKey="weight"
                  xAxisKey="date"
                  height={chartHeight}
                  strokeColor="#3182ce"
                  strokeWidth={isMobile ? 2 : 3}
                />
              </Box>
            </Box>
          )}

          {/* Mobile-specific optimizations */}
          {isMobile && (
            <VStack spacing={2} align="stretch">
              <Text fontSize="xs" color="gray.500" textAlign="center">
                {t('tipSwipeChart' as any, language) || 'Tip: Swipe the chart to see more data points'}
              </Text>
            </VStack>
          )}
        </VStack>
      </CardBody>

      {/* Update Weight Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size={isMobile ? 'sm' : 'md'}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader fontSize={headingSize}>
            {t('updateWeight' as any, language)}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel fontSize={textSize}>
                  {t('newWeight' as any, language)}
                </FormLabel>
                <Input
                  type="number"
                  value={newWeight}
                  onChange={(e) => setNewWeight(e.target.value)}
                  placeholder={`${t('enterWeight' as any, language)} (${measurementSystem === 'metric' ? 'kg' : 'lbs'})`}
                  size={isMobile ? 'sm' : 'md'}
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose} size={isMobile ? 'sm' : 'md'}>
              {t('cancel' as any, language)}
            </Button>
            <Button colorScheme="blue" onClick={handleWeightUpdate} size={isMobile ? 'sm' : 'md'}>
              {t('update' as any, language)}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Card>
  );
};

export default MobileOptimizedWeightCard;
