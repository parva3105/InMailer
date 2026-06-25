import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowRight, FileText, Mail, Send, ShieldCheck, Upload, Users } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  React.useEffect(() => {
    if (user) navigate('/dashboard');
  }, [user, navigate]);

  const steps = [
    { icon: FileText, title: 'Template', description: 'Write reusable messages with variables for every recipient.' },
    { icon: Upload, title: 'Contacts', description: 'Upload a CSV and map the fields you already use.' },
    { icon: Send, title: 'Send', description: 'Preview, schedule, or send through your Gmail account.' },
  ];

  const stats = [
    { label: 'Templates', value: '18' },
    { label: 'Contacts ready', value: '642' },
    { label: 'Sent this week', value: '1.2k' },
  ];

  return (
    <div className="auth-bg grid-overlay flex min-h-screen flex-col">
      <div className="hero-orb" aria-hidden="true" />

      <header className="sticky top-0 z-20 border-b border-white/[0.08] bg-[#08090b]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <button type="button" onClick={() => navigate('/')} className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-teal-300/20 bg-teal-400/15 text-teal-200">
              <Mail className="h-4 w-4" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-zinc-100">InMailer</span>
          </button>

          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/signin')} className="btn-ghost px-3 py-2">
              Sign in
            </button>
            <button onClick={() => navigate('/signup')} className="btn-primary px-4 py-2">
              Get started
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1 px-4 pb-16 pt-14 sm:px-6 lg:px-8 lg:pt-20">
        <section className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-400/10 px-3 py-1.5 text-xs font-medium text-teal-200">
              <ShieldCheck className="h-3.5 w-3.5" />
              Gmail-powered outreach workspace
            </div>

            <h1 className="text-4xl font-semibold leading-[1.05] tracking-tight text-zinc-100 sm:text-6xl">
              Email outreach that feels precise, calm, and ready to send.
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-zinc-400 sm:text-lg">
              Create personalized templates, upload contacts, preview every campaign, and send through your own Gmail account from one focused workspace.
            </p>

            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <button onClick={() => navigate('/signup')} className="btn-primary px-6 py-3 text-base">
                Start for free
                <ArrowRight className="h-4 w-4" />
              </button>
              <button onClick={() => navigate('/signin')} className="btn-secondary px-6 py-3 text-base">
                Sign in
              </button>
            </div>
          </div>

          <div className="product-depth mx-auto mt-14 max-w-5xl rounded-2xl border border-white/[0.10] bg-white/[0.045] p-3 shadow-[0_28px_90px_rgba(0,0,0,0.42)]">
            <div className="rounded-xl border border-white/[0.08] bg-[#0b0d10] p-4 sm:p-5">
              <div className="mb-5 flex items-center justify-between border-b border-white/[0.08] pb-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-600">Campaign cockpit</p>
                  <p className="mt-1 text-sm font-semibold text-zinc-100">Q3 founder outreach</p>
                </div>
                <span className="badge-green">Ready</span>
              </div>

              <div className="grid gap-4 lg:grid-cols-[1fr_1.1fr]">
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3">
                    {stats.map((stat) => (
                      <div key={stat.label} className="panel p-3">
                        <p className="text-lg font-semibold text-zinc-100">{stat.value}</p>
                        <p className="mt-1 truncate text-[11px] text-zinc-600">{stat.label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="panel p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-semibold text-zinc-200">Workflow</p>
                      <span className="text-xs text-zinc-600">3 steps</span>
                    </div>
                    <div className="space-y-3">
                      {steps.map((step, index) => (
                        <div key={step.title} className="flex gap-3 rounded-lg border border-white/[0.07] bg-white/[0.035] p-3">
                          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-teal-400/10 text-teal-200">
                            <step.icon className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-xs font-semibold text-zinc-200">{index + 1}. {step.title}</p>
                            <p className="mt-0.5 text-xs leading-5 text-zinc-500">{step.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="panel p-4">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-zinc-200">Personalized preview</p>
                      <p className="text-xs text-zinc-600">Before sending to 642 contacts</p>
                    </div>
                    <Users className="h-4 w-4 text-zinc-600" />
                  </div>
                  <div className="rounded-xl border border-white/[0.08] bg-black/25 p-4">
                    <p className="text-xs uppercase tracking-wider text-zinc-600">Subject</p>
                    <p className="mt-1 text-sm font-medium text-zinc-200">Partnership idea for Acme</p>
                    <div className="my-4 h-px bg-white/[0.08]" />
                    <p className="text-sm leading-7 text-zinc-400">
                      Hi Maya,<br />
                      I saw the team at Acme is expanding outbound motion. InMailer can help your reps keep each email personal while moving faster.
                    </p>
                    <div className="mt-5 flex flex-wrap gap-2">
                      <span className="badge-indigo">First_Name</span>
                      <span className="badge-indigo">Company</span>
                      <span className="badge-zinc">Gmail attached</span>
                    </div>
                  </div>
                  <button onClick={() => navigate('/signup')} className="btn-primary mt-4 w-full">
                    Build your first campaign
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-white/[0.08] px-4 py-6">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 text-xs text-zinc-600 sm:flex-row">
          <p>c 2025 Made by <a href="https://www.linkedin.com/in/parva3105" target="_blank" rel="noopener noreferrer" className="text-zinc-400 transition-colors hover:text-teal-300">Parva Shah</a></p>
          <div className="flex items-center gap-4">
            <a href="/terms-of-service" className="transition-colors hover:text-zinc-400">Terms</a>
            <a href="/privacy-policy" className="transition-colors hover:text-zinc-400">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
