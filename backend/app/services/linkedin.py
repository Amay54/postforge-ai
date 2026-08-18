import logging
import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from app.schemas.linkedin_schemas import LinkedInPublishResponse
from app.services.ssl_context import get_secure_ssl_context
from app.config import settings

logger = logging.getLogger(__name__)

CURRENT_SUPPORTED_LINKEDIN_VERSION = "202607"

def get_current_linkedin_version() -> str:
    v = getattr(settings, "LINKEDIN_API_VERSION", None)
    if not v or v in ["202401", "202502"]:
        return CURRENT_SUPPORTED_LINKEDIN_VERSION
    return v

class BaseLinkedInProvider:
    def get_authorization_url(self, state: str) -> str:
        raise NotImplementedError
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        raise NotImplementedError
    async def publish_post(self, access_token: str, linkedin_member_urn: str, post_text: str) -> LinkedInPublishResponse:
        raise NotImplementedError

class MockLinkedInProvider(BaseLinkedInProvider):
    def get_authorization_url(self, state: str) -> str:
        params = {"response_type": "code", "client_id": "mock_client_id", "redirect_uri": "http://localhost:8000/api/linkedin/callback", "state": state, "scope": "openid profile email w_member_social"}
        return f"http://localhost:8000/api/linkedin/callback?mock_code=mock_auth_code_success&state={state}"
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        return {"access_token": "mock_access_token_12345", "refresh_token": "mock_refresh_token_12345", "expires_in": 5184000, "member_id": "simulation_member", "member_urn": "urn:li:person:simulation_member", "name": "Amay Yadav (Simulation)", "scopes": "openid profile email w_member_social"}
    async def publish_post(self, access_token: str, linkedin_member_urn: str, post_text: str) -> LinkedInPublishResponse:
        import uuid
        from datetime import datetime, timezone
        mock_id = f"urn:li:share:mock_{uuid.uuid4().hex[:12]}"
        return LinkedInPublishResponse(success=True, linkedin_post_id=mock_id, status="PUBLISHED", provider="mock", is_mock=True, message="Post published in Simulation Mode (No real LinkedIn post was created).", published_at=datetime.now(timezone.utc))

class LinkedInOfficialProvider(BaseLinkedInProvider):
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
    POSTS_URL = "https://api.linkedin.com/rest/posts"
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI
        self.api_version = get_current_linkedin_version()
    def get_authorization_url(self, state: str) -> str:
        if not self.client_id:
            raise ValueError("LinkedIn OAuth is not configured. Add LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to your .env file.")
        params = {"response_type": "code", "client_id": self.client_id, "redirect_uri": self.redirect_uri, "state": state, "scope": "openid profile email w_member_social"}
        return f"{self.AUTH_URL}?{urlencode(params)}"
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        if not self.client_id or not self.client_secret:
            raise ValueError("LinkedIn client credentials are missing.")
        data = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri or self.redirect_uri, "client_id": self.client_id, "client_secret": self.client_secret}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient(timeout=15.0, verify=get_secure_ssl_context()) as client:
            resp = await client.post(self.TOKEN_URL, data=data, headers=headers)
            if resp.status_code != 200:
                raise ValueError(f"Failed to exchange OAuth code with LinkedIn ({resp.status_code}): {resp.text}")
            token_resp = resp.json()
            access_token = token_resp.get("access_token")
            user_info = await self.get_user_profile(access_token)
            return {"access_token": access_token, "refresh_token": token_resp.get("refresh_token"), "expires_in": token_resp.get("expires_in", 5184000), "scopes": token_resp.get("scope", "openid profile email w_member_social"), "member_id": user_info.get("sub"), "member_urn": f"urn:li:person:{user_info.get('sub')}", "name": user_info.get("name"), "email": user_info.get("email"), "picture": user_info.get("picture")}
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=15.0, verify=get_secure_ssl_context()) as client:
            resp = await client.get(self.USERINFO_URL, headers=headers)
            if resp.status_code != 200:
                raise ValueError(f"Failed to retrieve user profile from LinkedIn ({resp.status_code}): {resp.text}")
            return resp.json()
    async def publish_post(self, access_token: str, linkedin_member_urn: str, post_text: str) -> LinkedInPublishResponse:
        from datetime import datetime, timezone
        if not access_token:
            raise ValueError("No access token provided for LinkedIn publishing.")
        if not linkedin_member_urn:
            raise ValueError("No LinkedIn Member URN found. Please reconnect your account.")
        headers = {"Linkedin-Version": self.api_version, "X-Restli-Protocol-Version": "2.0.0", "Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {"author": linkedin_member_urn, "commentary": post_text, "visibility": "PUBLIC", "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []}, "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
        redacted_urn = f"{linkedin_member_urn[:18]}...{linkedin_member_urn[-4:]}" if len(linkedin_member_urn) > 22 else "urn:li:person:***"
        logger.info(f"[Publish Diagnostics]\nProvider: official\nEndpoint: /rest/posts\nAPI Version: {self.api_version}\nAuthenticated member: {redacted_urn}\nContent type: text")
        async with httpx.AsyncClient(timeout=20.0, verify=get_secure_ssl_context()) as client:
            resp = await client.post(self.POSTS_URL, json=payload, headers=headers)
            if resp.status_code == 201:
                post_id = resp.headers.get("x-restli-id", "")
                if not post_id and resp.text:
                    try:
                        post_id = resp.json().get("id", "")
                    except Exception:
                        pass
                logger.info(f"LinkedIn post published successfully! Status: 201, Post ID: {post_id}")
                return LinkedInPublishResponse(success=True, linkedin_post_id=post_id or f"urn:li:share:{resp.status_code}", status="PUBLISHED", provider="official", is_mock=False, message="Post published to real LinkedIn feed successfully!", published_at=datetime.now(timezone.utc))
            elif resp.status_code == 403:
                raise ValueError("LinkedIn Authorization Error (403): Insufficient permissions. Ensure your LinkedIn App has 'w_member_social' permission approved.")
            elif resp.status_code == 401:
                raise ValueError(f"LinkedIn Authorization Error (401): Invalid or expired access token. Please reconnect LinkedIn.")
            else:
                raise ValueError(f"LinkedIn API Error ({resp.status_code}): {resp.text}")

def get_linkedin_provider() -> BaseLinkedInProvider:
    mode = getattr(settings, "LINKEDIN_PROVIDER", "mock").lower()
    if mode == "official":
        return LinkedInOfficialProvider()
    return MockLinkedInProvider()
