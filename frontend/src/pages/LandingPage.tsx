import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Upload, FileText, Send, Users, Zap, ArrowRight } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  React.useEffect(() => {
    if (user) navigate('/dashboard');
  }, [user, navigate]);

  const steps = [
    {
      number: '01',
      icon: FileText,
      title: 'Create Templates',
      description: 'Design personalized email templates with dynamic variables like {name} and {company}.',
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
    },
    {
      number: '02',
      icon: Upload,
      title: 'Upload Contacts',
      description: 'Import your contact list via CSV. Include names, emails, and any custom fields you need.',
      color: 'text-violet-400',
      bg: 'bg-violet-500/10',
      border: 'border-violet-500/20',
    },
    {
      number: '03',
      icon: Send,
      title: 'Send Campaigns',
      description: 'Launch your personalized outreach. Each recipient gets a uniquely tailored message via Gmail.',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
    },
  ];

  const features = [
    { icon: Zap, label: 'Lightning Fast', desc: 'Send hundreds of personalized emails in seconds', color: 'text-yellow-400' },
    { icon: Users, label: 'Personal Touch', desc: 'Every email is uniquely personalized with recipient data', color: 'text-indigo-400' },
    { icon: Mail, label: 'Gmail Integration', desc: 'Sends securely through your own Gmail account', color: 'text-violet-400' },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 grid-overlay flex flex-col relative overflow-hidden">
      {/* Ambient orb */}
      <div className="hero-orb" aria-hidden="true" />

      {/* Nav */}
      <header className="relative z-10 border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-md sticky top-0">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Mail className="w-4.5 h-4.5 text-white" style={{ width: 18, height: 18 }} />
            </div>
            <span className="text-base font-semibold text-zinc-100 tracking-tight">InMailer</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/signin')}
              className="btn-ghost text-zinc-400 px-3 py-2"
            >
              Sign in
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="btn-primary px-4 py-2"
            >
              Get started
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10 flex-1 flex items-start justify-center pt-24 pb-16 px-4 sm:px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-8 animate-fade-in">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Gmail-powered email outreach
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold text-zinc-100 tracking-tight leading-[1.08] mb-6 animate-fade-up">
            Email outreach,
            <span className="block text-gradient-indigo">done right.</span>
          </h1>

          <p className="text-lg text-zinc-400 max-w-xl mx-auto mb-10 leading-relaxed animate-fade-up animate-delay-100">
            Create personalized email templates, upload your contact list, and send at scale — all through your own Gmail account.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-fade-up animate-delay-200">
            <button
              onClick={() => navigate('/signup')}
              className="btn-primary px-6 py-3 text-base gap-2.5"
            >
              Start for free
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/signin')}
              className="btn-secondary px-6 py-3 text-base"
            >
              Sign in
            </button>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 px-4 sm:px-6 pb-20">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs text-zinc-600 font-medium uppercase tracking-widest mb-3">How it works</p>
            <h2 className="text-3xl font-bold text-zinc-100 tracking-tight">
              Three steps to your inbox
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {steps.map((step) => (
              <div key={step.number} className={`card p-6 border ${step.border} relative overflow-hidden`}>
                <div className={`absolute top-4 right-4 text-4xl font-bold opacity-[0.06] text-zinc-100`}>
                  {step.number}
                </div>
                <div className={`w-10 h-10 rounded-lg ${step.bg} border ${step.border} flex items-center justify-center mb-5`}>
                  <step.icon className={`w-5 h-5 ${step.color}`} />
                </div>
                <h3 className="text-base font-semibold text-zinc-100 mb-2">{step.title}</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>

          {/* Features */}
          <div className="mt-12 grid md:grid-cols-3 gap-6">
            {features.map((f) => (
              <div key={f.label} className="flex items-start gap-4 px-4 py-5 rounded-xl bg-zinc-900/40 border border-zinc-800/50">
                <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center flex-shrink-0">
                  <f.icon className={`w-4 h-4 ${f.color}`} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-zinc-200 mb-0.5">{f.label}</p>
                  <p className="text-xs text-zinc-500 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="mt-12 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-10 text-center">
            <h3 className="text-2xl font-bold text-zinc-100 mb-3">Ready to start sending?</h3>
            <p className="text-zinc-500 mb-6 max-w-sm mx-auto text-sm">
              Join professionals who trust InMailer for their email outreach campaigns.
            </p>
            <button
              onClick={() => navigate('/signup')}
              className="btn-primary px-6 py-3 text-base"
            >
              Get started free
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-zinc-800/60 py-6 px-4">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-zinc-600">
          <p>
            © 2025 Made by{' '}
            <a
              href="https://www.linkedin.com/in/parva3105"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-400 hover:text-indigo-400 transition-colors"
            >
              Parva Shah
            </a>
          </p>
          <div className="flex items-center gap-4">
            <a href="/terms-of-service" className="hover:text-zinc-400 transition-colors">Terms</a>
            <a href="/privacy-policy" className="hover:text-zinc-400 transition-colors">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
