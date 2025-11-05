/**
 * Recipe Rating Service
 * Handles all API calls related to recipe ratings and reviews
 */

export interface RecipeRating {
  id: number;
  user_id: string;
  recipe_id: string;
  rating: number;
  review_text?: string;
  is_verified: boolean;
  difficulty_rating?: number;
  taste_rating?: number;
  would_make_again: boolean;
  created_at: string;
  updated_at: string;
}

export interface RecipeReview {
  id: number;
  user_id: string;
  recipe_id: string;
  title?: string;
  content: string;
  is_helpful: boolean;
  cooking_tips?: string;
  modifications?: string;
  created_at: string;
  updated_at: string;
  helpful_count: number;
  not_helpful_count: number;
  user?: {
    email: string;
    profile_picture?: string;
  };
}

export interface RecipeStats {
  recipe_id: string;
  average_rating: number;
  total_ratings: number;
  rating_distribution: { [key: string]: number };
  total_reviews: number;
  verified_cooks: number;
  would_make_again_percentage: number;
  average_difficulty_rating?: number;
  average_taste_rating?: number;
}

export interface UserRatingSummary {
  total_ratings: number;
  total_reviews: number;
  average_rating_given?: number;
  most_rated_cuisine?: string;
  favorite_recipe?: string;
}

export interface RatingCreateData {
  recipe_id: string;
  rating: number;
  review_text?: string;
  is_verified: boolean;
  difficulty_rating?: number;
  taste_rating?: number;
  would_make_again: boolean;
}

export interface ReviewCreateData {
  recipe_id: string;
  title?: string;
  content: string;
  is_helpful: boolean;
  cooking_tips?: string;
  modifications?: string;
}

class RecipeRatingService {
  private baseUrl = 'http://localhost:8000/recipe-ratings';

  private async getAuthHeaders(): Promise<HeadersInit> {
    const { supabase } = await import('@/lib/supabase');
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No authentication session found');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    };
  }

  // Rating methods
  async createRating(ratingData: RatingCreateData): Promise<RecipeRating> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/rate`, {
      method: 'POST',
      headers,
      body: JSON.stringify(ratingData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create rating');
    }

    return response.json();
  }

  async updateRating(ratingId: number, ratingData: Partial<RatingCreateData>): Promise<RecipeRating> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/rate/${ratingId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(ratingData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update rating');
    }

    return response.json();
  }

  async deleteRating(ratingId: number): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/rate/${ratingId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete rating');
    }
  }

  async getUserRating(recipeId: string): Promise<RecipeRating | null> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/rate/${recipeId}`, {
      method: 'GET',
      headers,
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user rating');
    }

    return response.json();
  }

  // Review methods
  async createReview(reviewData: ReviewCreateData): Promise<RecipeReview> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/review`, {
      method: 'POST',
      headers,
      body: JSON.stringify(reviewData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create review');
    }

    return response.json();
  }

  async updateReview(reviewId: number, reviewData: Partial<ReviewCreateData>): Promise<RecipeReview> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/review/${reviewId}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(reviewData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update review');
    }

    return response.json();
  }

  async deleteReview(reviewId: number): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/review/${reviewId}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete review');
    }
  }

  async getRecipeReviews(
    recipeId: string,
    options: {
      limit?: number;
      offset?: number;
      helpful_only?: boolean;
      verified_only?: boolean;
      has_tips?: boolean;
      has_modifications?: boolean;
    } = {}
  ): Promise<RecipeReview[]> {
    const headers = await this.getAuthHeaders();
    
    const params = new URLSearchParams();
    params.append('limit', (options.limit || 20).toString());
    params.append('offset', (options.offset || 0).toString());
    if (options.helpful_only) params.append('helpful_only', 'true');
    if (options.verified_only) params.append('verified_only', 'true');
    if (options.has_tips) params.append('has_tips', 'true');
    if (options.has_modifications) params.append('has_modifications', 'true');

    const response = await fetch(`${this.baseUrl}/review/${recipeId}?${params}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get recipe reviews');
    }

    return response.json();
  }

  // Helpful vote methods
  async voteHelpful(reviewId: number, isHelpful: boolean): Promise<void> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/review/${reviewId}/helpful`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ is_helpful: isHelpful }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to vote helpful');
    }
  }

  // Statistics methods
  async getRecipeStats(recipeId: string): Promise<RecipeStats> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/stats/${recipeId}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get recipe stats');
    }

    return response.json();
  }

  async getUserRatingSummary(): Promise<UserRatingSummary> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/user-summary`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user rating summary');
    }

    return response.json();
  }

  // Search methods
  async searchRecipesByRating(filters: {
    min_rating?: number;
    max_rating?: number;
    verified_only?: boolean;
    would_make_again?: boolean;
    min_reviews?: number;
    cuisine?: string;
    meal_type?: string;
    difficulty_level?: string;
    limit?: number;
    offset?: number;
  }): Promise<any[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/search`, {
      method: 'POST',
      headers,
      body: JSON.stringify(filters),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search recipes by rating');
    }

    return response.json();
  }

  async getTopRatedRecipes(options: {
    limit?: number;
    min_ratings?: number;
    cuisine?: string;
    meal_type?: string;
  } = {}): Promise<any[]> {
    const headers = await this.getAuthHeaders();
    
    const params = new URLSearchParams();
    params.append('limit', (options.limit || 10).toString());
    params.append('min_ratings', (options.min_ratings || 5).toString());
    if (options.cuisine) params.append('cuisine', options.cuisine);
    if (options.meal_type) params.append('meal_type', options.meal_type);

    const response = await fetch(`${this.baseUrl}/top-rated?${params}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get top rated recipes');
    }

    return response.json();
  }

  async getRecentReviews(limit: number = 10): Promise<RecipeReview[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/recent-reviews?limit=${limit}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get recent reviews');
    }

    return response.json();
  }
}

export default new RecipeRatingService();







