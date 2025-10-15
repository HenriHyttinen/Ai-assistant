import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Select,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  Progress,
  VStack,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
} from '@chakra-ui/react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { useState, useEffect } from 'react';
import { analytics, goals } from '../services/api';
import { useApp } from '../contexts/AppContext';
import { convertWeightForDisplay, getWeightUnit } from '../utils/unitConversion';

// Inline translation function to avoid module loading issues
const translations = {
  en: {
    analytics: 'Analytics',
    last30Days: 'Last 30 days',
    last7Days: 'Last 7 days',
    last90Days: 'Last 90 days',
    lastYear: 'Last year',
    weightProgress: 'Weight Progress',
    weeklyActivity: 'Weekly Activity',
    goalProgress: 'Goal Progress',
    keyMetrics: 'Key Metrics',
    readyToTrack: 'Ready to track your weight journey?',
    startLogging: 'Start logging your weight to see meaningful trends and stay motivated toward your health goals',
    logYourWeight: 'Log Your Weight',
    currentWeight: 'Current Weight',
    recordedOn: 'Recorded on',
    startYourWeightJourney: 'Start Your Weight Journey',
    addEntries: 'Add 2-3 more entries to see trends',
    trackDaily: 'Track daily or weekly for best insights',
    setWeightGoal: 'Set a weight goal to track progress',
    addWeightEntry: 'Add Weight Entry',
    setWeightGoalBtn: 'Set Weight Goal',
    everyJourney: 'Every journey begins with a single step!',
    readyToTrackActivities: 'Ready to track your activities?',
    logDailyActivities: 'Log your daily activities to see your weekly progress and build healthy habits',
    logTodaysActivity: 'Log Today\'s Activity',
    recommended: 'Recommended: 30+ minutes of activity daily',
    totalGoals: 'Total Goals',
    completed: 'Completed',
    inProgress: 'In Progress',
    averageProgress: 'Average Progress',
    yourGoals: 'Your Goals',
    currentBMI: 'Current BMI',
    wellnessScore: 'Wellness Score',
    needsImprovement: 'Needs Improvement',
    excellent: 'Excellent',
    good: 'Good',
    underweight: 'Underweight',
    normal: 'Normal',
    overweight: 'Overweight',
    obese: 'Obese',
    keepGoing: 'Keep going!',
    goodProgress: 'Good progress',
    almostThere: 'Almost there!',
    goodActivity: 'Good activity',
    veryActive: 'Very active!',
    addMoreActivities: 'Add more activities',
  },
  es: {
    analytics: 'Analíticas',
    last30Days: 'Últimos 30 días',
    last7Days: 'Últimos 7 días',
    last90Days: 'Últimos 90 días',
    lastYear: 'Último año',
    weightProgress: 'Progreso de Peso',
    weeklyActivity: 'Actividad Semanal',
    goalProgress: 'Progreso de Objetivos',
    keyMetrics: 'Métricas Clave',
    readyToTrack: '¿Listo para rastrear tu viaje de peso?',
    startLogging: 'Comienza a registrar tu peso para ver tendencias significativas y mantenerte motivado hacia tus objetivos de salud',
    logYourWeight: 'Registra tu Peso',
    currentWeight: 'Peso Actual',
    recordedOn: 'Registrado el',
    startYourWeightJourney: 'Comienza tu Viaje de Peso',
    addEntries: 'Agrega 2-3 entradas más para ver tendencias',
    trackDaily: 'Registra diaria o semanalmente para mejores perspectivas',
    setWeightGoal: 'Establece una meta de peso para rastrear el progreso',
    addWeightEntry: 'Agregar Entrada de Peso',
    setWeightGoalBtn: 'Establecer Meta de Peso',
    everyJourney: '¡Cada viaje comienza con un solo paso!',
    readyToTrackActivities: '¿Listo para rastrear tus actividades?',
    logDailyActivities: 'Registra tus actividades diarias para ver tu progreso semanal y construir hábitos saludables',
    logTodaysActivity: 'Registrar Actividad de Hoy',
    recommended: 'Recomendado: 30+ minutos de actividad diaria',
    totalGoals: 'Total de Objetivos',
    completed: 'Completados',
    inProgress: 'En Progreso',
    averageProgress: 'Progreso Promedio',
    yourGoals: 'Tus Objetivos',
    currentBMI: 'IMC Actual',
    wellnessScore: 'Puntuación de Bienestar',
    needsImprovement: 'Necesita Mejora',
    excellent: 'Excelente',
    good: 'Bueno',
    underweight: 'Bajo Peso',
    normal: 'Normal',
    overweight: 'Sobrepeso',
    obese: 'Obeso',
    keepGoing: '¡Sigue adelante!',
    goodProgress: 'Buen progreso',
    almostThere: '¡Casi ahí!',
    goodActivity: 'Buena actividad',
    veryActive: '¡Muy activo!',
    addMoreActivities: 'Agregar más actividades',
  },
  fr: {
    analytics: 'Analytiques',
    last30Days: '30 derniers jours',
    last7Days: '7 derniers jours',
    last90Days: '90 derniers jours',
    lastYear: 'Dernière année',
    weightProgress: 'Progrès de Poids',
    weeklyActivity: 'Activité Hebdomadaire',
    goalProgress: 'Progrès des Objectifs',
    keyMetrics: 'Métriques Clés',
    readyToTrack: 'Prêt à suivre votre voyage de poids ?',
    startLogging: 'Commencez à enregistrer votre poids pour voir des tendances significatives et rester motivé vers vos objectifs de santé',
    logYourWeight: 'Enregistrer votre Poids',
    currentWeight: 'Poids Actuel',
    recordedOn: 'Enregistré le',
    startYourWeightJourney: 'Commencez votre Voyage de Poids',
    addEntries: 'Ajoutez 2-3 entrées de plus pour voir les tendances',
    trackDaily: 'Suivez quotidiennement ou hebdomadairement pour de meilleures perspectives',
    setWeightGoal: 'Définissez un objectif de poids pour suivre les progrès',
    addWeightEntry: 'Ajouter Entrée de Poids',
    setWeightGoalBtn: 'Définir Objectif de Poids',
    everyJourney: 'Chaque voyage commence par un seul pas !',
    readyToTrackActivities: 'Prêt à suivre vos activités ?',
    logDailyActivities: 'Enregistrez vos activités quotidiennes pour voir vos progrès hebdomadaires et construire des habitudes saines',
    logTodaysActivity: 'Enregistrer l\'Activité d\'Aujourd\'hui',
    recommended: 'Recommandé : 30+ minutes d\'activité quotidienne',
    totalGoals: 'Total des Objectifs',
    completed: 'Terminés',
    inProgress: 'En Cours',
    averageProgress: 'Progrès Moyen',
    yourGoals: 'Vos Objectifs',
    currentBMI: 'IMC Actuel',
    wellnessScore: 'Score de Bien-être',
    needsImprovement: 'Nécessite Amélioration',
    excellent: 'Excellent',
    good: 'Bon',
    underweight: 'Insuffisance Pondérale',
    normal: 'Normal',
    overweight: 'Surpoids',
    obese: 'Obèse',
    keepGoing: 'Continuez !',
    goodProgress: 'Bon progrès',
    almostThere: 'Presque là !',
    goodActivity: 'Bonne activité',
    veryActive: 'Très actif !',
    addMoreActivities: 'Ajouter plus d\'activités',
  },
  de: {
    analytics: 'Analytik',
    last30Days: 'Letzte 30 Tage',
    last7Days: 'Letzte 7 Tage',
    last90Days: 'Letzte 90 Tage',
    lastYear: 'Letztes Jahr',
    weightProgress: 'Gewichtsfortschritt',
    weeklyActivity: 'Wöchentliche Aktivität',
    goalProgress: 'Ziel-Fortschritt',
    keyMetrics: 'Schlüsselmetriken',
    readyToTrack: 'Bereit, Ihre Gewichtsreise zu verfolgen?',
    startLogging: 'Beginnen Sie mit der Aufzeichnung Ihres Gewichts, um bedeutungsvolle Trends zu sehen und motiviert zu bleiben für Ihre Gesundheitsziele',
    logYourWeight: 'Ihr Gewicht Aufzeichnen',
    currentWeight: 'Aktuelles Gewicht',
    recordedOn: 'Aufgezeichnet am',
    startYourWeightJourney: 'Beginnen Sie Ihre Gewichtsreise',
    addEntries: 'Fügen Sie 2-3 weitere Einträge hinzu, um Trends zu sehen',
    trackDaily: 'Verfolgen Sie täglich oder wöchentlich für beste Einblicke',
    setWeightGoal: 'Setzen Sie ein Gewichtsziel, um den Fortschritt zu verfolgen',
    addWeightEntry: 'Gewichtseintrag Hinzufügen',
    setWeightGoalBtn: 'Gewichtsziel Setzen',
    everyJourney: 'Jede Reise beginnt mit einem einzigen Schritt!',
    readyToTrackActivities: 'Bereit, Ihre Aktivitäten zu verfolgen?',
    logDailyActivities: 'Zeichnen Sie Ihre täglichen Aktivitäten auf, um Ihren wöchentlichen Fortschritt zu sehen und gesunde Gewohnheiten aufzubauen',
    logTodaysActivity: 'Heutige Aktivität Aufzeichnen',
    recommended: 'Empfohlen: 30+ Minuten Aktivität täglich',
    totalGoals: 'Gesamte Ziele',
    completed: 'Abgeschlossen',
    inProgress: 'In Bearbeitung',
    averageProgress: 'Durchschnittlicher Fortschritt',
    yourGoals: 'Ihre Ziele',
    currentBMI: 'Aktueller BMI',
    wellnessScore: 'Wohlfühl-Score',
    needsImprovement: 'Benötigt Verbesserung',
    excellent: 'Ausgezeichnet',
    good: 'Gut',
    underweight: 'Untergewicht',
    normal: 'Normal',
    overweight: 'Übergewicht',
    obese: 'Fettleibig',
    keepGoing: 'Weiter so!',
    goodProgress: 'Guter Fortschritt',
    almostThere: 'Fast da!',
    goodActivity: 'Gute Aktivität',
    veryActive: 'Sehr aktiv!',
    addMoreActivities: 'Mehr Aktivitäten hinzufügen',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

// Helper functions for BMI and wellness score statuses
const getBMIStatus = (bmi: number, lang: string) => {
  if (bmi < 18.5) return t('underweight', lang);
  if (bmi < 25) return t('normal', lang);
  if (bmi < 30) return t('overweight', lang);
  return t('obese', lang);
};

const getWellnessStatus = (score: number, lang: string) => {
  if (score >= 80) return t('excellent', lang);
  if (score >= 60) return t('good', lang);
  return t('needsImprovement', lang);
};

const getProgressStatus = (progress: number, lang: string) => {
  if (progress >= 80) return t('almostThere', lang);
  if (progress >= 50) return t('goodProgress', lang);
  return t('keepGoing', lang);
};

const getActivityStatus = (count: number, lang: string) => {
  if (count >= 5) return t('veryActive', lang);
  if (count >= 3) return t('goodActivity', lang);
  return t('addMoreActivities', lang);
};

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

interface Goal {
  id: string;
  title: string;
  target: string;
  progress: number;
  deadline: string;
  status: 'completed' | 'in_progress' | 'not_started' | 'failed';
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'green';
    case 'in_progress':
      return 'blue';
    case 'not_started':
      return 'gray';
    case 'failed':
      return 'red';
    default:
      return 'gray';
  }
};

const Analytics = () => {
  const { measurementSystem, language } = useApp();
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [goalsList, setGoalsList] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('30');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch analytics data
        const analyticsResponse = await analytics.getAnalytics();
        setAnalyticsData(analyticsResponse.data);
        
        // Fetch goals data
        const goalsResponse = await goals.getGoals();
        setGoalsList(goalsResponse.data);
        
      } catch (err: any) {
        if (err?.response?.status === 404) {
          // No profile or no metrics yet
          setError(null);
          setAnalyticsData(null);
        } else {
          setError(err.response?.data?.detail || 'Failed to load analytics data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange, measurementSystem, language]);

  // Prepare weight progress data
  const prepareWeightProgressData = () => {
    if (!analyticsData?.weight_trend) return [];
    
    return analyticsData.weight_trend.map((weight, index) => ({
      date: `Day ${index + 1}`,
      weight: convertWeightForDisplay(weight, measurementSystem),
    }));
  };

  // Prepare activity data (mock weekly data for now)
  const prepareActivityData = () => {
    if (!analyticsData?.activity_summary) return [];
    
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const avgDuration = analyticsData.activity_summary.average_duration;
    
    return days.map(day => ({
      day,
      minutes: Math.round(avgDuration * (0.5 + Math.random() * 1.5)), // Simulate daily variation
    }));
  };

  // Calculate goal statistics
  const goalStats = {
    total: goalsList.length,
    completed: goalsList.filter(g => g.status === 'completed').length,
    inProgress: goalsList.filter(g => g.status === 'in_progress').length,
    notStarted: goalsList.filter(g => g.status === 'not_started').length,
    averageProgress: goalsList.length > 0 ? Math.round(goalsList.reduce((sum, goal) => sum + goal.progress, 0) / goalsList.length) : 0,
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

  if (!analyticsData) {
    return (
      <Box p={4}>
        <Alert status="info">
          <AlertIcon />
          No analytics data available. Please complete your health profile first.
        </Alert>
        <Box mt={4}>
          <Button colorScheme="blue" as="a" href="/profile">Create your health profile</Button>
        </Box>
      </Box>
    );
  }

  const weightProgressData = prepareWeightProgressData();
  const activityData = prepareActivityData();

  return (
    <Box p={4}>
      <HStack justify="space-between" mb={6}>
        <Heading>{t('analytics', language)}</Heading>
        <Select 
          placeholder="Select time range" 
          w="200px" 
          value={timeRange}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTimeRange(e.target.value)}
        >
          <option value="7">{t('last7Days', language)}</option>
          <option value="30">{t('last30Days', language)}</option>
          <option value="90">{t('last90Days', language)}</option>
          <option value="365">{t('lastYear', language)}</option>
        </Select>
      </HStack>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        <Card>
          <CardHeader>
            <Heading size="md">{t('weightProgress', language)}</Heading>
          </CardHeader>
          <CardBody>
            {weightProgressData.length === 0 ? (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4} fontSize="lg">
                  📊 {t('readyToTrack', language)}
                </Text>
                <Text color="gray.600" mb={6} fontSize="sm">
                  {t('startLogging', language)}
                </Text>
                <Button colorScheme="blue" as="a" href="/profile">
                  {t('logYourWeight', language)}
                </Button>
              </Box>
            ) : weightProgressData.length === 1 ? (
              <VStack spacing={6} align="stretch">
                {/* Current Weight Display */}
                <Box textAlign="center" py={4} bg="gray.50" borderRadius="md">
                  <Text color="blue.600" fontSize="3xl" fontWeight="bold">
                    {convertWeightForDisplay(weightProgressData[0].weight, measurementSystem).toFixed(1)} {getWeightUnit(measurementSystem)}
                  </Text>
                  <Text color="gray.600" fontSize="md" mb={2}>
                    {t('currentWeight', language)}
                  </Text>
                  <Text color="gray.500" fontSize="sm">
                    {t('recordedOn', language)} {weightProgressData[0].date}
                  </Text>
                </Box>

                {/* Progress Insights */}
                <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                  <Text color="blue.800" fontWeight="bold" mb={3} fontSize="lg">
                    📊 {t('startYourWeightJourney', language)}
                  </Text>
                  <VStack spacing={3} align="stretch">
                    <Text color="blue.700" fontSize="sm">
                      <strong>Next Steps:</strong>
                    </Text>
                    <Text color="blue.600" fontSize="sm">
                      • {t('addEntries', language)}
                    </Text>
                    <Text color="blue.600" fontSize="sm">
                      • {t('trackDaily', language)}
                    </Text>
                    <Text color="blue.600" fontSize="sm">
                      • {t('setWeightGoal', language)}
                    </Text>
                  </VStack>
                </Box>

                {/* Action Buttons */}
                <HStack spacing={3} justify="center">
                  <Button colorScheme="blue" size="sm" as="a" href="/profile">
                    {t('addWeightEntry', language)}
                  </Button>
                  <Button colorScheme="green" variant="outline" size="sm" as="a" href="/goals">
                    {t('setWeightGoalBtn', language)}
                  </Button>
                </HStack>

                {/* Motivational Message */}
                <Box p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
                  <Text color="green.800" fontSize="sm" textAlign="center">
                    💪 {t('everyJourney', language)}
                  </Text>
                </Box>
              </VStack>
            ) : (
              <Box h="300px">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weightProgressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="weight"
                      stroke="#0967D2"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('weeklyActivity', language)}</Heading>
          </CardHeader>
          <CardBody>
            {activityData.every(day => day.minutes === 0) ? (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4} fontSize="lg">
                  🏃‍♂️ {t('readyToTrackActivities', language)}
                </Text>
                <Text color="gray.600" mb={6} fontSize="sm">
                  {t('logDailyActivities', language)}
                </Text>
                <VStack spacing={3}>
                  <Button colorScheme="green" as="a" href="/profile">
                    {t('logTodaysActivity', language)}
                  </Button>
                  <Text color="gray.500" fontSize="xs">
                    {t('recommended', language)}
                  </Text>
                </VStack>
              </Box>
            ) : (
              <VStack spacing={4} align="stretch">
                <Box h="250px">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={activityData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="minutes" fill="#0967D2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
                <Box p={3} bg="green.50" borderRadius="md">
                  <HStack justify="space-between">
                    <Text color="green.800" fontWeight="medium">
                      Weekly Total: {activityData.reduce((sum, day) => sum + day.minutes, 0)} minutes
                    </Text>
                    <Text color="green.600" fontSize="sm">
                      Goal: 150+ minutes
                    </Text>
                  </HStack>
                </Box>
              </VStack>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('goalProgress', language)}</Heading>
          </CardHeader>
          <CardBody>
            {goalsList.length === 0 ? (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4}>No goals set yet</Text>
                <Button colorScheme="blue" as="a" href="/goals">Create your first goal</Button>
              </Box>
            ) : (
              <VStack spacing={6} align="stretch">
                {/* Goal Statistics */}
                <SimpleGrid columns={2} spacing={4}>
                  <Stat>
                    <StatLabel>{t('totalGoals', language)}</StatLabel>
                    <StatNumber>{goalStats.total}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>{t('completed', language)}</StatLabel>
                    <StatNumber color="green.500">{goalStats.completed}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>{t('inProgress', language)}</StatLabel>
                    <StatNumber color="blue.500">{goalStats.inProgress}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>{t('averageProgress', language)}</StatLabel>
                    <StatNumber>{goalStats.averageProgress}%</StatNumber>
                  </Stat>
                </SimpleGrid>

                {/* Individual Goal Progress */}
                <Box>
                  <Text fontWeight="bold" mb={3}>{t('yourGoals', language)}</Text>
                  <VStack spacing={3} align="stretch">
                    {goalsList.slice(0, 5).map((goal) => (
                      <Box key={goal.id} p={3} border="1px" borderColor="gray.200" borderRadius="md">
                        <HStack justify="space-between" mb={2}>
                          <Text fontWeight="medium">{goal.title}</Text>
                          <Badge colorScheme={getStatusColor(goal.status)}>
                            {goal.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </HStack>
                        <Text fontSize="sm" color="gray.600" mb={2}>{goal.target}</Text>
                        <Progress 
                          value={goal.progress} 
                          colorScheme={goal.progress === 100 ? 'green' : 'blue'} 
                          size="sm"
                        />
                        <Text fontSize="xs" color="gray.500" mt={1}>
                          {goal.progress}% complete
                        </Text>
                      </Box>
                    ))}
                    {goalsList.length > 5 && (
                      <Text fontSize="sm" color="gray.500" textAlign="center">
                        +{goalsList.length - 5} more goals
                      </Text>
                    )}
                  </VStack>
                </Box>
              </VStack>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('keyMetrics', language)}</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={2} spacing={4}>
              <Box p={3} border="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="bold" color="gray.500" mb={1}>
                  {t('currentBMI', language)}
                </Text>
                <Text fontSize="2xl" color={analyticsData.current_bmi < 25 ? 'green.500' : analyticsData.current_bmi < 30 ? 'orange.500' : 'red.500'}>
                  {analyticsData.current_bmi.toFixed(1)}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {getBMIStatus(analyticsData.current_bmi, language)}
                </Text>
              </Box>
              <Box p={3} border="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="bold" color="gray.500" mb={1}>
                  {t('wellnessScore', language)}
                </Text>
                <Text fontSize="2xl" color={analyticsData.current_wellness_score >= 80 ? 'green.500' : analyticsData.current_wellness_score >= 60 ? 'orange.500' : 'red.500'}>
                  {analyticsData.current_wellness_score.toFixed(0)}/100
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {getWellnessStatus(analyticsData.current_wellness_score, language)}
                </Text>
              </Box>
              <Box p={3} border="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="bold" color="gray.500" mb={1}>
                  {t('goalProgress', language)}
                </Text>
                <Text fontSize="2xl" color={analyticsData.progress_towards_goal >= 80 ? 'green.500' : analyticsData.progress_towards_goal >= 50 ? 'orange.500' : 'blue.500'}>
                  {analyticsData.progress_towards_goal.toFixed(0)}%
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {getProgressStatus(analyticsData.progress_towards_goal, language)}
                </Text>
              </Box>
              <Box p={3} border="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="bold" color="gray.500" mb={1}>
                  {t('weeklyActivity', language)}
                </Text>
                <Text fontSize="2xl" color={analyticsData.activity_summary.activity_count >= 5 ? 'green.500' : analyticsData.activity_summary.activity_count >= 3 ? 'orange.500' : 'blue.500'}>
                  {analyticsData.activity_summary.activity_count}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  {getActivityStatus(analyticsData.activity_summary.activity_count, language)}
                </Text>
              </Box>
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
};

export default Analytics; 