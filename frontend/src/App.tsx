import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { CreatePost } from './pages/CreatePost';
import { PostDetail } from './pages/PostDetail';
import { Evaluation } from './pages/Evaluation';
import { Observability } from './pages/Observability';
import { Settings } from './pages/Settings';
import { LinkedInConnectModal } from './components/LinkedInConnectModal';
import { api } from './services/api';
import { LinkedInStatus } from './types';

export const App: React.FC = () => {
  const [linkedInStatus, setLinkedInStatus] = useState<LinkedInStatus | null>(null);
  const [connectModalOpen, setConnectModalOpen] = useState(false);

  const loadStatus = async () => {
    try {
      const status = await api.getLinkedInStatus();
      setLinkedInStatus(status);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
        <Navbar
          linkedInStatus={linkedInStatus}
          onConnectClick={() => setConnectModalOpen(true)}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreatePost />} />
            <Route path="/posts/:id" element={<PostDetail />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="/observability" element={<Observability />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        <LinkedInConnectModal
          isOpen={connectModalOpen}
          linkedInStatus={linkedInStatus}
          onClose={() => setConnectModalOpen(false)}
          onStatusUpdated={loadStatus}
        />
      </div>
    </BrowserRouter>
  );
};
