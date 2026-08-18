import React from 'react';
import { CheckCircle2, Loader2, Sparkles, Search, FileEdit, CheckCheck, RefreshCw, Send } from 'lucide-react';
import { PostRevision, PostReview } from '../types';

interface AgentWorkflowVisualizerProps {
  status: string;
  iterationCount: number;
  maxIterations: number;
  revisions: PostRevision[];
  reviews: PostReview[];
  finalScore?: number;
  qualityThreshold: number;
}

export const AgentWorkflowVisualizer: React.FC<AgentWorkflowVisualizerProps> = ({
  status,
  iterationCount,
  maxIterations,
  revisions,
  reviews,
  finalScore,
  qualityThreshold,
}) => {
  const steps = [
    { id: 'planner', name: 'Planner Agent', desc: 'Strategy & Hook Ideation', icon: Sparkles },
    { id: 'researcher', name: 'Researcher Agent', desc: 'Verified Fact Retrieval', icon: Search },
    { id: 'generator', name: 'Generator Agent', desc: `Post Drafting (Iter ${iterationCount})`, icon: FileEdit },
    { id: 'reviewer', name: 'Reviewer Agent', desc: '10-Dimension Rubric Scoring', icon: CheckCheck },
    { id: 'approval', name: 'Human Approval', desc: 'Mandatory Policy Verification', icon: Send },
  ];

  const getStepStatus = (index: number) => {
    if (status === 'published' || status === 'approved' || status === 'awaiting_approval') {
      return 'completed';
    }
    if (status === 'generating') {
      if (index <= 2) return 'completed';
      if (index === 3) return 'active';
      return 'pending';
    }
    return 'completed';
  };

  return (
    <div className="glass-panel p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 text-blue-400 ${status === 'generating' ? 'animate-spin' : ''}`} />
            Agentic Orchestration State Machine
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            LangGraph Multi-Agent Feedback Loop & Discriminator Quality Gate
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            Iteration: <span className="text-blue-400 font-bold">{iterationCount}</span> / {maxIterations}
          </div>
          <div className="px-3 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            Threshold: <span className="text-emerald-400 font-bold">{qualityThreshold}</span>/100
          </div>
        </div>
      </div>

      {/* Visual Pipeline Bar */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const s = getStepStatus(idx);
          const isDone = s === 'completed';
          const isActive = s === 'active';

          return (
            <div
              key={step.id}
              className={`relative p-3.5 rounded-lg border transition-all ${
                isActive
                  ? 'bg-blue-500/10 border-blue-500/50 shadow-lg shadow-blue-500/10'
                  : isDone
                  ? 'bg-slate-900/90 border-slate-700/80'
                  : 'bg-slate-900/30 border-slate-800/50 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`p-1.5 rounded-md ${isActive ? 'bg-blue-500 text-white' : isDone ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                {isActive ? (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                ) : isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-slate-700" />
                )}
              </div>
              <p className="text-xs font-semibold text-slate-200">{step.name}</p>
              <p className="text-[11px] text-slate-400 mt-0.5">{step.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
