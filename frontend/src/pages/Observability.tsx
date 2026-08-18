import React, { useEffect, useState } from 'react';
import { Activity, Clock, Cpu, FileText, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { SessionListItem, ObservabilityLog } from '../types';

export const Observability: React.FC = () => {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [logs, setLogs] = useState<ObservabilityLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSessions() {
      try {
        const posts = await api.listPosts();
        setSessions(posts);
        if (posts.length > 0) {
          setSelectedSessionId(posts[0].id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSessions();
  }, []);

  useEffect(() => {
    async function loadTraces() {
      if (!selectedSessionId) return;
      try {
        const traces = await api.getSessionTraces(selectedSessionId);
        setLogs(traces);
      } catch (err) {
        console.error(err);
      }
    }
    loadTraces();
  }, [selectedSessionId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-blue-400" />
          Multi-Agent Observability & Traces
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Real-time step latencies, prompt/completion token telemetry, and raw agent execution outputs.
        </p>
      </div>

      {/* Session Selector */}
      <div className="glass-panel p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <span className="text-xs font-semibold text-slate-300">Select Content Session:</span>
        <select
          value={selectedSessionId}
          onChange={(e) => setSelectedSessionId(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none max-w-md"
        >
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              {s.topic.slice(0, 50)}... ({s.status})
            </option>
          ))}
        </select>
      </div>

      {/* Traces Timeline */}
      <div className="space-y-4">
        {logs.length === 0 ? (
          <div className="glass-panel p-12 text-center text-xs text-slate-500">
            No execution logs found for this session.
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="glass-panel p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-mono font-bold text-[10px]">
                    {log.step_number}
                  </span>
                  <span className="font-bold text-white text-sm">{log.agent_name}</span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono">
                    {log.model_name || 'gemini-2.5-flash'}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-slate-400 text-[11px] font-mono">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-400" />
                    <span>{log.latency_ms} ms</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Cpu className="w-3.5 h-3.5 text-purple-400" />
                    <span>{log.tokens_total} tokens</span>
                  </div>
                </div>
              </div>

              {log.raw_output && (
                <div>
                  <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1">
                    Execution Output
                  </label>
                  <pre className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {log.raw_output}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
