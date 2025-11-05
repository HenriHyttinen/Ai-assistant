import { createContext, useContext, useState, useEffect, useRef, useMemo, type ReactNode } from 'react';
import { useSupabaseAuth } from './SupabaseAuthContext';
import { settings } from '../services/api';

// Inline types to avoid module loading issues
type Language = 'en' | 'es' | 'fr' | 'de';

// Simple language functions
// let currentLanguage: Language = 'en';
const setLanguage = (language: Language) => { /* currentLanguage = language; */ };
// const getLanguage = (): Language => currentLanguage;

interface AppContextType {
  language: Language;
  measurementSystem: 'metric' | 'imperial';
  setLanguage: (language: Language) => void;
  setMeasurementSystem: (system: 'metric' | 'imperial') => void;
  loading: boolean;
  user: any | null; // Allow user to be null
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Export AppContext as a named export
export { AppContext };

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const { user } = useSupabaseAuth();
  const [language, setLanguageState] = useState<Language>('en');
  const [measurementSystem, setMeasurementSystemState] = useState<'metric' | 'imperial'>('metric');
  const [loading, setLoading] = useState(true);
  const settingsLoadedRef = useRef<string | boolean>(false);
  const lastErrorTimeRef = useRef<number>(0);

  // Load settings when user is authenticated
  useEffect(() => {
    const loadSettings = async () => {
      if (!user) {
        setLoading(false);
        settingsLoadedRef.current = false;
        return;
      }
      
      // Only load settings if user is authenticated and we haven't loaded them yet
      if (settingsLoadedRef.current === user.id) {
        return;
      }

      if (!user.id || !user.email) {
        console.log('User not fully authenticated, skipping settings API call');
        setLoading(false);
        return;
      }

      // Double-check authentication with Supabase
      try {
        const { supabase } = await import('@/lib/supabase');
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session?.access_token) {
          console.log('No valid session, skipping settings API call');
          setLoading(false);
          return;
        }
      } catch (error) {
        console.log('Error checking session, skipping settings API call:', error);
        setLoading(false);
        return;
      }

      settingsLoadedRef.current = user.id;
      
      await new Promise(resolve => setTimeout(resolve, 100));

      const now = Date.now();
      if (lastErrorTimeRef.current > 0 && (now - lastErrorTimeRef.current) < 5000) {
        console.log('Circuit breaker: Too many recent errors, skipping settings API call');
        setLoading(false);
        return;
      }
      
      try {
        const response = await settings.getSettings();
        const settingsData = response.data;
        
        if (settingsData) {
          setLanguageState(settingsData.language || 'en');
          setLanguage(settingsData.language || 'en');
          setMeasurementSystemState(settingsData.measurementSystem || 'metric');
        } else {
          // Use defaults if no settings found
          setLanguageState('en');
          setLanguage('en');
          setMeasurementSystemState('metric');
        }
      } catch (error) {
        console.warn('Failed to load settings, using defaults:', error);
        // Use defaults on error
        setLanguageState('en');
        setLanguage('en');
        setMeasurementSystemState('metric');
      }
      
      setLoading(false);
    };

    loadSettings();
  }, [user?.id, user?.email]); // Use specific user properties to prevent unnecessary re-renders

  const handleSetLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    setLanguage(newLanguage);
  };

  const handleSetMeasurementSystem = (newSystem: 'metric' | 'imperial') => {
    setMeasurementSystemState(newSystem);
  };

  // Memoize the user object to prevent unnecessary re-renders
  const stableUser = useMemo(() => {
    if (!user) return null;
    return {
      id: user.id,
      email: user.email,
      // Only include essential properties to prevent object reference changes
    };
  }, [user?.id, user?.email]);

  return (
    <AppContext.Provider
      value={{
        language,
        measurementSystem,
        setLanguage: handleSetLanguage,
        setMeasurementSystem: handleSetMeasurementSystem,
        loading,
        user: stableUser,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
