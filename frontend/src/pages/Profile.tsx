import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Select,
  Button,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  SimpleGrid,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Textarea,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import { healthProfile, analytics } from '../services/api';
import ConsentModal from '../components/ConsentModal';
import NutritionPreferencesSummary from '../components/profile/NutritionPreferencesSummary';
import { getErrorMessage } from '../utils/errorUtils';
import { 
  convertWeightForDisplay, 
  convertWeightToKg, 
  convertHeightForDisplay, 
  convertHeightToCm,
  getWeightUnit,
  getHeightUnit,
  getTargetWeightUnit
} from '../utils/unitConversion';
import { useApp } from '../contexts/AppContext';

// Translation object
const translations = {
  en: {
    healthProfile: 'Health Profile',
    personalInfo: 'Personal Information',
    age: 'Age',
    gender: 'Gender',
    male: 'Male',
    female: 'Female',
    other: 'Other',
    height: 'Height',
    weight: 'Weight',
    targetWeight: 'Target Weight',
    lifestyle: 'Lifestyle',
    occupationType: 'Occupation Type',
    sedentary: 'Sedentary',
    lightActivity: 'Light Activity',
    moderateActivity: 'Moderate Activity',
    heavyActivity: 'Heavy Activity',
    activityLevel: 'Activity Level',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    veryHigh: 'Very High',
    fitnessGoal: 'Primary Goal',
    weightLoss: 'Weight Loss',
    muscleGain: 'Muscle Gain',
    endurance: 'Endurance',
    generalFitness: 'General Fitness',
    strength: 'Strength',
    weeklyActivityFrequency: 'Weekly Activity Frequency',
    days: 'days',
    fitnessAssessment: 'Fitness Assessment',
    currentEnduranceMinutes: 'Current Endurance (minutes)',
    pushupCount: 'Push-up Count',
    squatCount: 'Squat Count',
    enduranceLevel: 'Endurance Level',
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced',
    dietaryPreferences: 'Dietary Preferences',
    dietaryRestrictions: 'Dietary Restrictions',
    vegetarian: 'Vegetarian',
    vegan: 'Vegan',
    glutenFree: 'Gluten-Free',
    dairyFree: 'Dairy-Free',
    keto: 'Keto',
    paleo: 'Paleo',
    mediterranean: 'Mediterranean',
    none: 'None',
    saveProfile: 'Save Profile',
    updateProfile: 'Update Profile',
    loading: 'Loading...',
    saving: 'Saving...',
    profileSaved: 'Profile Saved',
    profileUpdated: 'Profile Updated',
    profileSavedDesc: 'Your health profile has been saved successfully.',
    profileUpdatedDesc: 'Your health profile has been updated successfully.',
    error: 'Error',
    errorDesc: 'An error occurred while saving your profile.',
    required: 'This field is required',
    ageRequired: 'Age is required',
    ageMin: 'Must be at least 13 years old',
    genderRequired: 'Gender is required',
    heightRequired: 'Height is required',
    heightMin: 'Height must be at least 100cm',
    weightRequired: 'Weight is required',
    weightMin: 'Weight must be at least 30kg',
    occupationRequired: 'Occupation type is required',
    activityRequired: 'Activity level is required',
    goalRequired: 'Primary goal is required',
    frequencyRequired: 'Weekly activity frequency is required',
    frequencyRange: 'Must be between 0 and 7',
    enduranceMin: 'Must be 0 or greater',
    pushupMin: 'Must be 0 or greater',
    squatMin: 'Must be 0 or greater',
    noProfileFound: 'No health profile found. Please fill the form below to create one.',
    selectGender: 'Select gender',
    selectOccupationType: 'Select occupation type',
    sedentaryOffice: 'Sedentary (Office work)',
    lightStanding: 'Light (Standing work)',
    moderatePhysical: 'Moderate (Physical work)',
    activeHeavy: 'Active (Heavy physical work)',
    selectActivityLevel: 'Select activity level',
    veryActive: 'Very Active',
    dietaryInformation: 'Dietary Information',
    dietaryPreferencesPlaceholder: 'e.g., vegetarian, vegan, Mediterranean diet, low-carb...',
    dietaryRestrictionsPlaceholder: 'e.g., gluten-free, dairy-free, nut allergies...',
    mealPreferences: 'Meal Preferences',
    mealPreferencesPlaceholder: 'e.g., prefer breakfast, skip lunch, heavy dinner...',
    fitnessGoals: 'Fitness Goals',
    selectPrimaryGoal: 'Select primary goal',
    targetActivityLevel: 'Target Activity Level',
    selectTargetLevel: 'Select target level',
    weeklyActivityFrequencyDays: 'Weekly Activity Frequency (days)',
    exercisePreferences: 'Exercise Preferences',
    preferredExerciseTime: 'Preferred Exercise Time',
    selectPreferredTime: 'Select preferred time',
    morning: 'Morning',
    afternoon: 'Afternoon',
    evening: 'Evening',
    flexible: 'Flexible',
    preferredExerciseEnvironment: 'Preferred Exercise Environment',
    selectEnvironment: 'Select environment',
    home: 'Home',
    gym: 'Gym',
    outdoors: 'Outdoors',
    mixed: 'Mixed',
    exerciseTypes: 'Exercise Types',
    exerciseTypesPlaceholder: 'e.g., cardio, strength training, yoga, swimming...',
    averageSessionDuration: 'Average Session Duration',
    selectDuration: 'Select duration',
    duration15_30: '15-30 minutes',
    duration30_60: '30-60 minutes',
    duration60Plus: '60+ minutes',
    fitnessLevel: 'Fitness Level',
    selectFitnessLevel: 'Select fitness level',
    enduranceLevel1_10: 'Endurance Level (1-10)',
    currentEndurancePlaceholder: 'How long can you run/walk?',
    pushupsMax: 'Push-ups (max)',
    squatsMax: 'Squats (max)',
    strengthIndicators: 'Strength Indicators',
    strengthIndicatorsPlaceholder: 'e.g., can lift 50kg, bench press 80kg...',
    light: 'Light',
    moderate: 'Moderate',
    active: 'Active',
    currentHealthMetrics: 'Current Health Metrics',
    bmi: 'BMI',
    wellnessScore: 'Wellness Score',
    progressTowardsGoal: 'Progress Towards Goal',
    calculating: 'Calculating...',
    notSet: 'Not set',
  },
  de: {
    healthProfile: 'Gesundheitsprofil',
    personalInfo: 'Persönliche Informationen',
    age: 'Alter',
    gender: 'Geschlecht',
    male: 'Männlich',
    female: 'Weiblich',
    other: 'Andere',
    height: 'Größe',
    weight: 'Gewicht',
    targetWeight: 'Zielgewicht',
    lifestyle: 'Lebensstil',
    occupationType: 'Berufstyp',
    sedentary: 'Sitzend',
    lightActivity: 'Leichte Aktivität',
    moderateActivity: 'Mäßige Aktivität',
    heavyActivity: 'Schwere Aktivität',
    activityLevel: 'Aktivitätsniveau',
    low: 'Niedrig',
    medium: 'Mittel',
    high: 'Hoch',
    veryHigh: 'Sehr hoch',
    fitnessGoal: 'Hauptziel',
    weightLoss: 'Gewichtsverlust',
    muscleGain: 'Muskelaufbau',
    endurance: 'Ausdauer',
    generalFitness: 'Allgemeine Fitness',
    strength: 'Kraft',
    weeklyActivityFrequency: 'Wöchentliche Aktivitätshäufigkeit',
    days: 'Tage',
    fitnessAssessment: 'Fitness-Bewertung',
    currentEnduranceMinutes: 'Aktuelle Ausdauer (Minuten)',
    pushupCount: 'Liegestütz-Anzahl',
    squatCount: 'Kniebeugen-Anzahl',
    enduranceLevel: 'Ausdauerniveau',
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte',
    dietaryPreferences: 'Ernährungsvorlieben',
    dietaryRestrictions: 'Ernährungseinschränkungen',
    vegetarian: 'Vegetarisch',
    vegan: 'Vegan',
    glutenFree: 'Glutenfrei',
    dairyFree: 'Laktosefrei',
    keto: 'Keto',
    paleo: 'Paleo',
    mediterranean: 'Mittelmeer',
    none: 'Keine',
    saveProfile: 'Profil Speichern',
    updateProfile: 'Profil Aktualisieren',
    loading: 'Laden...',
    saving: 'Speichern...',
    profileSaved: 'Profil Gespeichert',
    profileUpdated: 'Profil Aktualisiert',
    profileSavedDesc: 'Ihr Gesundheitsprofil wurde erfolgreich gespeichert.',
    profileUpdatedDesc: 'Ihr Gesundheitsprofil wurde erfolgreich aktualisiert.',
    error: 'Fehler',
    errorDesc: 'Ein Fehler ist beim Speichern Ihres Profils aufgetreten.',
    required: 'Dieses Feld ist erforderlich',
    ageRequired: 'Alter ist erforderlich',
    ageMin: 'Muss mindestens 13 Jahre alt sein',
    genderRequired: 'Geschlecht ist erforderlich',
    heightRequired: 'Größe ist erforderlich',
    heightMin: 'Größe muss mindestens 100cm betragen',
    weightRequired: 'Gewicht ist erforderlich',
    weightMin: 'Gewicht muss mindestens 30kg betragen',
    occupationRequired: 'Berufstyp ist erforderlich',
    activityRequired: 'Aktivitätsniveau ist erforderlich',
    goalRequired: 'Hauptziel ist erforderlich',
    frequencyRequired: 'Wöchentliche Aktivitätshäufigkeit ist erforderlich',
    frequencyRange: 'Muss zwischen 0 und 7 liegen',
    enduranceMin: 'Muss 0 oder größer sein',
    pushupMin: 'Muss 0 oder größer sein',
    squatMin: 'Muss 0 oder größer sein',
    noProfileFound: 'Kein Gesundheitsprofil gefunden. Bitte füllen Sie das untenstehende Formular aus, um eines zu erstellen.',
    selectGender: 'Geschlecht auswählen',
    selectOccupationType: 'Berufstyp auswählen',
    sedentaryOffice: 'Sitzend (Büroarbeit)',
    lightStanding: 'Leicht (Stehende Arbeit)',
    moderatePhysical: 'Mäßig (Körperliche Arbeit)',
    activeHeavy: 'Aktiv (Schwere körperliche Arbeit)',
    selectActivityLevel: 'Aktivitätsniveau auswählen',
    veryActive: 'Sehr aktiv',
    dietaryInformation: 'Ernährungsinformationen',
    dietaryPreferencesPlaceholder: 'z.B., vegetarisch, vegan, Mittelmeerdiät, kohlenhydratarm...',
    dietaryRestrictionsPlaceholder: 'z.B., glutenfrei, laktosefrei, Nussallergien...',
    mealPreferences: 'Mahlzeitenvorlieben',
    mealPreferencesPlaceholder: 'z.B., bevorzuge Frühstück, überspringe Mittagessen, schweres Abendessen...',
    fitnessGoals: 'Fitness-Ziele',
    selectPrimaryGoal: 'Hauptziel auswählen',
    targetActivityLevel: 'Ziel-Aktivitätsniveau',
    selectTargetLevel: 'Zielniveau auswählen',
    weeklyActivityFrequencyDays: 'Wöchentliche Aktivitätshäufigkeit (Tage)',
    exercisePreferences: 'Trainingsvorlieben',
    preferredExerciseTime: 'Bevorzugte Trainingszeit',
    selectPreferredTime: 'Bevorzugte Zeit auswählen',
    morning: 'Morgen',
    afternoon: 'Nachmittag',
    evening: 'Abend',
    flexible: 'Flexibel',
    preferredExerciseEnvironment: 'Bevorzugte Trainingsumgebung',
    selectEnvironment: 'Umgebung auswählen',
    home: 'Zuhause',
    gym: 'Fitnessstudio',
    outdoors: 'Draußen',
    mixed: 'Gemischt',
    exerciseTypes: 'Trainingsarten',
    exerciseTypesPlaceholder: 'z.B., Cardio, Krafttraining, Yoga, Schwimmen...',
    averageSessionDuration: 'Durchschnittliche Trainingsdauer',
    selectDuration: 'Dauer auswählen',
    duration15_30: '15-30 Minuten',
    duration30_60: '30-60 Minuten',
    duration60Plus: '60+ Minuten',
    fitnessLevel: 'Fitnessniveau',
    selectFitnessLevel: 'Fitnessniveau auswählen',
    enduranceLevel1_10: 'Ausdauerniveau (1-10)',
    currentEndurancePlaceholder: 'Wie lange können Sie laufen/gehen?',
    pushupsMax: 'Liegestütze (max)',
    squatsMax: 'Kniebeugen (max)',
    strengthIndicators: 'Kraftindikatoren',
    strengthIndicatorsPlaceholder: 'z.B., kann 50kg heben, Bankdrücken 80kg...',
    light: 'Leicht',
    moderate: 'Mäßig',
    active: 'Aktiv',
    currentHealthMetrics: 'Aktuelle Gesundheitsmetriken',
    bmi: 'BMI',
    wellnessScore: 'Wohlfühl-Score',
    progressTowardsGoal: 'Fortschritt zum Ziel',
    calculating: 'Berechne...',
    notSet: 'Nicht festgelegt',
  },
  es: {
    healthProfile: 'Perfil de Salud',
    personalInfo: 'Información Personal',
    age: 'Edad',
    gender: 'Género',
    male: 'Masculino',
    female: 'Femenino',
    other: 'Otro',
    height: 'Altura',
    weight: 'Peso',
    targetWeight: 'Peso Objetivo',
    lifestyle: 'Estilo de Vida',
    occupationType: 'Tipo de Ocupación',
    sedentary: 'Sedentario',
    lightActivity: 'Actividad Ligera',
    moderateActivity: 'Actividad Moderada',
    heavyActivity: 'Actividad Intensa',
    activityLevel: 'Nivel de Actividad',
    low: 'Bajo',
    medium: 'Medio',
    high: 'Alto',
    veryHigh: 'Muy Alto',
    fitnessGoal: 'Objetivo Principal',
    weightLoss: 'Pérdida de Peso',
    muscleGain: 'Ganancia de Músculo',
    endurance: 'Resistencia',
    generalFitness: 'Fitness General',
    strength: 'Fuerza',
    weeklyActivityFrequency: 'Frecuencia de Actividad Semanal',
    days: 'días',
    fitnessAssessment: 'Evaluación de Fitness',
    currentEnduranceMinutes: 'Resistencia Actual (minutos)',
    pushupCount: 'Cantidad de Flexiones',
    squatCount: 'Cantidad de Sentadillas',
    enduranceLevel: 'Nivel de Resistencia',
    beginner: 'Principiante',
    intermediate: 'Intermedio',
    advanced: 'Avanzado',
    dietaryPreferences: 'Preferencias Alimentarias',
    dietaryRestrictions: 'Restricciones Alimentarias',
    vegetarian: 'Vegetariano',
    vegan: 'Vegano',
    glutenFree: 'Sin Gluten',
    dairyFree: 'Sin Lácteos',
    keto: 'Keto',
    paleo: 'Paleo',
    mediterranean: 'Mediterráneo',
    none: 'Ninguna',
    saveProfile: 'Guardar Perfil',
    updateProfile: 'Actualizar Perfil',
    loading: 'Cargando...',
    saving: 'Guardando...',
    profileSaved: 'Perfil Guardado',
    profileUpdated: 'Perfil Actualizado',
    profileSavedDesc: 'Su perfil de salud ha sido guardado exitosamente.',
    profileUpdatedDesc: 'Su perfil de salud ha sido actualizado exitosamente.',
    error: 'Error',
    errorDesc: 'Ocurrió un error al guardar su perfil.',
    required: 'Este campo es requerido',
    ageRequired: 'La edad es requerida',
    ageMin: 'Debe tener al menos 13 años',
    genderRequired: 'El género es requerido',
    heightRequired: 'La altura es requerida',
    heightMin: 'La altura debe ser al menos 100cm',
    weightRequired: 'El peso es requerido',
    weightMin: 'El peso debe ser al menos 30kg',
    occupationRequired: 'El tipo de ocupación es requerido',
    activityRequired: 'El nivel de actividad es requerido',
    goalRequired: 'El objetivo principal es requerido',
    frequencyRequired: 'La frecuencia de actividad semanal es requerida',
    frequencyRange: 'Debe estar entre 0 y 7',
    enduranceMin: 'Debe ser 0 o mayor',
    pushupMin: 'Debe ser 0 o mayor',
    squatMin: 'Debe ser 0 o mayor',
    noProfileFound: 'No se encontró perfil de salud. Por favor complete el formulario a continuación para crear uno.',
    selectGender: 'Seleccionar género',
    selectOccupationType: 'Seleccionar tipo de ocupación',
    sedentaryOffice: 'Sedentario (Trabajo de oficina)',
    lightStanding: 'Ligero (Trabajo de pie)',
    moderatePhysical: 'Moderado (Trabajo físico)',
    activeHeavy: 'Activo (Trabajo físico pesado)',
    selectActivityLevel: 'Seleccionar nivel de actividad',
    veryActive: 'Muy Activo',
    dietaryInformation: 'Información Dietética',
    dietaryPreferencesPlaceholder: 'ej., vegetariano, vegano, dieta mediterránea, baja en carbohidratos...',
    dietaryRestrictionsPlaceholder: 'ej., sin gluten, sin lácteos, alergias a frutos secos...',
    mealPreferences: 'Preferencias de Comidas',
    mealPreferencesPlaceholder: 'ej., prefiero desayuno, salto el almuerzo, cena pesada...',
    fitnessGoals: 'Objetivos de Fitness',
    selectPrimaryGoal: 'Seleccionar objetivo principal',
    targetActivityLevel: 'Nivel de Actividad Objetivo',
    selectTargetLevel: 'Seleccionar nivel objetivo',
    weeklyActivityFrequencyDays: 'Frecuencia de Actividad Semanal (días)',
    exercisePreferences: 'Preferencias de Ejercicio',
    preferredExerciseTime: 'Hora Preferida de Ejercicio',
    selectPreferredTime: 'Seleccionar hora preferida',
    morning: 'Mañana',
    afternoon: 'Tarde',
    evening: 'Noche',
    flexible: 'Flexible',
    preferredExerciseEnvironment: 'Entorno de Ejercicio Preferido',
    selectEnvironment: 'Seleccionar entorno',
    home: 'Casa',
    gym: 'Gimnasio',
    outdoors: 'Exterior',
    mixed: 'Mixto',
    exerciseTypes: 'Tipos de Ejercicio',
    exerciseTypesPlaceholder: 'ej., cardio, entrenamiento de fuerza, yoga, natación...',
    averageSessionDuration: 'Duración Promedio de Sesión',
    selectDuration: 'Seleccionar duración',
    duration15_30: '15-30 minutos',
    duration30_60: '30-60 minutos',
    duration60Plus: '60+ minutos',
    fitnessLevel: 'Nivel de Fitness',
    selectFitnessLevel: 'Seleccionar nivel de fitness',
    enduranceLevel1_10: 'Nivel de Resistencia (1-10)',
    currentEndurancePlaceholder: '¿Cuánto tiempo puedes correr/caminar?',
    pushupsMax: 'Flexiones (máx)',
    squatsMax: 'Sentadillas (máx)',
    strengthIndicators: 'Indicadores de Fuerza',
    strengthIndicatorsPlaceholder: 'ej., puede levantar 50kg, press de banca 80kg...',
    light: 'Ligero',
    moderate: 'Moderado',
    active: 'Activo',
    currentHealthMetrics: 'Métricas de Salud Actuales',
    bmi: 'IMC',
    wellnessScore: 'Puntuación de Bienestar',
    progressTowardsGoal: 'Progreso Hacia el Objetivo',
    calculating: 'Calculando...',
    notSet: 'No establecido',
  },
  fr: {
    healthProfile: 'Profil de Santé',
    personalInfo: 'Informations Personnelles',
    age: 'Âge',
    gender: 'Genre',
    male: 'Masculin',
    female: 'Féminin',
    other: 'Autre',
    height: 'Taille',
    weight: 'Poids',
    targetWeight: 'Poids Cible',
    lifestyle: 'Mode de Vie',
    occupationType: 'Type d\'Occupation',
    sedentary: 'Sédentaire',
    lightActivity: 'Activité Légère',
    moderateActivity: 'Activité Modérée',
    heavyActivity: 'Activité Intense',
    activityLevel: 'Niveau d\'Activité',
    low: 'Faible',
    medium: 'Moyen',
    high: 'Élevé',
    veryHigh: 'Très Élevé',
    fitnessGoal: 'Objectif Principal',
    weightLoss: 'Perte de Poids',
    muscleGain: 'Prise de Muscle',
    endurance: 'Endurance',
    generalFitness: 'Fitness Général',
    strength: 'Force',
    weeklyActivityFrequency: 'Fréquence d\'Activité Hebdomadaire',
    days: 'jours',
    fitnessAssessment: 'Évaluation de Fitness',
    currentEnduranceMinutes: 'Endurance Actuelle (minutes)',
    pushupCount: 'Nombre de Pompes',
    squatCount: 'Nombre de Squats',
    enduranceLevel: 'Niveau d\'Endurance',
    beginner: 'Débutant',
    intermediate: 'Intermédiaire',
    advanced: 'Avancé',
    dietaryPreferences: 'Préférences Alimentaires',
    dietaryRestrictions: 'Restrictions Alimentaires',
    vegetarian: 'Végétarien',
    vegan: 'Végan',
    glutenFree: 'Sans Gluten',
    dairyFree: 'Sans Laitage',
    keto: 'Keto',
    paleo: 'Paleo',
    mediterranean: 'Méditerranéen',
    none: 'Aucune',
    saveProfile: 'Sauvegarder le Profil',
    updateProfile: 'Mettre à Jour le Profil',
    loading: 'Chargement...',
    saving: 'Sauvegarde...',
    profileSaved: 'Profil Sauvegardé',
    profileUpdated: 'Profil Mis à Jour',
    profileSavedDesc: 'Votre profil de santé a été sauvegardé avec succès.',
    profileUpdatedDesc: 'Votre profil de santé a été mis à jour avec succès.',
    error: 'Erreur',
    errorDesc: 'Une erreur s\'est produite lors de la sauvegarde de votre profil.',
    required: 'Ce champ est requis',
    ageRequired: 'L\'âge est requis',
    ageMin: 'Doit avoir au moins 13 ans',
    genderRequired: 'Le genre est requis',
    heightRequired: 'La taille est requise',
    heightMin: 'La taille doit être d\'au moins 100cm',
    weightRequired: 'Le poids est requis',
    weightMin: 'Le poids doit être d\'au moins 30kg',
    occupationRequired: 'Le type d\'occupation est requis',
    activityRequired: 'Le niveau d\'activité est requis',
    goalRequired: 'L\'objectif principal est requis',
    frequencyRequired: 'La fréquence d\'activité hebdomadaire est requise',
    frequencyRange: 'Doit être entre 0 et 7',
    enduranceMin: 'Doit être 0 ou plus',
    pushupMin: 'Doit être 0 ou plus',
    squatMin: 'Doit être 0 ou plus',
    noProfileFound: 'Aucun profil de santé trouvé. Veuillez remplir le formulaire ci-dessous pour en créer un.',
    selectGender: 'Sélectionner le genre',
    selectOccupationType: 'Sélectionner le type d\'occupation',
    sedentaryOffice: 'Sédentaire (Travail de bureau)',
    lightStanding: 'Léger (Travail debout)',
    moderatePhysical: 'Modéré (Travail physique)',
    activeHeavy: 'Actif (Travail physique intense)',
    selectActivityLevel: 'Sélectionner le niveau d\'activité',
    veryActive: 'Très Actif',
    dietaryInformation: 'Informations Alimentaires',
    dietaryPreferencesPlaceholder: 'ex., végétarien, végan, régime méditerranéen, faible en glucides...',
    dietaryRestrictionsPlaceholder: 'ex., sans gluten, sans produits laitiers, allergies aux noix...',
    mealPreferences: 'Préférences de Repas',
    mealPreferencesPlaceholder: 'ex., préfère le petit-déjeuner, saute le déjeuner, dîner copieux...',
    fitnessGoals: 'Objectifs de Fitness',
    selectPrimaryGoal: 'Sélectionner l\'objectif principal',
    targetActivityLevel: 'Niveau d\'Activité Cible',
    selectTargetLevel: 'Sélectionner le niveau cible',
    weeklyActivityFrequencyDays: 'Fréquence d\'Activité Hebdomadaire (jours)',
    exercisePreferences: 'Préférences d\'Exercice',
    preferredExerciseTime: 'Heure d\'Exercice Préférée',
    selectPreferredTime: 'Sélectionner l\'heure préférée',
    morning: 'Matin',
    afternoon: 'Après-midi',
    evening: 'Soir',
    flexible: 'Flexible',
    preferredExerciseEnvironment: 'Environnement d\'Exercice Préféré',
    selectEnvironment: 'Sélectionner l\'environnement',
    home: 'Maison',
    gym: 'Salle de Sport',
    outdoors: 'Extérieur',
    mixed: 'Mixte',
    exerciseTypes: 'Types d\'Exercice',
    exerciseTypesPlaceholder: 'ex., cardio, musculation, yoga, natation...',
    averageSessionDuration: 'Durée Moyenne de Séance',
    selectDuration: 'Sélectionner la durée',
    duration15_30: '15-30 minutes',
    duration30_60: '30-60 minutes',
    duration60Plus: '60+ minutes',
    fitnessLevel: 'Niveau de Fitness',
    selectFitnessLevel: 'Sélectionner le niveau de fitness',
    enduranceLevel1_10: 'Niveau d\'Endurance (1-10)',
    currentEndurancePlaceholder: 'Combien de temps pouvez-vous courir/marcher ?',
    pushupsMax: 'Pompes (max)',
    squatsMax: 'Squats (max)',
    strengthIndicators: 'Indicateurs de Force',
    strengthIndicatorsPlaceholder: 'ex., peut soulever 50kg, développé couché 80kg...',
    light: 'Léger',
    moderate: 'Modéré',
    active: 'Actif',
    currentHealthMetrics: 'Métriques de Santé Actuelles',
    bmi: 'IMC',
    wellnessScore: 'Score de Bien-être',
    progressTowardsGoal: 'Progrès Vers l\'Objectif',
    calculating: 'Calcul en cours...',
    notSet: 'Non défini',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

function toSafeErrorString(value: any): string {
  if (!value) return 'Unexpected error';
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    const msgs = value
      .map((v) => (typeof v === 'string' ? v : v?.msg || v?.message))
      .filter(Boolean);
    if (msgs.length > 0) return msgs.join(', ');
  }
  if (typeof value === 'object') {
    if (value.msg || value.message) return value.msg || value.message;
    try {
      return JSON.stringify(value);
    } catch {
      return 'Unexpected error';
    }
  }
  return String(value);
}

function prepareNumericSafePayload(values: any): any {
  const numericFields = [
    'age',
    'height',
    'weight',
    'weekly_activity_frequency',
    'current_endurance_minutes',
    'pushup_count',
    'squat_count',
    'endurance_level',
    'target_weight',
  ];
  const payload: any = {};
  Object.entries(values).forEach(([key, value]) => {
    if (value === '' || value === null || typeof value === 'undefined') {
      return;
    }
    if (numericFields.includes(key)) {
      const num = Number(value);
      if (!Number.isNaN(num)) {
        payload[key] = num;
      }
      return;
    }
    payload[key] = value;
  });
  return payload;
}

const createValidationSchema = (language: string) => Yup.object({
  age: Yup.number().required(t('ageRequired', language)).min(13, t('ageMin', language)),
  gender: Yup.string().required(t('genderRequired', language)),
  height: Yup.number().required(t('heightRequired', language)).min(100, t('heightMin', language)),
  weight: Yup.number().required(t('weightRequired', language)).min(30, t('weightMin', language)),
  occupation_type: Yup.string().required(t('occupationRequired', language)),
  activity_level: Yup.string().required(t('activityRequired', language)),
  fitness_goal: Yup.string().required(t('goalRequired', language)),
  weekly_activity_frequency: Yup.number()
    .required(t('frequencyRequired', language))
    .min(0, t('frequencyRange', language))
    .max(7, t('frequencyRange', language)),
  current_endurance_minutes: Yup.number().min(0, t('enduranceMin', language)),
  pushup_count: Yup.number().min(0, t('pushupMin', language)),
  squat_count: Yup.number().min(0, t('squatMin', language)),
});

interface HealthMetrics {
  bmi: number;
  wellness_score: number;
  activity_level: string;
  progress: number;
}

const Profile = () => {
  const toast = useToast();
  const { language } = useApp();
  const [profileData, setProfileData] = useState<any>(null);
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsCreate, setNeedsCreate] = useState(false);
  const [measurementSystem] = useState<'metric' | 'imperial'>('metric');
  const [showConsentModal, setShowConsentModal] = useState(false);

  const handleConsentGiven = () => {
    setShowConsentModal(false);
    // Consent has been given, user can continue using the app
  };

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        
        /*
        try {
          const settingsResponse = await settings.getSettings();
          setMeasurementSystem(settingsResponse.data.measurementSystem);
        } catch (settingsError) {
          // Settings not found, using default metric system
        }
        */
        
        const response = await healthProfile.getProfile();
        setProfileData(response.data);
        
        // Fetch analytics for metrics
        const analyticsResponse = await analytics.getAnalytics();
        const analyticsData = analyticsResponse.data;
        
        setMetrics({
          bmi: analyticsData.current_bmi,
          wellness_score: analyticsData.current_wellness_score,
          activity_level: response.data.activity_level,
          progress: analyticsData.progress_towards_goal,
        });
      } catch (err: any) {
        if (err?.response?.status === 404) {
          setNeedsCreate(true);
          setError(null);
        } else {
          const detail = err?.response?.data?.detail ?? 'Failed to load profile';
          setError(toSafeErrorString(detail));
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);


  const formik = useFormik({
    initialValues: {
      age: profileData?.age || '',
      gender: profileData?.gender || '',
      height: profileData?.height ? convertHeightForDisplay(profileData.height, measurementSystem) : '',
      weight: profileData?.weight ? convertWeightForDisplay(profileData.weight, measurementSystem) : '',
      occupation_type: profileData?.occupation_type || '',
      activity_level: profileData?.activity_level || '',
      fitness_goal: profileData?.fitness_goal || '',
      target_weight: profileData?.target_weight ? convertWeightForDisplay(profileData.target_weight, measurementSystem) : '',
      target_activity_level: profileData?.target_activity_level || '',
      preferred_exercise_time: profileData?.preferred_exercise_time || '',
      preferred_exercise_environment: profileData?.preferred_exercise_environment || '',
      weekly_activity_frequency: profileData?.weekly_activity_frequency || '',
      exercise_types: profileData?.exercise_types || '',
      average_session_duration: profileData?.average_session_duration || '',
      fitness_level: profileData?.fitness_level || '',
      endurance_level: profileData?.endurance_level || '',
      strength_indicators: profileData?.strength_indicators || '',
      current_endurance_minutes: profileData?.current_endurance_minutes || '',
      pushup_count: profileData?.pushup_count || '',
      squat_count: profileData?.squat_count || '',
      dietary_preferences: profileData?.dietary_preferences || '',
      dietary_restrictions: profileData?.dietary_restrictions || '',
      meal_preferences: profileData?.meal_preferences || '',
    },
    validationSchema: createValidationSchema(language),
    enableReinitialize: true,
    onSubmit: async (values: any) => {
      try {
        setSaving(true);
        const payload = prepareNumericSafePayload(values);
        
        // Convert units to metric (kg, cm) for backend storage
        if (payload.weight) {
          payload.weight = convertWeightToKg(payload.weight, measurementSystem);
        }
        if (payload.height) {
          payload.height = convertHeightToCm(payload.height, measurementSystem);
        }
        if (payload.target_weight) {
          payload.target_weight = convertWeightToKg(payload.target_weight, measurementSystem);
        }
        
        if (needsCreate) {
          await healthProfile.createProfile(payload);
          setNeedsCreate(false);
        } else {
          await healthProfile.updateProfile(payload);
        }
        toast({
          title: needsCreate ? t('profileSaved', language) : t('profileUpdated', language),
          description: needsCreate
            ? t('profileSavedDesc', language)
            : t('profileUpdatedDesc', language),
          status: 'success',
          duration: 5000,
          isClosable: true,
        });

        // Trigger insights refresh on dashboard
        localStorage.setItem('profile_updated', 'true');
        
        // Check if this is a new profile creation and show consent modal
        if (needsCreate) {
          setShowConsentModal(true);
        }
        
        // Refresh data
        const response = await healthProfile.getProfile();
        setProfileData(response.data);
        // Refresh analytics metrics after creation/update
        try {
          const analyticsResponse = await analytics.getAnalytics();
          const analyticsData = analyticsResponse.data;
          setMetrics({
            bmi: analyticsData.current_bmi,
            wellness_score: analyticsData.current_wellness_score,
            activity_level: response.data.activity_level,
            progress: analyticsData.progress_towards_goal,
          });
        } catch (_) {
          // ignore analytics failure here
        }
      } catch (err: any) {
        toast({
          title: t('error', language),
          description: toSafeErrorString(err?.response?.data?.detail ?? t('errorDesc', language)),
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setSaving(false);
      }
    },
  });

  const loadNutritionPreferences = async () => {
    try {
      const { supabase } = await import('../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No authentication session found');
      }
      
      const response = await fetch('http://localhost:8000/nutrition/preferences', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        return await response.json();
      } else if (response.status === 404) {
        return null; // No preferences set yet
      } else {
        throw new Error('Failed to load nutrition preferences');
      }
    } catch (error) {
      console.error('Error loading nutrition preferences:', error);
      throw error;
    }
  };

  // Reload form when measurement system changes
  useEffect(() => {
    if (profileData) {
      const convertedValues = {
        ...formik.values,
        height: profileData?.height ? convertHeightForDisplay(profileData.height, measurementSystem) : '',
        weight: profileData?.weight ? convertWeightForDisplay(profileData.weight, measurementSystem) : '',
        target_weight: profileData?.target_weight ? convertWeightForDisplay(profileData.target_weight, measurementSystem) : '',
      };
      
      formik.setValues(convertedValues);
    }
  }, [measurementSystem]);

  useEffect(() => {
    const handleFocus = async () => {
      if (profileData) {
        /*
        try {
          const settingsResponse = await settings.getSettings();
          const newMeasurementSystem = settingsResponse.data.measurementSystem;
          if (newMeasurementSystem !== measurementSystem) {
            setMeasurementSystem(newMeasurementSystem);
          }
        } catch (settingsError) {
          // Settings not found, using current measurement system
        }
        */
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [measurementSystem, profileData]);

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
          {getErrorMessage(error)}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Heading mb={6}>{t('healthProfile', language)}</Heading>
      {needsCreate && (
        <Box mb={6}>
          <Alert status="info">
            <AlertIcon />
            {t('noProfileFound', language)}
          </Alert>
        </Box>
      )}

      <form onSubmit={formik.handleSubmit}>
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Basic Information */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('personalInfo', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl isInvalid={formik.touched.age && formik.errors.age}>
                  <FormLabel>{t('age', language)}</FormLabel>
                  <Input
                    type="number"
                    {...formik.getFieldProps('age')}
                  />
                  {formik.touched.age && formik.errors.age && (
                    <Text color="red.500" fontSize="sm">{formik.errors.age}</Text>
                  )}
                </FormControl>

                <FormControl isInvalid={formik.touched.gender && formik.errors.gender}>
                  <FormLabel>{t('gender', language)}</FormLabel>
                  <Select {...formik.getFieldProps('gender')}>
                    <option value="">{t('selectGender', language)}</option>
                    <option value="male">{t('male', language)}</option>
                    <option value="female">{t('female', language)}</option>
                    <option value="other">{t('other', language)}</option>
                  </Select>
                  {formik.touched.gender && formik.errors.gender && (
                    <Text color="red.500" fontSize="sm">{formik.errors.gender}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl isInvalid={formik.touched.height && formik.errors.height}>
                    <FormLabel>{t('height', language)} ({getHeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('height')}
                    />
                    {formik.touched.height && formik.errors.height && (
                      <Text color="red.500" fontSize="sm">{formik.errors.height}</Text>
                    )}
                  </FormControl>

                  <FormControl isInvalid={formik.touched.weight && formik.errors.weight}>
                    <FormLabel>{t('weight', language)} ({getWeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('weight')}
                    />
                    {formik.touched.weight && formik.errors.weight && (
                      <Text color="red.500" fontSize="sm">{formik.errors.weight}</Text>
                    )}
                  </FormControl>
                </HStack>

                <FormControl isInvalid={formik.touched.occupation_type && formik.errors.occupation_type}>
                  <FormLabel>{t('occupationType', language)}</FormLabel>
                  <Select {...formik.getFieldProps('occupation_type')}>
                    <option value="">{t('selectOccupationType', language)}</option>
                    <option value="sedentary">{t('sedentaryOffice', language)}</option>
                    <option value="light">{t('lightStanding', language)}</option>
                    <option value="moderate">{t('moderatePhysical', language)}</option>
                    <option value="active">{t('activeHeavy', language)}</option>
                  </Select>
                  {formik.touched.occupation_type && formik.errors.occupation_type && (
                    <Text color="red.500" fontSize="sm">{formik.errors.occupation_type}</Text>
                  )}
                </FormControl>

                <FormControl isInvalid={formik.touched.activity_level && formik.errors.activity_level}>
                  <FormLabel>{t('activityLevel', language)}</FormLabel>
                  <Select {...formik.getFieldProps('activity_level')}>
                    <option value="">{t('selectActivityLevel', language)}</option>
                    <option value="sedentary">{t('sedentary', language)}</option>
                    <option value="light">{t('light', language)}</option>
                    <option value="moderate">{t('moderate', language)}</option>
                    <option value="active">{t('active', language)}</option>
                    <option value="very_active">{t('veryActive', language)}</option>
                  </Select>
                  {formik.touched.activity_level && formik.errors.activity_level && (
                    <Text color="red.500" fontSize="sm">{formik.errors.activity_level}</Text>
                  )}
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Dietary Information */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('dietaryInformation', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>{t('dietaryPreferences', language)}</FormLabel>
                  <Textarea
                    placeholder={t('dietaryPreferencesPlaceholder', language)}
                    {...formik.getFieldProps('dietary_preferences')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('dietaryRestrictions', language)}</FormLabel>
                  <Textarea
                    placeholder={t('dietaryRestrictionsPlaceholder', language)}
                    {...formik.getFieldProps('dietary_restrictions')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('mealPreferences', language)}</FormLabel>
                  <Textarea
                    placeholder={t('mealPreferencesPlaceholder', language)}
                    {...formik.getFieldProps('meal_preferences')}
                  />
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Fitness Goals */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('fitnessGoals', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl isInvalid={formik.touched.fitness_goal && formik.errors.fitness_goal}>
                  <FormLabel>{t('fitnessGoal', language)}</FormLabel>
                  <Select {...formik.getFieldProps('fitness_goal')}>
                    <option value="">{t('selectPrimaryGoal', language)}</option>
                    <option value="weight_loss">{t('weightLoss', language)}</option>
                    <option value="muscle_gain">{t('muscleGain', language)}</option>
                    <option value="general_fitness">{t('generalFitness', language)}</option>
                    <option value="endurance">{t('endurance', language)}</option>
                    <option value="strength">{t('strength', language)}</option>
                  </Select>
                  {formik.touched.fitness_goal && formik.errors.fitness_goal && (
                    <Text color="red.500" fontSize="sm">{formik.errors.fitness_goal}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl>
                    <FormLabel>{t('targetWeight', language)} ({getTargetWeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('target_weight')}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>{t('targetActivityLevel', language)}</FormLabel>
                    <Select {...formik.getFieldProps('target_activity_level')}>
                      <option value="">{t('selectTargetLevel', language)}</option>
                      <option value="sedentary">{t('sedentary', language)}</option>
                      <option value="light">{t('light', language)}</option>
                      <option value="moderate">{t('moderate', language)}</option>
                      <option value="active">{t('active', language)}</option>
                      <option value="very_active">{t('veryActive', language)}</option>
                    </Select>
                  </FormControl>
                </HStack>

                <FormControl isInvalid={formik.touched.weekly_activity_frequency && formik.errors.weekly_activity_frequency}>
                  <FormLabel>{t('weeklyActivityFrequencyDays', language)}</FormLabel>
                  <Input
                    type="number"
                    min="0"
                    max="7"
                    {...formik.getFieldProps('weekly_activity_frequency')}
                  />
                  {formik.touched.weekly_activity_frequency && formik.errors.weekly_activity_frequency && (
                    <Text color="red.500" fontSize="sm">{formik.errors.weekly_activity_frequency}</Text>
                  )}
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Exercise Preferences */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('exercisePreferences', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>{t('preferredExerciseTime', language)}</FormLabel>
                  <Select {...formik.getFieldProps('preferred_exercise_time')}>
                    <option value="">{t('selectPreferredTime', language)}</option>
                    <option value="morning">{t('morning', language)}</option>
                    <option value="afternoon">{t('afternoon', language)}</option>
                    <option value="evening">{t('evening', language)}</option>
                    <option value="flexible">{t('flexible', language)}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('preferredExerciseEnvironment', language)}</FormLabel>
                  <Select {...formik.getFieldProps('preferred_exercise_environment')}>
                    <option value="">{t('selectEnvironment', language)}</option>
                    <option value="home">{t('home', language)}</option>
                    <option value="gym">{t('gym', language)}</option>
                    <option value="outdoors">{t('outdoors', language)}</option>
                    <option value="mixed">{t('mixed', language)}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('exerciseTypes', language)}</FormLabel>
                  <Textarea
                    placeholder={t('exerciseTypesPlaceholder', language)}
                    {...formik.getFieldProps('exercise_types')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('averageSessionDuration', language)}</FormLabel>
                  <Select {...formik.getFieldProps('average_session_duration')}>
                    <option value="">{t('selectDuration', language)}</option>
                    <option value="15-30min">{t('duration15_30', language)}</option>
                    <option value="30-60min">{t('duration30_60', language)}</option>
                    <option value="60+min">{t('duration60Plus', language)}</option>
                  </Select>
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Fitness Assessment */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('fitnessAssessment', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>{t('fitnessLevel', language)}</FormLabel>
                  <Select {...formik.getFieldProps('fitness_level')}>
                    <option value="">{t('selectFitnessLevel', language)}</option>
                    <option value="beginner">{t('beginner', language)}</option>
                    <option value="intermediate">{t('intermediate', language)}</option>
                    <option value="advanced">{t('advanced', language)}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('enduranceLevel1_10', language)}</FormLabel>
                  <Input
                    type="number"
                    min="1"
                    max="10"
                    {...formik.getFieldProps('endurance_level')}
                  />
                </FormControl>

                <FormControl isInvalid={formik.touched.current_endurance_minutes && formik.errors.current_endurance_minutes}>
                  <FormLabel>{t('currentEnduranceMinutes', language)}</FormLabel>
                  <Input
                    type="number"
                    placeholder={t('currentEndurancePlaceholder', language)}
                    {...formik.getFieldProps('current_endurance_minutes')}
                  />
                  {formik.touched.current_endurance_minutes && formik.errors.current_endurance_minutes && (
                    <Text color="red.500" fontSize="sm">{formik.errors.current_endurance_minutes}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl isInvalid={formik.touched.pushup_count && formik.errors.pushup_count}>
                    <FormLabel>{t('pushupsMax', language)}</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('pushup_count')}
                    />
                    {formik.touched.pushup_count && formik.errors.pushup_count && (
                      <Text color="red.500" fontSize="sm">{formik.errors.pushup_count}</Text>
                    )}
                  </FormControl>

                  <FormControl isInvalid={formik.touched.squat_count && formik.errors.squat_count}>
                    <FormLabel>{t('squatsMax', language)}</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('squat_count')}
                    />
                    {formik.touched.squat_count && formik.errors.squat_count && (
                      <Text color="red.500" fontSize="sm">{formik.errors.squat_count}</Text>
                    )}
                  </FormControl>
                </HStack>

                <FormControl>
                  <FormLabel>{t('strengthIndicators', language)}</FormLabel>
                  <Textarea
                    placeholder={t('strengthIndicatorsPlaceholder', language)}
                    {...formik.getFieldProps('strength_indicators')}
                  />
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Current Health Metrics */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>{t('currentHealthMetrics', language)}</Heading>
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontWeight="bold">{t('bmi', language)}</Text>
                  <Text fontSize="xl">{metrics?.bmi ? metrics.bmi.toFixed(1) : t('calculating', language)}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">{t('wellnessScore', language)}</Text>
                  <Text fontSize="xl">{metrics?.wellness_score ? metrics.wellness_score.toFixed(1) : t('calculating', language)}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">{t('activityLevel', language)}</Text>
                  <Text fontSize="xl">{metrics?.activity_level || t('notSet', language)}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">{t('progressTowardsGoal', language)}</Text>
                  <Text fontSize="xl">{metrics?.progress ? `${metrics.progress.toFixed(1)}%` : t('calculating', language)}</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Nutrition Preferences Summary */}
          <NutritionPreferencesSummary
            onLoad={loadNutritionPreferences}
          />
        </SimpleGrid>

        <Box mt={8} textAlign="center">
          <Button
            type="submit"
            colorScheme="blue"
            size="lg"
            isLoading={saving}
          >
            {t('saveProfile', language)}
          </Button>
        </Box>
      </form>

      {/* Consent Modal */}
      <ConsentModal
        isOpen={showConsentModal}
        onClose={() => setShowConsentModal(false)}
        onConsentGiven={handleConsentGiven}
        language={language}
      />
    </Box>
  );
};

export default Profile; 