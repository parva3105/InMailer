import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { AlertCircle, CheckCircle, Mail } from 'lucide-react';

const AuthSuccess: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { checkSession } = useAuth();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processOAuthSuccess = async () => {
      try {
        setIsProcessing(true);
        const email = searchParams.get('email');
        const name = searchParams.get('name');

        if (!email || !name) {
          setError('Missing authentication information');
          return;
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
        await checkSession();
        await new Promise(resolve => setTimeout(resolve, 1000));
        navigate('/dashboard', { replace: true });
      } catch {
        setError('Failed to complete authentication. Please try again.');
      } finally {
        setIsProcessing(false);
      }
    };

    processOAuthSuccess();
  }, [searchParams, checkSession, navigate]);

  if (error) {
    return (
      <div className="auth-bg grid min-h-screen place-items-center p-4">
        <div className="card w-full max-w-sm p-8 text-center">
          <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-xl border border-red-500/20 bg-red-500/10">
            <AlertCircle className="h-6 w-6 text-red-400" />
          </div>
          <h1 className="mb-2 text-lg font-semibold text-zinc-100">Authentication failed</h1>
          <p className="mb-6 text-sm text-zinc-500">{error}</p>
          <button onClick={() => navigate('/signin')} className="btn-primary w-full">
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-bg grid-overlay grid min-h-screen place-items-center p-4">
      <div className="hero-orb" aria-hidden="true" />
      <div className="card relative z-10 w-full max-w-sm p-8 text-center glow-indigo-sm">
        <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-xl border border-teal-300/20 bg-teal-400/15 text-teal-200">
          {isProcessing ? <Mail className="h-6 w-6 animate-pulse" /> : <CheckCircle className="h-6 w-6 text-emerald-400" />}
        </div>
        <h1 className="mb-2 text-lg font-semibold text-zinc-100">
          {isProcessing ? 'Completing sign in...' : "You're in"}
        </h1>
        <p className="text-sm text-zinc-500">
          {isProcessing ? 'Setting up your session, just a moment.' : 'Redirecting to your dashboard...'}
        </p>
        {isProcessing && <div className="mt-6 flex justify-center"><div className="spinner" /></div>}
      </div>
    </div>
  );
};

export default AuthSuccess;
