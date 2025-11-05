import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  VStack,
  HStack,
  Text,
  Button,
  Badge,
  Progress,
  Spinner,
  Alert,
  AlertIcon,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
import AchievementCard from '../components/AchievementCard';
import api from '../services/api';

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

const Achievements = () => {
  const { language } = useApp();
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    unlocked: 0,
    totalPoints: 0,
    unlockedPoints: 0
  });
  const toast = useToast();

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('@/lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
      
      const response = await api.get('/achievements/available', { headers });
      const achievementsData = response.data.achievements || [];
      setAchievements(achievementsData);
      
      // Calculate stats
      const unlocked = achievementsData.filter(a => a.is_unlocked);
      const totalPoints = achievementsData.reduce((sum, a) => sum + a.points, 0);
      const unlockedPoints = unlocked.reduce((sum, a) => sum + a.points, 0);
      
      setStats({
        total: achievementsData.length,
        unlocked: unlocked.length,
        totalPoints,
        unlockedPoints
      });
    } catch (err) {
      console.error('Error fetching achievements:', err);
      setError(t('error', language));
      toast({
        title: t('error', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('Loading achievements');
    fetchAchievements();
  }, []);

  const unlockedAchievements = achievements.filter(a => a.is_unlocked);
  const lockedAchievements = achievements.filter(a => !a.is_unlocked);

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      activity: 'blue',
      duration: 'green',
      consistency: 'purple',
      variety: 'orange',
      weekly_consistency: 'pink'
    };
    return colors[category] || 'gray';
  };

  const getCategoryName = (category: string) => {
    const names: { [key: string]: string } = {
      activity: t('activity', language),
      duration: t('duration', language),
      consistency: t('consistency', language),
      variety: t('variety', language),
      weekly_consistency: t('weeklyConsistency', language)
    };
    return names[category] || category;
  };

  if (loading) {
    return (
      <Box p={4}>
        <VStack spacing={4} py={8}>
          <Spinner size="lg" />
          <Text>{t('loading', language)}</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={6} pb={12}>
      <Heading mb={6}>🏆 {t('achievements', language)}</Heading>

      {/* Stats Overview */}
      <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6} mb={8}>
        <Stat textAlign="center" p={4} bg="blue.50" borderRadius="md">
          <StatLabel>{t('totalAchievements', language)}</StatLabel>
          <StatNumber color="blue.600">{stats.total}</StatNumber>
        </Stat>
        
        <Stat textAlign="center" p={4} bg="green.50" borderRadius="md">
          <StatLabel>{t('unlockedAchievements', language)}</StatLabel>
          <StatNumber color="green.600">{stats.unlocked}</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            {Math.round((stats.unlocked / stats.total) * 100)}%
          </StatHelpText>
        </Stat>
        
        <Stat textAlign="center" p={4} bg="purple.50" borderRadius="md">
          <StatLabel>{t('totalPoints', language)}</StatLabel>
          <StatNumber color="purple.600">{stats.totalPoints}</StatNumber>
        </Stat>
        
        <Stat textAlign="center" p={4} bg="orange.50" borderRadius="md">
          <StatLabel>{t('earnedPoints', language)}</StatLabel>
          <StatNumber color="orange.600">{stats.unlockedPoints}</StatNumber>
          <StatHelpText>
            <StatArrow type="increase" />
            {Math.round((stats.unlockedPoints / stats.totalPoints) * 100)}%
          </StatHelpText>
        </Stat>
      </SimpleGrid>

      {/* Achievement Categories */}
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>{t('allAchievements', language)} ({achievements.length})</Tab>
          <Tab>{t('unlockedAchievements', language)} ({unlockedAchievements.length})</Tab>
          <Tab>{t('lockedAchievements', language)} ({lockedAchievements.length})</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8} py={4}>
              {achievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  showProgress={true}
                />
              ))}
            </SimpleGrid>
          </TabPanel>

          <TabPanel px={0}>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8} py={4}>
              {unlockedAchievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  showProgress={false}
                />
              ))}
            </SimpleGrid>
          </TabPanel>

          <TabPanel px={0}>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8} py={4}>
              {lockedAchievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  showProgress={true}
                />
              ))}
            </SimpleGrid>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Category Breakdown */}
      <Box mt={8}>
        <Heading size="md" mb={4}>{t('achievementCategories', language)}</Heading>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {Object.entries(
            achievements.reduce((acc, achievement) => {
              const category = achievement.category;
              if (!acc[category]) {
                acc[category] = { total: 0, unlocked: 0, points: 0 };
              }
              acc[category].total++;
              if (achievement.is_unlocked) {
                acc[category].unlocked++;
                acc[category].points += achievement.points;
              }
              return acc;
            }, {} as { [key: string]: { total: number; unlocked: number; points: number } })
          ).map(([category, data]) => (
            <Box key={category} p={4} border="1px" borderColor="gray.200" borderRadius="md">
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="bold" color={`${getCategoryColor(category)}.600`}>
                  {getCategoryName(category)}
                </Text>
                <Badge colorScheme={getCategoryColor(category)} textTransform="none">
                  {data.unlocked}/{data.total}
                </Badge>
              </HStack>
              <Progress 
                value={(data.unlocked / data.total) * 100} 
                colorScheme={getCategoryColor(category)}
                size="sm"
                mb={2}
              />
              <Text fontSize="sm" color="gray.600">
                {data.points} {t('points', language)}
              </Text>
            </Box>
          ))}
        </SimpleGrid>
      </Box>
    </Box>
  );
};

export default Achievements;
