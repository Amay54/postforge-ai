from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PostGenerationState(BaseModel):
    session_id: str
    user_id: str
    topic: str
    target_audience: str = "Tech Professionals"
    tone: str = "thought-provoking"
    content_objective: str = "Thought Leadership"
    quality_threshold: int = 85
    max_iterations: int = 5
    
    # Workflow Progression
    requires_research: bool = True
    iteration: int = 0
    
    # Agent Artifacts
    plan: Optional[Dict[str, Any]] = None
    research: Optional[Dict[str, Any]] = None
    current_post: Optional[str] = None
    hook: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    
    # Review & Feedback
    latest_review: Optional[Dict[str, Any]] = None
    quality_score: int = 0
    feedback_history: List[str] = Field(default_factory=list)
    
    # Terminal Decisions
    quality_passed: bool = False
    max_iterations_reached: bool = False
    status: str = "initializing"
    current_step: str = "start"
    error: Optional[str] = None
