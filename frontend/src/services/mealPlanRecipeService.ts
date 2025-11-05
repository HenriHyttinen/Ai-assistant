/**
 * Meal Plan Recipe Service
 * Handles recipe-to-meal-plan integration with serving size adjustments
 */

export interface AddRecipeToMealPlanRequest {
  recipe_id: string;
  meal_date: string;
  meal_type: string;
  servings: number;
  meal_time?: string;
  custom_meal_name?: string;
}

export interface UpdateRecipeServingsRequest {
  recipe_id: string;
  new_servings: number;
}

export interface MealPlanRecipe {
  id: number;
  meal_plan_id: string;
  meal_id: number;
  recipe_id: string;
  servings: number;
  is_alternative: boolean;
  recipe: {
    id: string;
    title: string;
    description?: string;
    cuisine: string;
    meal_type: string;
    prep_time?: number;
    cook_time?: number;
    difficulty_level?: string;
    servings: number;
    image_url?: string;
    dietary_tags?: string[];
    allergens?: string[];
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    sodium?: number;
  };
}

export interface ServingAdjustmentSuggestion {
  recipe_id: string;
  recipe_title: string;
  current_servings: number;
  adjustments: {
    [key: string]: {
      factor: number;
      new_servings: number;
      new_value: number;
    };
  };
}

export interface NutritionSummary {
  total_nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    sodium: number;
  };
  meal_type_breakdown: {
    [mealType: string]: {
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
      sodium: number;
      recipe_count: number;
    };
  };
  recipe_count: number;
  date?: string;
}

export interface ShoppingListItem {
  name: string;
  unit: string;
  total_quantity: number;
  recipes: Array<{
    recipe_title: string;
    quantity: number;
    servings: number;
  }>;
}

export interface ShoppingList {
  ingredients: ShoppingListItem[];
  recipe_count: number;
  date?: string;
}

class MealPlanRecipeService {
  private baseUrl = 'http://localhost:8000/meal-plan-recipes';

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

  // Add recipe to meal plan
  async addRecipeToMealPlan(
    mealPlanId: string, 
    request: AddRecipeToMealPlanRequest
  ): Promise<any> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}/add-recipe`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add recipe to meal plan');
    }

    return response.json();
  }

  // Update recipe servings
  async updateRecipeServings(
    mealPlanId: string,
    mealId: number,
    request: UpdateRecipeServingsRequest
  ): Promise<any> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}/meals/${mealId}/update-servings`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update recipe servings');
    }

    return response.json();
  }

  // Remove recipe from meal plan
  async removeRecipeFromMealPlan(
    mealPlanId: string,
    mealId: number,
    recipeId: string
  ): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}/meals/${mealId}/remove-recipe?recipe_id=${recipeId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove recipe from meal plan');
    }
  }

  // Get meal plan recipes
  async getMealPlanRecipes(
    mealPlanId: string,
    mealDate?: string
  ): Promise<MealPlanRecipe[]> {
    const headers = await this.getAuthHeaders();
    
    const url = mealDate 
      ? `${this.baseUrl}/${mealPlanId}/recipes?meal_date=${mealDate}`
      : `${this.baseUrl}/${mealPlanId}/recipes`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get meal plan recipes');
    }

    return response.json();
  }

  // Get serving suggestions
  async getServingSuggestions(
    mealPlanId: string,
    targetCalories?: number,
    targetProtein?: number
  ): Promise<ServingAdjustmentSuggestion[]> {
    const headers = await this.getAuthHeaders();
    
    const params = new URLSearchParams();
    if (targetCalories) params.append('target_calories', targetCalories.toString());
    if (targetProtein) params.append('target_protein', targetProtein.toString());
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}/serving-suggestions?${params}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get serving suggestions');
    }

    return response.json();
  }

  // Bulk add recipes
  async bulkAddRecipesToMealPlan(
    mealPlanId: string,
    requests: AddRecipeToMealPlanRequest[]
  ): Promise<any> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/${mealPlanId}/bulk-add-recipes`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requests),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to bulk add recipes');
    }

    return response.json();
  }

  // Get nutrition summary
  async getNutritionSummary(
    mealPlanId: string,
    mealDate?: string
  ): Promise<NutritionSummary> {
    const headers = await this.getAuthHeaders();
    
    const url = mealDate 
      ? `${this.baseUrl}/${mealPlanId}/nutrition-summary?meal_date=${mealDate}`
      : `${this.baseUrl}/${mealPlanId}/nutrition-summary`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get nutrition summary');
    }

    return response.json();
  }

  // Generate shopping list
  async generateShoppingList(
    mealPlanId: string,
    mealDate?: string
  ): Promise<ShoppingList> {
    const headers = await this.getAuthHeaders();
    
    const url = mealDate 
      ? `${this.baseUrl}/${mealPlanId}/shopping-list?meal_date=${mealDate}`
      : `${this.baseUrl}/${mealPlanId}/shopping-list`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate shopping list');
    }

    return response.json();
  }

  // Helper methods
  formatMealType(mealType: string): string {
    return mealType.charAt(0).toUpperCase() + mealType.slice(1).replace('_', ' ');
  }

  getMealTypeColor(mealType: string): string {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return 'orange';
      case 'lunch':
        return 'yellow';
      case 'dinner':
        return 'blue';
      case 'snack':
        return 'green';
      default:
        return 'gray';
    }
  }

  calculateNutritionPerServing(recipe: any, servings: number) {
    const baseServings = recipe.servings || 1;
    const scaleFactor = servings / baseServings;
    
    return {
      calories: (recipe.calories || 0) * scaleFactor,
      protein: (recipe.protein || 0) * scaleFactor,
      carbs: (recipe.carbs || 0) * scaleFactor,
      fat: (recipe.fat || 0) * scaleFactor,
      sodium: (recipe.sodium || 0) * scaleFactor
    };
  }

  formatNutritionValue(value: number, unit: string = ''): string {
    if (value === 0) return '0';
    if (value < 1) return value.toFixed(2) + unit;
    if (value < 10) return value.toFixed(1) + unit;
    return Math.round(value).toString() + unit;
  }
}

export default new MealPlanRecipeService();







