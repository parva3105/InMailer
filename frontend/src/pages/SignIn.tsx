import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, AlertCircle } from 'lucide-react';

const SignIn: React.FC = () => {
  const [error] = useState('');

  const handleGoogleSignIn = () => {
    const apiUrl = process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com';
    window.location.href = `${apiUrl}/auth/google`;
  };

  return (
    <div className="min-h-screen bg-zinc-950 grid-overlay flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient orb */}
      <div className="hero-orb" aria-hidden="true" />

      {/* Logo at top */}
      <div className="relative z-10 mb-8 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Mail className="w-4.5 h-4.5 text-white" style={{ width: 18, height: 18 }} />
        </div>
        <span className="text-base font-semibold text-zinc-100 tracking-tight">InMailer</span>
      </div>

      {/* Card */}
      <div className="relative z-10 w-full max-w-sm">
        <div className="card p-8 glow-indigo-sm">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-xl font-semibold text-zinc-100 mb-1.5">Welcome back</h1>
            <p className="text-sm text-zinc-500">Sign in with Google to continue</p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-red-400">{error}</p>
            </div>
          )}

          {/* Google button */}
          <button
            onClick={handleGoogleSignIn}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg
                       bg-zinc-800 border border-zinc-700 text-zinc-200 text-sm font-medium
                       hover:bg-zinc-700 hover:border-zinc-600 active:scale-[0.98]
                       transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
          >
            <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
          </button>

          {/* Divider */}
          <div className="mt-8 pt-6 border-t border-zinc-800 text-center">
            <p className="text-sm text-zinc-600">
              Don't have an account?{' '}
              <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                Sign up
              </Link>
            </p>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-zinc-700">
          By signing in, you agree to our{' '}
          <a href="/terms-of-service" className="hover:text-zinc-500 transition-colors underline">Terms</a>
          {' '}and{' '}
          <a href="/privacy-policy" className="hover:text-zinc-500 transition-colors underline">Privacy Policy</a>
        </p>
      </div>
    </div>
  );
};

export default SignIn;
