// Offline-first API service
// Handles caching, offline storage, and syncing

import offlineStorage from './offlineStorage';
import { useOffline } from '../hooks/useOffline';

interface ApiResponse<T> {
  data: T;
  fromCache: boolean;
  offline: boolean;
  lastUpdated?: string;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  forceRefresh?: boolean;
  offlineFirst?: boolean;
}

class OfflineApiService {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  constructor() {
    // Initialize offline storage
    offlineStorage.init().catch(console.error);
  }

  // Generic API call with offline support
  async request<T>(
    url: string,
    options: RequestInit = {},
    cacheOptions: CacheOptions = {}
  ): Promise<ApiResponse<T>> {
    const {
      ttl = this.defaultTTL,
      forceRefresh = false,
      offlineFirst = true
    } = cacheOptions;

    const cacheKey = this.getCacheKey(url, options);
    const isOffline = !navigator.onLine;

    // Check cache first if offline-first or offline
    if (offlineFirst || isOffline) {
      const cachedData = this.getFromCache<T>(cacheKey);
      if (cachedData && !forceRefresh) {
        return {
          data: cachedData,
          fromCache: true,
          offline: isOffline,
          lastUpdated: new Date(this.cache.get(cacheKey)?.timestamp || 0).toISOString()
        };
      }
    }

    // Try network request if online
    if (!isOffline) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        if (response.ok) {
          const data = await response.json();
          
          // Cache the response
          this.setCache(cacheKey, data, ttl);
          
          // Store in IndexedDB for offline access
          await this.storeForOffline(url, data);

          return {
            data,
            fromCache: false,
            offline: false,
            lastUpdated: new Date().toISOString()
          };
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Network request failed:', error);
        
        // Fall back to cache if available
        const cachedData = this.getFromCache<T>(cacheKey);
        if (cachedData) {
          return {
            data: cachedData,
            fromCache: true,
            offline: true,
            lastUpdated: new Date(this.cache.get(cacheKey)?.timestamp || 0).toISOString()
          };
        }
        
        throw error;
      }
    }

