/**
 * Nutrition Goals Service
 * Handles all API calls related to nutrition goals tracking
 */

export interface NutritionGoal {
  id: number;
  user_id: string;
  goal_type: string;
  goal_name: string;
  description?: string;
  target_value: number;
  current_value: number;
  unit: string;
  frequency: string;
  start_date: string;
  target_date?: string;
  is_flexible: boolean;
  status: string;
  priority: number;
  is_public: boolean;
  progress_percentage: number;
  days_achieved: number;
  total_days: number;
  streak_days: number;
  best_streak: number;
  created_at: string;
  updated_at: string;
  progress_logs: GoalProgressLog[];
  milestones: GoalMilestone[];
}

export interface GoalProgressLog {
  id: number;
  goal_id: number;
  user_id: string;
  date: string;
  achieved_value: number;
  target_value: number;
  is_achieved: boolean;
  progress_percentage: number;
  notes?: string;
  difficulty_rating?: number;
  mood_rating?: number;
  created_at: string;
  updated_at: string;
}

export interface GoalMilestone {
  id: number;
  goal_id: number;
  user_id: string;
  milestone_name: string;
  description?: string;
  target_value: number;
  achieved_value: number;
  is_achieved: boolean;
  achieved_date?: string;
  is_automatic: boolean;
  reward_description?: string;
  created_at: string;
  updated_at: string;
}

export interface GoalTemplate {
  id: number;
  name: string;
  description?: string;
  goal_type: string;
  default_target_value: number;
  default_unit: string;
  default_frequency: string;
  default_duration_days?: number;
  category?: string;
  difficulty_level: number;
  is_public: boolean;
  usage_count: number;
  instructions?: string;
  tips?: string;
  common_challenges?: string;
  success_metrics?: string;
  created_at: string;
  updated_at: string;
}

export interface GoalSummary {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  paused_goals: number;
  total_streak_days: number;
  best_streak: number;
  goals_achieved_today: number;
  goals_on_track: number;
  goals_behind: number;
}

export interface GoalProgressSummary {
  goal_id: number;
  goal_name: string;
  goal_type: string;
  target_value: number;
  current_value: number;
  progress_percentage: number;
  status: string;
  streak_days: number;
  days_remaining?: number;
  is_on_track: boolean;
  last_achieved?: string;
  next_milestone?: GoalMilestone;
}

export interface GoalDashboard {
  summary: GoalSummary;
  active_goals: GoalProgressSummary[];
  recent_achievements: GoalProgressLog[];
  upcoming_milestones: GoalMilestone[];
  streak_leaderboard: Array<{
    goal_name: string;
    streak_days: number;
    goal_type: string;
  }>;
}

export interface GoalAnalytics {
  goal_id: number;
  goal_name: string;
  goal_type: string;
  total_days: number;
  days_achieved: number;
  achievement_rate: number;
  current_streak: number;
  best_streak: number;
  average_progress: number;
  trend_direction: string;
  weekly_progress: Array<{
    week_start: string;
    average_progress: number;
    days_achieved: number;
    total_days: number;
  }>;
  monthly_progress: Array<{
    month: string;
    average_progress: number;
    days_achieved: number;
    total_days: number;
  }>;
  milestone_achievements: number;
  total_milestones: number;
}

export interface GoalInsights {
  insights: string[];
  recommendations: string[];
  challenges: string[];
  successes: string[];
  next_actions: string[];
}

class NutritionGoalsService {
  private baseUrl = 'http://localhost:8000/nutrition-goals';

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

  // Goal CRUD operations
  async createGoal(goalData: Partial<NutritionGoal>): Promise<NutritionGoal> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(goalData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create goal');
    }

    return response.json();
  }

  async getGoal(goalId: number): Promise<NutritionGoal> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal');
    }

    return response.json();
  }

  async getUserGoals(params?: {
    query?: string;
    status?: string;
    goal_type?: string;
    frequency?: string;
    priority?: number;
    is_public?: boolean;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
    offset?: number;
  }): Promise<NutritionGoal[]> {
    const headers = await this.getAuthHeaders();
    
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${this.baseUrl}/?${searchParams}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goals');
    }

    return response.json();
  }

  async updateGoal(goalId: number, goalData: Partial<NutritionGoal>): Promise<NutritionGoal> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(goalData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update goal');
    }

    return response.json();
  }

  async deleteGoal(goalId: number): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete goal');
    }
  }

  // Progress tracking
  async logProgress(progressData: {
    goal_id: number;
    date: string;
    achieved_value: number;
    notes?: string;
    difficulty_rating?: number;
    mood_rating?: number;
  }): Promise<GoalProgressLog> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/progress`, {
      method: 'POST',
      headers,
      body: JSON.stringify(progressData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to log progress');
    }

    return response.json();
  }

  async getGoalProgress(goalId: number, days: number = 30): Promise<GoalProgressLog[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}/progress?days=${days}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal progress');
    }

    return response.json();
  }

  // Milestones
  async createMilestone(milestoneData: {
    goal_id: number;
    milestone_name: string;
    description?: string;
    target_value: number;
    is_automatic?: boolean;
    reward_description?: string;
  }): Promise<GoalMilestone> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/milestones`, {
      method: 'POST',
      headers,
      body: JSON.stringify(milestoneData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create milestone');
    }

    return response.json();
  }

  async getGoalMilestones(goalId: number): Promise<GoalMilestone[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}/milestones`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get milestones');
    }

    return response.json();
  }

  async checkMilestones(goalId: number): Promise<GoalMilestone[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}/check-milestones`, {
      method: 'POST',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check milestones');
    }

    return response.json();
  }

  // Dashboard and analytics
  async getGoalDashboard(): Promise<GoalDashboard> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/dashboard/summary`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal dashboard');
    }

    return response.json();
  }

  async getGoalAnalytics(goalId: number): Promise<GoalAnalytics> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}/analytics`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal analytics');
    }

    return response.json();
  }

  // Templates
  async getGoalTemplates(category?: string): Promise<GoalTemplate[]> {
    const headers = await this.getAuthHeaders();
    
    const url = category ? `${this.baseUrl}/templates/?category=${category}` : `${this.baseUrl}/templates/`;
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal templates');
    }

    return response.json();
  }

  async createGoalFromTemplate(templateId: number, customizations?: Record<string, any>): Promise<NutritionGoal> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/templates/${templateId}/create-goal`, {
      method: 'POST',
      headers,
      body: JSON.stringify(customizations || {}),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create goal from template');
    }

    return response.json();
  }

  // Bulk operations
  async logBulkProgress(progressData: Array<{
    goal_id: number;
    date: string;
    achieved_value: number;
    notes?: string;
    difficulty_rating?: number;
    mood_rating?: number;
  }>): Promise<GoalProgressLog[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/bulk/progress`, {
      method: 'POST',
      headers,
      body: JSON.stringify(progressData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to log bulk progress');
    }

    return response.json();
  }

  async checkAllMilestones(): Promise<GoalMilestone[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/bulk/check-milestones`, {
      method: 'POST',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check all milestones');
    }

    return response.json();
  }

  // Insights
  async getGoalInsights(goalId: number): Promise<GoalInsights> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${goalId}/insights`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get goal insights');
    }

    return response.json();
  }
}

export default new NutritionGoalsService();







