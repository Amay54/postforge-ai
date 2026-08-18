import pytest
from unittest.mock import patch, AsyncMock
from app.models.entities import ContentSession, LinkedInConnection
from app.services.security import encrypt_token
from app.config import settings

@pytest.mark.asyncio
async def test_health_check(async_client):
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["app"] == "PostForge AI"

@pytest.mark.asyncio
async def test_generate_post_endpoint_authenticated(async_client, auth_headers):
    payload = {
        "topic": "Why Vector Databases and RAG beat monolithic context",
        "target_audience": "Data Leaders",
        "tone": "thought-provoking",
        "content_objective": "Industry Insights",
        "quality_threshold": 85,
        "max_iterations": 3
    }
    resp = await async_client.post("/api/posts/generate", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["topic"] == payload["topic"]
    assert len(data["revisions"]) >= 1
    assert len(data["reviews"]) >= 1

@pytest.mark.asyncio
async def test_generate_post_endpoint_unauthenticated_fallback(async_client):
    payload = {
        "topic": "Write a LinkedIn post explaining why RAG is becoming important for enterprise AI.",
        "target_audience": "Tech Leaders & Engineers",
        "tone": "thought-provoking",
        "content_objective": "Thought Leadership",
        "quality_threshold": 85,
        "max_iterations": 5
    }
    resp = await async_client.post("/api/posts/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["topic"] == payload["topic"]

@pytest.mark.asyncio
async def test_publish_guardrail_unapproved(async_client, auth_headers, db_session, test_user):
    session = ContentSession(
        user_id=test_user.id,
        topic="Unapproved Post",
        status="awaiting_approval",
        human_approved=False,
        final_post_content="Content that lacks human approval."
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    pub_payload = {
        "session_id": session.id,
        "confirmation": True
    }
    resp = await async_client.post("/api/linkedin/publish", json=pub_payload, headers=auth_headers)
    # MUST reject publishing if human_approved is False
    assert resp.status_code == 400
    assert "approval" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_publish_mock_mode_success(async_client, auth_headers, db_session, test_user):
    session = ContentSession(
        user_id=test_user.id,
        topic="Approved Post",
        status="approved",
        human_approved=True,
        final_post_content="Content with explicit human approval ready for LinkedIn."
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    pub_payload = {
        "session_id": session.id,
        "confirmation": True
    }
    resp = await async_client.post("/api/linkedin/publish", json=pub_payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["status"] == "PUBLISHED"
    assert data["is_mock"] is True
    assert data["provider"] == "mock"

@pytest.mark.asyncio
async def test_linkedin_status_mock(async_client, auth_headers):
    resp = await async_client.get("/api/linkedin/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "mock"
    assert data["mode"] == "simulation"

@pytest.mark.asyncio
async def test_publish_official_mode_requires_oauth(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        session = ContentSession(
            user_id=test_user.id,
            topic="Approved Post Live Test",
            status="approved",
            human_approved=True,
            final_post_content="Post for live testing."
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Attempt publish without official LinkedInConnection in DB
        pub_payload = {
            "session_id": session.id,
            "confirmation": True
        }
        resp = await async_client.post("/api/linkedin/publish", json=pub_payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "not connected" in resp.json()["detail"].lower()
