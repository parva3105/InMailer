import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowRight, Clock, FileText, Mail, Send, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { getApiUrl, apiEndpoints } from '../config';
import AppShell from '../components/AppShell';

interface DashboardStats {
  template_count: number;
  emails_sent: number;
  orphaned_emails: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({ template_count: 0, emails_sent: 0, orphaned_emails: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchDashboardStats();
      fetch(getApiUrl('api/cron/process-scheduled'), { method: 'POST', credentials: 'include' }).catch(() => {});
    }
  }, [user]);

  useEffect(() => {
    const handleFocus = () => { if (user) fetchDashboardStats(); };
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [user]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const dashboardUrl = getApiUrl(apiEndpoints.dashboard);
      const response = await axios.get(dashboardUrl, { withCredentials: true });

      if (response.status === 200) {
        const d = response.data;
        setStats({
          template_count: d.template_count || 0,
          emails_sent: d.emails_sent || 0,
          orphaned_emails: d.orphaned_emails || 0,
        });
      } else {
        try {
          const templatesResponse = await axios.get(getApiUrl(apiEndpoints.templates), { withCredentials: true });
          const emailResponse = await axios.get(getApiUrl(apiEndpoints.userStats), { withCredentials: true });
          setStats({
            template_count: templatesResponse.data?.length || 0,
            emails_sent: emailResponse.data?.sent_emails || 0,
            orphaned_emails: 0,
          });
        } catch { /* silent */ }
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="grid min-h-screen place-items-center bg-[#08090b]">
        <div className="spinner" />
      </div>
    );
  }

  const statCards = [
    { label: 'Templates', value: stats.template_count, icon: FileText, color: 'text-sky-300', bg: 'bg-sky-400/10', border: 'border-sky-300/20' },
    { label: 'Emails sent', value: stats.emails_sent, icon: Send, color: 'text-emerald-300', bg: 'bg-emerald-400/10', border: 'border-emerald-300/20' },
    { label: 'Orphaned', value: stats.orphaned_emails, icon: TrendingUp, color: 'text-amber-300', bg: 'bg-amber-400/10', border: 'border-amber-300/20', hint: stats.orphaned_emails > 0 ? 'Emails sent with deleted templates' : undefined },
  ];

  const quickActions = [
    { title: 'Templates', description: 'Browse, create, and refine reusable email templates.', icon: FileText, path: '/templates', color: 'text-sky-300', bg: 'bg-sky-400/10', border: 'border-sky-300/20', btnLabel: 'Open templates' },
    { title: 'Mail Merge', description: 'Upload contacts, preview personalization, and send.', icon: Send, path: '/merge', color: 'text-teal-300', bg: 'bg-teal-400/10', border: 'border-teal-300/20', btnLabel: 'Start merge' },
    { title: 'Test Email', description: 'Verify content and sender access before a campaign.', icon: Mail, path: '/test-email', color: 'text-violet-300', bg: 'bg-violet-400/10', border: 'border-violet-300/20', btnLabel: 'Send test' },
    { title: 'Email History', description: 'Review sent, pending, and failed messages.', icon: Clock, path: '/history', color: 'text-amber-300', bg: 'bg-amber-400/10', border: 'border-amber-300/20', btnLabel: 'View history' },
  ];

  return (
    <AppShell>
      <div className="app-container">
        <div className="page-header">
          <div>
            <p className="section-title">Overview</p>
            <h1 className="page-title mt-2">Good to see you, {user.name.split(' ')[0]}</h1>
            <p className="page-description">Monitor sending activity and jump into the next campaign workflow.</p>
          </div>
          <button onClick={() => navigate('/merge')} className="btn-primary">
            <Send className="h-4 w-4" />
            New campaign
          </button>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {statCards.map((stat) => (
            <div key={stat.label} className="metric-card">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">{stat.label}</span>
                <div className={`flex h-9 w-9 items-center justify-center rounded-lg border ${stat.border} ${stat.bg}`}>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </div>
              {loading ? (
                <div className="h-9 w-20 animate-pulse rounded bg-white/[0.055]" />
              ) : (
                <p className="text-3xl font-semibold text-zinc-100">{stat.value}</p>
              )}
              {!loading && stat.hint && <p className="mt-2 text-xs text-amber-400">{stat.hint}</p>}
            </div>
          ))}
        </div>

        <div className="mb-4 flex items-center justify-between">
          <h2 className="section-title">Quick actions</h2>
          <button onClick={() => navigate('/history')} className="btn-ghost px-3 py-2 text-xs">
            View history
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => (
            <button
              key={action.path}
              type="button"
              className="card-hover group p-5 text-left"
              onClick={() => navigate(action.path)}
            >
              <div className={`mb-4 flex h-10 w-10 items-center justify-center rounded-lg border ${action.border} ${action.bg}`}>
                <action.icon className={`h-5 w-5 ${action.color}`} />
              </div>
              <h3 className="text-sm font-semibold text-zinc-200">{action.title}</h3>
              <p className="mt-2 min-h-[42px] text-xs leading-5 text-zinc-500">{action.description}</p>
              <div className={`mt-4 flex items-center gap-1.5 text-xs font-medium ${action.color} transition-all duration-150 group-hover:gap-2.5`}>
                {action.btnLabel}
                <ArrowRight className="h-3.5 w-3.5" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </AppShell>
  );
};

export default Dashboard;
