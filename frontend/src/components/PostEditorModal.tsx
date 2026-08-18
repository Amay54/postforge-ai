import React, { useState } from 'react';
import { X, Save, Edit3 } from 'lucide-react';

interface PostEditorModalProps {
  isOpen: boolean;
  initialContent: string;
  onClose: () => void;
  onSave: (content: string) => Promise<void>;
}

export const PostEditorModal: React.FC<PostEditorModalProps> = ({
  isOpen,
  initialContent,
  onClose,
  onSave,
}) => {
  const [content, setContent] = useState(initialContent);
  const [saving, setSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(content);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Edit3 className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">Human Post Editor</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="my-4 flex-1 flex flex-col">
          <label className="text-xs font-semibold text-slate-300 mb-1">
            Edit Post Content (Overrides AI Output)
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={12}
            className="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-xs sm:text-sm font-sans focus:outline-none focus:border-blue-500/50 resize-none leading-relaxed flex-1"
          />
          <div className="flex justify-between items-center text-[11px] text-slate-400 mt-2 font-mono">
            <span>Characters: {content.length}</span>
            <span>Words: {content.split(/\s+/).filter(Boolean).length}</span>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{saving ? 'Saving...' : 'Save Changes'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
