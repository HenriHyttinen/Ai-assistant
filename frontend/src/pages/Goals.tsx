import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Progress,
  Button,
  VStack,
  HStack,
  Badge,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Divider,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { DeleteIcon } from '@chakra-ui/icons';
import { goals } from '../services/api';
import { useApp } from '../contexts/AppContext';

// Inline translation function to avoid module loading issues
const translations = {
  en: {
    goals: 'Goals',
    addNewGoal: 'Add New Goal',
    target: 'Target',
    progress: 'Progress',
    deadline: 'Deadline',
    noDeadline: 'No deadline',
    complete: 'complete',
    update: 'Update',
    startGoal: 'Start Goal',
    completeGoal: 'Complete Goal',
    goalCompleted: 'Goal Completed!',
    addNewGoalModal: 'Add New Goal',
    goalTitle: 'Goal Title',
    goalTitlePlaceholder: 'e.g., Weight Loss',
    targetPlaceholder: 'e.g., Lose 5kg',
    goalType: 'Goal Type',
    weight: 'Weight',
    activity: 'Activity',
    habit: 'Habit',
    createGoal: 'Create Goal',
    creating: 'Creating...',
    goalRemoved: 'Goal Removed',
    goalRemovedDesc: 'Your goal has been successfully removed.',
    goalActivated: 'Goal Activated',
    goalActivatedDesc: 'You have started working on this goal!',
    goalCompletedToast: 'Goal Completed',
    goalCompletedDesc: 'Congratulations! You have completed this goal.',
    newGoalAdded: 'New Goal Added',
    newGoalAddedDesc: 'New goal has been successfully created.',
    updateFailed: 'Update Failed',
    creationFailed: 'Creation Failed',
    unableToRemoveGoal: 'Unable to Remove Goal',
    unableToRemoveGoalDesc: 'We couldn\'t remove your goal. Please try again.',
    completed: 'COMPLETED',
    inProgress: 'IN PROGRESS',
    notStarted: 'NOT STARTED',
    failed: 'FAILED',
    progressUpdated: 'Progress Updated',
    progressUpdatedDesc: 'Progress updated to',
  },
  es: {
    goals: 'Objetivos',
    addNewGoal: 'Agregar Nuevo Objetivo',
    target: 'Objetivo',
    progress: 'Progreso',
    deadline: 'Fecha Límite',
    noDeadline: 'Sin fecha límite',
    complete: 'completo',
    update: 'Actualizar',
    startGoal: 'Iniciar Objetivo',
    completeGoal: 'Completar Objetivo',
    goalCompleted: '¡Objetivo Completado!',
    addNewGoalModal: 'Agregar Nuevo Objetivo',
    goalTitle: 'Título del Objetivo',
    goalTitlePlaceholder: 'ej., Pérdida de Peso',
    targetPlaceholder: 'ej., Perder 5kg',
    goalType: 'Tipo de Objetivo',
    weight: 'Peso',
    activity: 'Actividad',
    habit: 'Hábito',
    createGoal: 'Crear Objetivo',
    creating: 'Creando...',
    goalRemoved: 'Objetivo Eliminado',
    goalRemovedDesc: 'Tu objetivo ha sido eliminado exitosamente.',
    goalActivated: 'Objetivo Activado',
    goalActivatedDesc: '¡Has comenzado a trabajar en este objetivo!',
    goalCompletedToast: 'Objetivo Completado',
    goalCompletedDesc: '¡Felicidades! Has completado este objetivo.',
    newGoalAdded: 'Nuevo Objetivo Agregado',
    newGoalAddedDesc: 'El nuevo objetivo ha sido creado exitosamente.',
    updateFailed: 'Actualización Fallida',
    creationFailed: 'Creación Fallida',
    unableToRemoveGoal: 'No se Pudo Eliminar el Objetivo',
    unableToRemoveGoalDesc: 'No pudimos eliminar tu objetivo. Por favor, inténtalo de nuevo.',
    completed: 'COMPLETADO',
    inProgress: 'EN PROGRESO',
    notStarted: 'NO INICIADO',
    failed: 'FALLIDO',
    progressUpdated: 'Progreso Actualizado',
    progressUpdatedDesc: 'Progreso actualizado a',
  },
  fr: {
    goals: 'Objectifs',
    addNewGoal: 'Ajouter un Nouvel Objectif',
    target: 'Cible',
    progress: 'Progrès',
    deadline: 'Date Limite',
    noDeadline: 'Aucune date limite',
    complete: 'terminé',
    update: 'Mettre à Jour',
    startGoal: 'Commencer l\'Objectif',
    completeGoal: 'Terminer l\'Objectif',
    goalCompleted: 'Objectif Terminé !',
    addNewGoalModal: 'Ajouter un Nouvel Objectif',
    goalTitle: 'Titre de l\'Objectif',
    goalTitlePlaceholder: 'ex., Perte de Poids',
    targetPlaceholder: 'ex., Perdre 5kg',
    goalType: 'Type d\'Objectif',
    weight: 'Poids',
    activity: 'Activité',
    habit: 'Habitude',
    createGoal: 'Créer l\'Objectif',
    creating: 'Création...',
    goalRemoved: 'Objectif Supprimé',
    goalRemovedDesc: 'Votre objectif a été supprimé avec succès.',
    goalActivated: 'Objectif Activé',
    goalActivatedDesc: 'Vous avez commencé à travailler sur cet objectif !',
    goalCompletedToast: 'Objectif Terminé',
    goalCompletedDesc: 'Félicitations ! Vous avez terminé cet objectif.',
    newGoalAdded: 'Nouvel Objectif Ajouté',
    newGoalAddedDesc: 'Le nouvel objectif a été créé avec succès.',
    updateFailed: 'Mise à Jour Échouée',
    creationFailed: 'Création Échouée',
    unableToRemoveGoal: 'Impossible de Supprimer l\'Objectif',
    unableToRemoveGoalDesc: 'Nous n\'avons pas pu supprimer votre objectif. Veuillez réessayer.',
    completed: 'TERMINÉ',
    inProgress: 'EN COURS',
    notStarted: 'PAS COMMENCÉ',
    failed: 'ÉCHOUÉ',
    progressUpdated: 'Progrès Mis à Jour',
    progressUpdatedDesc: 'Progrès mis à jour à',
  },
  de: {
    goals: 'Ziele',
    addNewGoal: 'Neues Ziel Hinzufügen',
    target: 'Ziel',
    progress: 'Fortschritt',
    deadline: 'Frist',
    noDeadline: 'Keine Frist',
    complete: 'abgeschlossen',
    update: 'Aktualisieren',
    startGoal: 'Ziel Starten',
    completeGoal: 'Ziel Abschließen',
    goalCompleted: 'Ziel Abgeschlossen!',
    addNewGoalModal: 'Neues Ziel Hinzufügen',
    goalTitle: 'Zieltitel',
    goalTitlePlaceholder: 'z.B., Gewichtsverlust',
    targetPlaceholder: 'z.B., 5kg abnehmen',
    goalType: 'Zieltyp',
    weight: 'Gewicht',
    activity: 'Aktivität',
    habit: 'Gewohnheit',
    createGoal: 'Ziel Erstellen',
    creating: 'Erstellen...',
    goalRemoved: 'Ziel Entfernt',
    goalRemovedDesc: 'Ihr Ziel wurde erfolgreich entfernt.',
    goalActivated: 'Ziel Aktiviert',
    goalActivatedDesc: 'Sie haben begonnen, an diesem Ziel zu arbeiten!',
    goalCompletedToast: 'Ziel Abgeschlossen',
    goalCompletedDesc: 'Herzlichen Glückwunsch! Sie haben dieses Ziel abgeschlossen.',
    newGoalAdded: 'Neues Ziel Hinzugefügt',
    newGoalAddedDesc: 'Das neue Ziel wurde erfolgreich erstellt.',
    updateFailed: 'Aktualisierung Fehlgeschlagen',
    creationFailed: 'Erstellung Fehlgeschlagen',
    unableToRemoveGoal: 'Ziel Kann Nicht Entfernt Werden',
    unableToRemoveGoalDesc: 'Wir konnten Ihr Ziel nicht entfernen. Bitte versuchen Sie es erneut.',
    completed: 'ABGESCHLOSSEN',
    inProgress: 'IN BEARBEITUNG',
    notStarted: 'NICHT GESTARTET',
    failed: 'FEHLGESCHLAGEN',
    progressUpdated: 'Fortschritt Aktualisiert',
    progressUpdatedDesc: 'Fortschritt aktualisiert auf',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

interface Goal {
  id: string;
  title: string;
  target: string;
  progress: number;
  deadline: string;
  status: 'completed' | 'in_progress' | 'not_started' | 'failed';
}

const Goals = () => {
  const { language } = useApp();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [goalsList, setGoalsList] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [progressInputs, setProgressInputs] = useState<{[key: string]: number}>({});
  const toast = useToast();
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    target: '',
    type: 'weight',
    deadline: '',
  });

  // Load goals on component mount
  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await goals.getGoals();
      setGoalsList(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load goals');
      // Fallback to mock data for development
      setGoalsList([
        {
          id: '1',
          title: 'Weight Loss',
          target: 'Lose 5kg',
          progress: 60,
          deadline: '2024-06-30',
          status: 'in_progress',
        },
        {
          id: '2',
          title: 'Activity',
          target: '30 minutes daily',
          progress: 75,
          deadline: '2024-05-31',
          status: 'in_progress',
        },
        {
          id: '3',
          title: 'Strength',
          target: '20 pushups',
          progress: 90,
          deadline: '2024-04-30',
          status: 'completed',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await goals.deleteGoal(goalId);
      setGoalsList(goalsList.filter(goal => goal.id !== goalId));
      toast({
        title: t('goalRemoved', language),
        description: t('goalRemovedDesc', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: t('unableToRemoveGoal', language),
        description: err.response?.data?.detail || t('unableToRemoveGoalDesc', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleStartGoal = async (goalId: string) => {
    try {
      await goals.updateGoal(goalId, { status: 'in_progress' });
      setGoalsList(goalsList.map(goal => 
        goal.id === goalId ? { ...goal, status: 'in_progress' as const } : goal
      ));
      toast({
        title: t('goalActivated', language),
        description: t('goalActivatedDesc', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: t('updateFailed', language),
        description: err.response?.data?.detail || t('updateFailed', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleCompleteGoal = async (goalId: string) => {
    try {
      await goals.updateGoal(goalId, { status: 'completed', progress: 100 });
      setGoalsList(goalsList.map(goal => 
        goal.id === goalId ? { ...goal, status: 'completed' as const, progress: 100 } : goal
      ));
      toast({
        title: t('goalCompletedToast', language),
        description: t('goalCompletedDesc', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: t('updateFailed', language),
        description: err.response?.data?.detail || t('updateFailed', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleUpdateProgress = async (goalId: string, newProgress: number) => {
    try {
      await goals.updateGoal(goalId, { progress: newProgress });
      setGoalsList(goalsList.map(goal => 
        goal.id === goalId ? { ...goal, progress: newProgress } : goal
      ));
      toast({
        title: t('progressUpdated', language),
        description: `${t('progressUpdatedDesc', language)} ${newProgress}%`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: t('updateFailed', language),
        description: err.response?.data?.detail || t('updateFailed', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleSubmitGoal = async () => {
    try {
      setSubmitting(true);
      
      // Convert date to full datetime format if provided
      let deadline = null;
      if (formData.deadline) {
        deadline = `${formData.deadline}T23:59:59`;
      }
      
      const newGoal = {
        title: formData.title,
        target: formData.target,
        type: formData.type as 'weight' | 'activity' | 'habit',
        deadline: deadline || '',
        status: 'not_started' as const,
        progress: 0,
      };
      
      const response = await goals.createGoal(newGoal);
      setGoalsList([...goalsList, response.data]);
      
      // Reset form
      setFormData({
        title: '',
        target: '',
        type: 'weight',
        deadline: '',
      });
      
      onClose();
      
      toast({
        title: t('newGoalAdded', language),
        description: t('newGoalAddedDesc', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: t('creationFailed', language),
        description: err.response?.data?.detail || t('creationFailed', language),
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'in_progress':
        return 'blue';
      case 'not_started':
        return 'gray';
      default:
        return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return t('completed', language);
      case 'in_progress':
        return t('inProgress', language);
      case 'not_started':
        return t('notStarted', language);
      case 'failed':
        return t('failed', language);
      default:
        return status.toUpperCase();
    }
  };

  if (loading) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
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
    <Box p={4}>
      <HStack justify="space-between" mb={6}>
        <Heading>{t('goals', language)}</Heading>
        <Button colorScheme="blue" onClick={onOpen}>
          {t('addNewGoal', language)}
        </Button>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {goalsList.map((goal) => (
          <Card key={goal.id}>
            <CardHeader>
              <HStack justify="space-between">
                <Heading size="md">{goal.title}</Heading>
                <HStack>
                  <Badge colorScheme={getStatusColor(goal.status)}>
                    {getStatusText(goal.status)}
                  </Badge>
                  <IconButton
                    aria-label="Delete goal"
                    icon={<DeleteIcon />}
                    size="sm"
                    colorScheme="red"
                    variant="ghost"
                    onClick={() => handleDeleteGoal(goal.id)}
                  />
                </HStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text color="gray.500">{t('target', language)}</Text>
                  <Text fontWeight="bold">{goal.target}</Text>
                </Box>
                
                <Box>
                  <Text color="gray.500">{t('progress', language)}</Text>
                  <Progress value={goal.progress} colorScheme="blue" mb={2} />
                  <Text fontSize="sm">{goal.progress}% {t('complete', language)}</Text>
                  
                  {/* Milestone Message */}
                  {goal.progress > 0 && (
                    <Box mt={2} p={2} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
                      <Text fontSize="xs" color="green.800" textAlign="center" fontWeight="medium">
                        {goal.progress >= 100 ? "🎉 Goal completed!" :
                         goal.progress >= 90 ? `🔥 Almost there! ${100 - goal.progress}% to go!` :
                         goal.progress >= 75 ? `💪 Great progress! Keep it up!` :
                         goal.progress >= 50 ? `🎯 Halfway there! You're doing great!` :
                         goal.progress >= 25 ? `⭐ Good start! ${goal.progress}% done!` :
                         `🌱 Getting started! ${goal.progress}% complete!`}
                      </Text>
                    </Box>
                  )}
                  
                  {/* Progress Input for in_progress goals */}
                  {goal.status === 'in_progress' && (
                    <Box mt={3}>
                      <HStack>
                        <NumberInput
                          size="sm"
                          min={0}
                          max={100}
                          value={progressInputs[goal.id] || goal.progress}
                          onChange={(value: string) => setProgressInputs({
                            ...progressInputs,
                            [goal.id]: parseInt(value) || 0
                          })}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                        <Button
                          size="sm"
                          colorScheme="blue"
                          onClick={() => {
                            const newProgress = progressInputs[goal.id] || goal.progress;
                            handleUpdateProgress(goal.id, newProgress);
                          }}
                        >
                          {t('update', language)}
                        </Button>
                      </HStack>
                    </Box>
                  )}
                </Box>
                
                <Box>
                  <Text color="gray.500">{t('deadline', language)}</Text>
                  <Text>{goal.deadline ? new Date(goal.deadline).toLocaleDateString() : t('noDeadline', language)}</Text>
                </Box>

                <Divider />

                {/* Action Buttons */}
                <VStack spacing={2}>
                  {goal.status === 'not_started' && (
                    <Button
                      colorScheme="green"
                      size="sm"
                      width="full"
                      onClick={() => handleStartGoal(goal.id)}
                    >
                      {t('startGoal', language)}
                    </Button>
                  )}
                  
                  {goal.status === 'in_progress' && (
                    <HStack width="full">
                      <Button
                        colorScheme="green"
                        size="sm"
                        flex={1}
                        onClick={() => handleCompleteGoal(goal.id)}
                      >
                        {t('completeGoal', language)}
                      </Button>
                    </HStack>
                  )}
                  
                  {goal.status === 'completed' && (
                    <Text color="green.500" fontWeight="bold" textAlign="center">
                      🎉 {t('goalCompleted', language)}
                    </Text>
                  )}
                </VStack>
              </VStack>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('addNewGoalModal', language)}</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>{t('goalTitle', language)}</FormLabel>
                <Input 
                  placeholder={t('goalTitlePlaceholder', language)} 
                  value={formData.title}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, title: e.target.value})}
                />
              </FormControl>

              <FormControl>
                <FormLabel>{t('target', language)}</FormLabel>
                <Input 
                  placeholder={t('targetPlaceholder', language)} 
                  value={formData.target}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, target: e.target.value})}
                />
              </FormControl>

              <FormControl>
                <FormLabel>{t('goalType', language)}</FormLabel>
                <Select 
                  value={formData.type}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFormData({...formData, type: e.target.value})}
                >
                  <option value="weight">{t('weight', language)}</option>
                  <option value="activity">{t('activity', language)}</option>
                  <option value="habit">{t('habit', language)}</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>{t('deadline', language)}</FormLabel>
                <Input 
                  type="date" 
                  value={formData.deadline}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, deadline: e.target.value})}
                />
              </FormControl>

              <Button 
                colorScheme="blue" 
                mr={3} 
                width="full"
                onClick={handleSubmitGoal}
                isLoading={submitting}
                loadingText={t('creating', language)}
              >
                {t('createGoal', language)}
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Goals; 