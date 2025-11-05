import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Text,
  Heading,
  VStack,
  HStack,
  Icon,
  Badge,
  useToast,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Button,
  SimpleGrid,
} from '@chakra-ui/react';
import { useApp } from '../contexts/AppContext';
import { t, translateAchievementName, translateAchievementDesc } from '../utils/translations';
import AchievementCard from './AchievementCard';
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

interface AchievementNotificationProps {
  onAchievementUnlocked?: (achievement: Achievement) => void;
}

const AchievementNotification: React.FC<AchievementNotificationProps> = ({ 
  onAchievementUnlocked 
}) => {
  const { language } = useApp();
  const [recentAchievements, setRecentAchievements] = useState<Achievement[]>([]);
  const [showNotification, setShowNotification] = useState(false);
  const [currentAchievement, setCurrentAchievement] = useState<Achievement | null>(null);
  const [shownAchievements, setShownAchievements] = useState<Set<number>>(new Set());
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Clear shown achievements on component mount (fresh login)
  useEffect(() => {
    setShownAchievements(new Set());
  }, []);

  // Check for new achievements periodically
  useEffect(() => {
    console.log('Starting achievement checking');
    
    const nextAllowedCheckRef = { current: 0 } as { current: number };

    const checkForNewAchievements = async () => {
      try {
        // Simple backoff if we recently timed out
        if (Date.now() < nextAllowedCheckRef.current) {
          return;
        }
        // Get Supabase session token for authentication
        const { supabase } = await import('@/lib/supabase');
        const { data: { session } } = await supabase.auth.getSession();
        
        // Only make API calls if user is authenticated
        if (!session?.access_token) {
          console.log('No authentication token, skipping achievement check');
          return;
        }
        
        const headers = { Authorization: `Bearer ${session.access_token}` };
        
        // Use the check endpoint to get only newly unlocked achievements
        // Add a shorter timeout specifically for achievements
        const response = await api.post('/achievements/check', {}, { 
          headers,
          timeout: 3000 // 3 second timeout for achievements
        });
        const newAchievements = response.data.new_achievements || [];
        
        if (newAchievements.length > 0) {
          // Filter out achievements we've already shown
          const trulyNewAchievements = newAchievements.filter(
            achievement => !shownAchievements.has(achievement.id)
          );
          
          if (trulyNewAchievements.length > 0) {
            setRecentAchievements(prev => [...prev, ...trulyNewAchievements]);
            
            // Show notification for the first new achievement only
            const firstNewAchievement = trulyNewAchievements[0];
            setCurrentAchievement(firstNewAchievement);
            setShowNotification(true);
            
            // Mark this achievement as shown
            setShownAchievements(prev => new Set([...prev, firstNewAchievement.id]));
            
            // Show toast notification
            toast({
              title: t('congratulations', language),
              description: `${t('achievementUnlocked', language)}: ${translateAchievementName(firstNewAchievement.name, language)}`,
              status: 'success',
              duration: 5000,
              isClosable: true,
              position: 'top-right',
            });
            
            if (onAchievementUnlocked) {
              onAchievementUnlocked(firstNewAchievement);
            }
            
            // If there are more achievements, show them one by one with a delay
            if (trulyNewAchievements.length > 1) {
              const remainingAchievements = trulyNewAchievements.slice(1);
              remainingAchievements.forEach((achievement, index) => {
                setTimeout(() => {
                  setCurrentAchievement(achievement);
                  setShowNotification(true);
                  setShownAchievements(prev => new Set([...prev, achievement.id]));
                  
                  toast({
                    title: t('congratulations', language),
                    description: `${t('achievementUnlocked', language)}: ${translateAchievementName(achievement.name, language)}`,
                    status: 'success',
                    duration: 5000,
                    isClosable: true,
                    position: 'top-right',
                  });
                  
                  if (onAchievementUnlocked) {
                    onAchievementUnlocked(achievement);
                  }
                }, (index + 1) * 3000); // 3 second delay between notifications
              });
            }
          }
        }
      } catch (error) {
        // Don't log timeout errors as they're expected when the service is slow
        if (error.code !== 'ECONNABORTED') {
          console.error('Error checking achievements:', error);
        } else {
          console.warn('Achievement check timed out, will retry later');
          // Backoff 10 minutes after a timeout
          nextAllowedCheckRef.current = Date.now() + 10 * 60 * 1000;
        }
        // Silently fail - don't show error toasts for background checks
      }
    };

          // Check every 5 minutes to reduce backend load
          const interval = setInterval(checkForNewAchievements, 300000);
    
    // Initial check
    checkForNewAchievements();

    return () => clearInterval(interval);
  }, [language, toast, onAchievementUnlocked]); // Removed shownAchievements from dependencies

  // Auto-hide notification after 5 seconds
  useEffect(() => {
    if (showNotification) {
      const timer = setTimeout(() => {
        setShowNotification(false);
        setCurrentAchievement(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [showNotification]);

  if (!showNotification || !currentAchievement) {
    return null;
  }

  return (
    <>
      {/* Floating Achievement Notification */}
      <Box
        position="fixed"
        top="20px"
        right="20px"
        zIndex={9999}
        bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        color="white"
        p={6}
        borderRadius="lg"
        boxShadow="0 10px 25px rgba(0,0,0,0.3)"
        maxW="400px"
        animation="slideInRight 0.5s ease-out"
        css={{
          '@keyframes slideInRight': {
            '0%': {
              transform: 'translateX(100%)',
              opacity: 0,
            },
            '100%': {
              transform: 'translateX(0)',
              opacity: 1,
            },
          },
        }}
      >
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between" align="start">
            <HStack spacing={3}>
              <Box
                p={3}
                borderRadius="full"
                bg="whiteAlpha.200"
                display="flex"
                alignItems="center"
                justifyContent="center"
                minW="56px"
                minH="56px"
              >
                <Text fontSize="3xl">
                  {currentAchievement.icon}
                </Text>
              </Box>
              <VStack align="start" spacing={1}>
                <Heading size="sm" color="white">
                  🎉 {t('congratulations', language)}!
                </Heading>
                <Text fontSize="sm" color="whiteAlpha.900">
                  {t('achievementUnlocked', language)}
                </Text>
              </VStack>
            </HStack>
            <Badge colorScheme="yellow" variant="solid">
              +{currentAchievement.points} {t('points', language)}
            </Badge>
          </HStack>
          
          <Box bg="whiteAlpha.200" p={3} borderRadius="md">
            <Text fontWeight="bold" color="white" mb={1}>
              {translateAchievementName(currentAchievement.name, language)}
            </Text>
            <Text fontSize="sm" color="whiteAlpha.900">
              {translateAchievementDesc(currentAchievement.description, language)}
            </Text>
          </Box>
          
          <HStack justify="space-between">
            <Button
              size="sm"
              variant="outline"
              colorScheme="whiteAlpha"
              onClick={onOpen}
            >
              {t('viewAll', language)}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              color="white"
              onClick={() => setShowNotification(false)}
            >
              ✕
            </Button>
          </HStack>
        </VStack>
      </Box>

      {/* Achievement Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <Icon as={() => <span style={{ fontSize: '1.5rem' }}>🏆</span>} />
              <Text>{t('yourAchievements', language)}</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              {recentAchievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  showProgress={false}
                />
              ))}
            </SimpleGrid>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default AchievementNotification;
