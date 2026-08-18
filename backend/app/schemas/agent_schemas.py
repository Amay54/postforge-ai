from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PlannerOutput(BaseModel):
    hook_angle: str = Field(description="The primary disruptive hook angle for the post.")
    target_audience_pains: List[str] = Field(description="Identified pain points of the target audience.")
    narrative_beats: List[str] = Field(description="Step-by-step structural progression of the post.")
    requires_research: bool = Field(description="Whether live external research/facts are needed.")
    research_queries: List[str] = Field(default_factory=list, description="Search queries if research is needed.")
    key_takeaway: str = Field(description="Core moral, actionable takeaway, or conclusion.")

class ResearchSource(BaseModel):
    title: str
    url: str
    source: str
    claim: str
    confidence: float = 0.9

class ResearchOutput(BaseModel):
    topic: str
    findings: List[ResearchSource] = Field(default_factory=list)
    summary: str

class GeneratorOutput(BaseModel):
    post_text: str = Field(description="The complete, polished LinkedIn post draft with spacing.")
    hook: str = Field(description="The opening 1-2 lines designed to stop scrolling.")
    call_to_action: str = Field(description="Ending question or invitation to comment.")
    hashtags: List[str] = Field(default_factory=list, description="3-5 relevant LinkedIn hashtags.")
    word_count: int = Field(default=0)
    character_count: int = Field(default=0)

class ReviewScores(BaseModel):
    hook_impact: int = Field(ge=0, le=100)
    storytelling: int = Field(ge=0, le=100)
    professional_depth: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    engagement_potential: int = Field(ge=0, le=100)
    originality: int = Field(ge=0, le=100)
    structure: int = Field(ge=0, le=100)
    actionability: int = Field(ge=0, le=100)
    emotional_resonance: int = Field(ge=0, le=100)
    authenticity: int = Field(ge=0, le=100)

class ReviewerOutput(BaseModel):
    dimension_scores: ReviewScores
    overall_score: int = Field(ge=0, le=100, description="Weighted aggregate quality score.")
    approved: bool = Field(description="True only if overall_score >= quality_threshold.")
    issues: List[str] = Field(default_factory=list, description="Specific identified weaknesses.")
    feedback: str = Field(description="Constructive critique detailing what must improve.")
    improvement_instructions: List[str] = Field(default_factory=list, description="Step-by-step directives for the generator.")

class AgentExecutionResult(BaseModel):
    agent_name: str
    content: Dict[str, Any]
    latency_ms: int
    tokens_prompt: int = 0
    tokens_completion: int = 0
    model_name: str = "gemini-2.5-flash"
