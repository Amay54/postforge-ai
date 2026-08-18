import React, { useState } from 'react';
import { X, Linkedin, CheckCircle2, ShieldCheck, AlertTriangle, ExternalLink, PowerOff } from 'lucide-react';
import { api } from '../services/api';
import { LinkedInStatus } from '../types';

interface LinkedInConnectModalProps {
  isOpen: boolean;
  accountStatus: LinkedInStatus | null;
  onClose: () => void;
  onStatusUpdated: () => void;
}

export const LinkedInConnectModal: React.FC<LinkedInConnectModalProps> = ({
  isOpen,
  accountStatus,
  onClose,
  onStatusUpdated,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const isMock = !accountStatus || accountStatus.provider === 'mock';
  const isLiveConnected = accountStatus?.provider === 'official' && accountStatus.connected;

  const handleLaunchOAuth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getLinkedInAuthUrl();
      if (res.authorization_url.includes('http')) {
        window.location.href = res.authorization_url;
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate LinkedIn OAuth authorization URL.');
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    try {
      await api.disconnectLinkedIn();
      onStatusUpdated();
      onClose();
    } catch (err: any) {
      setError('Failed to disconnect LinkedIn account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="w-12 h-12 rounded-xl bg-[#0a66c2]/20 border border-[#0a66c2]/40 flex items-center justify-center text-[#0a66c2] mb-4">
          <Linkedin className="w-6 h-6" />
        </div>

        <h3 className="text-lg font-bold text-white">LinkedIn Integration Manager</h3>
        <p className="text-xs text-slate-400 mt-1">
          PostForge AI supports both official member publishing via LinkedIn's Posts API and simulated sandbox execution.
        </p>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <div className="my-6 space-y-3">
          {/* Provider Mode Banner */}
          <div className={`p-4 rounded-xl border ${
            isLiveConnected 
              ? 'bg-emerald-500/10 border-emerald-500/30' 
              : isMock 
              ? 'bg-amber-500/10 border-amber-500/30' 
              : 'bg-slate-950 border-slate-800'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Active Mode:</span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold font-mono uppercase ${
                isLiveConnected ? 'text-emerald-400 bg-emerald-500/20' : isMock ? 'text-amber-400 bg-amber-500/20' : 'text-slate-400'
              }`}>
                {accountStatus?.mode || 'Simulation'}
              </span>
            </div>

            {isMock ? (
              <div className="mt-2 text-xs text-amber-200/90 leading-relaxed">
                <p className="font-semibold">?? Simulation Mode Active</p>
                <p className="text-[11px] text-amber-300/80 mt-0.5">
                  Mock profile: <strong>Amay Yadav</strong>. In simulation mode, no real posts will be sent to live LinkedIn.
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  To publish to your live LinkedIn profile, set <code className="text-blue-300 font-mono">LINKEDIN_PROVIDER=official</code> in <code className="text-blue-300 font-mono">.env</code> and add your Developer App credentials.
                </p>
              </div>
            ) : isLiveConnected ? (
              <div className="mt-2 text-xs text-emerald-200 leading-relaxed">
                <p className="font-semibold">?? Live LinkedIn Connected</p>
                <p className="text-[11px] text-emerald-300/90 mt-0.5">
                  Member: <strong>{accountStatus?.profile?.name}</strong> (URN: <code className="font-mono text-[10px]">{accountStatus?.profile?.member_urn}</code>)
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Posts approved by you will be published directly to your live LinkedIn feed.
                </p>
              </div>
            ) : (
              <div className="mt-2 text-xs text-slate-300 leading-relaxed">
                <p className="font-semibold text-rose-400">?? Live Mode Unconnected</p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Official provider is active, but your LinkedIn account has not yet authorized <code className="font-mono text-blue-300">w_member_social</code> permission.
                </p>
              </div>
            )}
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
            <div className="text-xs text-slate-300">
              <p className="font-semibold text-white">OAuth 2.0 Security & Encryption</p>
              <p className="text-slate-400 text-[11px]">Tokens encrypted at rest via 256-bit Fernet keys. Client secrets are never exposed.</p>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
          {!isMock && !isLiveConnected && (
            <button
              onClick={handleLaunchOAuth}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-[#0a66c2] hover:bg-[#004182] text-white text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20"
            >
              <Linkedin className="w-4 h-4" />
              <span>{loading ? 'Connecting...' : 'Authorize with LinkedIn (w_member_social)'}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          )}

          {isLiveConnected && (
            <button
              onClick={handleDisconnect}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 transition-all"
            >
              <PowerOff className="w-4 h-4" />
              <span>Disconnect LinkedIn Account</span>
            </button>
          )}

          <button
            onClick={onClose}
            className="w-full py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
