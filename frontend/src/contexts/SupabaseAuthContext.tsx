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
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
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
    const { error } = await supabase.auth.signOut();
    return { error };
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