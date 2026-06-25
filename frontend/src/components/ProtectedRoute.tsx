import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="auth-bg grid min-h-screen place-items-center p-4">
        <div className="card flex w-full max-w-xs flex-col items-center p-8 text-center glow-indigo-sm">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl border border-teal-300/20 bg-teal-400/15 text-teal-200">
            <Mail className="h-6 w-6" />
          </div>
          <div className="spinner" />
          <p className="mt-4 text-sm font-medium text-zinc-300">Loading workspace</p>
          <p className="mt-1 text-xs text-zinc-600">Checking your session</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/signin" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
