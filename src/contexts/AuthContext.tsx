'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import authService from '@/services/auth';
import { AUTH, TIME } from '@/lib/constants';

interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (data: {
    email: string;
    password: string;
    full_name: string;
    phone_number: string;
  }) => Promise<void>;
  signOut: () => void;
  checkSession: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const SESSION_TIMEOUT = AUTH.SESSION_TIMEOUT;
const ACTIVITY_CHECK_INTERVAL = AUTH.ACTIVITY_CHECK_INTERVAL;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastActivity, setLastActivity] = useState(Date.now());
  const router = useRouter();

  // Track user activity
  const updateLastActivity = () => {
    setLastActivity(Date.now());
  };

  // Listen for user activity
  useEffect(() => {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    
    events.forEach(event => {
      document.addEventListener(event, updateLastActivity);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateLastActivity);
      });
    };
  }, []);

  // Check for session timeout
  useEffect(() => {
    const checkTimeout = setInterval(() => {
      if (user && Date.now() - lastActivity > SESSION_TIMEOUT) {
        console.log('Session timeout - signing out user');
        signOut();
        alert('Your session has expired. Please sign in again.');
      }
    }, ACTIVITY_CHECK_INTERVAL);

    return () => clearInterval(checkTimeout);
  }, [user, lastActivity]);

  // Check if user is already signed in on mount
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const token = authService.getToken();
      if (token) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Session check failed:', error);
      // Only remove token if it's an authentication error
      if (error instanceof Error && error.message.includes('unauthorized')) {
        authService.removeToken();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const authResponse = await authService.signIn({ email, password });
      const userData = await authService.getCurrentUser();
      setUser(userData);
      updateLastActivity();
      // Don't redirect here - let the signin page handle redirect
      // router.push('/');
    } catch (error) {
      throw error;
    }
  };

  const signUp = async (data: {
    email: string;
    password: string;
    full_name: string;
    phone_number: string;
  }) => {
    try {
      const userResponse = await authService.signUp(data);
      // Sign in after successful registration
      await signIn(data.email, data.password);
    } catch (error) {
      throw error;
    }
  };

  const signOut = () => {
    authService.signOut();
    setUser(null);
    // Don't redirect here - let components handle their own redirects
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        signIn,
        signUp,
        signOut,
        checkSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
