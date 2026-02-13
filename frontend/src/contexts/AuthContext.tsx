import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  name: string;
  is_google_user?: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signout: () => Promise<void>;
  checkSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Configure axios defaults
  axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com';
  axios.defaults.withCredentials = true; // Important for sending cookies with requests

  const signout = async () => {
    try {
      await axios.get('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const checkSession = async () => {
    try {
      const response = await axios.get('/auth/user', { withCredentials: true });
      if (response.data && response.data.email) {
        setUser({
          id: response.data.id || 'oauth_user',
          email: response.data.email,
          name: response.data.name,
          is_google_user: true
        });
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Set axios base URL from environment variable
    const apiUrl = process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com';
    axios.defaults.baseURL = apiUrl;
    
    // Check if user is already authenticated
    checkSession();
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    signout,
    checkSession
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
