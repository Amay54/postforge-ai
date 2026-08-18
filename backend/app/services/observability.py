from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import AgentExecutionLog

class ObservabilityService:
    @staticmethod
    async def log_step(
        db: AsyncSession,
        session_id: str,
        agent_name: str,
        step_number: int,
        prompt: Optional[str] = None,
        raw_output: Optional[str] = None,
        model_name: Optional[str] = "gemini-2.5-flash",
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        latency_ms: int = 0,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AgentExecutionLog:
        log_entry = AgentExecutionLog(
            session_id=session_id,
            agent_name=agent_name,
            step_number=step_number,
            prompt=prompt,
            raw_output=raw_output,
            model_name=model_name,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            tokens_total=tokens_prompt + tokens_completion,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            created_at=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry
