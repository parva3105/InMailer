import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Mail, ShieldCheck } from 'lucide-react';

const SignIn: React.FC = () => {
  const [error] = useState('');

  const handleGoogleSignIn = () => {
    const apiUrl = process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com';
    window.location.href = `${apiUrl}/auth/google`;
  };

  return (
    <div className="auth-bg grid-overlay flex min-h-screen items-center justify-center p-4">
      <div className="hero-orb" aria-hidden="true" />

      <div className="relative z-10 grid w-full max-w-5xl gap-6 lg:grid-cols-[1fr_420px] lg:items-center">
        <div className="hidden lg:block">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-teal-300/20 bg-teal-400/15 text-teal-200">
              <Mail className="h-4 w-4" />
            </div>
            <span className="text-sm font-semibold text-zinc-100">InMailer</span>
          </div>
          <h1 className="max-w-xl text-4xl font-semibold leading-tight text-zinc-100">
            Return to a focused workspace for templates, contacts, and campaigns.
          </h1>
          <p className="mt-5 max-w-lg text-sm leading-6 text-zinc-500">
            Continue with Google to keep sending through your Gmail account with your existing session and permissions.
          </p>
        </div>

        <div className="card p-8 glow-indigo-sm">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-xl border border-teal-300/20 bg-teal-400/15 text-teal-200">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h1 className="text-xl font-semibold text-zinc-100">Welcome back</h1>
            <p className="mt-1.5 text-sm text-zinc-500">Sign in with Google to continue</p>
          </div>

          {error && (
            <div className="alert-error mb-6 flex items-start gap-2.5 p-3">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
              <p className="text-xs">{error}</p>
            </div>
          )}

          <button onClick={handleGoogleSignIn} className="btn-secondary w-full py-3">
            <svg className="h-4 w-4 flex-shrink-0" viewBox="0 0 24 24" aria-hidden="true">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
          </button>

          <div className="mt-8 border-t border-white/[0.08] pt-6 text-center">
            <p className="text-sm text-zinc-600">
              Do not have an account?{' '}
              <Link to="/signup" className="font-medium text-teal-300 transition-colors hover:text-teal-200">
                Sign up
              </Link>
            </p>
          </div>

          <p className="mt-6 text-center text-xs leading-5 text-zinc-700">
            By signing in, you agree to our <a href="/terms-of-service" className="underline transition-colors hover:text-zinc-500">Terms</a> and <a href="/privacy-policy" className="underline transition-colors hover:text-zinc-500">Privacy Policy</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
