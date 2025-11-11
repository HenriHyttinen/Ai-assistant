// @ts-nocheck
import React from 'react';
import './utils/consoleSuppression'; // Suppress non-critical console warnings
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SupabaseAuthProvider } from './contexts/SupabaseAuthContext';
import { AppProvider } from './contexts/AppContext';
import theme from './theme';
import SupabaseLogin from './pages/SupabaseLogin';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import Goals from './pages/Goals';
import Achievements from './pages/Achievements';
import Settings from './pages/Settings';
import ActivityHistory from './pages/ActivityHistory';
import Nutrition from './pages/Nutrition';
import DailyLogging from './pages/Nutrition/DailyLogging';
import Assistant from './pages/Assistant';
import DataExport from './pages/DataExport';
import DataConsent from './pages/DataConsent';
import Verify2FA from './pages/Verify2FA';
import VerifyEmail from './pages/VerifyEmail';
import OAuthCallback from './pages/OAuthCallback';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import ResponsiveLayout from './components/ResponsiveLayout';
import ProtectedRoute from './components/ProtectedRoute';
import OfflineIndicator from './components/OfflineIndicator';
import PWAInstallPrompt from './components/PWAInstallPrompt';
import { registerServiceWorker } from './utils/serviceWorker';

const App = () => {
  // Suppress React DevTools message in development
  if (process.env.NODE_ENV === 'development') {
    const originalConsoleLog = console.log;
    console.log = (...args) => {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('React DevTools')) {
        return;
      }
      originalConsoleLog(...args);
    };
  }

  // Register service worker for offline functionality
  React.useEffect(() => {
    registerServiceWorker({
      onUpdate: (registration) => {
        console.log('New content available, please refresh');
        // You could show a notification to the user here
      },
      onSuccess: (registration) => {
        console.log('Service Worker registered successfully');
      },
      onOfflineReady: () => {
        console.log('App is ready for offline use');
      },
    });
  }, []);

  return (
    <ChakraProvider theme={theme}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <SupabaseAuthProvider>
          <AppProvider>
            <OfflineIndicator showDetails={true} />
            <PWAInstallPrompt />
            <Routes>
              <Route path="/login" element={<SupabaseLogin />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/verify-2fa" element={<Verify2FA />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/oauth/callback" element={<OAuthCallback />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <ResponsiveLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="profile" element={<Profile />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="activities" element={<ActivityHistory />} />
                <Route path="nutrition" element={<Nutrition />} />
                <Route path="nutrition/daily-logging" element={<DailyLogging />} />
                <Route path="assistant" element={<Assistant />} />
                <Route path="goals" element={<Goals />} />
                <Route path="achievements" element={<Achievements />} />
                <Route path="settings" element={<Settings />} />
                <Route path="export" element={<DataExport />} />
                <Route path="consent" element={<DataConsent />} />
              </Route>
            </Routes>
          </AppProvider>
        </SupabaseAuthProvider>
      </Router>
    </ChakraProvider>
  );
};

export default App;
