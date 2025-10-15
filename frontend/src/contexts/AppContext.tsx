import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { settings } from '../services/api';
import { useAuth } from './AuthContext';

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
  const { user } = useAuth();
  const [language, setLanguageState] = useState<Language>('en');
  const [measurementSystem, setMeasurementSystemState] = useState<'metric' | 'imperial'>('metric');
  const [loading, setLoading] = useState(true);

  // Load settings when user is authenticated
  useEffect(() => {
    const loadSettings = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const response = await settings.getSettings();
        const { language: userLanguage, measurementSystem: userMeasurementSystem } = response.data;
        
        setLanguageState(userLanguage);
        setLanguage(userLanguage);
        setMeasurementSystemState(userMeasurementSystem);
      } catch (error) {
        // Settings not found, using defaults
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [user]);

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
