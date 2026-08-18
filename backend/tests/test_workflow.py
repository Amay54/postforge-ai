import pytest
from app.graph.workflow import PostGenerationWorkflow
from app.models.entities import ContentSession, User
from app.services.security import get_password_hash

@pytest.mark.asyncio
async def test_post_generation_workflow_end_to_end(db_session, test_user):
    session = ContentSession(
        user_id=test_user.id,
        topic="The Future of Autonomous AI Coding Agents in 2026",
        target_audience="CTOs and Senior Architects",
        tone="strategic",
        content_objective="Thought Leadership",
        quality_threshold=80,
        max_iterations=3,
        status="generating"
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    workflow = PostGenerationWorkflow(db=db_session)
    final_state = await workflow.run({
        "session_id": session.id,
        "user_id": test_user.id,
        "topic": session.topic,
        "target_audience": session.target_audience,
        "tone": session.tone,
        "content_objective": session.content_objective,
        "quality_threshold": session.quality_threshold,
        "max_iterations": session.max_iterations
    })

    assert final_state.current_post is not None
    assert len(final_state.current_post) > 50
    assert final_state.iteration >= 1
    assert final_state.quality_score >= 0
    assert final_state.status == "awaiting_approval"
