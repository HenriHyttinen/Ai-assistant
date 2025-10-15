// @ts-nocheck
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  two_factor_enabled: boolean;
  oauth_provider?: 'google' | 'github';
  profile_picture?: string;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  verify2FA: (email: string, code: string) => Promise<void>;
  setup2FA: () => Promise<{ secret: string; qr_code: string }>;
  verify2FASetup: (code: string) => Promise<void>;
  disable2FA: (code: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authService.getProfile()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      const response = await authService.login({ email, password });
      
      if (response.requires_2fa) {
        navigate('/verify-2fa', { state: { email } });
        return;
      }

      localStorage.setItem('token', response.access_token);
      const userData = await authService.getProfile();
      setUser(userData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      setError(null);
      const response = await authService.register({ email, password });
      localStorage.setItem('token', response.access_token);
      setUser(response.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/login');
  };

  const verify2FA = async (email: string, code: string) => {
    try {
      setError(null);
      const response = await authService.verify2FA({ email, code });
      localStorage.setItem('token', response.access_token);
      setUser(response.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || '2FA verification failed');
      throw err;
    }
  };

  const setup2FA = async () => {
    try {
      setError(null);
      return await authService.setup2FA();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup 2FA');
      throw err;
    }
  };

  const verify2FASetup = async (code: string) => {
    try {
      setError(null);
      await authService.verify2FASetup({ code });
      if (user) {
        setUser({ ...user, is_2fa_enabled: true });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify 2FA setup');
      throw err;
    }
  };

  const disable2FA = async (code: string) => {
    try {
      setError(null);
      await authService.disable2FA({ code });
      if (user) {
        setUser({ ...user, is_2fa_enabled: false });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disable 2FA');
      throw err;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        register,
        logout,
        verify2FA,
        setup2FA,
        verify2FASetup,
        disable2FA,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 