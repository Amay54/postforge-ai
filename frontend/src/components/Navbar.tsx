import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Sparkles, 
  LayoutDashboard, 
  PenTool, 
  BarChart3, 
  Activity, 
  Settings as SettingsIcon,
  Linkedin,
  Radio
} from 'lucide-react';
import { LinkedInStatus } from '../types';

interface NavbarProps {
  accountStatus: LinkedInStatus | null;
  onConnectClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ accountStatus, onConnectClick }) => {
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Create Post', path: '/create', icon: PenTool },
    { label: 'Evaluation', path: '/evaluation', icon: BarChart3 },
    { label: 'Observability', path: '/observability', icon: Activity },
    { label: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  const isMock = !accountStatus || accountStatus.provider === 'mock';
  const isLiveConnected = accountStatus?.provider === 'official' && accountStatus.connected;
  const profileName = accountStatus?.profile?.name || 'Member';

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                PostForge AI
              </span>
              <span className="ml-2 text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={onConnectClick}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              isLiveConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
                : isMock
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30 hover:bg-rose-500/20'
            }`}
          >
            <Linkedin className="w-3.5 h-3.5" />
            {isLiveConnected ? (
              <>
                <span>?? Live Connected: {profileName}</span>
              </>
            ) : isMock ? (
              <>
                <span>?? LinkedIn Simulation</span>
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              </>
            ) : (
              <>
                <span>?? Connect Live LinkedIn</span>
                <span className="w-2 h-2 rounded-full bg-rose-500" />
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
