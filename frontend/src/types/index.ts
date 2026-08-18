export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
}

export interface PostRevision {
  id: string;
  iteration_number: number;
  content: string;
  hook?: string;
  hashtags?: string[];
  character_count: number;
  word_count: number;
  generated_by_model?: string;
  created_at: string;
}

export interface PostReview {
  id: string;
  revision_id: string;
  iteration_number: number;
  overall_score: number;
  approved: boolean;
  score_hook_impact: number;
  score_storytelling: number;
  score_professional_depth: number;
  score_clarity: number;
  score_engagement_potential: number;
  score_originality: number;
  score_structure: number;
  score_actionability: number;
  score_emotional_resonance: number;
  score_authenticity: number;
  identified_flaws?: string[];
  feedback?: string;
  improvement_instructions?: string[];
  created_at: string;
}

export interface PublishingHistory {
  id: string;
  linkedin_post_id?: string;
  post_content: string;
  status: string;
  provider: string;
  published_at: string;
  is_mock: boolean;
}

export interface ContentSessionDetail {
  id: string;
  user_id: string;
  topic: string;
  target_audience: string;
  tone: string;
  content_objective: string;
  quality_threshold: number;
  max_iterations: number;
  final_post_content?: string;
  final_quality_score?: number;
  iteration_count: number;
  status: string;
  human_approved: boolean;
  approved_at?: string;
  created_at: string;
  updated_at: string;
  revisions: PostRevision[];
  reviews: PostReview[];
  publishing_records?: PublishingHistory[];
}

export interface SessionListItem {
  id: string;
  topic: string;
  target_audience: string;
  tone: string;
  status: string;
  final_quality_score?: number;
  iteration_count: number;
  human_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface GeneratePostRequest {
  topic: string;
  target_audience?: string;
  tone?: string;
  content_objective?: string;
  quality_threshold?: number;
  max_iterations?: number;
}

export interface LinkedInProfileData {
  name?: string;
  member_id?: string;
  member_urn?: string;
  email?: string;
  picture_url?: string;
  profile_url?: string;
}

export interface LinkedInStatus {
  provider: 'mock' | 'official';
  mode: 'simulation' | 'live';
  connected: boolean;
  publishing_available: boolean;
  profile?: LinkedInProfileData;
  error?: string;
  expires_at?: string;
}

export interface LinkedInPublishResponse {
  success: boolean;
  linkedin_post_id?: string;
  status: string;
  provider: string;
  is_mock: boolean;
  message: string;
  published_at?: string;
  error_details?: string;
}

export interface DimensionAverage {
  dimension: string;
  display_name: string;
  average_score: number;
}

export interface EvaluationReport {
  total_sessions: number;
  quality_pass_rate: number;
  avg_iterations_to_pass: number;
  avg_final_quality_score: number;
  dimension_averages: DimensionAverage[];
  iteration_distribution: Record<string, number>;
  total_tokens_consumed: number;
  avg_pipeline_duration_seconds: number;
}

export interface DashboardStats {
  total_posts_generated: number;
  total_posts_published: number;
  total_posts_approved: number;
  avg_quality_score: number;
  recent_sessions_count: number;
}

export interface ObservabilityLog {
  id: string;
  session_id: string;
  agent_name: string;
  step_number: number;
  prompt?: string;
  raw_output?: string;
  model_name?: string;
  tokens_prompt: number;
  tokens_completion: number;
  tokens_total: number;
  latency_ms: number;
  status: string;
  error_message?: string;
  created_at: string;
}
