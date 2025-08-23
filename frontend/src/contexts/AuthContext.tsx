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
  sessionToken: string | null;
  isLoading: boolean;
  signup: (email: string, password: string, name: string) => Promise<void>;
  signin: (email: string, password: string) => Promise<void>;
  signout: () => void;
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
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Configure axios defaults
  axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com';
  axios.defaults.withCredentials = true; // Important for sending cookies with requests

  const signup = async (email: string, password: string, name: string) => {
    try {
      const response = await axios.post('/api/auth/signup', {
        email,
        password,
        name
      });

      const { user: newUser, session_token } = response.data;
      setUser(newUser);
      setSessionToken(session_token);
      localStorage.setItem('sessionToken', session_token);
      
      // Set default authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${session_token}`;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Signup failed');
    }
  };

  const signin = async (email: string, password: string) => {
    try {
      const response = await axios.post('/api/auth/signin', {
        email,
        password
      });

      const { user: signedInUser, session_token } = response.data;
      setUser(signedInUser);
      setSessionToken(session_token);
      localStorage.setItem('sessionToken', session_token);
      
      // Set default authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${session_token}`;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Signin failed');
    }
  };

  const signout = async () => {
    try {
      if (sessionToken) {
        await axios.post('/api/auth/logout', {}, {
          headers: { Authorization: `Bearer ${sessionToken}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setSessionToken(null);
      localStorage.removeItem('sessionToken');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const checkSession = async () => {
    try {
      // First try to check if we have a backend session (for OAuth users)
      try {
        const response = await axios.get('/auth/user', { withCredentials: true });
        if (response.data && response.data.email) {
          // We have a backend session, create a local session
          const user = {
            id: response.data.id || 'oauth_user',
            email: response.data.email,
            name: response.data.name,
            is_google_user: true
          };
          setUser(user);
          setIsLoading(false);
          return;
        }
      } catch (backendError) {
        console.log('No backend session found, checking local token...');
        // No backend session, continue to check local token
      }

      // Check local session token
      const token = localStorage.getItem('sessionToken');
      if (!token) {
        setIsLoading(false);
        return;
      }

      setSessionToken(token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      const response = await axios.get('/api/auth/session');
      setUser(response.data.user);
    } catch (error) {
      console.error('Session check failed:', error);
      localStorage.removeItem('sessionToken');
      delete axios.defaults.headers.common['Authorization'];
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
    sessionToken,
    isLoading,
    signup,
    signin,
    signout,
    checkSession
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
