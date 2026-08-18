from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GeneratePostRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic or prompt for the post")
    target_audience: str = Field(default="Tech Leaders & Engineers")
    tone: str = Field(default="thought-provoking")
    content_objective: str = Field(default="Thought Leadership")
    quality_threshold: int = Field(default=85, ge=50, le=100)
    max_iterations: int = Field(default=5, ge=1, le=10)

class HumanApprovalRequest(BaseModel):
    approved: bool
    feedback_comment: Optional[str] = None

class EditPostRequest(BaseModel):
    content: str = Field(..., min_length=10)

class PostRevisionResponse(BaseModel):
    id: str
    iteration_number: int
    content: str
    hook: Optional[str] = None
    hashtags: Optional[List[str]] = []
    character_count: int
    word_count: int
    generated_by_model: Optional[str] = None
    created_at: datetime

class PostReviewResponse(BaseModel):
    id: str
    revision_id: str
    iteration_number: int
    overall_score: int
    approved: bool
    score_hook_impact: int
    score_storytelling: int
    score_professional_depth: int
    score_clarity: int
    score_engagement_potential: int
    score_originality: int
    score_structure: int
    score_actionability: int
    score_emotional_resonance: int
    score_authenticity: int
    identified_flaws: Optional[List[str]] = []
    feedback: Optional[str] = None
    improvement_instructions: Optional[List[str]] = []
    created_at: datetime

class PublishingHistoryResponse(BaseModel):
    id: str
    linkedin_post_id: Optional[str] = None
    post_content: str
    status: str
    published_at: datetime
    is_mock: bool

class SessionDetailResponse(BaseModel):
    id: str
    user_id: str
    topic: str
    target_audience: str
    tone: str
    content_objective: str
    quality_threshold: int
    max_iterations: int
    final_post_content: Optional[str] = None
    final_quality_score: Optional[int] = None
    iteration_count: int
    status: str
    human_approved: bool
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    revisions: List[PostRevisionResponse] = []
    reviews: List[PostReviewResponse] = []
    publishing_records: List[PublishingHistoryResponse] = []

class SessionListItemResponse(BaseModel):
    id: str
    topic: str
    target_audience: str
    tone: str
    status: str
    final_quality_score: Optional[int] = None
    iteration_count: int
    human_approved: bool
    created_at: datetime
    updated_at: datetime
