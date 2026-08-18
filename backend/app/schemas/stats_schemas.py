from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class DimensionScoreAverage(BaseModel):
    dimension: str
    display_name: str
    average_score: float

class EvaluationReportResponse(BaseModel):
    total_sessions: int
    quality_pass_rate: float
    avg_iterations_to_pass: float
    avg_final_quality_score: float
    dimension_averages: List[DimensionScoreAverage]
    iteration_distribution: Dict[str, int]
    total_tokens_consumed: int
    avg_pipeline_duration_seconds: float

class DashboardStatsResponse(BaseModel):
    total_posts_generated: int
    total_posts_published: int
    total_posts_approved: int
    avg_quality_score: float
    recent_sessions_count: int

class ObservabilityLogResponse(BaseModel):
    id: str
    session_id: str
    agent_name: str
    step_number: int
    prompt: Optional[str] = None
    raw_output: Optional[str] = None
    model_name: Optional[str] = None
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    latency_ms: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
