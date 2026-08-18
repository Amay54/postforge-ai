from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.entities import User, AgentExecutionLog
from app.schemas.stats_schemas import ObservabilityLogResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/observability", tags=["Observability & Tracing"])

@router.get("/traces/{session_id}", response_model=List[ObservabilityLogResponse])
async def get_session_traces(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AgentExecutionLog).where(AgentExecutionLog.session_id == session_id).order_by(AgentExecutionLog.step_number.asc())
    res = await db.execute(stmt)
    logs = res.scalars().all()
    
    return [
        ObservabilityLogResponse(
            id=log.id,
            session_id=log.session_id,
            agent_name=log.agent_name,
            step_number=log.step_number,
            prompt=log.prompt,
            raw_output=log.raw_output,
            model_name=log.model_name,
            tokens_prompt=log.tokens_prompt,
            tokens_completion=log.tokens_completion,
            tokens_total=log.tokens_total,
            latency_ms=log.latency_ms,
            status=log.status,
            error_message=log.error_message,
            created_at=log.created_at
        )
        for log in logs
    ]