    // Offline and no cache available
    throw new Error('No data available offline');
  }

  // Recipe-specific methods
  async getRecipes(filters?: any): Promise<ApiResponse<any[]>> {
    const url = '/api/recipes';
    const queryParams = filters ? this.buildQueryString(filters) : '';
    const fullUrl = queryParams ? `${url}?${queryParams}` : url;

    try {
      return await this.request<any[]>(fullUrl, {}, { offlineFirst: true });
    } catch (error) {
      // Fall back to offline storage
      const offlineRecipes = await offlineStorage.searchRecipes('', filters);
      return {
        data: offlineRecipes,
        fromCache: true,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }
  }

  async getRecipe(id: string): Promise<ApiResponse<any>> {
    const url = `/api/recipes/${id}`;

    try {
      return await this.request<any>(url, {}, { offlineFirst: true });
    } catch (error) {
      // Fall back to offline storage
      const offlineRecipe = await offlineStorage.getRecipe(id);
      if (offlineRecipe) {
        return {
          data: offlineRecipe,
          fromCache: true,
          offline: true,
          lastUpdated: offlineRecipe.last_updated
        };
      }
      throw new Error('Recipe not found offline');
    }
  }

  async saveRecipe(recipe: any): Promise<ApiResponse<any>> {
    const url = '/api/recipes';
    const isOffline = !navigator.onLine;

    if (isOffline) {
      // Store locally and queue for sync
      await offlineStorage.saveRecipe(recipe);
      await offlineStorage.addToOfflineQueue('save_recipe', recipe);
      
      return {
        data: recipe,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }

    try {
      const response = await this.request<any>(url, {
        method: 'POST',
        body: JSON.stringify(recipe),
      }, { offlineFirst: false });

      // Also store locally for offline access
      await offlineStorage.saveRecipe(recipe);

      return response;
    } catch (error) {
      // Fall back to offline storage
      await offlineStorage.saveRecipe(recipe);
      await offlineStorage.addToOfflineQueue('save_recipe', recipe);
      
      return {
        data: recipe,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }
  }

  // Meal plan methods
  async getMealPlans(): Promise<ApiResponse<any[]>> {
    const url = '/api/meal-plans';

    try {
      return await this.request<any[]>(url, {}, { offlineFirst: true });
    } catch (error) {
      // Fall back to offline storage
      const offlineMealPlans = await offlineStorage.getAllMealPlans();
      return {
        data: offlineMealPlans,
        fromCache: true,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }
  }

  async getMealPlan(id: string): Promise<ApiResponse<any>> {
    const url = `/api/meal-plans/${id}`;

    try {
      return await this.request<any>(url, {}, { offlineFirst: true });
    } catch (error) {
      // Fall back to offline storage
      const offlineMealPlan = await offlineStorage.getMealPlan(id);
      if (offlineMealPlan) {
        return {
          data: offlineMealPlan,
          fromCache: true,
          offline: true,
          lastUpdated: offlineMealPlan.last_updated
        };
      }
      throw new Error('Meal plan not found offline');
    }
  }

  async saveMealPlan(mealPlan: any): Promise<ApiResponse<any>> {
    const url = '/api/meal-plans';
    const isOffline = !navigator.onLine;

    if (isOffline) {
      // Store locally and queue for sync
      await offlineStorage.saveMealPlan(mealPlan);
      await offlineStorage.addToOfflineQueue('save_meal_plan', mealPlan);
      
      return {
        data: mealPlan,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }

    try {
      const response = await this.request<any>(url, {
        method: 'POST',
        body: JSON.stringify(mealPlan),
      }, { offlineFirst: false });

      // Also store locally for offline access
      await offlineStorage.saveMealPlan(mealPlan);

      return response;
    } catch (error) {
      // Fall back to offline storage
      await offlineStorage.saveMealPlan(mealPlan);
      await offlineStorage.addToOfflineQueue('save_meal_plan', mealPlan);
      
      return {
        data: mealPlan,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }
  }

  // User preferences methods
  async getUserPreferences(): Promise<ApiResponse<any>> {
    const url = '/api/user/preferences';

    try {
      return await this.request<any>(url, {}, { offlineFirst: true });
    } catch (error) {
      // Fall back to offline storage
      const offlinePreferences = await offlineStorage.getUserPreferences();
      if (offlinePreferences) {
        return {
          data: offlinePreferences,
          fromCache: true,
          offline: true,
          lastUpdated: offlinePreferences.last_updated
        };
      }
      throw new Error('User preferences not found offline');
    }
  }

  async saveUserPreferences(preferences: any): Promise<ApiResponse<any>> {
    const url = '/api/user/preferences';
    const isOffline = !navigator.onLine;

    if (isOffline) {
      // Store locally and queue for sync
      await offlineStorage.saveUserPreferences(preferences);
      await offlineStorage.addToOfflineQueue('save_preferences', preferences);
      
      return {
        data: preferences,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }

    try {
      const response = await this.request<any>(url, {
        method: 'PUT',
        body: JSON.stringify(preferences),
      }, { offlineFirst: false });

      // Also store locally for offline access
      await offlineStorage.saveUserPreferences(preferences);

      return response;
    } catch (error) {
      // Fall back to offline storage
      await offlineStorage.saveUserPreferences(preferences);
      await offlineStorage.addToOfflineQueue('save_preferences', preferences);
      
      return {
        data: preferences,
        fromCache: false,
        offline: true,
        lastUpdated: new Date().toISOString()
      };
    }
  }

  // Sync methods
  async syncOfflineData(): Promise<void> {
    if (!navigator.onLine) {
      throw new Error('Cannot sync while offline');
    }

    const queue = await offlineStorage.getOfflineQueue();
    
    for (const item of queue) {
      try {
        await this.syncQueueItem(item);
      } catch (error) {
        console.error('Failed to sync item:', item, error);
      }
    }

    // Clear queue after successful sync
    await offlineStorage.clearOfflineQueue();
  }

  private async syncQueueItem(item: any): Promise<void> {
    const { type, data } = item;

    switch (type) {
      case 'save_recipe':
        await this.saveRecipe(data);
        break;
      case 'save_meal_plan':
        await this.saveMealPlan(data);
        break;
      case 'save_preferences':
        await this.saveUserPreferences(data);
        break;
      default:
        console.warn('Unknown queue item type:', type);
    }
  }

  // Cache management
  private getCacheKey(url: string, options: RequestInit): string {
    const method = options.method || 'GET';
    const body = options.body ? JSON.stringify(options.body) : '';
    return `${method}:${url}:${body}`;
  }

  private getFromCache<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  private setCache(key: string, data: any, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  private buildQueryString(params: any): string {
    return Object.entries(params)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
      .join('&');
  }

  private async storeForOffline(url: string, data: any): Promise<void> {
    // Store data in IndexedDB based on URL pattern
    if (url.includes('/recipes')) {
      if (Array.isArray(data)) {
        for (const recipe of data) {
          await offlineStorage.saveRecipe(recipe);
        }
      } else {
        await offlineStorage.saveRecipe(data);
      }
    } else if (url.includes('/meal-plans')) {
      if (Array.isArray(data)) {
        for (const mealPlan of data) {
          await offlineStorage.saveMealPlan(mealPlan);
        }
      } else {
        await offlineStorage.saveMealPlan(data);
      }
    } else if (url.includes('/preferences')) {
      await offlineStorage.saveUserPreferences(data);
    }
  }

  // Clear all caches
  async clearCache(): Promise<void> {
    this.cache.clear();
    await offlineStorage.clearAllData();
  }

  // Get cache statistics
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Export singleton instance
export const offlineApiService = new OfflineApiService();
export default offlineApiService;


