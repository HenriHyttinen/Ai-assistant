import { useState, useCallback, useRef } from 'react';

interface NutritionState {
  // Recipe Search State
  recipes: any[];
  totalResults: number;
  totalPages: number;
  currentPage: number;
  loading: boolean;
  error: string | null;
  
  // Filters
  searchQuery: string;
  filters: {
    cuisine: string;
    mealType: string;
    difficulty: string;
    maxCalories: string;
    maxPrepTime: string;
    dietaryTags: string[];
  };
  
  // Sorting
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  
  // Meal Planning State
  mealPlans: any[];
  selectedDate: string;
  preferences: any;
}

interface NutritionActions {
  // Recipe Search Actions
  setRecipes: (recipes: any[]) => void;
  setTotalResults: (total: number) => void;
  setTotalPages: (pages: number) => void;
  setCurrentPage: (page: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Filter Actions
  setSearchQuery: (query: string) => void;
  setFilters: (filters: Partial<NutritionState['filters']>) => void;
  setSortBy: (sortBy: string) => void;
  setSortOrder: (order: 'asc' | 'desc') => void;
  
  // Meal Planning Actions
  setMealPlans: (plans: any[]) => void;
  setSelectedDate: (date: string) => void;
  setPreferences: (preferences: any) => void;
  
  // Combined Actions
  resetRecipeSearch: () => void;
  updateRecipeSearch: (updates: Partial<NutritionState>) => void;
}

export function useNutritionState(): [NutritionState, NutritionActions] {
  // Centralized state
  const [state, setState] = useState<NutritionState>({
    // Recipe Search
    recipes: [],
    totalResults: 0,
    totalPages: 0,
    currentPage: 1,
    loading: false,
    error: null,
    
    // Filters
    searchQuery: '',
    filters: {
      cuisine: '',
      mealType: '',
      difficulty: '',
      maxCalories: '',
      maxPrepTime: '',
      dietaryTags: [],
    },
    
    // Sorting
    sortBy: 'id',
    sortOrder: 'asc',
    
    // Meal Planning
    mealPlans: [],
    selectedDate: new Date().toISOString().split('T')[0],
    preferences: null,
  });

  // Prevent unnecessary re-renders
  const stateRef = useRef(state);
  stateRef.current = state;

  // Actions
  const actions: NutritionActions = {
    setRecipes: useCallback((recipes: any[]) => {
      setState(prev => ({ ...prev, recipes }));
    }, []),

    setTotalResults: useCallback((total: number) => {
      setState(prev => ({ ...prev, totalResults: total }));
    }, []),

    setTotalPages: useCallback((pages: number) => {
      setState(prev => ({ ...prev, totalPages: pages }));
    }, []),

    setCurrentPage: useCallback((page: number) => {
      setState(prev => ({ ...prev, currentPage: page }));
    }, []),

    setLoading: useCallback((loading: boolean) => {
      setState(prev => ({ ...prev, loading }));
    }, []),

    setError: useCallback((error: string | null) => {
      setState(prev => ({ ...prev, error }));
    }, []),

    setSearchQuery: useCallback((query: string) => {
      setState(prev => ({ ...prev, searchQuery: query }));
    }, []),

    setFilters: useCallback((filters: Partial<NutritionState['filters']>) => {
      setState(prev => ({ 
        ...prev, 
        filters: { ...prev.filters, ...filters } 
      }));
    }, []),

    setSortBy: useCallback((sortBy: string) => {
      setState(prev => ({ ...prev, sortBy }));
    }, []),

    setSortOrder: useCallback((order: 'asc' | 'desc') => {
      setState(prev => ({ ...prev, sortOrder: order }));
    }, []),

    setMealPlans: useCallback((plans: any[]) => {
      setState(prev => ({ ...prev, mealPlans: plans }));
    }, []),

    setSelectedDate: useCallback((date: string) => {
      setState(prev => ({ ...prev, selectedDate: date }));
    }, []),

    setPreferences: useCallback((preferences: any) => {
      setState(prev => ({ ...prev, preferences }));
    }, []),

    resetRecipeSearch: useCallback(() => {
      setState(prev => ({
        ...prev,
        recipes: [],
        totalResults: 0,
        totalPages: 0,
        currentPage: 1,
        error: null,
      }));
    }, []),

    updateRecipeSearch: useCallback((updates: Partial<NutritionState>) => {
      setState(prev => ({ ...prev, ...updates }));
    }, []),
  };

  return [state, actions];
}









