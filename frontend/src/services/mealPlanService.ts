/**
 * Meal Plan Service
 * Handles basic meal plan operations
 */

export interface MealPlan {
  id: string;
  user_id: string;
  plan_type: string;
  start_date: string;
  end_date?: string;
  version: string;
  is_active: boolean;
  generation_strategy?: any;
  ai_model_used?: string;
  generation_parameters?: any;
  created_at: string;
  updated_at: string;
}

class MealPlanService {
  private baseUrl = 'http://localhost:8000/nutrition/meal-plans';

  private async getAuthHeaders(): Promise<HeadersInit> {
    const { supabase } = await import('../lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No authentication session found');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    };
  }

  async getMealPlans(): Promise<MealPlan[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(this.baseUrl, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get meal plans');
    }

    return response.json();
  }

  async getMealPlan(mealPlanId: string): Promise<MealPlan> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get meal plan');
    }

    return response.json();
  }

  async createMealPlan(planData: {
    plan_type: string;
    start_date: string;
    end_date?: string;
  }): Promise<MealPlan> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(planData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create meal plan');
    }

    return response.json();
  }

  async deleteMealPlan(mealPlanId: string): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete meal plan');
    }
  }
}

export default new MealPlanService();


