import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  FileText,
  Send,
  Clock,
  Mail,
  LogOut,
  Menu,
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

  const handleSignOut = async () => {
    await signout();
    navigate('/');
  };

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === path;
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-zinc-800 flex-shrink-0">
        <Link
          to="/dashboard"
          className="flex items-center gap-2.5 group"
          onClick={() => setMobileOpen(false)}
        >
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 group-hover:bg-indigo-500 transition-colors duration-150">
            <Mail className="w-4 h-4 text-white" />
          </div>
          <span className="text-base font-semibold text-zinc-100 tracking-tight">InMailer</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={isActive(item.path) ? 'nav-item-active' : 'nav-item'}
            onClick={() => setMobileOpen(false)}
          >
            <item.icon className="w-4 h-4 flex-shrink-0" />
            {item.label}
          </Link>
        ))}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-zinc-800 flex-shrink-0">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800 mb-2">
          <div className="w-7 h-7 rounded-full bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-semibold text-indigo-400">
              {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-zinc-200 truncate">{user?.name}</p>
            <p className="text-xs text-zinc-600 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="nav-item text-zinc-600 hover:text-red-400 hover:bg-red-500/5 hover:border-transparent"
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          Sign out
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-zinc-950">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col w-60 flex-shrink-0 border-r border-zinc-800 bg-zinc-950 sticky top-0 h-screen">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-zinc-950/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative w-64 flex-shrink-0 bg-zinc-950 border-r border-zinc-800 z-10">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center h-14 px-4 border-b border-zinc-800 bg-zinc-950 sticky top-0 z-40">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors mr-3"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center">
              <Mail className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-zinc-100">InMailer</span>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
