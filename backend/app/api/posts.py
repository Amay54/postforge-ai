import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.entities import User, ContentSession, PostRevision, PostReview
from app.schemas.post_schemas import (
    GeneratePostRequest,
    SessionDetailResponse,
    SessionListItemResponse,
    HumanApprovalRequest,
    EditPostRequest,
    PostRevisionResponse,
    PostReviewResponse
)
from app.api.auth import get_current_user
from app.graph.workflow import PostGenerationWorkflow

router = APIRouter(prefix="/posts", tags=["Post Generation"])

@router.post("/generate", response_model=SessionDetailResponse)
async def generate_post(
    req: GeneratePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = ContentSession(
        user_id=current_user.id,
        topic=req.topic,
        target_audience=req.target_audience,
        tone=req.tone,
        content_objective=req.content_objective,
        quality_threshold=req.quality_threshold,
        max_iterations=req.max_iterations,
        status="generating"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    workflow = PostGenerationWorkflow(db=db)
    final_state = await workflow.run({
        "session_id": session.id,
        "user_id": current_user.id,
        "topic": req.topic,
        "target_audience": req.target_audience,
        "tone": req.tone,
        "content_objective": req.content_objective,
        "quality_threshold": req.quality_threshold,
        "max_iterations": req.max_iterations
    })
    
    return await get_session_detail(session.id, current_user, db)

@router.get("", response_model=List[SessionListItemResponse])
async def list_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentSession).where(ContentSession.user_id == current_user.id).order_by(ContentSession.created_at.desc())
    res = await db.execute(stmt)
    sessions = res.scalars().all()
    
    return [
        SessionListItemResponse(
            id=s.id,
            topic=s.topic,
            target_audience=s.target_audience,
            tone=s.tone,
            status=s.status,
            final_quality_score=s.final_quality_score,
            iteration_count=s.iteration_count,
            human_approved=s.human_approved,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in sessions
    ]

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentSession).where(ContentSession.id == session_id, ContentSession.user_id == current_user.id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Post session not found")
        
    stmt_revs = select(PostRevision).where(PostRevision.session_id == session_id).order_by(PostRevision.iteration_number.asc())
    res_revs = await db.execute(stmt_revs)
    revisions = res_revs.scalars().all()
    
    stmt_reviews = select(PostReview).where(PostReview.session_id == session_id).order_by(PostReview.iteration_number.asc())
    res_reviews = await db.execute(stmt_reviews)
    reviews = res_reviews.scalars().all()
    
    return SessionDetailResponse(
        id=session.id,
        user_id=session.user_id,
        topic=session.topic,
        target_audience=session.target_audience,
        tone=session.tone,
        content_objective=session.content_objective,
        quality_threshold=session.quality_threshold,
        max_iterations=session.max_iterations,
        final_post_content=session.final_post_content,
        final_quality_score=session.final_quality_score,
        iteration_count=session.iteration_count,
        status=session.status,
        human_approved=session.human_approved,
        approved_at=session.approved_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
        revisions=[
            PostRevisionResponse(
                id=r.id,
                iteration_number=r.iteration_number,
                content=r.content,
                hook=r.hook,
                hashtags=r.hashtags,
                character_count=r.character_count,
                word_count=r.word_count,
                generated_by_model=r.generated_by_model,
                created_at=r.created_at
            )
            for r in revisions
        ],
        reviews=[
            PostReviewResponse(
                id=rv.id,
                revision_id=rv.revision_id,
                iteration_number=rv.iteration_number,
                overall_score=rv.overall_score,
                approved=rv.approved,
                score_hook_impact=rv.score_hook_impact,
                score_storytelling=rv.score_storytelling,
                score_professional_depth=rv.score_professional_depth,
                score_clarity=rv.score_clarity,
                score_engagement_potential=rv.score_engagement_potential,
                score_originality=rv.score_originality,
                score_structure=rv.score_structure,
                score_actionability=rv.score_actionability,
                score_emotional_resonance=rv.score_emotional_resonance,
                score_authenticity=rv.score_authenticity,
                identified_flaws=rv.identified_flaws,
                feedback=rv.feedback,
                improvement_instructions=rv.improvement_instructions,
                created_at=rv.created_at
            )
            for rv in reviews
        ]
    )

@router.post("/{session_id}/approve", response_model=SessionDetailResponse)
async def approve_post(
    session_id: str,
    req: HumanApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentSession).where(ContentSession.id == session_id, ContentSession.user_id == current_user.id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Post session not found")
        
    session.human_approved = req.approved
    session.status = "approved" if req.approved else "rejected"
    if req.feedback_comment:
        session.rejection_reason = req.feedback_comment
    await db.commit()
    await db.refresh(session)
    return await get_session_detail(session.id, current_user, db)

@router.put("/{session_id}/edit", response_model=SessionDetailResponse)
async def edit_post(
    session_id: str,
    req: EditPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentSession).where(ContentSession.id == session_id, ContentSession.user_id == current_user.id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Post session not found")
        
    session.final_post_content = req.content
    session.status = "edited"
    await db.commit()
    await db.refresh(session)
    return await get_session_detail(session.id, current_user, db)
