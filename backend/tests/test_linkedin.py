import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
import httpx
from app.services.linkedin import MockLinkedInProvider, LinkedInOfficialProvider, get_current_linkedin_version, LinkedInPublishResponse
from app.models.entities import ContentSession, LinkedInConnection, PublishingHistory
from app.services.security import encrypt_token
from app.config import settings

@pytest.mark.asyncio
async def test_mock_linkedin_provider_flow():
    provider = MockLinkedInProvider()
    auth_url = provider.get_authorization_url("state_test")
    assert "mock_code" in auth_url
    assert "state_test" in auth_url
    token_data = await provider.exchange_code("mock_code_abc", "http://localhost:8000/callback")
    assert "access_token" in token_data
    assert "member_id" in token_data
    assert "Amay Yadav" in token_data["name"]
    pub_res = await provider.publish_post(
        access_token=token_data["access_token"],
        linkedin_member_urn=token_data["member_urn"],
        post_text="Testing automated mock LinkedIn publish."
    )
    assert pub_res.success is True
    assert pub_res.status == "PUBLISHED"
    assert pub_res.is_mock is True
    assert pub_res.provider == "mock"
    assert pub_res.linkedin_post_id.startswith("urn:li:share:mock_")

@pytest.mark.asyncio
async def test_official_provider_unconfigured_error():
    with patch.object(settings, "LINKEDIN_CLIENT_ID", None):
        with patch.object(settings, "LINKEDIN_CLIENT_SECRET", None):
            provider = LinkedInOfficialProvider()
            with pytest.raises(ValueError, match="LinkedIn OAuth is not configured"):
                provider.get_authorization_url("state_123")

@pytest.mark.asyncio
async def test_official_provider_oauth_exchange_and_identity():
    provider = LinkedInOfficialProvider()
    provider.client_id = "test_client_id"
    provider.client_secret = "test_client_secret"

    mock_token_resp = AsyncMock(spec=httpx.Response)
    mock_token_resp.status_code = 200
    mock_token_resp.json.return_value = {
        "access_token": "live_real_oauth_token_xyz987",
        "expires_in": 5184000,
        "scope": "openid profile email w_member_social"
    }

    mock_user_resp = AsyncMock(spec=httpx.Response)
    mock_user_resp.status_code = 200
    mock_user_resp.json.return_value = {
        "sub": "real_member_id_9988",
        "name": "Amay Yadav",
        "email": "amay.yadav@example.com",
        "picture": "https://media.licdn.com/dms/image/v2/test.jpg"
    }

    with patch("httpx.AsyncClient.post", return_value=mock_token_resp), \
         patch("httpx.AsyncClient.get", return_value=mock_user_resp):
        token_data = await provider.exchange_code("auth_code_123", "http://localhost:8000/callback")
        assert token_data["access_token"] == "live_real_oauth_token_xyz987"
        assert token_data["member_id"] == "real_member_id_9988"
        assert token_data["member_urn"] == "urn:li:person:real_member_id_9988"
        assert token_data["name"] == "Amay Yadav"

@pytest.mark.asyncio
async def test_official_provider_posts_api_success():
    provider = LinkedInOfficialProvider()
    supported_version = get_current_linkedin_version()

    mock_post_resp = AsyncMock(spec=httpx.Response)
    mock_post_resp.status_code = 201
    mock_post_resp.headers = {
        "x-restli-id": "urn:li:share:716253448899001122",
        "content-type": "application/json"
    }
    mock_post_resp.text = ""

    with patch("httpx.AsyncClient.post", return_value=mock_post_resp) as mock_req:
        result = await provider.publish_post(
            access_token="live_token_123",
            linkedin_member_urn="urn:li:person:real_member_id_9988",
            post_text="Live post content for LinkedIn."
        )
        assert result.success is True
        assert result.status == "PUBLISHED"
        assert result.is_mock is False
        assert result.provider == "official"
        assert result.linkedin_post_id == "urn:li:share:716253448899001122"

        args, kwargs = mock_req.call_args
        assert args[0] == "https://api.linkedin.com/rest/posts"
        headers = kwargs["headers"]
        assert headers["Linkedin-Version"] == supported_version
        assert headers["X-Restli-Protocol-Version"] == "2.0.0"
        assert headers["Authorization"] == "Bearer live_token_123"
        assert headers["Content-Type"] == "application/json"

@pytest.mark.asyncio
async def test_official_provider_missing_permission_error():
    provider = LinkedInOfficialProvider()
    mock_err_resp = AsyncMock(spec=httpx.Response)
    mock_err_resp.status_code = 403
    mock_err_resp.text = "Not enough permissions to access: /posts. Required scope: w_member_social"

    with patch("httpx.AsyncClient.post", return_value=mock_err_resp):
        with pytest.raises(ValueError, match="w_member_social"):
            await provider.publish_post(
                access_token="live_token_123",
                linkedin_member_urn="urn:li:person:real_member_id_9988",
                post_text="Test"
            )

