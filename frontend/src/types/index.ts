export interface User {
  id: string;
  email: string;
  name?: string;
  is_active: boolean;
  is_verified: boolean;
  two_factor_enabled: boolean;
  oauth_provider?: 'google' | 'github';
  profile_picture?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthProfile {
  id: string;
  user_id: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  height: number; // in cm
  weight: number; // in kg
  occupation_type: 'sedentary' | 'moderate' | 'active';
  activity_level: 'low' | 'moderate' | 'high';
  dietary_preferences: string[];
  dietary_restrictions: string[];
  fitness_goals: ('weight_loss' | 'muscle_gain' | 'general_fitness')[];
  weekly_activity_frequency: number; // 0-7 days
  exercise_types: ('cardio' | 'strength' | 'flexibility' | 'sports')[];
  average_session_duration: '15-30min' | '30-60min' | '60+min';
  fitness_level: 'beginner' | 'intermediate' | 'advanced';
  preferred_exercise_environment: ('home' | 'gym' | 'outdoors')[];
  preferred_exercise_time: ('morning' | 'afternoon' | 'evening')[];
  endurance_level: number; // minutes
  strength_indicators: {
    pushups: number;
    squats: number;
  };
  created_at: string;
  updated_at: string;
}

export interface ActivityLog {
  id: string;
  user_id: string;
  activity_type: string;
  duration: number; // in minutes
  intensity: 'low' | 'moderate' | 'high';
  notes?: string;
  created_at: string;
}

export interface MetricsHistory {
  id: string;
  health_profile_id: string;
  weight: number;
  bmi: number;
  wellness_score: number;
  recorded_at: string;
}

export interface WellnessScore {
  bmi_score: number;
  activity_score: number;
  progress_score: number;
  habits_score: number;
  total_score: number;
}

export interface AIInsight {
  id: string;
  user_id: string;
  type: 'health_status' | 'progress' | 'recommendation';
  content: string;
  priority: 'high' | 'medium' | 'low';
  created_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  type: 'weight' | 'activity' | 'habit';
  target: number;
  current: number;
  unit: string;
  deadline?: string;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: string;
  goal_id: string;
  type: 'weight' | 'activity' | 'habit';
  value: number;
  achieved: boolean;
  achieved_at?: string;
  created_at: string;
}

export interface HealthMetrics {
  bmi: number;
  bmiCategory: 'underweight' | 'normal' | 'overweight' | 'obese';
  wellnessScore: number;
  activityScore: number;
  progressScore: number;
  habitsScore: number;
}

export interface ProgressData {
  date: string;
  weight: number;
  activityLevel: string;
  wellnessScore: number;
  achievements: string[];
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
} 