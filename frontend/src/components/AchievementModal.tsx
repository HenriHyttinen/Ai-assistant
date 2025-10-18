import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack,
  Text,
  Button,
  SimpleGrid,
  Box,
  Badge,
  useToast,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import AchievementCard from './AchievementCard';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
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

interface AchievementModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AchievementModal: React.FC<AchievementModalProps> = ({ isOpen, onClose }) => {
  const { language } = useApp();
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'unlocked' | 'all'>('unlocked');
  const toast = useToast();

  // Use centralized translation function

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/achievements/available');
      setAchievements(response.data.achievements || []);
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
    if (isOpen) {
      fetchAchievements();
    }
  }, [isOpen]);

  const unlockedAchievements = achievements.filter(a => a.is_unlocked);
  const lockedAchievements = achievements.filter(a => !a.is_unlocked);
  const displayedAchievements = activeTab === 'unlocked' ? unlockedAchievements : achievements;

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack justify="space-between" align="center">
            <Text>{t('yourAchievements', language)}</Text>
            <HStack spacing={2}>
              <Button
                size="sm"
                variant={activeTab === 'unlocked' ? 'solid' : 'outline'}
                colorScheme="green"
                onClick={() => setActiveTab('unlocked')}
              >
                {t('unlockedAchievements', language)} ({unlockedAchievements.length})
              </Button>
              <Button
                size="sm"
                variant={activeTab === 'all' ? 'solid' : 'outline'}
                colorScheme="blue"
                onClick={() => setActiveTab('all')}
              >
                {t('availableAchievements', language)} ({achievements.length})
              </Button>
            </HStack>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          {loading ? (
            <VStack spacing={4} py={8}>
              <Spinner size="lg" />
              <Text>{t('loading', language)}</Text>
            </VStack>
          ) : error ? (
            <Alert status="error">
              <AlertIcon />
              {error}
            </Alert>
          ) : displayedAchievements.length === 0 ? (
            <VStack spacing={4} py={8} textAlign="center">
              <Text fontSize="lg" color="gray.500">
                {activeTab === 'unlocked' ? t('noAchievements', language) : t('noAchievements', language)}
              </Text>
              <Text color="gray.400">
                {t('keepGoing', language)}
              </Text>
            </VStack>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              {displayedAchievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  showProgress={activeTab === 'all'}
                />
              ))}
            </SimpleGrid>
          )}
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default AchievementModal;