@pytest.mark.asyncio
async def test_invalid_access_token_requires_reauthorization(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        conn = LinkedInConnection(
            user_id=test_user.id,
            linkedin_member_id="invalid_user_123",
            linkedin_member_urn="urn:li:person:invalid_user_123",
            profile_name="Test Member",
            encrypted_access_token=encrypt_token("AQV_invalid_expired_token"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            scopes="openid profile email w_member_social",
            provider="official",
            is_active=True
        )
        db_session.add(conn)
        
        sess = ContentSession(
            user_id=test_user.id,
            topic="Test Invalid Token",
            status="approved",
            human_approved=True,
            final_post_content="Valid plain text post for testing token error."
        )
        db_session.add(sess)
        await db_session.commit()
        await db_session.refresh(conn)
        await db_session.refresh(sess)

        with patch("app.services.linkedin.LinkedInOfficialProvider.publish_post", side_effect=ValueError("LinkedIn Authorization Error (401): INVALID_ACCESS_TOKEN")):
            resp = await async_client.post("/api/linkedin/publish", json={"session_id": sess.id, "confirmation": True}, headers=auth_headers)
            assert resp.status_code == 400
            assert "reconnect" in resp.json()["detail"].lower()
            await db_session.refresh(conn)
            assert conn.is_active is False

@pytest.mark.asyncio
async def test_expired_token_requires_reauthorization(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        conn = LinkedInConnection(
            user_id=test_user.id,
            linkedin_member_id="expired_user_456",
            linkedin_member_urn="urn:li:person:expired_user_456",
            profile_name="Expired Member",
            encrypted_access_token=encrypt_token("AQV_expired_token"),
            token_expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
            scopes="openid profile email w_member_social",
            provider="official",
            is_active=True
        )
        db_session.add(conn)
        sess = ContentSession(
            user_id=test_user.id,
            topic="Test Expired Token",
            status="approved",
            human_approved=True,
            final_post_content="Valid plain text post for testing expired token."
        )
        db_session.add(sess)
        await db_session.commit()
        await db_session.refresh(conn)
        await db_session.refresh(sess)

        resp = await async_client.post("/api/linkedin/publish", json={"session_id": sess.id, "confirmation": True}, headers=auth_headers)
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_valid_token_is_used_for_publish(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        conn = LinkedInConnection(
            user_id=test_user.id,
            linkedin_member_id="valid_user_789",
            linkedin_member_urn="urn:li:person:valid_user_789",
            profile_name="Valid Member",
            encrypted_access_token=encrypt_token("AQV_strictly_valid_access_token_112233"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(days=60),
            scopes="openid profile email w_member_social",
            provider="official",
            is_active=True
        )
        db_session.add(conn)
        sess = ContentSession(
            user_id=test_user.id,
            topic="Test Valid Publish",
            status="approved",
            human_approved=True,
            final_post_content="Valid plain text post."
        )
        db_session.add(sess)
        await db_session.commit()
        await db_session.refresh(sess)

        with patch("app.services.linkedin.LinkedInOfficialProvider.publish_post") as mock_pub:
            mock_pub.return_value = LinkedInPublishResponse(
                success=True,
                linkedin_post_id="urn:li:share:9988776655",
                status="PUBLISHED",
                provider="official",
                is_mock=False,
                message="Post published successfully.",
                published_at=datetime.now(timezone.utc)
            )
            resp = await async_client.post("/api/linkedin/publish", json={"session_id": sess.id, "confirmation": True}, headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["success"] is True
            assert resp.json()["linkedin_post_id"] == "urn:li:share:9988776655"
            args, kwargs = mock_pub.call_args
            assert kwargs["access_token"] == "AQV_strictly_valid_access_token_112233"

@pytest.mark.asyncio
async def test_oauth_callback_replaces_old_token(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        old_conn = LinkedInConnection(
            user_id=test_user.id,
            linkedin_member_id="old_member",
            encrypted_access_token=encrypt_token("AQV_old_token_111"),
            token_expires_at=datetime.now(timezone.utc) - timedelta(days=5),
            provider="official",
            is_active=False
        )
        db_session.add(old_conn)
        await db_session.commit()

        fresh_token_data = {
            "access_token": "AQV_fresh_new_token_999",
            "refresh_token": "AQV_refresh_999",
            "expires_in": 5184000,
            "member_id": "new_member_id_222",
            "member_urn": "urn:li:person:new_member_id_222",
            "name": "Amay Yadav Fresh",
            "scopes": "openid profile email w_member_social"
        }

        with patch("app.services.linkedin.LinkedInOfficialProvider.exchange_code", return_value=fresh_token_data):
            resp = await async_client.get("/api/linkedin/callback?code=fresh_auth_code", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            await db_session.refresh(old_conn)
            assert old_conn.is_active is True
            assert old_conn.linkedin_member_id == "new_member_id_222"
            exp = old_conn.token_expires_at.replace(tzinfo=timezone.utc) if old_conn.token_expires_at.tzinfo is None else old_conn.token_expires_at
            assert exp > datetime.now(timezone.utc)

@pytest.mark.asyncio
async def test_token_is_never_exposed_in_api_response(async_client, auth_headers, db_session, test_user):
    with patch.object(settings, "LINKEDIN_PROVIDER", "official"):
        raw_secret_token = "AQV_SECRET_NEVER_LEAK_TOKEN_999888"
        conn = LinkedInConnection(
            user_id=test_user.id,
            linkedin_member_id="secret_user",
            linkedin_member_urn="urn:li:person:secret_user",
            profile_name="Secret Member",
            encrypted_access_token=encrypt_token(raw_secret_token),
            token_expires_at=datetime.now(timezone.utc) + timedelta(days=60),
            provider="official",
            is_active=True
        )
        db_session.add(conn)
        await db_session.commit()

        resp_status = await async_client.get("/api/linkedin/status", headers=auth_headers)
        status_text = resp_status.text
        assert raw_secret_token not in status_text
        assert "encrypted_access_token" not in status_text
        assert "access_token" not in status_text
