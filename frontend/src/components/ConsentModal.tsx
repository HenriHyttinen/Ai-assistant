import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  Switch,
  FormControl,
  FormLabel,
  Text,
  Badge,
  Alert,
  AlertIcon,
  Divider,
  useToast,
  Box,
} from '@chakra-ui/react';
import { useState } from 'react';
import { consentService } from '../services/api';

// Translation function
const translations = {
  en: {
    dataConsentRequired: 'Data Consent Required',
    consentRequiredText: 'To use our health tracking features, we need your explicit consent for data collection and processing.',
    dataCollection: 'Data Collection',
    dataProcessing: 'Data Processing',
    aiInsights: 'AI Insights',
    emailNotifications: 'Email Notifications',
    required: 'Required',
    optional: 'Optional',
    requiredForService: 'Required for basic service functionality',
    improvesRecommendations: 'Improves AI recommendations and insights',
    enablesNotifications: 'Enables email notifications and updates',
    giveConsent: 'Give Consent',
    cancel: 'Cancel',
    consentGiven: 'Thank you for providing your consent.',
    errorUpdatingConsent: 'Failed to update consent preferences.',
    personalInfo: 'Personal Information',
    healthMetrics: 'Health Metrics',
    activityData: 'Activity Data',
    usagePatterns: 'Usage Patterns',
    personalHealthData: 'Personal health data (age, gender, height, weight)',
    fitnessMetrics: 'Fitness metrics (BMI, wellness scores, activity levels)',
    exerciseData: 'Exercise and activity logs',
    appUsage: 'How you use the app (pages visited, features used)',
  },
  de: {
    dataConsentRequired: 'Dateneinverständnis erforderlich',
    consentRequiredText: 'Um unsere Gesundheits-Tracking-Funktionen zu nutzen, benötigen wir Ihre ausdrückliche Zustimmung zur Datenerfassung und -verarbeitung.',
    dataCollection: 'Datenerfassung',
    dataProcessing: 'Datenverarbeitung',
    aiInsights: 'KI-Einblicke',
    emailNotifications: 'E-Mail-Benachrichtigungen',
    required: 'Erforderlich',
    optional: 'Optional',
    requiredForService: 'Erforderlich für grundlegende Servicefunktionalität',
    improvesRecommendations: 'Verbessert KI-Empfehlungen und Einblicke',
    enablesNotifications: 'Aktiviert E-Mail-Benachrichtigungen und Updates',
    giveConsent: 'Zustimmung geben',
    cancel: 'Abbrechen',
    consentGiven: 'Vielen Dank für Ihre Zustimmung.',
    errorUpdatingConsent: 'Fehler beim Aktualisieren der Einverständniseinstellungen.',
    personalInfo: 'Persönliche Informationen',
    healthMetrics: 'Gesundheitsmetriken',
    activityData: 'Aktivitätsdaten',
    usagePatterns: 'Nutzungsmuster',
    personalHealthData: 'Persönliche Gesundheitsdaten (Alter, Geschlecht, Größe, Gewicht)',
    fitnessMetrics: 'Fitness-Metriken (BMI, Wohlfühl-Scores, Aktivitätsniveaus)',
    exerciseData: 'Übungs- und Aktivitätsprotokolle',
    appUsage: 'Wie Sie die App nutzen (besuchte Seiten, genutzte Funktionen)',
  },
  es: {
    dataConsentRequired: 'Consentimiento de Datos Requerido',
    consentRequiredText: 'Para usar nuestras funciones de seguimiento de salud, necesitamos su consentimiento explícito para la recopilación y procesamiento de datos.',
    dataCollection: 'Recopilación de Datos',
    dataProcessing: 'Procesamiento de Datos',
    aiInsights: 'Insights de IA',
    emailNotifications: 'Notificaciones por Email',
    required: 'Requerido',
    optional: 'Opcional',
    requiredForService: 'Requerido para la funcionalidad básica del servicio',
    improvesRecommendations: 'Mejora las recomendaciones e insights de IA',
    enablesNotifications: 'Habilita notificaciones por email y actualizaciones',
    giveConsent: 'Dar Consentimiento',
    cancel: 'Cancelar',
    consentGiven: 'Gracias por proporcionar su consentimiento.',
    errorUpdatingConsent: 'Error al actualizar las preferencias de consentimiento.',
    personalInfo: 'Información Personal',
    healthMetrics: 'Métricas de Salud',
    activityData: 'Datos de Actividad',
    usagePatterns: 'Patrones de Uso',
    personalHealthData: 'Datos de salud personales (edad, género, altura, peso)',
    fitnessMetrics: 'Métricas de fitness (IMC, puntuaciones de bienestar, niveles de actividad)',
    exerciseData: 'Registros de ejercicio y actividad',
    appUsage: 'Cómo usa la aplicación (páginas visitadas, funciones utilizadas)',
  },
  fr: {
    dataConsentRequired: 'Consentement aux Données Requis',
    consentRequiredText: 'Pour utiliser nos fonctionnalités de suivi de santé, nous avons besoin de votre consentement explicite pour la collecte et le traitement des données.',
    dataCollection: 'Collecte de Données',
    dataProcessing: 'Traitement des Données',
    aiInsights: 'Insights IA',
    emailNotifications: 'Notifications Email',
    required: 'Requis',
    optional: 'Optionnel',
    requiredForService: 'Requis pour la fonctionnalité de base du service',
    improvesRecommendations: 'Améliore les recommandations et insights IA',
    enablesNotifications: 'Active les notifications email et mises à jour',
    giveConsent: 'Donner le Consentement',
    cancel: 'Annuler',
    consentGiven: 'Merci d\'avoir fourni votre consentement.',
    errorUpdatingConsent: 'Échec de la mise à jour des préférences de consentement.',
    personalInfo: 'Informations Personnelles',
    healthMetrics: 'Métriques de Santé',
    activityData: 'Données d\'Activité',
    usagePatterns: 'Modèles d\'Utilisation',
    personalHealthData: 'Données de santé personnelles (âge, genre, taille, poids)',
    fitnessMetrics: 'Métriques de fitness (IMC, scores de bien-être, niveaux d\'activité)',
    exerciseData: 'Journaux d\'exercice et d\'activité',
    appUsage: 'Comment vous utilisez l\'application (pages visitées, fonctionnalités utilisées)',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

interface ConsentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConsentGiven: () => void;
  language: string;
}

interface ConsentData {
  data_collection: boolean;
  data_processing: boolean;
  data_sharing: boolean;
  ai_insights: boolean;
  email_notifications: boolean;
  analytics_tracking: boolean;
  health_metrics: boolean;
  activity_data: boolean;
  personal_info: boolean;
  usage_patterns: boolean;
}

const ConsentModal: React.FC<ConsentModalProps> = ({ isOpen, onClose, onConsentGiven, language }) => {
  const toast = useToast();
  const [consentData, setConsentData] = useState<ConsentData>({
    data_collection: true, // Default to true for required fields
    data_processing: true, // Default to true for required fields
    data_sharing: false,
    ai_insights: false,
    email_notifications: false,
    analytics_tracking: false,
    health_metrics: true, // Default to true for required fields
    activity_data: false,
    personal_info: true, // Default to true for required fields
    usage_patterns: false,
  });
  const [saving, setSaving] = useState(false);

  const handleConsentChange = (key: keyof ConsentData, value: boolean) => {
    setConsentData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleGiveConsent = async () => {
    setSaving(true);
    try {
      await consentService.giveConsent({
        consent_given: true,
        data_usage_consent: consentData
      });
      
      toast({
        title: t('consentGiven', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      onConsentGiven();
      onClose();
    } catch (error) {
      toast({
        title: t('errorUpdatingConsent', language),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" isCentered>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{t('dataConsentRequired', language)}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Alert status="info" mb={4}>
            <AlertIcon />
            {t('consentRequiredText', language)}
          </Alert>

          <VStack spacing={4} align="stretch">
            {/* Required Data Collection */}
            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('personalInfo', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('personalHealthData', language)}
                </Text>
                <Badge colorScheme="red" size="sm">{t('required', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.personal_info}
                onChange={(e) => handleConsentChange('personal_info', e.target.checked)}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('healthMetrics', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('fitnessMetrics', language)}
                </Text>
                <Badge colorScheme="red" size="sm">{t('required', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.health_metrics}
                onChange={(e) => handleConsentChange('health_metrics', e.target.checked)}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('dataProcessing', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('requiredForService', language)}
                </Text>
                <Badge colorScheme="red" size="sm">{t('required', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.data_processing}
                onChange={(e) => handleConsentChange('data_processing', e.target.checked)}
              />
            </FormControl>

            <Divider />

            {/* Optional Data Collection */}
            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('activityData', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('exerciseData', language)}
                </Text>
                <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.activity_data}
                onChange={(e) => handleConsentChange('activity_data', e.target.checked)}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('aiInsights', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('improvesRecommendations', language)}
                </Text>
                <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.ai_insights}
                onChange={(e) => handleConsentChange('ai_insights', e.target.checked)}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <FormLabel mb="0">{t('emailNotifications', language)}</FormLabel>
                <Text fontSize="sm" color="gray.500">
                  {t('enablesNotifications', language)}
                </Text>
                <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
              </Box>
              <Switch
                isChecked={consentData.email_notifications}
                onChange={(e) => handleConsentChange('email_notifications', e.target.checked)}
              />
            </FormControl>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={4}>
            <Button variant="ghost" onClick={onClose}>
              {t('cancel', language)}
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleGiveConsent}
              isLoading={saving}
              loadingText="Saving..."
              isDisabled={!consentData.personal_info || !consentData.health_metrics || !consentData.data_processing}
            >
              {t('giveConsent', language)}
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ConsentModal;
