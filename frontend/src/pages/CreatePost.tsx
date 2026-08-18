import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Loader2, Target, Sliders, Layers, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const CreatePost: React.FC = () => {
  const navigate = useNavigate();
  const [topic, setTopic] = useState('');
  const [targetAudience, setTargetAudience] = useState('Tech Leaders & Engineers');
  const [tone, setTone] = useState('thought-provoking');
  const [contentObjective, setContentObjective] = useState('Thought Leadership');
  const [qualityThreshold, setQualityThreshold] = useState(85);
  const [maxIterations, setMaxIterations] = useState(5);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const samplePrompts = [
    "Why fine-tuning LLMs on custom data fails without RAG architecture in 2026",
    "3 non-obvious lessons from scaling agentic workflows to 10M daily executions",
    "The death of monolithic microservices: Why serverless agent graphs are taking over",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || loading) return;

    setLoading(true);
    setErrorMessage(null);

    const payload = {
      topic: topic.trim(),
      target_audience: targetAudience,
      tone,
      content_objective: contentObjective,
      quality_threshold: qualityThreshold,
      max_iterations: maxIterations,
    };

    console.log('[PostForge] Launch button clicked');
    console.log('[PostForge] Payload prepared:', payload);

    try {
      console.log('[PostForge] Sending generation request to /api/posts/generate');
      const session = await api.generatePost(payload);
      console.log('[PostForge] API response received successfully:', session);
      navigate(`/posts/${session.id}`);
    } catch (err: any) {
      console.error('[PostForge] Generation request failed:', err);
      const safeMsg = err.response?.data?.detail || err.message || 'Unable to start autonomous generation workflow.';
      setErrorMessage(safeMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-blue-400" />
          Create Agentic LinkedIn Post
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Initiate autonomous Planner, Researcher, Generator, and Reviewer multi-agent workflow.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-rose-200">Generation Failed</h4>
            <p className="text-rose-300/90 text-[11px] mt-0.5">{errorMessage}</p>
            <button
              onClick={handleSubmit}
              className="mt-2.5 px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 rounded font-semibold text-[11px] flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry Generation</span>
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 space-y-6">
        {/* Prompt Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-200 mb-2">
            Topic or Prompt Objective <span className="text-rose-400">*</span>
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            required
            rows={4}
            placeholder="e.g. Write a LinkedIn post explaining why RAG is becoming important for enterprise AI. Target AI engineers. Use a professional and engaging tone. Include 3 practical reasons and a strong closing question."
            className="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-xs sm:text-sm focus:outline-none focus:border-blue-500/50 resize-none leading-relaxed"
          />

          {/* Prompt quick templates */}
          <div className="mt-2.5 flex flex-wrap gap-1.5 items-center">
            <span className="text-[11px] text-slate-500 font-medium">Quick ideas:</span>
            {samplePrompts.map((p, idx) => (
              <button
                type="button"
                key={idx}
                onClick={() => setTopic(p)}
                className="text-[11px] text-slate-400 hover:text-blue-300 bg-slate-900 hover:bg-slate-850 px-2.5 py-1 rounded border border-slate-800 transition-colors"
              >
                {p.slice(0, 45)}...
              </button>
            ))}
          </div>
        </div>

        {/* Controls Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Audience
            </label>
            <select
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none"
            >
              <option value="Tech Leaders & Engineers">Tech Leaders & Engineers</option>
              <option value="Product Managers & Founders">Product Managers & Founders</option>
              <option value="Enterprise C-Suite & Executives">Enterprise C-Suite & Executives</option>
              <option value="AI & ML Practitioners">AI & ML Practitioners</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Desired Tone
            </label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs focus:outline-none"
            >
              <option value="thought-provoking">Thought-Provoking & Contrarian</option>
              <option value="strategic">Strategic & Analytical</option>
              <option value="educational">Educational & Actionable</option>
              <option value="inspirational">Inspirational & Narrative</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Quality Target Threshold ({qualityThreshold}/100)
            </label>
            <input
              type="range"
              min={60}
              max={95}
              value={qualityThreshold}
              onChange={(e) => setQualityThreshold(Number(e.target.value))}
              className="w-full accent-blue-500 cursor-pointer"
            />
            <span className="text-[10px] text-slate-500">Discriminator threshold to approve post</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Max Iterations Loop ({maxIterations})
            </label>
            <input
              type="range"
              min={1}
              max={8}
              value={maxIterations}
              onChange={(e) => setMaxIterations(Number(e.target.value))}
              className="w-full accent-blue-500 cursor-pointer"
            />
            <span className="text-[10px] text-slate-500">Maximum Generator-Reviewer refinement rounds</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            disabled={loading || !topic.trim()}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span className="text-white">Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Launch Autonomous Generation</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
