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
  Badge,
  Image,
  useColorModeValue,
  useBreakpointValue,
  Icon,
  SimpleGrid,
  Progress,
  Divider,
  useToast,
  Spinner,
  Center,
  Link,
  Flex,
} from '@chakra-ui/react';
import {
  FiBookOpen, FiLightbulb, FiAward, FiTarget, FiTrendingUp,
  FiClock, FiStar, FiArrowRight, FiPlay, FiCheckCircle
} from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';

interface EducationDashboard {
  total_articles_read: number;
  total_tips_viewed: number;
  total_quizzes_completed: number;
  total_points_earned: number;
  current_learning_path: any;
  recent_activity: any[];
  recommended_content: any[];
  daily_tip: any;
}

const NutritionEducationDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<EducationDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const toast = useToast();
  
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/nutrition-education/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      } else {
        throw new Error('Failed to load dashboard');
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast({
        title: 'Error',
        description: 'Failed to load education dashboard',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!dashboard) {
    return (
      <Center h="400px">
        <Text>Failed to load education dashboard</Text>
      </Center>
    );
  }

  return (
    <VStack spacing={6} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <Text fontSize="2xl" fontWeight="bold">
          Nutrition Education
        </Text>
        <Button
          colorScheme="blue"
          leftIcon={<Icon as={FiBookOpen} />}
          onClick={() => navigate('/nutrition/education/articles')}
        >
          Browse Articles
        </Button>
      </HStack>

      {/* Stats Overview */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody textAlign="center">
            <Icon as={FiBookOpen} boxSize={8} color="blue.500" mb={2} />
            <Text fontSize="2xl" fontWeight="bold" color="blue.500">
              {dashboard.total_articles_read}
            </Text>
            <Text fontSize="sm" color={textColor}>
              Articles Read
            </Text>
          </CardBody>
        </Card>

        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody textAlign="center">
            <Icon as={FiLightbulb} boxSize={8} color="yellow.500" mb={2} />
            <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
              {dashboard.total_tips_viewed}
            </Text>
            <Text fontSize="sm" color={textColor}>
              Tips Viewed
            </Text>
          </CardBody>
        </Card>

        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody textAlign="center">
            <Icon as={FiAward} boxSize={8} color="green.500" mb={2} />
            <Text fontSize="2xl" fontWeight="bold" color="green.500">
              {dashboard.total_quizzes_completed}
            </Text>
            <Text fontSize="sm" color={textColor}>
              Quizzes Completed
            </Text>
          </CardBody>
        </Card>

        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody textAlign="center">
            <Icon as={FiStar} boxSize={8} color="purple.500" mb={2} />
            <Text fontSize="2xl" fontWeight="bold" color="purple.500">
              {dashboard.total_points_earned}
            </Text>
            <Text fontSize="sm" color={textColor}>
              Points Earned
            </Text>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Daily Tip */}
      {dashboard.daily_tip && (
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <Icon as={FiLightbulb} color="yellow.500" />
              <Text fontWeight="semibold">Today's Tip</Text>
              <Badge colorScheme="yellow" variant="subtle">
                Daily
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            <Text fontSize="lg" fontWeight="medium" mb={2}>
              {dashboard.daily_tip.title}
            </Text>
            <Text color={textColor} mb={4}>
              {dashboard.daily_tip.content}
            </Text>
            <HStack spacing={2}>
              <Badge colorScheme="blue" variant="subtle">
                {dashboard.daily_tip.category}
              </Badge>
              <Badge colorScheme="green" variant="subtle">
                {dashboard.daily_tip.difficulty_level}
              </Badge>
            </HStack>
          </CardBody>
        </Card>
      )}

      {/* Current Learning Path */}
      {dashboard.current_learning_path && (
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <HStack>
                <Icon as={FiTarget} color="purple.500" />
                <Text fontWeight="semibold">Current Learning Path</Text>
              </HStack>
              <Badge colorScheme="purple" variant="subtle">
                {dashboard.current_learning_path.difficulty_level}
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            <Text fontSize="lg" fontWeight="medium" mb={2}>
              {dashboard.current_learning_path.path_name}
            </Text>
            <Text color={textColor} mb={4}>
              {dashboard.current_learning_path.description}
            </Text>
            
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <Text fontSize="sm" color={textColor}>
                  Progress
                </Text>
                <Text fontSize="sm" fontWeight="medium">
                  {Math.round(dashboard.current_learning_path.completion_percentage)}%
                </Text>
              </HStack>
              <Progress
                value={dashboard.current_learning_path.completion_percentage}
                colorScheme="purple"
                size="lg"
                borderRadius="md"
              />
              <HStack justify="space-between">
                <Text fontSize="sm" color={textColor}>
                  Step {dashboard.current_learning_path.current_step} of {dashboard.current_learning_path.total_steps}
                </Text>
                <Text fontSize="sm" color={textColor}>
                  {dashboard.current_learning_path.estimated_duration_days} days
                </Text>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Recommended Content */}
      {dashboard.recommended_content.length > 0 && (
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <Icon as={FiTrendingUp} color="green.500" />
              <Text fontWeight="semibold">Recommended for You</Text>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            <VStack spacing={4} align="stretch">
              {dashboard.recommended_content.map((article) => (
                <Box
                  key={article.id}
                  p={4}
                  borderWidth={1}
                  borderRadius="md"
                  borderColor={borderColor}
                  _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                  cursor="pointer"
                  onClick={() => navigate(`/nutrition/education/articles/${article.slug}`)}
                >
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={2} flex={1}>
                      <Text fontWeight="medium" fontSize="md">
                        {article.title}
                      </Text>
                      <Text fontSize="sm" color={textColor} noOfLines={2}>
                        {article.summary}
                      </Text>
                      <HStack spacing={2}>
                        <Badge colorScheme="blue" variant="subtle" size="sm">
                          {article.category}
                        </Badge>
                        <Badge colorScheme="green" variant="subtle" size="sm">
                          {article.difficulty_level}
                        </Badge>
                        <HStack spacing={1}>
                          <Icon as={FiClock} boxSize={3} color={textColor} />
                          <Text fontSize="xs" color={textColor}>
                            {article.reading_time_minutes} min
                          </Text>
                        </HStack>
                      </HStack>
                    </VStack>
                    <Icon as={FiArrowRight} color={textColor} />
                  </HStack>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Recent Activity */}
      {dashboard.recent_activity.length > 0 && (
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack>
              <Icon as={FiClock} color="blue.500" />
              <Text fontWeight="semibold">Recent Activity</Text>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            <VStack spacing={3} align="stretch">
              {dashboard.recent_activity.map((activity, index) => (
                <HStack key={index} justify="space-between" align="center">
                  <HStack>
                    <Icon
                      as={activity.article_id ? FiBookOpen : FiLightbulb}
                      color={activity.is_completed ? 'green.500' : 'blue.500'}
                    />
                    <VStack align="start" spacing={0}>
                      <Text fontSize="sm" fontWeight="medium">
                        {activity.article_id ? 'Article' : 'Tip'}
                      </Text>
                      <Text fontSize="xs" color={textColor}>
                        {new Date(activity.last_accessed).toLocaleDateString()}
                      </Text>
                    </VStack>
                  </HStack>
                  <HStack>
                    {activity.is_completed && (
                      <Icon as={FiCheckCircle} color="green.500" />
                    )}
                    {activity.is_bookmarked && (
                      <Icon as={FiStar} color="yellow.500" />
                    )}
                    <Text fontSize="xs" color={textColor}>
                      {Math.round(activity.progress_percentage)}%
                    </Text>
                  </HStack>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Quick Actions */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
        <Button
          leftIcon={<Icon as={FiBookOpen} />}
          colorScheme="blue"
          variant="outline"
          onClick={() => navigate('/nutrition/education/articles')}
        >
          Browse Articles
        </Button>
        <Button
          leftIcon={<Icon as={FiAward} />}
          colorScheme="green"
          variant="outline"
          onClick={() => navigate('/nutrition/education/quiz')}
        >
          Take Quiz
        </Button>
        <Button
          leftIcon={<Icon as={FiTarget} />}
          colorScheme="purple"
          variant="outline"
          onClick={() => navigate('/nutrition/education/learning-paths')}
        >
          Learning Paths
        </Button>
      </SimpleGrid>
    </VStack>
  );
};

export default NutritionEducationDashboard;

