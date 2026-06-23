import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FileText, Send, Mail, Clock, ArrowRight, TrendingUp } from 'lucide-react';
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
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="spinner" />
      </div>
    );
  }

  const statCards = [
    {
      label: 'Templates',
      value: stats.template_count,
      icon: FileText,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
    },
    {
      label: 'Emails Sent',
      value: stats.emails_sent,
      icon: Send,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
    },
    {
      label: 'Orphaned',
      value: stats.orphaned_emails,
      icon: TrendingUp,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/20',
      hint: stats.orphaned_emails > 0 ? 'Emails sent with deleted templates' : undefined,
    },
  ];

  const quickActions = [
    {
      title: 'Templates',
      description: 'Browse, create, and manage your email templates.',
      icon: FileText,
      path: '/templates',
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
      btnLabel: 'Open templates',
    },
    {
      title: 'Mail Merge',
      description: 'Upload contacts and send personalized campaigns.',
      icon: Send,
      path: '/merge',
      color: 'text-violet-400',
      bg: 'bg-violet-500/10',
      border: 'border-violet-500/20',
      btnLabel: 'Start merge',
    },
    {
      title: 'Test Email',
      description: 'Verify your setup before sending to contacts.',
      icon: Mail,
      path: '/test-email',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      btnLabel: 'Send test',
    },
    {
      title: 'Email History',
      description: 'View all sent emails with status and grouped views.',
      icon: Clock,
      path: '/history',
      color: 'text-sky-400',
      bg: 'bg-sky-500/10',
      border: 'border-sky-500/20',
      btnLabel: 'View history',
    },
  ];

  return (
    <AppShell>
      <div className="px-6 py-8 max-w-6xl mx-auto w-full">
        {/* Welcome */}
        <div className="mb-10">
          <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">
            Good to see you, {user.name.split(' ')[0]}
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            You're one message away from your next breakthrough.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          {statCards.map((stat) => (
            <div key={stat.label} className={`card p-5 border ${stat.border}`}>
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-8 h-8 rounded-lg ${stat.bg} border ${stat.border} flex items-center justify-center`}>
                  <stat.icon className={`w-4 h-4 ${stat.color}`} />
                </div>
                <span className="text-xs font-medium text-zinc-500 uppercase tracking-wide">{stat.label}</span>
              </div>
              {loading ? (
                <div className="h-8 w-16 bg-zinc-800 rounded animate-pulse" />
              ) : (
                <p className="text-3xl font-bold text-zinc-100">{stat.value}</p>
              )}
              {!loading && stat.hint && (
                <p className="text-xs text-yellow-500 mt-1.5">{stat.hint}</p>
              )}
            </div>
          ))}
        </div>

        {/* Quick actions */}
        <div className="mb-2">
          <h2 className="text-sm font-medium text-zinc-500 uppercase tracking-wide mb-4">Quick actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <div
                key={action.path}
                className={`card-hover p-5 border ${action.border} cursor-pointer group`}
                onClick={() => navigate(action.path)}
              >
                <div className={`w-9 h-9 rounded-lg ${action.bg} border ${action.border} flex items-center justify-center mb-4`}>
                  <action.icon className={`w-4.5 h-4.5 ${action.color}`} style={{ width: 18, height: 18 }} />
                </div>
                <h3 className="text-sm font-semibold text-zinc-200 mb-1.5">{action.title}</h3>
                <p className="text-xs text-zinc-500 leading-relaxed mb-4">{action.description}</p>
                <div className={`flex items-center gap-1.5 text-xs font-medium ${action.color} group-hover:gap-2.5 transition-all duration-150`}>
                  {action.btnLabel}
                  <ArrowRight className="w-3 h-3" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* History shortcut */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={() => navigate('/history')}
            className="flex items-center gap-1.5 text-xs text-zinc-600 hover:text-indigo-400 transition-colors"
          >
            View email history
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </AppShell>
  );
};

export default Dashboard;
