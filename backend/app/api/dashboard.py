from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.entities import User, ContentSession, PublishingHistory
from app.schemas.stats_schemas import DashboardStatsResponse, EvaluationReportResponse
from app.services.evaluation import compute_evaluation_metrics
from app.api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ContentSession).where(ContentSession.user_id == current_user.id)
    res = await db.execute(stmt)
    sessions = res.scalars().all()
    
    stmt_pub = select(PublishingHistory).where(PublishingHistory.user_id == current_user.id)
    res_pub = await db.execute(stmt_pub)
    published = res_pub.scalars().all()
    
    total_generated = len(sessions)
    total_published = len(published)
    approved_count = len([s for s in sessions if s.human_approved])
    
    scores = [s.final_quality_score for s in sessions if s.final_quality_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    
    return DashboardStatsResponse(
        total_posts_generated=total_generated,
        total_posts_published=total_published,
        total_posts_approved=approved_count,
        avg_quality_score=avg_score,
        recent_sessions_count=min(total_generated, 5)
    )

@router.get("/evaluation", response_model=EvaluationReportResponse)
async def get_evaluation_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await compute_evaluation_metrics(db=db, user_id=current_user.id)
