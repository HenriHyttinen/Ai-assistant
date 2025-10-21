import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  VStack,
  HStack,
  Switch,
  FormControl,
  FormLabel,
  Button,
  Text,
  Divider,
  useToast,
  Alert,
  AlertIcon,
  Checkbox,
  CheckboxGroup,
  Stack,
  Badge,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { useApp } from '../contexts/AppContext';
import { consentService } from '../services/api';

// Translation function
const translations = {
  en: {
    dataConsent: 'Data Usage Consent',
    dataConsentDescription: 'Please review and provide your consent for how we collect, process, and use your health data.',
    dataCollection: 'Data Collection',
    dataProcessing: 'Data Processing',
    dataSharing: 'Data Sharing',
    aiInsights: 'AI Insights',
    emailNotifications: 'Email Notifications',
    analyticsTracking: 'Analytics Tracking',
    healthMetrics: 'Health Metrics',
    activityData: 'Activity Data',
    personalInfo: 'Personal Information',
    usagePatterns: 'Usage Patterns',
    whatWeCollect: 'What We Collect',
    howWeUse: 'How We Use Your Data',
    yourRights: 'Your Rights',
    giveConsent: 'Give Consent',
    withdrawConsent: 'Withdraw Consent',
    savePreferences: 'Save Preferences',
    consentGiven: 'Consent Given',
    consentWithdrawn: 'Consent Withdrawn',
    lastUpdated: 'Last Updated',
    required: 'Required',
    optional: 'Optional',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    consentUpdated: 'Your consent preferences have been updated.',
    consentWithdrawnSuccess: 'Your consent has been withdrawn. Some features may be limited.',
    consentGivenSuccess: 'Thank you for providing your consent.',
    errorUpdatingConsent: 'Failed to update consent preferences.',
    requiredForService: 'Required for basic service functionality',
    improvesRecommendations: 'Improves AI recommendations and insights',
    enablesNotifications: 'Enables email notifications and updates',
    helpsImproveService: 'Helps us improve our service',
    personalHealthData: 'Personal health data (age, gender, height, weight)',
    fitnessMetrics: 'Fitness metrics (BMI, wellness scores, activity levels)',
    exerciseData: 'Exercise and activity logs',
    appUsage: 'How you use the app (pages visited, features used)',
    dataRetention: 'Data Retention',
    dataSecurity: 'Data Security',
    yourControl: 'Your Control',
    dataRetentionText: 'We retain your data for as long as your account is active. You can request deletion at any time.',
    dataSecurityText: 'Your data is encrypted in transit and at rest. We follow industry-standard security practices.',
    yourControlText: 'You can modify or withdraw your consent at any time through your settings.',
    consentRequired: 'Consent Required',
    consentRequiredText: 'To use our health tracking features, we need your explicit consent for data collection and processing.',
  },
  de: {
    dataConsent: 'Datennutzungs-Einverständnis',
    dataConsentDescription: 'Bitte überprüfen Sie und geben Sie Ihre Zustimmung für die Erfassung, Verarbeitung und Nutzung Ihrer Gesundheitsdaten.',
    dataCollection: 'Datenerfassung',
    dataProcessing: 'Datenverarbeitung',
    dataSharing: 'Datenaustausch',
    aiInsights: 'KI-Einblicke',
    emailNotifications: 'E-Mail-Benachrichtigungen',
    analyticsTracking: 'Analytics-Tracking',
    healthMetrics: 'Gesundheitsmetriken',
    activityData: 'Aktivitätsdaten',
    personalInfo: 'Persönliche Informationen',
    usagePatterns: 'Nutzungsmuster',
    whatWeCollect: 'Was wir sammeln',
    howWeUse: 'Wie wir Ihre Daten nutzen',
    yourRights: 'Ihre Rechte',
    giveConsent: 'Zustimmung geben',
    withdrawConsent: 'Zustimmung widerrufen',
    savePreferences: 'Einstellungen speichern',
    consentGiven: 'Zustimmung erteilt',
    consentWithdrawn: 'Zustimmung widerrufen',
    lastUpdated: 'Zuletzt aktualisiert',
    required: 'Erforderlich',
    optional: 'Optional',
    loading: 'Laden...',
    success: 'Erfolg',
    error: 'Fehler',
    consentUpdated: 'Ihre Einverständniseinstellungen wurden aktualisiert.',
    consentWithdrawnSuccess: 'Ihr Einverständnis wurde widerrufen. Einige Funktionen können eingeschränkt sein.',
    consentGivenSuccess: 'Vielen Dank für Ihre Zustimmung.',
    errorUpdatingConsent: 'Fehler beim Aktualisieren der Einverständniseinstellungen.',
    requiredForService: 'Erforderlich für grundlegende Servicefunktionalität',
    improvesRecommendations: 'Verbessert KI-Empfehlungen und Einblicke',
    enablesNotifications: 'Aktiviert E-Mail-Benachrichtigungen und Updates',
    helpsImproveService: 'Hilft uns, unseren Service zu verbessern',
    personalHealthData: 'Persönliche Gesundheitsdaten (Alter, Geschlecht, Größe, Gewicht)',
    fitnessMetrics: 'Fitness-Metriken (BMI, Wohlfühl-Scores, Aktivitätsniveaus)',
    exerciseData: 'Übungs- und Aktivitätsprotokolle',
    appUsage: 'Wie Sie die App nutzen (besuchte Seiten, genutzte Funktionen)',
    dataRetention: 'Datenspeicherung',
    dataSecurity: 'Datensicherheit',
    yourControl: 'Ihre Kontrolle',
    dataRetentionText: 'Wir speichern Ihre Daten, solange Ihr Konto aktiv ist. Sie können jederzeit eine Löschung beantragen.',
    dataSecurityText: 'Ihre Daten werden während der Übertragung und im Ruhezustand verschlüsselt. Wir folgen branchenüblichen Sicherheitspraktiken.',
    yourControlText: 'Sie können Ihre Zustimmung jederzeit über Ihre Einstellungen ändern oder widerrufen.',
    consentRequired: 'Einverständnis erforderlich',
    consentRequiredText: 'Um unsere Gesundheits-Tracking-Funktionen zu nutzen, benötigen wir Ihre ausdrückliche Zustimmung zur Datenerfassung und -verarbeitung.',
  },
  es: {
    dataConsent: 'Consentimiento de Uso de Datos',
    dataConsentDescription: 'Por favor revise y proporcione su consentimiento para cómo recopilamos, procesamos y usamos sus datos de salud.',
    dataCollection: 'Recopilación de Datos',
    dataProcessing: 'Procesamiento de Datos',
    dataSharing: 'Compartir Datos',
    aiInsights: 'Insights de IA',
    emailNotifications: 'Notificaciones por Email',
    analyticsTracking: 'Seguimiento de Analytics',
    healthMetrics: 'Métricas de Salud',
    activityData: 'Datos de Actividad',
    personalInfo: 'Información Personal',
    usagePatterns: 'Patrones de Uso',
    whatWeCollect: 'Lo que Recopilamos',
    howWeUse: 'Cómo Usamos Sus Datos',
    yourRights: 'Sus Derechos',
    giveConsent: 'Dar Consentimiento',
    withdrawConsent: 'Retirar Consentimiento',
    savePreferences: 'Guardar Preferencias',
    consentGiven: 'Consentimiento Dado',
    consentWithdrawn: 'Consentimiento Retirado',
    lastUpdated: 'Última Actualización',
    required: 'Requerido',
    optional: 'Opcional',
    loading: 'Cargando...',
    success: 'Éxito',
    error: 'Error',
    consentUpdated: 'Sus preferencias de consentimiento han sido actualizadas.',
    consentWithdrawnSuccess: 'Su consentimiento ha sido retirado. Algunas funciones pueden estar limitadas.',
    consentGivenSuccess: 'Gracias por proporcionar su consentimiento.',
    errorUpdatingConsent: 'Error al actualizar las preferencias de consentimiento.',
    requiredForService: 'Requerido para la funcionalidad básica del servicio',
    improvesRecommendations: 'Mejora las recomendaciones e insights de IA',
    enablesNotifications: 'Habilita notificaciones por email y actualizaciones',
    helpsImproveService: 'Nos ayuda a mejorar nuestro servicio',
    personalHealthData: 'Datos de salud personales (edad, género, altura, peso)',
    fitnessMetrics: 'Métricas de fitness (IMC, puntuaciones de bienestar, niveles de actividad)',
    exerciseData: 'Registros de ejercicio y actividad',
    appUsage: 'Cómo usa la aplicación (páginas visitadas, funciones utilizadas)',
    dataRetention: 'Retención de Datos',
    dataSecurity: 'Seguridad de Datos',
    yourControl: 'Su Control',
    dataRetentionText: 'Retenemos sus datos mientras su cuenta esté activa. Puede solicitar la eliminación en cualquier momento.',
    dataSecurityText: 'Sus datos están encriptados en tránsito y en reposo. Seguimos prácticas de seguridad estándar de la industria.',
    yourControlText: 'Puede modificar o retirar su consentimiento en cualquier momento a través de su configuración.',
    consentRequired: 'Consentimiento Requerido',
    consentRequiredText: 'Para usar nuestras funciones de seguimiento de salud, necesitamos su consentimiento explícito para la recopilación y procesamiento de datos.',
  },
  fr: {
    dataConsent: 'Consentement d\'Utilisation des Données',
    dataConsentDescription: 'Veuillez examiner et fournir votre consentement pour la façon dont nous collectons, traitons et utilisons vos données de santé.',
    dataCollection: 'Collecte de Données',
    dataProcessing: 'Traitement des Données',
    dataSharing: 'Partage de Données',
    aiInsights: 'Insights IA',
    emailNotifications: 'Notifications Email',
    analyticsTracking: 'Suivi Analytics',
    healthMetrics: 'Métriques de Santé',
    activityData: 'Données d\'Activité',
    personalInfo: 'Informations Personnelles',
    usagePatterns: 'Modèles d\'Utilisation',
    whatWeCollect: 'Ce que Nous Collectons',
    howWeUse: 'Comment Nous Utilisons Vos Données',
    yourRights: 'Vos Droits',
    giveConsent: 'Donner le Consentement',
    withdrawConsent: 'Retirer le Consentement',
    savePreferences: 'Sauvegarder les Préférences',
    consentGiven: 'Consentement Donné',
    consentWithdrawn: 'Consentement Retiré',
    lastUpdated: 'Dernière Mise à Jour',
    required: 'Requis',
    optional: 'Optionnel',
    loading: 'Chargement...',
    success: 'Succès',
    error: 'Erreur',
    consentUpdated: 'Vos préférences de consentement ont été mises à jour.',
    consentWithdrawnSuccess: 'Votre consentement a été retiré. Certaines fonctionnalités peuvent être limitées.',
    consentGivenSuccess: 'Merci d\'avoir fourni votre consentement.',
    errorUpdatingConsent: 'Échec de la mise à jour des préférences de consentement.',
    requiredForService: 'Requis pour la fonctionnalité de base du service',
    improvesRecommendations: 'Améliore les recommandations et insights IA',
    enablesNotifications: 'Active les notifications email et mises à jour',
    helpsImproveService: 'Nous aide à améliorer notre service',
    personalHealthData: 'Données de santé personnelles (âge, genre, taille, poids)',
    fitnessMetrics: 'Métriques de fitness (IMC, scores de bien-être, niveaux d\'activité)',
    exerciseData: 'Journaux d\'exercice et d\'activité',
    appUsage: 'Comment vous utilisez l\'application (pages visitées, fonctionnalités utilisées)',
    dataRetention: 'Rétention des Données',
    dataSecurity: 'Sécurité des Données',
    yourControl: 'Votre Contrôle',
    dataRetentionText: 'Nous conservons vos données tant que votre compte est actif. Vous pouvez demander la suppression à tout moment.',
    dataSecurityText: 'Vos données sont chiffrées en transit et au repos. Nous suivons les pratiques de sécurité standard de l\'industrie.',
    yourControlText: 'Vous pouvez modifier ou retirer votre consentement à tout moment via vos paramètres.',
    consentRequired: 'Consentement Requis',
    consentRequiredText: 'Pour utiliser nos fonctionnalités de suivi de santé, nous avons besoin de votre consentement explicite pour la collecte et le traitement des données.',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

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

interface ConsentStatus {
  user_id: number;
  consent_given: boolean;
  consent_date: string;
  data_usage_consent: ConsentData;
  privacy_policy_version: string;
}

const DataConsent = () => {
  const toast = useToast();
  const { user } = useSupabaseAuth();
  const { language } = useApp();
  
  const [consentStatus, setConsentStatus] = useState<ConsentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [consentData, setConsentData] = useState<ConsentData>({
    data_collection: false,
    data_processing: false,
    data_sharing: false,
    ai_insights: false,
    email_notifications: false,
    analytics_tracking: false,
    health_metrics: false,
    activity_data: false,
    personal_info: false,
    usage_patterns: false,
  });

  useEffect(() => {
    const loadConsentStatus = async () => {
      if (!user) return;
      
      setLoading(true);
      try {
        const response = await consentService.getConsentStatus();
        setConsentStatus(response.data);
        setConsentData(response.data.data_usage_consent);
      } catch (error) {
        // No consent found, using defaults
        console.log('No consent data found, using defaults');
      } finally {
        setLoading(false);
      }
    };

    loadConsentStatus();
  }, [user]);

  const handleConsentChange = (key: keyof ConsentData, value: boolean) => {
    setConsentData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveConsent = async () => {
    if (!user) return;
    
    setSaving(true);
    try {
      const response = await consentService.giveConsent({
        consent_given: true,
        data_usage_consent: consentData
      });
      
      setConsentStatus(response.data);
      
      toast({
        title: t('success', language),
        description: t('consentUpdated', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: t('error', language),
        description: t('errorUpdatingConsent', language),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleWithdrawConsent = async () => {
    if (!user) return;
    
    setSaving(true);
    try {
      await consentService.withdrawConsent();
      setConsentStatus(null);
      setConsentData({
        data_collection: false,
        data_processing: false,
        data_sharing: false,
        ai_insights: false,
        email_notifications: false,
        analytics_tracking: false,
        health_metrics: false,
        activity_data: false,
        personal_info: false,
        usage_patterns: false,
      });
      
      toast({
        title: t('success', language),
        description: t('consentWithdrawnSuccess', language),
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: t('error', language),
        description: t('errorUpdatingConsent', language),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box p={4}>
        <Heading size="lg" mb={4}>{t('dataConsent', language)}</Heading>
        <Text>{t('loading', language)}</Text>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Heading size="lg" mb={6}>{t('dataConsent', language)}</Heading>
      
      <Text mb={6} color="gray.600">
        {t('dataConsentDescription', language)}
      </Text>

      {/* Current Status */}
      {consentStatus && (
        <Alert status="info" mb={6}>
          <AlertIcon />
          <Box>
            <Text fontWeight="bold">{t('consentGiven', language)}</Text>
            <Text fontSize="sm">
              {t('lastUpdated', language)}: {new Date(consentStatus.consent_date).toLocaleDateString()}
            </Text>
          </Box>
        </Alert>
      )}

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Data Collection Categories */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('dataCollection', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
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
                  <FormLabel mb="0">{t('usagePatterns', language)}</FormLabel>
                  <Text fontSize="sm" color="gray.500">
                    {t('appUsage', language)}
                  </Text>
                  <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
                </Box>
                <Switch
                  isChecked={consentData.usage_patterns}
                  onChange={(e) => handleConsentChange('usage_patterns', e.target.checked)}
                />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        {/* Data Usage Categories */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('howWeUse', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
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

              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <FormLabel mb="0">{t('analyticsTracking', language)}</FormLabel>
                  <Text fontSize="sm" color="gray.500">
                    {t('helpsImproveService', language)}
                  </Text>
                  <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
                </Box>
                <Switch
                  isChecked={consentData.analytics_tracking}
                  onChange={(e) => handleConsentChange('analytics_tracking', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <FormLabel mb="0">{t('dataSharing', language)}</FormLabel>
                  <Text fontSize="sm" color="gray.500">
                    {t('helpsImproveService', language)}
                  </Text>
                  <Badge colorScheme="orange" size="sm">{t('optional', language)}</Badge>
                </Box>
                <Switch
                  isChecked={consentData.data_sharing}
                  onChange={(e) => handleConsentChange('data_sharing', e.target.checked)}
                />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Additional Information */}
      <Card mt={6}>
        <CardHeader>
          <Heading size="md">{t('yourRights', language)}</Heading>
        </CardHeader>
        <CardBody>
          <Accordion allowToggle>
            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    {t('dataRetention', language)}
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <Text>{t('dataRetentionText', language)}</Text>
              </AccordionPanel>
            </AccordionItem>

            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    {t('dataSecurity', language)}
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <Text>{t('dataSecurityText', language)}</Text>
              </AccordionPanel>
            </AccordionItem>

            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    {t('yourControl', language)}
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <Text>{t('yourControlText', language)}</Text>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
        </CardBody>
      </Card>

      {/* Action Buttons */}
      <HStack spacing={4} mt={6} justify="center">
        <Button
          colorScheme="blue"
          onClick={handleSaveConsent}
          isLoading={saving}
          loadingText={t('saving', language)}
        >
          {consentStatus ? t('savePreferences', language) : t('giveConsent', language)}
        </Button>
        
        {consentStatus && (
          <Button
            colorScheme="red"
            variant="outline"
            onClick={handleWithdrawConsent}
            isLoading={saving}
            loadingText={t('saving', language)}
          >
            {t('withdrawConsent', language)}
          </Button>
        )}
      </HStack>
    </Box>
  );
};

export default DataConsent;
