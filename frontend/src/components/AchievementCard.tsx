import React from 'react';
import {
  Box,
  Card,
  CardBody,
  VStack,
  HStack,
  Text,
  Badge,
  Progress,
  Icon,
  Tooltip,
  useColorModeValue
} from '@chakra-ui/react';
import { useApp } from '../contexts/AppContext';
import { t, translateAchievementName, translateAchievementDesc } from '../utils/translations';

interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  points: number;
  category: string;
  is_unlocked: boolean;
  progress: number;
  requirement_value: number;
  requirement_type: string;
  unlocked_at?: string;
}

interface AchievementCardProps {
  achievement: Achievement;
  showProgress?: boolean;
}

const AchievementCard: React.FC<AchievementCardProps> = ({ 
  achievement, 
  showProgress = true 
}) => {
  const { language } = useApp();
  // Use centralized translation function

  const cardBg = useColorModeValue(
    achievement.is_unlocked ? 'green.50' : 'gray.50',
    achievement.is_unlocked ? 'green.900' : 'gray.700'
  );
  
  const borderColor = useColorModeValue(
    achievement.is_unlocked ? 'green.200' : 'gray.200',
    achievement.is_unlocked ? 'green.600' : 'gray.600'
  );

  const progressPercentage = achievement.requirement_value > 0 
    ? Math.min((achievement.progress / achievement.requirement_value) * 100, 100)
    : 0;

  return (
    <Card 
      bg={cardBg} 
      border="1px" 
      borderColor={borderColor}
      opacity={achievement.is_unlocked ? 1 : 0.7}
      transition="all 0.2s"
      _hover={{ transform: 'translateY(-2px)', shadow: 'md' }}
      minH="200px"
      h="auto"
    >
      <CardBody p={4}>
        <VStack spacing={4} align="stretch" h="full">
          <HStack justify="space-between" align="start" spacing={3}>
            <HStack spacing={3} flex="1" minW="0">
              <Box
                p={2}
                borderRadius="full"
                bg={achievement.is_unlocked ? 'green.100' : 'gray.100'}
                display="flex"
                alignItems="center"
                justifyContent="center"
                minW="48px"
                minH="48px"
                flexShrink={0}
              >
                <Text fontSize="2xl" filter={achievement.is_unlocked ? 'none' : 'grayscale(100%)'}>
                  {achievement.icon}
                </Text>
              </Box>
              <VStack align="start" spacing={2} flex="1" minW="0">
                <Text fontWeight="bold" fontSize="sm" lineHeight="1.2">
                  {translateAchievementName(achievement.name, language)}
                </Text>
                <Text 
                  fontSize="xs" 
                  color="gray.600" 
                  lineHeight="1.4"
                  wordBreak="break-word"
                  whiteSpace="normal"
                >
                  {translateAchievementDesc(achievement.description, language)}
                </Text>
              </VStack>
            </HStack>
            
            <VStack spacing={1} align="end" flexShrink={0}>
              <Badge 
                colorScheme={achievement.is_unlocked ? 'green' : 'gray'}
                size="sm"
                textTransform="none"
              >
                {achievement.is_unlocked ? t('unlocked', language) : t('locked', language)}
              </Badge>
              <HStack spacing={1}>
                <Text fontSize="xs" color="gray.500">
                  {achievement.points}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {t('points', language)}
                </Text>
              </HStack>
            </VStack>
          </HStack>

          <Box mt="auto">
            {showProgress && !achievement.is_unlocked && (
              <Box>
                <HStack justify="space-between" mb={2}>
                  <Text fontSize="xs" color="gray.600">
                    {t('progress', language)}
                  </Text>
                  <Text fontSize="xs" color="gray.600">
                    {achievement.progress}/{achievement.requirement_value}
                  </Text>
                </HStack>
                <Progress 
                  value={progressPercentage} 
                  size="sm" 
                  colorScheme="blue"
                  borderRadius="md"
                />
              </Box>
            )}

            {achievement.is_unlocked && achievement.unlocked_at && (
              <Text fontSize="xs" color="green.600" textAlign="center" mt={2}>
                {new Date(achievement.unlocked_at).toLocaleDateString()}
              </Text>
            )}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AchievementCard;
