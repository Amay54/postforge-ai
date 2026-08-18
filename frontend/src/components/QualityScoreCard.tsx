import React from 'react';
import { Award, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface QualityScoreCardProps {
  score: number;
  threshold: number;
  passed: boolean;
  iteration: number;
}

export const QualityScoreCard: React.FC<QualityScoreCardProps> = ({
  score,
  threshold,
  passed,
  iteration,
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 85) return 'text-emerald-400 from-emerald-500/20 to-emerald-500/5 border-emerald-500/30';
    if (val >= 70) return 'text-amber-400 from-amber-500/20 to-amber-500/5 border-amber-500/30';
    return 'text-rose-400 from-rose-500/20 to-rose-500/5 border-rose-500/30';
  };

  return (
    <div className={`p-5 rounded-xl border bg-gradient-to-b ${getScoreColor(score)}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          Reviewer Quality Score
        </span>
        <Award className="w-4 h-4 text-slate-400" />
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-4xl font-extrabold tracking-tight text-white">{score}</span>
        <span className="text-sm font-medium text-slate-400">/ 100</span>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          {passed ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Quality Gate Passed</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-amber-400 font-medium">Below Target ({threshold})</span>
            </>
          )}
        </div>
        <span className="text-slate-400 font-mono">Iteration #{iteration}</span>
      </div>
    </div>
  );
};
