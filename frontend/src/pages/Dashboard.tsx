import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  Send, 
  CheckCircle2, 
  Award, 
  Clock, 
  ArrowRight,
  TrendingUp,
  FileText,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardStats, SessionListItem } from '../types';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [posts, setPosts] = useState<SessionListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, postsData] = await Promise.all([
          api.getDashboardStats(),
          api.listPosts(),
        ]);
        setStats(statsData);
        setPosts(postsData);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="glass-panel p-8 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-blue-950/40">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Autonomous Multi-Agent Editorial Pipeline
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            PostForge AI
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-300 leading-relaxed">
            Generate viral, high-authority LinkedIn posts with iterative Generator-Reviewer feedback loops and verified citations.
          </p>
          <div className="mt-6 flex flex-wrap gap-4">
            <Link
              to="/create"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs sm:text-sm shadow-lg shadow-blue-500/20 flex items-center gap-2 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Create New Post</span>
            </Link>
            <Link
              to="/evaluation"
              className="px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 font-semibold text-xs sm:text-sm border border-slate-700/60 flex items-center gap-2 transition-all"
            >
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>View Evaluation Metrics</span>
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Posts Generated</span>
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{stats?.total_posts_generated ?? 0}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Multi-agent content sessions</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Quality Score</span>
            <Award className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-emerald-400">{stats?.avg_quality_score ?? 0}</span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">10-dimension rubric weighted average</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Human Approved</span>
            <CheckCircle2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{stats?.total_posts_approved ?? 0}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Explicit human-in-the-loop gates</p>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Published to LinkedIn</span>
            <Send className="w-4 h-4 text-[#0a66c2]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-[#0a66c2]">{stats?.total_posts_published ?? 0}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Official LinkedIn API & Sandbox</p>
        </div>
      </div>

      {/* Recent Content Sessions */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-bold text-white">Recent Content Generations</h3>
            <p className="text-xs text-slate-400">History of agentic drafting, reviews, and publishing</p>
          </div>
          <Link to="/create" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1">
            <span>New Generation</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-12 text-xs text-slate-400">Loading recent posts...</div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
            <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs font-semibold text-slate-300">No posts generated yet</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Click "Create New Post" to start the multi-agent pipeline.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="pb-3 px-4">Topic / Prompt</th>
                  <th className="pb-3 px-4">Target Audience</th>
                  <th className="pb-3 px-4">Score</th>
                  <th className="pb-3 px-4">Iterations</th>
                  <th className="pb-3 px-4">Status</th>
                  <th className="pb-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {posts.map((post) => (
                  <tr key={post.id} className="hover:bg-slate-900/60 transition-colors">
                    <td className="py-3 px-4 max-w-xs font-medium truncate text-white">
                      {post.topic}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{post.target_audience}</td>
                    <td className="py-3 px-4">
                      {post.final_quality_score ? (
                        <span className={`px-2 py-0.5 rounded font-mono font-bold ${post.final_quality_score >= 85 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                          {post.final_quality_score}/100
                        </span>
                      ) : (
                        <span className="text-slate-500 font-mono">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">{post.iteration_count}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${
                        post.status === 'published' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        post.status === 'approved' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                        post.status === 'awaiting_approval' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {post.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/posts/${post.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-[11px] transition-colors"
                      >
                        <span>View Workflow</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
