// @ts-nocheck
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout for better responsiveness
  headers: {
    'Content-Type': 'application/json',
  },
});

const responseCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Request debouncing to prevent rapid requests
const requestDebounce = new Map();
const DEBOUNCE_DELAY = 1; // 1ms - only block truly identical requests within milliseconds

// const activeRequests = new Map();

// Request interceptor - FIXED and re-enabled
api.interceptors.request.use(
  async (config) => {
    // Ensure config has required properties
    if (!config) {
      console.error('❌ Config is undefined');
      return Promise.reject(new Error('Request config is undefined'));
    }
    
    // Ensure method and url are defined and properly formatted
    const method = (config.method || 'GET').toString().toUpperCase();
    const url = (config.url || '').toString();
    
    // Ensure all required properties exist
    if (!config.headers) {
      config.headers = {};
    }
    
    if (!config.timeout) {
      config.timeout = 10000;
    }
    
    console.log(`API CALL: ${method} ${url}`);
    
    if (method === 'GET') {
      const cacheKey = `${url}${JSON.stringify(config.params || {})}`;
      const cached = responseCache.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log(`Using cached response for ${url}`);
        return Promise.resolve(cached.response);
      }
    }
    
    try {
      const { supabase } = await import('../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      // Ensure headers object exists
      if (!config.headers) {
        config.headers = {};
      }
      
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
        console.log(`Using Supabase token for ${url}`);
      } else {
        // Fallback to localStorage token (for FastAPI JWT)
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log(`Using localStorage token for ${url}`);
        } else {
          console.warn(`No auth token available for ${url} - request may fail`);
        }
      }
    } catch (authError) {
      console.error('Auth error:', authError);
      // Don't reject requests if auth fails - let the backend handle it
    }
    
    // This prevents Axios from encountering undefined when calling toUpperCase internally
    if (!config.method) {
      config.method = 'get';
    }
    
    // Ensure method is lowercase string (Axios expects this)
    config.method = config.method.toString().toLowerCase();
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    const method = (response.config?.method || 'GET').toString().toLowerCase();
    if (method === 'get' && response.status === 200) {
      const url = response.config?.url || '';
      const cacheKey = `${url}${JSON.stringify(response.config?.params || {})}`;
      responseCache.set(cacheKey, {
        response: response,
        timestamp: Date.now()
      });
    }
    return response;
  },
  async (error) => {
    if (error.code === 'ECONNABORTED' || error.code === 'ECONNREFUSED') {
      console.warn('Server not available, using cached data or fallback');
      // Try to return cached data if available
      const method = (error.config?.method || 'GET').toString().toLowerCase();
      if (method === 'get') {
        const url = error.config?.url || '';
        const cacheKey = `${url}${JSON.stringify(error.config?.params || {})}`;
        const cached = responseCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
          return Promise.resolve(cached.response);
        }
      }
    }
    if (!error.config) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;

    if (originalRequest.url?.includes('/settings/me')) {
      console.log('Skipping retry for /settings/me to prevent loop');
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
        const { access_token, refresh_token } = response.data;

        localStorage.setItem('token', access_token);
        if (refresh_token) {
          localStorage.setItem('refresh_token', refresh_token);
        }
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
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
  getProfile: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<HealthProfile>(`/health/profiles/me?t=${Date.now()}`, { headers });
  },
  updateProfile: async (data: Partial<HealthProfile>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.put<HealthProfile>('/health/profiles/me', data, { headers });
  },
  createProfile: async (data: Partial<HealthProfile>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.post<HealthProfile>('/health/profiles', data, { headers });
  },
  getInsights: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get('/health/insights', { headers });
  },
};

// Analytics API calls
export const analytics = {
  getAnalytics: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<HealthAnalytics>(`/health/profiles/me/analytics?t=${Date.now()}`, { headers });
  },
  getMetrics: async (days: number = 30) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<MetricsHistory[]>(`/health/profiles/me/metrics?days=${days}`, { headers });
  },
  getActivities: async (days: number = 7, sortOrder: string = 'desc') => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<ActivityLog[]>(`/health/profiles/me/activities?days=${days}&sort_order=${sortOrder}`, { headers });
  },
  createActivity: async (data: Partial<ActivityLog>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.post<ActivityLog>('/health/profiles/me/activities', data, { headers });
  },
  getWeeklySummary: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get('/health/profiles/me/weekly-summary', { headers });
  },
  getMonthlySummary: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get('/health/profiles/me/monthly-summary', { headers });
  },
  exportActivities: async (days: number = 30, format: string = 'csv') => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get(`/export/activities?days=${days}&format=${format}`, { responseType: 'blob', headers });
  },
  exportHealthData: async (format: string = 'json') => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get(`/export/health-data?format=${format}`, { responseType: 'blob', headers });
  },
};

// Settings API calls - RE-ENABLED
export const settings = {
  getSettings: async () => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<Settings>('/settings/me', { headers });
  },
  updateSettings: async (data: Partial<Settings>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.put<Settings>('/settings/me', data, { headers });
  },
  createSettings: async (data: Settings) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.post<Settings>('/settings/me', data, { headers });
  },
};

// Goals API calls
export const goals = {
  getGoals: async () => {
    // Simple auth without interceptor
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.get<Goal[]>('/goals', { headers });
  },
  createGoal: async (data: Omit<Goal, 'id'>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.post<Goal>('/goals', data, { headers });
  },
  updateGoal: async (id: string, data: Partial<Goal>) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.put<Goal>(`/goals/${id}`, data, { headers });
  },
  deleteGoal: async (id: string) => {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
    return api.delete(`/goals/${id}`, { headers });
  },
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
  exportWeeklySummary: (format: string = 'json') => api.get(`/export/weekly-summary?format=${format}`, { responseType: 'blob' }),
  exportMonthlySummary: (format: string = 'json') => api.get(`/export/monthly-summary?format=${format}`, { responseType: 'blob' }),
};

export default api; 