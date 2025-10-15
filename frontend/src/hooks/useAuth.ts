import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFormSubmit } from './useFormSubmit';
import { auth } from '../services/api';
import { AuthContext } from '../contexts/AuthContext';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
}

export function useAuth() {
  const context = useContext(AuthContext);
  const navigate = useNavigate();

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  const { user, loading, error, clearError } = context;

  const login = useFormSubmit<LoginData>(async (data) => {
    const response = await auth.login(data.email, data.password);
    localStorage.setItem('token', response.data.token);
    navigate('/dashboard');
  });

  const register = useFormSubmit<RegisterData>(async (data) => {
    const response = await auth.register(data.name, data.email, data.password);
    localStorage.setItem('token', response.data.token);
    navigate('/dashboard');
  });

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return {
    user,
    loading,
    error,
    clearError,
    login,
    register,
    logout,
  };
}

export default useAuth; 