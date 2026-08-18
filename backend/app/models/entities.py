import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

def gen_uuid() -> str:
    return str(uuid_pkg.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(191), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(191), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    linkedin_connections: Mapped[List["LinkedInConnection"]] = relationship("LinkedInConnection", back_populates="user", cascade="all, delete-orphan")
    content_sessions: Mapped[List["ContentSession"]] = relationship("ContentSession", back_populates="user", cascade="all, delete-orphan")
    publishing_history: Mapped[List["PublishingHistory"]] = relationship("PublishingHistory", back_populates="user", cascade="all, delete-orphan")

class LinkedInConnection(Base):
    __tablename__ = "linkedin_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    linkedin_member_id: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    linkedin_member_urn: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    profile_name: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[Optional[str]] = mapped_column(String(255), default="openid profile email w_member_social")
    provider: Mapped[str] = mapped_column(String(50), default="mock") # "mock" or "official"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped["User"] = relationship("User", back_populates="linkedin_connections")

class ContentSession(Base):
    __tablename__ = "content_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(191), default="Tech Professionals")
    tone: Mapped[str] = mapped_column(String(100), default="thought-provoking")
    content_objective: Mapped[str] = mapped_column(String(100), default="Thought Leadership")
    quality_threshold: Mapped[int] = mapped_column(Integer, default=85)
    max_iterations: Mapped[int] = mapped_column(Integer, default=5)
    
    final_post_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    # State machine: DRAFT, GENERATING, REVIEWING, READY_FOR_APPROVAL, APPROVED, PUBLISHING, PUBLISHED, PUBLISH_FAILED, REJECTED, OAUTH_REQUIRED, PERMISSION_REQUIRED
    status: Mapped[str] = mapped_column(String(50), default="initializing")
    
    human_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped["User"] = relationship("User", back_populates="content_sessions")
    revisions: Mapped[List["PostRevision"]] = relationship("PostRevision", back_populates="session", cascade="all, delete-orphan", order_by="PostRevision.iteration_number")
    reviews: Mapped[List["PostReview"]] = relationship("PostReview", back_populates="session", cascade="all, delete-orphan", order_by="PostReview.iteration_number")
    publishing_records: Mapped[List["PublishingHistory"]] = relationship("PublishingHistory", back_populates="session", cascade="all, delete-orphan")
    execution_logs: Mapped[List["AgentExecutionLog"]] = relationship("AgentExecutionLog", back_populates="session", cascade="all, delete-orphan")

class PostRevision(Base):
    __tablename__ = "post_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_sessions.id", ondelete="CASCADE"), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    character_count: Mapped[int] = mapped_column(Integer, default=0)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_by_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    session: Mapped["ContentSession"] = relationship("ContentSession", back_populates="revisions")

class PostReview(Base):
    __tablename__ = "post_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_sessions.id", ondelete="CASCADE"), nullable=False)
    revision_id: Mapped[str] = mapped_column(String(36), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    score_hook_impact: Mapped[int] = mapped_column(Integer, default=80)
    score_storytelling: Mapped[int] = mapped_column(Integer, default=80)
    score_professional_depth: Mapped[int] = mapped_column(Integer, default=80)
    score_clarity: Mapped[int] = mapped_column(Integer, default=80)
    score_engagement_potential: Mapped[int] = mapped_column(Integer, default=80)
    score_originality: Mapped[int] = mapped_column(Integer, default=80)
    score_structure: Mapped[int] = mapped_column(Integer, default=80)
    score_actionability: Mapped[int] = mapped_column(Integer, default=80)
    score_emotional_resonance: Mapped[int] = mapped_column(Integer, default=80)
    score_authenticity: Mapped[int] = mapped_column(Integer, default=80)
    
    identified_flaws: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_instructions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    session: Mapped["ContentSession"] = relationship("ContentSession", back_populates="reviews")

class PublishingHistory(Base):
    __tablename__ = "publishing_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_sessions.id", ondelete="CASCADE"), nullable=False)
    linkedin_post_id: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    post_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PUBLISHED") # "PUBLISHED", "PUBLISH_FAILED", "REJECTED"
    provider: Mapped[str] = mapped_column(String(50), default="mock") # "mock" or "official"
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship("User", back_populates="publishing_history")
    session: Mapped["ContentSession"] = relationship("ContentSession", back_populates="publishing_records")

class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_sessions.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, default=1)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), default="gemini-2.5-flash")
    tokens_prompt: Mapped[int] = mapped_column(Integer, default=0)
    tokens_completion: Mapped[int] = mapped_column(Integer, default=0)
    tokens_total: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    session: Mapped["ContentSession"] = relationship("ContentSession", back_populates="execution_logs")
