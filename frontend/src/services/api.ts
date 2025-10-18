// @ts-nocheck
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!error.config) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post('http://localhost:8001/auth/refresh', { refresh_token: refreshToken });
        const { access_token } = response.data;

        localStorage.setItem('token', access_token);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Types
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface HealthProfile {
  id: number;
  user_id: number;
  age: number;
  gender: string;
  height: number;
  weight: number;
  occupation_type: string;
  activity_level: string;
  
  // Dietary preferences and restrictions
  dietary_preferences?: string;
  dietary_restrictions?: string;
  meal_preferences?: string;
  
  fitness_goal: string;
  target_weight?: number;
  target_activity_level?: string;
  preferred_exercise_time?: string;
  preferred_exercise_environment?: string;
  weekly_activity_frequency: number;
  exercise_types?: string;
  average_session_duration?: string;
  fitness_level?: string;
  endurance_level?: number;
  strength_indicators?: string;
  current_endurance_minutes?: number;
  pushup_count?: number;
  squat_count?: number;
  created_at: string;
  updated_at: string;
}

interface ActivityLog {
  id: number;
  user_id: number;
  activity_type: string;
  duration: number;
  intensity?: string;
  notes?: string;
  created_at: string;
}

interface MetricsHistory {
  id: number;
  health_profile_id: number;
  weight: number;
  bmi: number;
  wellness_score: number;
  recorded_at: string;
}

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
  status: 'in_progress' | 'completed' | 'failed' | 'not_started';
}

interface Settings {
  emailNotifications: boolean;
  weeklyReports: boolean;
  aiInsights: boolean;
  dataSharing: boolean;
  measurementSystem: 'metric' | 'imperial';
  language: string;
}

// Health Profile API calls
export const healthProfile = {
  getProfile: () => api.get<HealthProfile>(`/health/profiles/me?t=${Date.now()}`),
  updateProfile: (data: Partial<HealthProfile>) => api.put<HealthProfile>('/health/profiles/me', data),
  createProfile: (data: Partial<HealthProfile>) => api.post<HealthProfile>('/health/profiles', data),
  getInsights: () => api.get('/health/insights'),
};

// Analytics API calls
export const analytics = {
  getAnalytics: () => api.get<HealthAnalytics>(`/health/profiles/me/analytics?t=${Date.now()}`),
  getMetrics: (days: number = 30) => api.get<MetricsHistory[]>(`/health/profiles/me/metrics?days=${days}`),
  getActivities: (days: number = 7) => api.get<ActivityLog[]>(`/health/profiles/me/activities?days=${days}`),
  createActivity: (data: Partial<ActivityLog>) => api.post<ActivityLog>('/health/profiles/me/activities', data),
};

// Settings API calls
export const settings = {
  getSettings: () => api.get<Settings>('/settings/me'),
  updateSettings: (data: Partial<Settings>) => api.put<Settings>('/settings/me', data),
  createSettings: (data: Settings) => api.post<Settings>('/settings/me', data),
};

// Goals API calls
export const goals = {
  getGoals: () => api.get<Goal[]>('/goals'),
  createGoal: (data: Omit<Goal, 'id'>) => api.post<Goal>('/goals', data),
  updateGoal: (id: string, data: Partial<Goal>) => api.put<Goal>(`/goals/${id}`, data),
  deleteGoal: (id: string) => api.delete(`/goals/${id}`),
};

// Auth API calls
export const auth = {
  login: (email: string, password: string) => api.post('/auth/token', { email, password }),
  register: (email: string, password: string) => api.post('/auth/register', { email, password }),
  getProfile: () => api.get('/auth/profile'),
  setup2FA: () => api.post('/auth/setup-2fa'),
  verify2FA: (data: { code: string }) => api.post('/auth/verify-2fa', data),
  disable2FA: () => api.post('/auth/disable-2fa'),
};

// Consent API calls
export const consentService = {
  giveConsent: (consentData: any) => api.post('/consent/give', consentData),
  getConsentStatus: () => api.get('/consent/status'),
  withdrawConsent: () => api.delete('/consent/withdraw'),
};

// Export API calls
export const exportService = {
  exportHealthData: (format: string) => api.get(`/export/health-data?format=${format}`),
  exportMetricsHistory: (days: number, format: string) => api.get(`/export/metrics-history?days=${days}&format=${format}`),
};

export default api; 