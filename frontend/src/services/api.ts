import axios from 'axios';
import {
  ContentSessionDetail,
  SessionListItem,
  GeneratePostRequest,
  LinkedInStatus,
  LinkedInPublishResponse,
  EvaluationReport,
  DashboardStats,
  ObservabilityLog,
  User,
} from '../types';

const API_BASE = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('pf_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  async getCurrentUser(): Promise<User> {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  async generatePost(payload: GeneratePostRequest): Promise<ContentSessionDetail> {
    const res = await apiClient.post<ContentSessionDetail>('/posts/generate', payload);
    return res.data;
  },

  async listPosts(): Promise<SessionListItem[]> {
    const res = await apiClient.get<SessionListItem[]>('/posts');
    return res.data;
  },

  async getPostDetail(sessionId: string): Promise<ContentSessionDetail> {
    const res = await apiClient.get<ContentSessionDetail>(`/posts/${sessionId}`);
    return res.data;
  },

  async approvePost(sessionId: string, approved: boolean, comment?: string): Promise<ContentSessionDetail> {
    const res = await apiClient.post<ContentSessionDetail>(`/posts/${sessionId}/approve`, {
      approved,
      feedback_comment: comment,
    });
    return res.data;
  },

  async editPost(sessionId: string, content: string): Promise<ContentSessionDetail> {
    const res = await apiClient.put<ContentSessionDetail>(`/posts/${sessionId}/edit`, {
      content,
    });
    return res.data;
  },

  // LinkedIn Endpoints
  async getLinkedInAuthUrl(): Promise<{ authorization_url: string; state: string; provider: string; is_mock: boolean }> {
    const res = await apiClient.get('/linkedin/auth-url');
    return res.data;
  },

  async getLinkedInStatus(): Promise<LinkedInStatus> {
    const res = await apiClient.get<LinkedInStatus>('/linkedin/status');
    return res.data;
  },

  async disconnectLinkedIn(): Promise<{ status: string; message: string }> {
    const res = await apiClient.post('/linkedin/disconnect');
    return res.data;
  },

  async publishToLinkedIn(sessionId: string, customContent?: string): Promise<LinkedInPublishResponse> {
    const res = await apiClient.post<LinkedInPublishResponse>('/linkedin/publish', {
      session_id: sessionId,
      confirmation: true,
      custom_content: customContent,
    });
    return res.data;
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await apiClient.get<DashboardStats>('/dashboard/stats');
    return res.data;
  },

  async getEvaluationReport(): Promise<EvaluationReport> {
    const res = await apiClient.get<EvaluationReport>('/dashboard/evaluation');
    return res.data;
  },

  async getSessionTraces(sessionId: string): Promise<ObservabilityLog[]> {
    const res = await apiClient.get<ObservabilityLog[]>(`/observability/traces/${sessionId}`);
    return res.data;
  },
};
