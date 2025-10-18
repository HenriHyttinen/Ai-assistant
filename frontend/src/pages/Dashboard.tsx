import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Stack,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useDisclosure,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { analytics, healthProfile } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import ActivityLogModal from '../components/ActivityLogModal';
import WeightProgressCard from '../components/WeightProgressCard';

// Move translations outside component to avoid recreation on every render
const translations = {
  en: {
    dashboard: 'Dashboard',
    wellnessScore: 'Wellness Score',
    bmi: 'BMI',
    currentWeight: 'Current Weight',
    targetWeight: 'Target Weight',
    towardsGoal: 'towards goal',
    weeklyActivity: 'Weekly Activity',
    weightProgress: 'Weight Progress',
    activitySummary: 'Activity Summary',
    personalizedHealthInsights: 'Personalized Health Insights',
    healthStatus: 'Health Status',
    recommendations: 'Recommendations',
    yourStrengths: 'Your Strengths',
    focusAreas: 'Focus Areas',
    obese: 'Obese',
    underweight: 'Underweight',
    normal: 'Normal',
    overweight: 'Overweight',
    minTotal: 'min total',
    currentWeightLabel: 'Current Weight',
    recordedOn: 'Recorded on',
    startYourWeightJourney: 'Start Your Weight Journey',
    addEntries: 'Add 2-3 more entries to see trends',
    trackDaily: 'Track daily or weekly for best insights',
    setWeightGoal: 'Set a weight goal to track progress',
    addEntry: 'Add Entry',
    setGoal: 'Set Goal',
    everyJourney: 'Every journey begins with a single step!',
    totalActivities: 'Total Activities',
    totalDuration: 'Total Duration',
    averageDuration: 'Average Duration',
    activityTypes: 'Activity Types',
    noneRecorded: 'None recorded',
    noWeightData: 'No Weight Data Yet',
    startTrackingWeight: 'Start tracking your weight to see progress over time',
    addWeightEntry: 'Add Weight Entry',
    healthJourney: 'Your health journey is off to a great start! Your consistent activity levels show you\'re committed to your wellness goals. Keep up the momentum!',
    waterGoal: 'Aim for 8-10 glasses of water daily to support your active lifestyle',
    stretching: 'Include 15 minutes of stretching in your routine for better recovery',
    sleepTracking: 'Track your sleep patterns to optimize your rest and recovery',
    regularExercise: 'Maintaining a regular exercise schedule',
    steadyProgress: 'Making steady progress toward your weight goals',
    nutritionTracking: 'Consider tracking your daily nutrition for better insights',
    workoutVariety: 'Mix up your workout routine to keep things interesting',
  },
  es: {
    dashboard: 'Panel de Control',
    wellnessScore: 'Puntuación de Bienestar',
    bmi: 'IMC',
    currentWeight: 'Peso Actual',
    targetWeight: 'Peso Objetivo',
    towardsGoal: 'hacia el objetivo',
    weeklyActivity: 'Actividad Semanal',
    weightProgress: 'Progreso de Peso',
    activitySummary: 'Resumen de Actividad',
    personalizedHealthInsights: 'Perspectivas de Salud Personalizadas',
    healthStatus: 'Estado de Salud',
    recommendations: 'Recomendaciones',
    yourStrengths: 'Tus Fortalezas',
    focusAreas: 'Áreas de Enfoque',
    obese: 'Obeso',
    underweight: 'Bajo Peso',
    normal: 'Normal',
    overweight: 'Sobrepeso',
    minTotal: 'min total',
    currentWeightLabel: 'Peso Actual',
    recordedOn: 'Registrado el',
    startYourWeightJourney: 'Comienza tu Viaje de Peso',
    addEntries: 'Agrega 2-3 entradas más para ver tendencias',
    trackDaily: 'Registra diaria o semanalmente para mejores perspectivas',
    setWeightGoal: 'Establece una meta de peso para rastrear el progreso',
    addEntry: 'Agregar Entrada',
    setGoal: 'Establecer Meta',
    everyJourney: '¡Cada viaje comienza con un solo paso!',
    totalActivities: 'Total de Actividades',
    totalDuration: 'Duración Total',
    averageDuration: 'Duración Promedio',
    activityTypes: 'Tipos de Actividad',
    noneRecorded: 'Ninguna registrada',
    noWeightData: 'Sin Datos de Peso Aún',
    startTrackingWeight: 'Comienza a rastrear tu peso para ver el progreso',
    addWeightEntry: 'Agregar Entrada de Peso',
    healthJourney: '¡Tu viaje de salud ha comenzado muy bien! Tus niveles de actividad consistentes muestran que estás comprometido con tus objetivos de bienestar. ¡Mantén el impulso!',
    waterGoal: 'Apunta a 8-10 vasos de agua diarios para apoyar tu estilo de vida activo',
    stretching: 'Incluye 15 minutos de estiramiento en tu rutina para mejor recuperación',
    sleepTracking: 'Rastrea tus patrones de sueño para optimizar tu descanso y recuperación',
    regularExercise: 'Mantener un horario regular de ejercicio',
    steadyProgress: 'Haciendo progreso constante hacia tus objetivos de peso',
    nutritionTracking: 'Considera rastrear tu nutrición diaria para mejores perspectivas',
    workoutVariety: 'Varía tu rutina de ejercicios para mantener las cosas interesantes',
  },
  fr: {
    dashboard: 'Tableau de Bord',
    wellnessScore: 'Score de Bien-être',
    bmi: 'IMC',
    currentWeight: 'Poids Actuel',
    targetWeight: 'Poids Cible',
    towardsGoal: 'vers l\'objectif',
    weeklyActivity: 'Activité Hebdomadaire',
    weightProgress: 'Progrès de Poids',
    activitySummary: 'Résumé d\'Activité',
    personalizedHealthInsights: 'Perspectives de Santé Personnalisées',
    healthStatus: 'État de Santé',
    recommendations: 'Recommandations',
    yourStrengths: 'Vos Forces',
    focusAreas: 'Domaines d\'Attention',
    obese: 'Obèse',
    underweight: 'Insuffisance Pondérale',
    normal: 'Normal',
    overweight: 'Surpoids',
    minTotal: 'min total',
    currentWeightLabel: 'Poids Actuel',
    recordedOn: 'Enregistré le',
    startYourWeightJourney: 'Commencez votre Voyage de Poids',
    addEntries: 'Ajoutez 2-3 entrées de plus pour voir les tendances',
    trackDaily: 'Suivez quotidiennement ou hebdomadairement pour de meilleures perspectives',
    setWeightGoal: 'Définissez un objectif de poids pour suivre les progrès',
    addEntry: 'Ajouter Entrée',
    setGoal: 'Définir Objectif',
    everyJourney: 'Chaque voyage commence par un seul pas !',
    totalActivities: 'Total d\'Activités',
    totalDuration: 'Durée Totale',
    averageDuration: 'Durée Moyenne',
    activityTypes: 'Types d\'Activité',
    noneRecorded: 'Aucune enregistrée',
    noWeightData: 'Pas de Données de Poids Encore',
    startTrackingWeight: 'Commencez à suivre votre poids pour voir les progrès',
    addWeightEntry: 'Ajouter une Entrée de Poids',
    healthJourney: 'Votre voyage de santé commence très bien ! Vos niveaux d\'activité constants montrent que vous êtes engagé envers vos objectifs de bien-être. Continuez sur cette lancée !',
    waterGoal: 'Visez 8-10 verres d\'eau par jour pour soutenir votre mode de vie actif',
    stretching: 'Incluez 15 minutes d\'étirement dans votre routine pour une meilleure récupération',
    sleepTracking: 'Suivez vos habitudes de sommeil pour optimiser votre repos et récupération',
    regularExercise: 'Maintenir un horaire d\'exercice régulier',
    steadyProgress: 'Faire des progrès constants vers vos objectifs de poids',
    nutritionTracking: 'Considérez suivre votre nutrition quotidienne pour de meilleures perspectives',
    workoutVariety: 'Variez votre routine d\'entraînement pour garder les choses intéressantes',
  },
  de: {
    dashboard: 'Dashboard',
    wellnessScore: 'Wohlfühl-Score',
    bmi: 'BMI',
    currentWeight: 'Aktuelles Gewicht',
    targetWeight: 'Zielgewicht',
    towardsGoal: 'zum Ziel',
    weeklyActivity: 'Wöchentliche Aktivität',
    weightProgress: 'Gewichtsfortschritt',
    activitySummary: 'Aktivitätszusammenfassung',
    personalizedHealthInsights: 'Personalisierte Gesundheitserkenntnisse',
    healthStatus: 'Gesundheitsstatus',
    recommendations: 'Empfehlungen',
    yourStrengths: 'Ihre Stärken',
    focusAreas: 'Fokusbereiche',
    obese: 'Fettleibig',
    underweight: 'Untergewicht',
    normal: 'Normal',
    overweight: 'Übergewicht',
    minTotal: 'min gesamt',
    currentWeightLabel: 'Aktuelles Gewicht',
    recordedOn: 'Aufgezeichnet am',
    startYourWeightJourney: 'Beginnen Sie Ihre Gewichtsreise',
    addEntries: 'Fügen Sie 2-3 weitere Einträge hinzu, um Trends zu sehen',
    trackDaily: 'Verfolgen Sie täglich oder wöchentlich für beste Einblicke',
    setWeightGoal: 'Setzen Sie ein Gewichtsziel, um den Fortschritt zu verfolgen',
    addEntry: 'Eintrag Hinzufügen',
    setGoal: 'Ziel Setzen',
    everyJourney: 'Jede Reise beginnt mit einem einzigen Schritt!',
    totalActivities: 'Gesamtaktivitäten',
    totalDuration: 'Gesamtdauer',
    averageDuration: 'Durchschnittsdauer',
    activityTypes: 'Aktivitätstypen',
    noneRecorded: 'Keine aufgezeichnet',
    noWeightData: 'Noch Keine Gewichtsdaten',
    startTrackingWeight: 'Beginnen Sie mit der Gewichtsverfolgung, um Fortschritte zu sehen',
    addWeightEntry: 'Gewichtseintrag Hinzufügen',
    healthJourney: 'Ihre Gesundheitsreise hat einen großartigen Start! Ihre konstanten Aktivitätsniveaus zeigen, dass Sie Ihren Wellnesszielen verpflichtet sind. Behalten Sie den Schwung bei!',
    waterGoal: 'Streben Sie 8-10 Gläser Wasser täglich an, um Ihren aktiven Lebensstil zu unterstützen',
    stretching: 'Fügen Sie 15 Minuten Dehnen in Ihre Routine für bessere Erholung ein',
    sleepTracking: 'Verfolgen Sie Ihre Schlafmuster, um Ihre Ruhe und Erholung zu optimieren',
    regularExercise: 'Einen regelmäßigen Trainingsplan einhalten',
    steadyProgress: 'Stetigen Fortschritt zu Ihren Gewichtszielen machen',
    nutritionTracking: 'Erwägen Sie, Ihre tägliche Ernährung zu verfolgen für bessere Einblicke',
    workoutVariety: 'Variieren Sie Ihre Trainingsroutine, um die Dinge interessant zu halten',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};
import { convertWeightForDisplay, getWeightUnit } from '../utils/unitConversion';

interface HealthAnalytics {
  current_bmi: number;
  current_wellness_score: number;
  weight_trend: number[];
  bmi_trend: number[];
  wellness_score_trend: number[];
  activity_summary: {
    total_duration: number;
    activity_count: number;
    average_duration: number;
    activity_types: string[];
  };
  progress_towards_goal: number;
}

interface HealthProfile {
  weight: number;
  target_weight?: number;
  activity_level: string;
}

interface AIInsights {
  status_analysis: string;
  recommendations: string[];
  strengths: string[];
  improvements: string[];
}

const Dashboard = () => {
  const { user } = useAuth();
  const { measurementSystem, language } = useApp();
  const { isOpen: isActivityModalOpen, onClose: onActivityModalClose } = useDisclosure();
  
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [profileData, setProfileData] = useState<HealthProfile | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch analytics data
        const analyticsResponse = await analytics.getAnalytics();
        setAnalyticsData(analyticsResponse.data);
        
        // Fetch profile data
        const profileResponse = await healthProfile.getProfile();
        setProfileData(profileResponse.data);
        
        // Fetch AI insights from the backend
        try {
          const insightsResponse = await healthProfile.getInsights();
          if (insightsResponse.data?.insights) {
            setAiInsights(insightsResponse.data.insights);
          }
        } catch (insightsError) {
          // AI insights are optional, don't fail the whole dashboard
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          // Likely missing health profile or analytics pre-reqs
          setError(null);
          setAnalyticsData(null);
          setProfileData(null);
        } else {
          setError(err.response?.data?.detail || 'Failed to load dashboard data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [measurementSystem, language]);

  // Add a function to refresh insights when profile changes
  const refreshInsights = async () => {
    try {
      const insightsResponse = await healthProfile.getInsights();
      if (insightsResponse.data?.insights) {
        setAiInsights(insightsResponse.data.insights);
      }
    } catch (insightsError) {
      console.log('Failed to refresh insights:', insightsError);
    }
  };

  // Listen for profile updates from other pages
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'profile_updated') {
        refreshInsights();
        // Remove the flag
        localStorage.removeItem('profile_updated');
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);


  // Get BMI category
  const getBMICategory = (bmi: number, lang: string) => {
    if (bmi < 18.5) return t('underweight', lang);
    if (bmi < 25) return t('normal', lang);
    if (bmi < 30) return t('overweight', lang);
    return t('obese', lang);
  };

  // Get wellness score color
  const getWellnessScoreColor = (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
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

  if (!analyticsData || !profileData) {
    return (
      <Box p={4}>
        <Alert status="info">
          <AlertIcon />
          No health data available. Please complete your health profile first.
        </Alert>
        <Box mt={4}>
          <Button colorScheme="blue" as="a" href="/profile">Create your health profile</Button>
        </Box>
      </Box>
    );
  }

  const bmiCategory = getBMICategory(analyticsData.current_bmi, language);
  const wellnessScoreColor = getWellnessScoreColor(analyticsData.current_wellness_score);

  return (
    <Box p={4}>
      <Heading mb={6}>{t('dashboard', language)}</Heading>
      
      {/* 2FA Security Reminder */}
      {user && !user.two_factor_enabled && (
        <Alert status="info" borderRadius="md" mb={6} border="1px" borderColor="blue.200">
          <AlertIcon />
          <Box flex="1">
            <Text fontSize="sm" color="blue.700">
              <strong>🔒 Security:</strong> Consider enabling 2FA for enhanced account protection
            </Text>
          </Box>
          <Button size="xs" colorScheme="blue" variant="outline" as="a" href="/settings">
            Enable 2FA
          </Button>
        </Alert>
      )}
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('wellnessScore', language)}</StatLabel>
              <StatNumber color={`${wellnessScoreColor}.500`}>
                {analyticsData.current_wellness_score.toFixed(1)}
              </StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                {analyticsData.progress_towards_goal.toFixed(1)}% {t('towardsGoal', language)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('bmi', language)}</StatLabel>
              <StatNumber>{analyticsData.current_bmi.toFixed(1)}</StatNumber>
              <StatHelpText>{bmiCategory}</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('currentWeight', language)}</StatLabel>
              <StatNumber>
                {profileData.weight ? convertWeightForDisplay(profileData.weight, measurementSystem).toFixed(1) : 'N/A'} {getWeightUnit(measurementSystem)}
              </StatNumber>
              <StatHelpText>
                {profileData.target_weight && (
                  <>
                    <StatArrow type={profileData.weight > profileData.target_weight ? "decrease" : "increase"} />
                    {t('targetWeight', language)}: {convertWeightForDisplay(profileData.target_weight, measurementSystem).toFixed(1)} {getWeightUnit(measurementSystem)}
                  </>
                )}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('weeklyActivity', language)}</StatLabel>
              <StatNumber>{analyticsData.activity_summary.activity_count}</StatNumber>
              <StatHelpText>
                {analyticsData.activity_summary.total_duration} {t('minTotal', language)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
        <GridItem>
          <WeightProgressCard
            currentWeight={profileData?.weight || 0}
            targetWeight={profileData?.target_weight || 0}
            weightTrend={analyticsData?.weight_trend || []}
            measurementSystem={measurementSystem}
          />
        </GridItem>

        <GridItem>
          <Card>
            <CardHeader>
              <Heading size="md">{t('activitySummary', language)}</Heading>
            </CardHeader>
            <CardBody>
              <Stack spacing={4}>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('totalActivities', language)}</Text>
                  <Text fontSize="2xl">{analyticsData.activity_summary.activity_count}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('totalDuration', language)}</Text>
                  <Text fontSize="2xl">{analyticsData.activity_summary.total_duration} min</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('averageDuration', language)}</Text>
                  <Text fontSize="2xl">{analyticsData.activity_summary.average_duration.toFixed(0)} min</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('activityTypes', language)}</Text>
                  <Text fontSize="sm">
                    {analyticsData.activity_summary.activity_types.join(', ') || t('noneRecorded', language)}
                  </Text>
                </Box>
              </Stack>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>

      {/* AI Health Recommendations Section */}
      {aiInsights && (
        <Box mt={8}>
          <Heading size="lg" mb={6} color="blue.600">
            🤖 {t('personalizedHealthInsights', language)}
          </Heading>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {/* Health Status Analysis */}
            <Card>
              <CardHeader>
                <Heading size="md" color="blue.600">{t('healthStatus', language)}</Heading>
              </CardHeader>
              <CardBody>
                <Text>{aiInsights.status_analysis}</Text>
              </CardBody>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <Heading size="md" color="green.600">{t('recommendations', language)}</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="stretch" spacing={2}>
                  {aiInsights.recommendations.map((rec, index) => (
                    <Box key={index} p={3} bg="green.50" borderRadius="md" borderLeft="4px" borderColor="green.400">
                      <Text fontSize="sm">{rec}</Text>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>

            {/* Strengths */}
            <Card>
              <CardHeader>
                <Heading size="md" color="purple.600">{t('yourStrengths', language)}</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="stretch" spacing={2}>
                  {aiInsights.strengths.map((strength, index) => (
                    <Box key={index} p={3} bg="purple.50" borderRadius="md" borderLeft="4px" borderColor="purple.400">
                      <Text fontSize="sm">✅ {strength}</Text>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>

            {/* Areas for Improvement */}
            <Card>
              <CardHeader>
                <Heading size="md" color="orange.600">{t('focusAreas', language)}</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="stretch" spacing={2}>
                  {aiInsights.improvements.map((improvement, index) => (
                    <Box key={index} p={3} bg="orange.50" borderRadius="md" borderLeft="4px" borderColor="orange.400">
                      <Text fontSize="sm">🎯 {improvement}</Text>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>
        </Box>
      )}

      {/* Activity Logging Modal */}
      <ActivityLogModal
        isOpen={isActivityModalOpen}
        onClose={onActivityModalClose}
        onActivityLogged={() => {
          // Refresh data when activity is logged
          window.location.reload();
        }}
      />
    </Box>
  );
};

export default Dashboard; 