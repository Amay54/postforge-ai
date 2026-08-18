import React, { useState } from 'react';
import * as Diff from 'diff';
import { PostRevision } from '../types';
import { GitCompare, ArrowRight } from 'lucide-react';

interface RevisionComparatorProps {
  revisions: PostRevision[];
}

export const RevisionComparator: React.FC<RevisionComparatorProps> = ({ revisions }) => {
  if (revisions.length < 2) {
    return (
      <div className="glass-panel p-6 text-center text-xs text-slate-400">
        Multiple revisions will appear here once the Reviewer agent initiates feedback iterations.
      </div>
    );
  }

  const [leftIter, setLeftIter] = useState<number>(revisions[0].iteration_number);
  const [rightIter, setRightIter] = useState<number>(revisions[revisions.length - 1].iteration_number);

  const leftRev = revisions.find((r) => r.iteration_number === leftIter) || revisions[0];
  const rightRev = revisions.find((r) => r.iteration_number === rightIter) || revisions[revisions.length - 1];

  const diffParts = Diff.diffWords(leftRev.content, rightRev.content);

  return (
    <div className="glass-panel p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-2">
          <GitCompare className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">Revision Diff Comparator</h3>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">From:</span>
            <select
              value={leftIter}
              onChange={(e) => setLeftIter(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs focus:outline-none"
            >
              {revisions.map((r) => (
                <option key={r.id} value={r.iteration_number}>
                  Iteration #{r.iteration_number}
                </option>
              ))}
            </select>
          </div>

          <ArrowRight className="w-3.5 h-3.5 text-slate-500" />

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">To:</span>
            <select
              value={rightIter}
              onChange={(e) => setRightIter(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs focus:outline-none"
            >
              {revisions.map((r) => (
                <option key={r.id} value={r.iteration_number}>
                  Iteration #{r.iteration_number}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800/90 font-mono text-xs leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
        {diffParts.map((part, index) => {
          if (part.added) {
            return (
              <span key={index} className="bg-emerald-500/20 text-emerald-300 font-semibold px-0.5 rounded">
                {part.value}
              </span>
            );
          }
          if (part.removed) {
            return (
              <span key={index} className="bg-rose-500/20 text-rose-300 line-through px-0.5 rounded opacity-75">
                {part.value}
              </span>
            );
          }
          return <span key={index} className="text-slate-300">{part.value}</span>;
        })}
      </div>
    </div>
  );
};
