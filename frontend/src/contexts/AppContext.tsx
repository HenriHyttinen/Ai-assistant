import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from 'react';
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
}

const AppContext = createContext<AppContextType | undefined>(undefined);

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

      // Prevent multiple calls - use user ID as part of the key
      const currentUserId = user.id;
      if (settingsLoadedRef.current === currentUserId) {
        return;
      }

      settingsLoadedRef.current = currentUserId;
      
      if (!user.id || !user.email) {
        console.log('User not fully authenticated, skipping settings API call');
        setLoading(false);
        return;
      }
      
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
  }, [user?.id]); // Use user.id instead of entire user object to prevent unnecessary re-renders

  const handleSetLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    setLanguage(newLanguage);
  };

  const handleSetMeasurementSystem = (newSystem: 'metric' | 'imperial') => {
    setMeasurementSystemState(newSystem);
  };

  return (
    <AppContext.Provider
      value={{
        language,
        measurementSystem,
        setLanguage: handleSetLanguage,
        setMeasurementSystem: handleSetMeasurementSystem,
        loading,
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
