// @ts-nocheck
import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import theme from './theme';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import Goals from './pages/Goals';
import Settings from './pages/Settings';
import DataExport from './pages/DataExport';
import Verify2FA from './pages/Verify2FA';
import VerifyEmail from './pages/VerifyEmail';
import OAuthCallback from './pages/OAuthCallback';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <ChakraProvider theme={theme}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
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
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="profile" element={<Profile />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="goals" element={<Goals />} />
              <Route path="settings" element={<Settings />} />
              <Route path="export" element={<DataExport />} />
            </Route>
            </Routes>
        </AuthProvider>
      </Router>
    </ChakraProvider>
  );
};

export default App;
