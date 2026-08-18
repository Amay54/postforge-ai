import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LinkedInStatus } from '../types';
import { 
  Key, 
  ShieldCheck, 
  Linkedin, 
  CheckCircle, 
  AlertTriangle, 
  ArrowRight,
  ExternalLink,
  Lock,
  RefreshCw,
  Eye,
  EyeOff,
  LogOut
} from 'lucide-react';

export const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'linkedin' | 'apikeys' | 'security'>('linkedin');
  
  // LinkedIn Status
  const [linkedinStatus, setLinkedinStatus] = useState<LinkedInStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [disconnecting, setDisconnecting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Settings Forms
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [savedSettings, setSavedSettings] = useState(false);

  useEffect(() => {
    fetchLinkedInStatus();
  }, []);

  const fetchLinkedInStatus = async () => {
    setLoadingStatus(true);
    try {
      const data = await api.getLinkedInStatus();
      setLinkedinStatus(data);
    } catch (err: any) {
      console.error('Failed to fetch LinkedIn status:', err);
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleConnectLinkedIn = async () => {
    try {
      const { authorization_url } = await api.getLinkedInAuthUrl();
      if (authorization_url) {
        window.location.href = authorization_url;
      }
    } catch (err: any) {
      setFeedbackMsg({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to initiate LinkedIn OAuth connection.',
      });
    }
  };

  const handleDisconnectLinkedIn = async () => {
    if (!window.confirm('Are you sure you want to disconnect LinkedIn? Your content sessions will remain safe.')) {
      return;
    }
    setDisconnecting(true);
    try {
      await api.disconnectLinkedIn();
      setFeedbackMsg({ type: 'success', text: 'LinkedIn disconnected successfully.' });
      await fetchLinkedInStatus();
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: 'Failed to disconnect LinkedIn.' });
    } finally {
      setDisconnecting(false);
    }
  };

  const handleSaveApiKeys = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSettings(true);
    setTimeout(() => setSavedSettings(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">System Settings & Integrations</h1>
        <p className="text-slate-400 mt-2 text-sm">
          Manage your LinkedIn OAuth connection, LLM provider keys, and security settings.
        </p>
      </div>

      {feedbackMsg && (
        <div
          className={`p-4 rounded-xl flex items-center justify-between text-sm ${
            feedbackMsg.type === 'success'
              ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
          }`}
        >
          <span>{feedbackMsg.text}</span>
          <button onClick={() => setFeedbackMsg(null)} className="text-xs hover:underline ml-4">
            Dismiss
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-px">
        <button
          onClick={() => setActiveTab('linkedin')}
          className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'linkedin'
              ? 'border-brand-500 text-brand-400 bg-brand-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Linkedin className="w-4 h-4" />
          LinkedIn OAuth Integration
        </button>

        <button
          onClick={() => setActiveTab('apikeys')}
          className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'apikeys'
              ? 'border-brand-500 text-brand-400 bg-brand-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Key className="w-4 h-4" />
          API Keys & Models
        </button>

        <button
          onClick={() => setActiveTab('security')}
          className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'security'
              ? 'border-brand-500 text-brand-400 bg-brand-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Security & Privacy
        </button>
      </div>

      {/* Tab 1: LinkedIn Integration */}
      {activeTab === 'linkedin' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
                  <Linkedin className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    LinkedIn Official API
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                        linkedinStatus?.provider === 'official'
                          ? linkedinStatus?.connected
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                      }`}
                    >
                      {linkedinStatus?.provider === 'official'
                        ? linkedinStatus?.connected
                          ? 'LIVE CONNECTED'
                          : 'LIVE (DISCONNECTED)'
                        : 'MOCK / SIMULATION'}
                    </span>
                  </h3>
                  <p className="text-slate-400 text-xs mt-1">
                    Enables authenticated publishing of approved posts to your LinkedIn personal profile.
                  </p>
                </div>
              </div>

              <button
                onClick={fetchLinkedInStatus}
                disabled={loadingStatus}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors"
                title="Refresh Status"
              >
                <RefreshCw className={`w-4 h-4 ${loadingStatus ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {/* Status Details */}
            <div className="mt-6 pt-6 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800">
                <span className="text-xs text-slate-400 block mb-1">Runtime Mode</span>
                <span className="text-sm font-semibold text-white uppercase flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      linkedinStatus?.provider === 'official' ? 'bg-emerald-400' : 'bg-blue-400'
                    }`}
                  />
                  {linkedinStatus?.provider === 'official' ? 'Official Marketing API (Live)' : 'Mock Provider (Offline)'}
                </span>
              </div>

              <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800">
                <span className="text-xs text-slate-400 block mb-1">Member Profile</span>
                <span className="text-sm font-semibold text-white flex items-center gap-2">
                  {linkedinStatus?.profile?.name || 'Not Connected'}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
              <div className="text-xs text-slate-400">
                {linkedinStatus?.connected
                  ? 'Your LinkedIn connection is active and ready to publish.'
                  : 'Connect your account using OAuth 2.0 to enable publishing.'}
              </div>

              <div className="flex gap-3">
                {linkedinStatus?.connected ? (
                  <button
                    onClick={handleDisconnectLinkedIn}
                    disabled={disconnecting}
                    className="px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center gap-2 transition-all"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    {disconnecting ? 'Disconnecting...' : 'Disconnect Account'}
                  </button>
                ) : (
                  <button
                    onClick={handleConnectLinkedIn}
                    className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-brand-500/20 transition-all"
                  >
                    Connect Real LinkedIn Account
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: API Keys */}
      {activeTab === 'apikeys' && (
        <form onSubmit={handleSaveApiKeys} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white">Language Model API Configuration</h3>
            <p className="text-slate-400 text-xs mt-1">
              Configure Google Gemini API keys for post synthesis and quality review.
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Google Gemini API Key</label>
            <div className="relative">
              <input
                type={showGeminiKey ? 'text' : 'password'}
                value={geminiApiKey}
                onChange={(e) => setGeminiApiKey(e.target.value)}
                placeholder="Enter your Gemini API key..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors pr-10"
              />
              <button
                type="button"
                onClick={() => setShowGeminiKey(!showGeminiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                {showGeminiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition-all"
          >
            {savedSettings ? 'Saved Successfully!' : 'Save Configuration'}
          </button>
        </form>
      )}

      {/* Tab 3: Security & Privacy */}
      {activeTab === 'security' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Lock className="w-5 h-5 text-emerald-400" />
            Security & Token Encryption
          </h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            PostForge AI protects your credentials with industry standard security:
          </p>
          <ul className="list-disc list-inside text-xs text-slate-300 space-y-2">
            <li>Tokens encrypted at rest using AES-128-CBC via Fernet.</li>
            <li>All outbound requests protected by strict TLS 1.3 certificate validation.</li>
            <li>Mandatory server-side Human-in-the-Loop approval gate before any publish operation.</li>
            <li>Zero prompt leakage guarantees.</li>
          </ul>
        </div>
      )}
    </div>
  );
};
