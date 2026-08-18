import React from 'react';
import { ThumbsUp, MessageSquare, Repeat2, Send, Globe, MoreHorizontal, ShieldCheck } from 'lucide-react';
import { LinkedInProfileData } from '../types';

interface PostPreviewProps {
  content: string;
  authorProfile?: LinkedInProfileData;
  isMock?: boolean;
}

export const PostPreview: React.FC<PostPreviewProps> = ({ content, authorProfile, isMock = true }) => {
  const name = authorProfile?.name || 'Amay Yadav';
  const avatar = authorProfile?.picture_url || 'https://ui-avatars.com/api/?name=Amay+Yadav&background=0a66c2&color=fff&size=150';

  return (
    <div className="space-y-2">
      {/* Simulation / Live Badge */}
      <div className="flex items-center justify-between px-1">
        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
          isMock 
            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
        }`}>
          {isMock ? '?? Simulation Preview Mockup' : '?? Live Feed Target Preview'}
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          Author: {name}
        </span>
      </div>

      <div className="bg-white text-slate-900 rounded-xl shadow-2xl border border-slate-200 max-w-xl mx-auto overflow-hidden">
        {/* Header */}
        <div className="p-4 flex items-start justify-between border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <img
              src={avatar}
              alt={name}
              className="w-12 h-12 rounded-full object-cover border border-slate-200"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <h4 className="text-sm font-bold text-slate-900 hover:text-blue-600 cursor-pointer">
                  {name}
                </h4>
                <span className="text-xs text-slate-400">? 1st</span>
              </div>
              <p className="text-xs text-slate-500 leading-tight">
                Enterprise AI Architect | Generative Systems Leadership
              </p>
              <div className="flex items-center gap-1 text-[10px] text-slate-400 mt-0.5">
                <span>Just now</span>
                <span>?</span>
                <Globe className="w-2.5 h-2.5" />
              </div>
            </div>
          </div>

          <button className="text-slate-400 hover:text-slate-600 p-1">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>

        {/* Post Body */}
        <div className="p-4 text-xs sm:text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
          {content || 'Post content will be previewed here...'}
        </div>

        {/* Social Counts Mock */}
        <div className="px-4 py-2 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-100">
          <div className="flex items-center space-x-1">
            <span className="flex -space-x-1">
              <span className="w-4 h-4 rounded-full bg-blue-600 flex items-center justify-center text-[8px] text-white">??</span>
              <span className="w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center text-[8px] text-white">??</span>
            </span>
            <span className="ml-1 font-medium">142 reactions</span>
          </div>
          <span>38 comments ? 12 reposts</span>
        </div>

        {/* Action Buttons */}
        <div className="px-2 py-1.5 flex items-center justify-around border-t border-slate-100 text-slate-600">
          <button className="flex items-center space-x-1.5 py-2 px-3 rounded hover:bg-slate-50 text-xs font-medium">
            <ThumbsUp className="w-4 h-4 text-slate-500" />
            <span>Like</span>
          </button>
          <button className="flex items-center space-x-1.5 py-2 px-3 rounded hover:bg-slate-50 text-xs font-medium">
            <MessageSquare className="w-4 h-4 text-slate-500" />
            <span>Comment</span>
          </button>
          <button className="flex items-center space-x-1.5 py-2 px-3 rounded hover:bg-slate-50 text-xs font-medium">
            <Repeat2 className="w-4 h-4 text-slate-500" />
            <span>Repost</span>
          </button>
          <button className="flex items-center space-x-1.5 py-2 px-3 rounded hover:bg-slate-50 text-xs font-medium">
            <Send className="w-4 h-4 text-slate-500" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
};
