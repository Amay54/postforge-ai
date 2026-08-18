import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  Send, 
  CheckCircle2, 
  XCircle, 
  Edit3, 
  ArrowLeft, 
  AlertTriangle,
  Radio,
  CheckCheck,
  Globe,
  Loader2,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { ContentSessionDetail, LinkedInStatus } from '../types';
import { AgentWorkflowVisualizer } from '../components/AgentWorkflowVisualizer';
import { QualityScoreCard } from '../components/QualityScoreCard';
import { ReviewerRadar } from '../components/ReviewerRadar';
import { RevisionComparator } from '../components/RevisionComparator';
import { PostPreview } from '../components/PostPreview';
import { PostEditorModal } from '../components/PostEditorModal';
import { LinkedInConnectModal } from '../components/LinkedInConnectModal';

export const PostDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<ContentSessionDetail | null>(null);
  const [accountStatus, setAccountStatus] = useState<LinkedInStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'preview' | 'reviews' | 'diff'>('preview');

  // Modals & Action States
  const [editorOpen, setEditorOpen] = useState(false);
  const [connectModalOpen, setConnectModalOpen] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [publishSuccessMsg, setPublishSuccessMsg] = useState<{ id: string; mock: boolean; msg: string } | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!id) return;
      try {
        const [sessData, statusData] = await Promise.all([
          api.getPostDetail(id),
          api.getLinkedInStatus(),
        ]);
        setSession(sessData);
        setAccountStatus(statusData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleApprove = async () => {
    if (!id) return;
    try {
      const updated = await api.approvePost(id, true);
      setSession(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async () => {
    if (!id) return;
    try {
      const updated = await api.approvePost(id, false, "Rejected for further manual refinement");
      setSession(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveEdit = async (newContent: string) => {
    if (!id) return;
    const updated = await api.editPost(id, newContent);
    setSession(updated);
  };

  const handleApproveAndPublish = async () => {
    if (!id || !session) return;
    setPublishing(true);
    setPublishError(null);
    setPublishSuccessMsg(null);

    try {
      // Step 1: Ensure approved in DB if not already
      if (!session.human_approved) {
        await api.approvePost(id, true);
      }

      // Step 2: Publish to LinkedIn provider (Official or Mock)
      const res = await api.publishToLinkedIn(id);
      if (res.success) {
        setPublishSuccessMsg({
          id: res.linkedin_post_id || 'N/A',
          mock: res.is_mock,
          msg: res.message,
        });
        const updated = await api.getPostDetail(id);
        setSession(updated);
        setShowApprovalModal(false);
      }
    } catch (err: any) {
      const safeErr = err.response?.data?.detail || err.message || 'Failed to publish post to LinkedIn.';
      setPublishError(safeErr);
    } finally {
      setPublishing(false);
    }
  };

  if (loading || !session) {
    return <div className="text-center py-24 text-xs text-slate-400">Loading session detail...</div>;
  }

  const latestReview = session.reviews[session.reviews.length - 1];
  const latestRevision = session.revisions[session.revisions.length - 1];
  const displayContent = session.final_post_content || latestRevision?.content || '';
  const isMock = !accountStatus || accountStatus.provider === 'mock';
  const targetProfileName = accountStatus?.profile?.name || 'Amay Yadav';

  return (
    <div className="space-y-6">
      {/* Top Navigation & Status Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-blue-400 uppercase tracking-wider">
                Session #{session.id.slice(0, 8)}
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                isMock ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              }`}>
                {isMock ? '?? Simulation Mode' : '?? Live Publishing'}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white max-w-xl truncate mt-0.5">{session.topic}</h1>
          </div>
        </div>

        {/* Human Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEditorOpen(true)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-850 text-slate-200 text-xs font-semibold flex items-center gap-1.5"
          >
            <Edit3 className="w-3.5 h-3.5 text-blue-400" />
            <span>Edit Post</span>
          </button>

          {!session.human_approved && session.status !== 'PUBLISHED' && session.status !== 'published' && (
            <>
              <button
                onClick={handleReject}
                className="px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 text-rose-300 text-xs font-semibold flex items-center gap-1.5"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => setShowApprovalModal(true)}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-600/20 cursor-pointer"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Review & Approve</span>
              </button>
            </>
          )}

          {session.human_approved && session.status !== 'PUBLISHED' && session.status !== 'published' && (
            <button
              onClick={() => setShowApprovalModal(true)}
              className="px-5 py-2 rounded-lg bg-[#0a66c2] hover:bg-[#004182] text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/20 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Publish to LinkedIn</span>
            </button>
          )}
        </div>
      </div>

      {/* Success Notification Banner */}
      {publishSuccessMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs space-y-1">
          <div className="flex items-center gap-2 font-bold text-sm text-emerald-200">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>? Published Successfully!</span>
            {publishSuccessMsg.mock && (
              <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                SIMULATION
              </span>
            )}
          </div>
          <p className="text-[11px] text-emerald-300/90">
            LinkedIn Post ID: <code className="font-mono bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-500/20">{publishSuccessMsg.id}</code>
          </p>
          <p className="text-[11px] text-slate-400">{publishSuccessMsg.msg}</p>
        </div>
      )}

      {/* Error Banner */}
      {publishError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-rose-200">Publishing Failed</h4>
            <p className="text-[11px] text-rose-300/90 mt-0.5">{publishError}</p>
          </div>
        </div>
      )}

      {/* Multi-Agent Orchestration Visualizer */}
      <AgentWorkflowVisualizer
        status={session.status}
        iterationCount={session.iteration_count}
        maxIterations={session.max_iterations}
        revisions={session.revisions}
        reviews={session.reviews}
        finalScore={session.final_quality_score}
        qualityThreshold={session.quality_threshold}
      />

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Score & 10-Dimension Radar */}
        <div className="lg:col-span-4 space-y-6">
          <QualityScoreCard
            score={session.final_quality_score ?? latestReview?.overall_score ?? 0}
            threshold={session.quality_threshold}
            passed={session.human_approved || (session.final_quality_score ?? 0) >= session.quality_threshold}
            iteration={session.iteration_count}
          />

          <div className="glass-panel p-5">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              10-Dimension Quality Radar
            </h4>
            <ReviewerRadar review={latestReview} />
          </div>

          {/* Feedback Instructions */}
          {latestReview && (
            <div className="glass-panel p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Reviewer Directives
              </h4>
              <p className="text-xs text-slate-300 italic bg-slate-950 p-3 rounded-lg border border-slate-800">
                "{latestReview.feedback || 'Post satisfies quality threshold criteria.'}"
              </p>
              {latestReview.improvement_instructions && latestReview.improvement_instructions.length > 0 && (
                <ul className="text-xs text-slate-400 space-y-1 pl-4 list-disc">
                  {latestReview.improvement_instructions.map((inst, i) => (
                    <li key={i}>{inst}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Feed Preview / Tabs */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex border-b border-slate-800 gap-4 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('preview')}
              className={`pb-3 transition-colors ${activeTab === 'preview' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              LinkedIn Feed View
            </button>
            <button
              onClick={() => setActiveTab('diff')}
              className={`pb-3 transition-colors ${activeTab === 'diff' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Revision Diff ({session.revisions.length})
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`pb-3 transition-colors ${activeTab === 'reviews' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Review History ({session.reviews.length})
            </button>
          </div>

          {activeTab === 'preview' && (
            <div className="py-2">
              <PostPreview
                content={displayContent}
                authorProfile={accountStatus?.profile}
                isMock={isMock}
              />
            </div>
          )}

          {activeTab === 'diff' && (
            <RevisionComparator revisions={session.revisions} />
          )}

          {activeTab === 'reviews' && (
            <div className="space-y-4">
              {session.reviews.map((rev) => (
                <div key={rev.id} className="glass-panel p-5 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">Iteration #{rev.iteration_number} Review</span>
                    <span className="font-mono font-bold text-blue-400">{rev.overall_score}/100</span>
                  </div>
                  <p className="text-xs text-slate-300">{rev.feedback}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* FINAL APPROVAL & PUBLISH MODAL (Section 11) */}
      {showApprovalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Send className="w-5 h-5 text-blue-400" />
              Ready to publish to LinkedIn
            </h3>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Quality Score:</span>
                <span className="font-mono font-bold text-emerald-400">
                  {session.final_quality_score ?? latestReview?.overall_score ?? 85}/100
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Target Profile:</span>
                <span className="font-semibold text-white">{targetProfileName}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Publishing Mode:</span>
                <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                  isMock ? 'bg-amber-500/10 text-amber-300' : 'bg-emerald-500/10 text-emerald-300'
                }`}>
                  {isMock ? 'SIMULATION (Mock Provider)' : 'OFFICIAL LINKEDIN POSTS API'}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {isMock ? (
                <span>This post will be processed in <strong>Simulation Mode</strong> without posting to live LinkedIn.</span>
              ) : (
                <span>This will publish the approved post directly to your authenticated live LinkedIn feed on behalf of <strong>{targetProfileName}</strong>.</span>
              )}
            </p>

            <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
              <button
                onClick={() => setShowApprovalModal(false)}
                disabled={publishing}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleApproveAndPublish}
                disabled={publishing}
                className="px-5 py-2 rounded-lg bg-[#0a66c2] hover:bg-[#004182] text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20"
              >
                {publishing ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Publishing...</span>
                  </>
                ) : (
                  <>
                    <CheckCheck className="w-3.5 h-3.5" />
                    <span>Approve & Publish</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Editor Modal */}
      <PostEditorModal
        isOpen={editorOpen}
        initialContent={displayContent}
        onClose={() => setEditorOpen(false)}
        onSave={handleSaveEdit}
      />

      {/* LinkedIn Connect Modal */}
      <LinkedInConnectModal
        isOpen={connectModalOpen}
        accountStatus={accountStatus}
        onClose={() => setConnectModalOpen(false)}
        onStatusUpdated={async () => {
          const statusData = await api.getLinkedInStatus();
          setAccountStatus(statusData);
        }}
      />
    </div>
  );
};
