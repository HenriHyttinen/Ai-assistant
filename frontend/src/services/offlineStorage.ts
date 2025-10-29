// IndexedDB service for offline storage
// Stores recipes, meal plans, and user data locally

interface Recipe {
  id: string;
  title: string;
  cuisine: string;
  meal_type: string;
  servings: number;
  prep_time: number;
  cook_time: number;
  difficulty_level: string;
  dietary_tags: string[];
  image_url?: string;
  ingredients: any[];
  instructions: any[];
  nutrition: any;
  last_updated: string;
  offline_synced: boolean;
}

interface MealPlan {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  meals: any[];
  created_at: string;
  last_updated: string;
  offline_synced: boolean;
}

interface UserPreferences {
  id: string;
  dietary_preferences: string[];
  allergies: string[];
  disliked_ingredients: string[];
  cuisine_preferences: string[];
  daily_calorie_target: number;
  protein_target: number;
  carbs_target: number;
  fats_target: number;
  last_updated: string;
  offline_synced: boolean;
}

class OfflineStorageService {
  private dbName = 'NumbersDontLieDB';
  private version = 1;
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => {
        console.error('Failed to open IndexedDB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('IndexedDB opened successfully');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        this.createObjectStores(db);
      };
    });
  }

  private createObjectStores(db: IDBDatabase): void {
    // Recipes store
    if (!db.objectStoreNames.contains('recipes')) {
      const recipesStore = db.createObjectStore('recipes', { keyPath: 'id' });
      recipesStore.createIndex('cuisine', 'cuisine', { unique: false });
      recipesStore.createIndex('meal_type', 'meal_type', { unique: false });
      recipesStore.createIndex('last_updated', 'last_updated', { unique: false });
      recipesStore.createIndex('offline_synced', 'offline_synced', { unique: false });
    }

    // Meal plans store
    if (!db.objectStoreNames.contains('meal_plans')) {
      const mealPlansStore = db.createObjectStore('meal_plans', { keyPath: 'id' });
      mealPlansStore.createIndex('start_date', 'start_date', { unique: false });
      mealPlansStore.createIndex('end_date', 'end_date', { unique: false });
      mealPlansStore.createIndex('last_updated', 'last_updated', { unique: false });
      mealPlansStore.createIndex('offline_synced', 'offline_synced', { unique: false });
    }

    // User preferences store
    if (!db.objectStoreNames.contains('user_preferences')) {
      const preferencesStore = db.createObjectStore('user_preferences', { keyPath: 'id' });
      preferencesStore.createIndex('last_updated', 'last_updated', { unique: false });
      preferencesStore.createIndex('offline_synced', 'offline_synced', { unique: false });
    }

    // Offline queue store (for syncing when online)
    if (!db.objectStoreNames.contains('offline_queue')) {
      const queueStore = db.createObjectStore('offline_queue', { keyPath: 'id', autoIncrement: true });
      queueStore.createIndex('type', 'type', { unique: false });
      queueStore.createIndex('timestamp', 'timestamp', { unique: false });
    }
  }

  // Recipe methods
  async saveRecipe(recipe: Recipe): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['recipes'], 'readwrite');
      const store = transaction.objectStore('recipes');
      
      const recipeData = {
        ...recipe,
        last_updated: new Date().toISOString(),
        offline_synced: false
      };

      const request = store.put(recipeData);

      request.onsuccess = () => {
        console.log('Recipe saved offline:', recipe.id);
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to save recipe:', request.error);
        reject(request.error);
      };
    });
  }

  async getRecipe(id: string): Promise<Recipe | null> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['recipes'], 'readonly');
      const store = transaction.objectStore('recipes');
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result || null);
      };

      request.onerror = () => {
        console.error('Failed to get recipe:', request.error);
        reject(request.error);
      };
    });
  }

  async getAllRecipes(): Promise<Recipe[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['recipes'], 'readonly');
      const store = transaction.objectStore('recipes');
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        console.error('Failed to get recipes:', request.error);
        reject(request.error);
      };
    });
  }

  async searchRecipes(query: string, filters?: any): Promise<Recipe[]> {
    const allRecipes = await this.getAllRecipes();
    
    let filtered = allRecipes.filter(recipe => 
      recipe.title.toLowerCase().includes(query.toLowerCase()) ||
      recipe.cuisine.toLowerCase().includes(query.toLowerCase()) ||
      recipe.meal_type.toLowerCase().includes(query.toLowerCase())
    );

    if (filters) {
      if (filters.cuisine) {
        filtered = filtered.filter(recipe => recipe.cuisine === filters.cuisine);
      }
      if (filters.meal_type) {
        filtered = filtered.filter(recipe => recipe.meal_type === filters.meal_type);
      }
      if (filters.difficulty) {
        filtered = filtered.filter(recipe => recipe.difficulty_level === filters.difficulty);
      }
      if (filters.dietary_tags && filters.dietary_tags.length > 0) {
        filtered = filtered.filter(recipe => 
          filters.dietary_tags.some((tag: string) => 
            recipe.dietary_tags.includes(tag)
          )
        );
      }
    }

    return filtered;
  }

  // Meal plan methods
  async saveMealPlan(mealPlan: MealPlan): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['meal_plans'], 'readwrite');
      const store = transaction.objectStore('meal_plans');
      
      const mealPlanData = {
        ...mealPlan,
        last_updated: new Date().toISOString(),
        offline_synced: false
      };

      const request = store.put(mealPlanData);

      request.onsuccess = () => {
        console.log('Meal plan saved offline:', mealPlan.id);
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to save meal plan:', request.error);
        reject(request.error);
      };
    });
  }

  async getMealPlan(id: string): Promise<MealPlan | null> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['meal_plans'], 'readonly');
      const store = transaction.objectStore('meal_plans');
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result || null);
      };

      request.onerror = () => {
        console.error('Failed to get meal plan:', request.error);
        reject(request.error);
      };
    });
  }

  async getAllMealPlans(): Promise<MealPlan[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['meal_plans'], 'readonly');
      const store = transaction.objectStore('meal_plans');
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        console.error('Failed to get meal plans:', request.error);
        reject(request.error);
      };
    });
  }

  // User preferences methods
  async saveUserPreferences(preferences: UserPreferences): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['user_preferences'], 'readwrite');
      const store = transaction.objectStore('user_preferences');
      
      const preferencesData = {
        ...preferences,
        last_updated: new Date().toISOString(),
        offline_synced: false
      };

      const request = store.put(preferencesData);

      request.onsuccess = () => {
        console.log('User preferences saved offline');
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to save user preferences:', request.error);
        reject(request.error);
      };
    });
  }

  async getUserPreferences(): Promise<UserPreferences | null> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['user_preferences'], 'readonly');
      const store = transaction.objectStore('user_preferences');
      const request = store.get('default');

      request.onsuccess = () => {
        resolve(request.result || null);
      };

      request.onerror = () => {
        console.error('Failed to get user preferences:', request.error);
        reject(request.error);
      };
    });
  }

  // Offline queue methods
  async addToOfflineQueue(type: string, data: any): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offline_queue'], 'readwrite');
      const store = transaction.objectStore('offline_queue');
      
      const queueItem = {
        type,
        data,
        timestamp: new Date().toISOString()
      };

      const request = store.add(queueItem);

      request.onsuccess = () => {
        console.log('Added to offline queue:', type);
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to add to offline queue:', request.error);
        reject(request.error);
      };
    });
  }

  async getOfflineQueue(): Promise<any[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offline_queue'], 'readonly');
      const store = transaction.objectStore('offline_queue');
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        console.error('Failed to get offline queue:', request.error);
        reject(request.error);
      };
    });
  }

  async clearOfflineQueue(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offline_queue'], 'readwrite');
      const store = transaction.objectStore('offline_queue');
      const request = store.clear();

      request.onsuccess = () => {
        console.log('Offline queue cleared');
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to clear offline queue:', request.error);
        reject(request.error);
      };
    });
  }

  // Utility methods
  async isOffline(): Promise<boolean> {
    return !navigator.onLine;
  }

  async getStorageUsage(): Promise<{ used: number; available: number }> {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      return {
        used: estimate.usage || 0,
        available: estimate.quota || 0
      };
    }
    return { used: 0, available: 0 };
  }

  async clearAllData(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(
        ['recipes', 'meal_plans', 'user_preferences', 'offline_queue'], 
        'readwrite'
      );

      const clearPromises = [
        transaction.objectStore('recipes').clear(),
        transaction.objectStore('meal_plans').clear(),
        transaction.objectStore('user_preferences').clear(),
        transaction.objectStore('offline_queue').clear()
      ];

      Promise.all(clearPromises)
        .then(() => {
          console.log('All offline data cleared');
          resolve();
        })
        .catch((error) => {
          console.error('Failed to clear offline data:', error);
          reject(error);
        });
    });
  }
}

// Export singleton instance
export const offlineStorage = new OfflineStorageService();
export default offlineStorage;


