import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Cpu, 
  Award, 
  CheckCircle2, 
  Activity 
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { api } from '../services/api';
import { EvaluationReport } from '../types';

export const Evaluation: React.FC = () => {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getEvaluationReport();
        setReport(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return <div className="text-center py-24 text-xs text-slate-400">Loading evaluation report...</div>;
  }

  const dimensionData = report?.dimension_averages || [];
  const distributionData = Object.entries(report?.iteration_distribution || {}).map(([iter, count]) => ({
    iteration: `Iter ${iter}`,
    count,
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-400" />
          Evaluation & Quality Rubric Analytics
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Benchmarking generator convergence, 10-dimension rubric averages, and discriminator pass rates.
        </p>
      </div>

      {/* Aggregate Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Quality Pass Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-emerald-400">{report?.quality_pass_rate ?? 0}%</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Sessions reaching threshold</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Iterations To Pass</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{report?.avg_iterations_to_pass ?? 0}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Rounds until Reviewer approval</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Final Score</span>
            <Award className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{report?.avg_final_quality_score ?? 0}</span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Across approved drafts</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Total Tokens</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white font-mono">{report?.total_tokens_consumed.toLocaleString() ?? 0}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Prompt & completion usage</p>
        </div>
      </div>

      {/* 10-Dimension Score Breakdown */}
      <div className="glass-panel p-6">
        <h3 className="text-base font-bold text-white mb-1">10-Dimension Editorial Rubric Performance</h3>
        <p className="text-xs text-slate-400 mb-6">Historical averages across all generated drafts</p>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dimensionData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis 
                dataKey="display_name" 
                tick={{ fill: '#94a3b8', fontSize: 10 }}
                angle={-25}
                textAnchor="end"
                interval={0}
              />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#f8fafc',
                }}
              />
              <Bar dataKey="average_score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Iteration Distribution Chart */}
      <div className="glass-panel p-6">
        <h3 className="text-base font-bold text-white mb-1">Generator Convergence Distribution</h3>
        <p className="text-xs text-slate-400 mb-6">Number of feedback loops required before satisfying quality threshold</p>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distributionData} margin={{ top: 10, right: 20, left: -10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="iteration" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#f8fafc',
                }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
