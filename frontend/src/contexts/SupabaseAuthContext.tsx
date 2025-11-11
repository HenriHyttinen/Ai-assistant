import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthError } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase.ts';

interface SupabaseAuthContextType {
  user: any | null;
  session: any | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<{ user: any | null; error: AuthError | null }>;
  signIn: (email: string, password: string) => Promise<{ user: any | null; error: AuthError | null }>;
  signInWithGitHub: () => Promise<{ user: any | null; error: AuthError | null }>;
  signInWithGoogle: () => Promise<{ user: any | null; error: AuthError | null }>;
  signInWithFacebook: () => Promise<{ user: any | null; error: AuthError | null }>;
  signInWithApple: () => Promise<{ user: any | null; error: AuthError | null }>;
  signInWithDiscord: () => Promise<{ user: any | null; error: AuthError | null }>;
  signOut: () => Promise<{ error: AuthError | null }>;
  error: string | null;
  clearError: () => void;
}

const SupabaseAuthContext = createContext<SupabaseAuthContextType | undefined>(undefined);

export const useSupabaseAuth = () => {
  const context = useContext(SupabaseAuthContext);
  if (context === undefined) {
    throw new Error('useSupabaseAuth must be used within a SupabaseAuthProvider');
  }
  return context;
};

interface SupabaseAuthProviderProps {
  children: React.ReactNode;
}

export const SupabaseAuthProvider: React.FC<SupabaseAuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [session, setSession] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      // Only update state if we have a session, or if it's a SIGNED_OUT event
      // This prevents temporary null sessions during token refresh from clearing the user
      if (session || event === 'SIGNED_OUT') {
        setSession(session);
        setUser(session?.user ?? null);
      }
      // Only set loading to false if we have a definitive state
      if (event === 'SIGNED_IN' || event === 'SIGNED_OUT' || event === 'TOKEN_REFRESHED') {
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string) => {
    setError(null);
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });
    return { user: data?.user || null, error };
  };

  const signIn = async (email: string, password: string) => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { user: data?.user || null, error };
  };

  const signInWithGitHub = async () => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });
    return { user: data?.user || null, error };
  };

  const signInWithGoogle = async () => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });
    return { user: data?.user || null, error };
  };

  const signInWithFacebook = async () => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'facebook',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });
    return { user: data?.user || null, error };
  };

  const signInWithApple = async () => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'apple',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });
    return { user: data?.user || null, error };
  };

  const signInWithDiscord = async () => {
    setError(null);
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'discord',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });
    return { user: data?.user || null, error };
  };

  const signOut = async () => {
    setError(null);
    try {
      // Sign out from Supabase first
      const { error } = await supabase.auth.signOut();
      
      // Clear only authentication-related storage
      // Don't clear all localStorage as it may contain cached data
      localStorage.removeItem('supabase.auth.token');
      localStorage.removeItem('supabase.auth.refresh_token');
      
      // Clear session storage
      sessionStorage.clear();
      
      // Clear state immediately
      setUser(null);
      setSession(null);
      
      return { error };
    } catch (err: any) {
      setError(err.message || 'Failed to sign out');
      return { error: err };
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signInWithGitHub,
    signInWithGoogle,
    signInWithFacebook,
    signInWithApple,
    signInWithDiscord,
    signOut,
    error,
    clearError,
  };

  return (
    <SupabaseAuthContext.Provider value={value}>
      {children}
    </SupabaseAuthContext.Provider>
  );
};