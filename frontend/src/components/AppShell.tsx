import React, { useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  BarChart3,
  Clock,
  FileText,
  LayoutDashboard,
  LogOut,
  Mail,
  Menu,
  Send,
  X,
} from 'lucide-react';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { label: 'Templates', icon: FileText, path: '/templates' },
  { label: 'Mail Merge', icon: Send, path: '/merge' },
  { label: 'Email History', icon: Clock, path: '/history' },
  { label: 'Test Email', icon: Mail, path: '/test-email' },
];

interface AppShellProps {
  children: React.ReactNode;
}

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { user, signout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const currentPage = useMemo(() => {
    const match = navItems.find((item) => {
      if (item.path === '/dashboard') return location.pathname === item.path;
      return location.pathname === item.path || location.pathname.startsWith(`${item.path}/`);
    });
    return match?.label ?? 'InMailer';
  }, [location.pathname]);

  const handleSignOut = async () => {
    await signout();
    navigate('/');
  };

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === path;
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  const SidebarContent = () => (
    <div className="flex h-full flex-col">
      <div className="flex h-16 flex-shrink-0 items-center border-b border-white/[0.08] px-5">
        <Link
          to="/dashboard"
          className="group flex items-center gap-3"
          onClick={() => setMobileOpen(false)}
        >
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-teal-300/20 bg-teal-400/15 text-teal-200 transition-colors group-hover:bg-teal-400/20">
            <Mail className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <span className="block text-sm font-semibold tracking-tight text-zinc-100">InMailer</span>
            <span className="block text-[11px] font-medium text-zinc-600">Outreach OS</span>
          </div>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <p className="section-title px-3 pb-2">Workspace</p>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={isActive(item.path) ? 'nav-item-active' : 'nav-item'}
            onClick={() => setMobileOpen(false)}
          >
            <item.icon className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="flex-shrink-0 border-t border-white/[0.08] px-3 py-4">
        <div className="mb-2 rounded-xl border border-white/[0.08] bg-white/[0.035] p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border border-sky-300/20 bg-sky-400/10">
              <span className="text-xs font-semibold text-sky-300">
                {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-zinc-200">{user?.name}</p>
              <p className="truncate text-xs text-zinc-600">{user?.email}</p>
            </div>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="nav-item text-zinc-600 hover:bg-red-500/5 hover:text-red-400"
        >
          <LogOut className="h-4 w-4 flex-shrink-0" />
          Sign out
        </button>
      </div>
    </div>
  );

  return (
    <div className="app-bg flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-64 flex-shrink-0 border-r border-white/[0.08] bg-black/20 backdrop-blur-xl lg:flex lg:flex-col">
        <SidebarContent />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <button
            type="button"
            aria-label="Close navigation overlay"
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative z-10 w-72 flex-shrink-0 border-r border-white/[0.08] bg-[#0b0d10] shadow-2xl">
            <button
              type="button"
              aria-label="Close navigation"
              onClick={() => setMobileOpen(false)}
              className="icon-button absolute right-4 top-4"
            >
              <X className="h-4 w-4" />
            </button>
            <SidebarContent />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-white/[0.08] bg-[#08090b]/82 px-4 backdrop-blur-xl lg:h-16 lg:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button
              type="button"
              aria-label="Open navigation"
              onClick={() => setMobileOpen(true)}
              className="icon-button lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="hidden h-8 w-8 items-center justify-center rounded-lg border border-teal-300/15 bg-teal-400/10 text-teal-200 lg:flex">
              <BarChart3 className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-zinc-100">{currentPage}</p>
              <p className="hidden truncate text-xs text-zinc-600 sm:block">Campaigns, templates, contacts, and sending history</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => navigate('/merge')}
              className="btn-primary hidden px-3 py-2 text-xs sm:inline-flex"
            >
              <Send className="h-3.5 w-3.5" />
              New send
            </button>
            <div className="flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/[0.05] lg:hidden">
              <span className="text-xs font-semibold text-zinc-300">
                {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
              </span>
            </div>
          </div>
        </header>

        <main className="min-w-0 flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
