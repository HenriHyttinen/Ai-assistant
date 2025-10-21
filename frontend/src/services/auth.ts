// @ts-nocheck
import api from './api';
import type { User } from '../types/index';

interface LoginResponse {
  access_token: string;
  token_type: string;
  requires_2fa: boolean;
}

interface RegisterData {
  email: string;
  password: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface Verify2FAData {
  email: string;
  code: string;
}

interface Setup2FAData {
  code: string;
}

interface Setup2FAResponse {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

interface PasswordResetData {
  email: string;
}

interface PasswordResetConfirmData {
  token: string;
  new_password: string;
}

export const authService = {
  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginData) => {
    const response = await api.post('/auth/token', {
      email: data.email,
      password: data.password
    });
    return response.data;
  },

  verify2FA: async (data: Verify2FAData) => {
    const response = await api.post('/auth/verify-2fa', data);
    return response.data;
  },

  setup2FA: async (): Promise<Setup2FAResponse> => {
    const response = await api.post('/auth/setup-2fa');
    return response.data;
  },

  verify2FASetup: async (data: Setup2FAData) => {
    const response = await api.post('/auth/verify-2fa-setup', data);
    return response.data;
  },

  disable2FA: async (data: Setup2FAData) => {
    const response = await api.post('/auth/disable-2fa', data);
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const response = await api.post('/auth/reset-password', null, { params: { email } });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post(`/auth/reset-password/${token}`, null, { 
      params: { new_password: newPassword } 
    });
    return response.data;
  },

  resetPasswordWith2FA: async (email: string, backupCode: string, newPassword: string) => {
    const response = await api.post('/auth/reset-password-with-2fa', null, {
      params: {
        email,
        backup_code: backupCode,
        new_password: newPassword
      }
    });
    return response.data;
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  updateProfile: async (data: any) => {
    const response = await api.put('/auth/profile', data);
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  deleteAccount: async () => {
    const response = await api.delete('/auth/delete-account');
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  async verifyEmail(token: string): Promise<void> {
    await api.post(`/auth/verify-email/${token}`);
  },

  async resendVerificationEmail(): Promise<void> {
    await api.post('/auth/resend-verification');
  },

  async loginWithOAuth(provider: 'google' | 'github'): Promise<LoginResponse> {
    const response = await api.get(`/auth/oauth/${provider}`);
    return response.data;
  }
}; 