/**
 * Nutrition Analytics Service
 * Handles all API calls related to advanced nutrition analytics
 */

export interface NutritionTrend {
  direction: 'increasing' | 'decreasing' | 'stable';
  strength: number;
  current_avg: number;
  previous_avg: number;
  change_percent: number;
  daily_values: number[];
  dates: string[];
}

export interface NutritionInsight {
  type: 'warning' | 'info' | 'success';
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
}

export interface NutritionTrends {
  period_days: number;
  total_days_logged: number;
  trends: {
    [key: string]: NutritionTrend;
  };
  summary: {
    avg_calories: number;
    avg_protein: number;
    avg_carbs: number;
    avg_fat: number;
    avg_fiber: number;
    avg_sodium: number;
  };
}

export interface NutritionInsights {
  insights: NutritionInsight[];
  recommendations: string[];
  summary: {
    avg_calories: number;
    avg_protein: number;
    avg_carbs: number;
    avg_fat: number;
    avg_fiber: number;
    avg_sodium: number;
    total_days: number;
  };
}

export interface MealPattern {
  total_meals_logged: number;
  avg_meals_per_day: number;
  meal_timing: {
    breakfast_avg_time?: string;
    lunch_avg_time?: string;
    dinner_avg_time?: string;
  };
  meal_consistency: {
    breakfast: number;
    lunch: number;
    dinner: number;
  };
  calorie_distribution: {
    [key: string]: {
      avg_calories: number;
      total_meals: number;
      percentage: number;
    };
  };
  meal_type_frequency: {
    [key: string]: number;
  };
}

export interface GoalProgress {
  current: number;
  target: number;
  min: number;
  max: number;
  status: 'on_track' | 'below_target' | 'above_target';
  progress_percent: number;
}

export interface NutritionGoalsProgress {
  goals: {
    [key: string]: {
      target: number;
      min: number;
      max: number;
    };
  };
  progress: {
    [key: string]: GoalProgress;
  };
  overall_status: 'excellent' | 'good' | 'fair' | 'needs_improvement' | 'no_data';
  days_tracked: number;
}

export interface AnalyticsDashboard {
  trends: NutritionTrends;
  insights: NutritionInsights;
  meal_patterns: MealPattern;
  goals_progress: NutritionGoalsProgress;
  period_days: number;
  generated_at: string;
}

class NutritionAnalyticsService {
  private baseUrl = 'http://localhost:8000/nutrition-analytics';

  private async getAuthHeaders(): Promise<HeadersInit> {
    const { supabase } = await import('../lib/supabase.ts');
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No authentication session found');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    };
  }

  async getNutritionTrends(days: number = 30): Promise<NutritionTrends> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/trends?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get nutrition trends');
    }

    return response.json();
  }

  async getNutritionInsights(days: number = 30): Promise<NutritionInsights> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/insights?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get nutrition insights');
    }

    return response.json();
  }

  async getMealPatterns(days: number = 30): Promise<MealPattern> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/meal-patterns?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get meal patterns');
    }

    return response.json();
  }

  async getGoalsProgress(days: number = 30): Promise<NutritionGoalsProgress> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/goals-progress?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goals progress');
    }

    return response.json();
  }

  async getAnalyticsDashboard(days: number = 30): Promise<AnalyticsDashboard> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/dashboard?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get analytics dashboard');
    }

    return response.json();
  }

  async exportAnalyticsData(days: number = 30, format: 'json' | 'csv' = 'json'): Promise<any> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/export?days=${days}&format=${format}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to export analytics data');
    }

    return response.json();
  }

  async getComprehensiveAnalysis(startDate: string, endDate: string, analysisType: string = 'daily'): Promise<any> {
    const headers = await this.getAuthHeaders();
    
    // Use the nutrition route for comprehensive analysis
    const response = await fetch(`http://localhost:8000/nutrition/comprehensive-ai-analysis?start_date=${startDate}&end_date=${endDate}&analysis_type=${analysisType}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get comprehensive analysis');
    }

    return response.json();
  }
}

export default new NutritionAnalyticsService();
