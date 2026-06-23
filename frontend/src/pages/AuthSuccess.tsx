import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, CheckCircle, AlertCircle } from 'lucide-react';

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
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
        <div className="card p-8 max-w-sm w-full text-center">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-5">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <h1 className="text-lg font-semibold text-zinc-100 mb-2">Authentication failed</h1>
          <p className="text-sm text-zinc-500 mb-6">{error}</p>
          <button
            onClick={() => navigate('/signin')}
            className="btn-primary w-full"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 grid-overlay flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="hero-orb" aria-hidden="true" />

      <div className="relative z-10 w-full max-w-sm">
        <div className="card p-8 text-center glow-indigo-sm">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center mx-auto mb-5">
            {isProcessing ? (
              <Mail className="w-6 h-6 text-indigo-400 animate-pulse" />
            ) : (
              <CheckCircle className="w-6 h-6 text-emerald-400" />
            )}
          </div>

          <h1 className="text-lg font-semibold text-zinc-100 mb-2">
            {isProcessing ? 'Completing sign in…' : "You're in!"}
          </h1>
          <p className="text-sm text-zinc-500">
            {isProcessing
              ? 'Setting up your session, just a moment.'
              : 'Redirecting to your dashboard…'}
          </p>

          {isProcessing && (
            <div className="mt-6 flex justify-center">
              <div className="spinner" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthSuccess;
