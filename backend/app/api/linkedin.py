import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.entities import User, LinkedInConnection, ContentSession, PublishingHistory
from app.schemas.linkedin_schemas import (
    LinkedInAuthUrlResponse,
    LinkedInStatusResponse,
    LinkedInProfileData,
    LinkedInPublishRequest,
    LinkedInPublishResponse
)
from app.services.linkedin import get_linkedin_provider, MockLinkedInProvider, LinkedInOfficialProvider
from app.services.security import encrypt_token, decrypt_token
from app.api.auth import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/linkedin", tags=["LinkedIn Integration"])

@router.get("/auth-url", response_model=LinkedInAuthUrlResponse)
async def get_auth_url(current_user: User = Depends(get_current_user)):
    provider = get_linkedin_provider()
    is_mock = isinstance(provider, MockLinkedInProvider)
    state = f"user_{current_user.id}"
    
    try:
        url = provider.get_authorization_url(state=state)
        return LinkedInAuthUrlResponse(
            authorization_url=url,
            state=state,
            provider=settings.LINKEDIN_PROVIDER,
            is_mock=is_mock
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    provider = get_linkedin_provider()
    
    try:
        token_data = await provider.exchange_code(
            code=code,
            redirect_uri=settings.LINKEDIN_REDIRECT_URI
        )
    except Exception as e:
        logger.error(f"OAuth code exchange failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LinkedIn OAuth authorization failed: {str(e)}"
        )
    
    enc_access = encrypt_token(token_data["access_token"])
    enc_refresh = encrypt_token(token_data["refresh_token"]) if token_data.get("refresh_token") else None
    expires_in = int(token_data.get("expires_in", 5184000))
    token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    
    # Query existing connection and replace with fresh token
    stmt = select(LinkedInConnection).where(
        LinkedInConnection.user_id == current_user.id,
        LinkedInConnection.provider == settings.LINKEDIN_PROVIDER
    )
    res = await db.execute(stmt)
    conn = res.scalar_one_or_none()
    
    if not conn:
        conn = LinkedInConnection(
            user_id=current_user.id,
            linkedin_member_id=token_data.get("member_id"),
            linkedin_member_urn=token_data.get("member_urn"),
            profile_name=token_data.get("name"),
            profile_url=f"https://www.linkedin.com/in/{token_data.get('member_id')}" if token_data.get("member_id") else None,
            encrypted_access_token=enc_access,
            encrypted_refresh_token=enc_refresh,
            token_expires_at=token_expires_at,
            scopes=token_data.get("scopes", "openid profile email w_member_social"),
            provider=settings.LINKEDIN_PROVIDER,
            is_active=True,
            connected_at=datetime.now(timezone.utc)
        )
        db.add(conn)
    else:
        conn.linkedin_member_id = token_data.get("member_id")
        conn.linkedin_member_urn = token_data.get("member_urn")
        conn.profile_name = token_data.get("name")
        conn.encrypted_access_token = enc_access
        conn.encrypted_refresh_token = enc_refresh
        conn.token_expires_at = token_expires_at
        conn.scopes = token_data.get("scopes", "openid profile email w_member_social")
        conn.provider = settings.LINKEDIN_PROVIDER
        conn.is_active = True
        conn.connected_at = datetime.now(timezone.utc)
        
    await db.commit()
    return {
        "status": "success",
        "provider": settings.LINKEDIN_PROVIDER,
        "message": "LinkedIn connected successfully with fresh OAuth token.",
        "member_name": token_data.get("name"),
        "member_urn": token_data.get("member_urn")
    }


@router.get("/status", response_model=LinkedInStatusResponse)
async def get_connection_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    provider_mode = settings.LINKEDIN_PROVIDER.lower()
    
    # 1. Mock / Simulation Mode
    if provider_mode == "mock":
        return LinkedInStatusResponse(
            provider="mock",
            mode="simulation",
            connected=False,
            publishing_available=True,
            profile=LinkedInProfileData(
                name="Amay Yadav (Simulation)",
                member_id="simulation_member",
                member_urn="urn:li:person:simulation_member",
                profile_url="https://www.linkedin.com/in/amay-yadav-976716387"
            )
        )
        
    # 2. Official Mode
    stmt = select(LinkedInConnection).where(
        LinkedInConnection.user_id == current_user.id,
        LinkedInConnection.provider == "official",
        LinkedInConnection.is_active == True
    )
    res = await db.execute(stmt)
    conn = res.scalar_one_or_none()
    
    if not conn or not conn.encrypted_access_token:
        return LinkedInStatusResponse(
            provider="official",
            mode="live",
            connected=False,
            publishing_available=False,
            error="LinkedIn account is not connected. Connect via OAuth in Settings to publish to real LinkedIn."
        )
        
    # Token expiration check
    if conn.token_expires_at:
        exp = conn.token_expires_at if conn.token_expires_at.tzinfo else conn.token_expires_at.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            conn.is_active = False
            await db.commit()
            return LinkedInStatusResponse(
                provider="official",
                mode="live",
                connected=False,
                publishing_available=False,
                error="LinkedIn authorization has expired or is invalid. Please reconnect LinkedIn."
            )
            
    # Scope check
    if "w_member_social" not in (conn.scopes or ""):
        return LinkedInStatusResponse(
            provider="official",
            mode="live",
            connected=True,
            publishing_available=False,
            profile=LinkedInProfileData(
                name=conn.profile_name or "Authenticated Member",
                member_id=conn.linkedin_member_id,
                member_urn=conn.linkedin_member_urn,
                profile_url=conn.profile_url
            ),
            expires_at=conn.token_expires_at,
            error="LinkedIn application is missing required 'w_member_social' posting permission. Please reconnect and grant permission."
        )
        
    return LinkedInStatusResponse(
        provider="official",
        mode="live",
        connected=True,
        publishing_available=True,
        profile=LinkedInProfileData(
            name=conn.profile_name or "Authenticated Member",
            member_id=conn.linkedin_member_id,
            member_urn=conn.linkedin_member_urn,
            profile_url=conn.profile_url
        ),
        expires_at=conn.token_expires_at
    )


@router.post("/disconnect")
async def disconnect_linkedin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LinkedInConnection).where(LinkedInConnection.user_id == current_user.id)
    res = await db.execute(stmt)
    connections = res.scalars().all()
    for conn in connections:
        conn.is_active = False
    await db.commit()
    return {"status": "success", "message": "LinkedIn connection disconnected successfully. Publishing and session history preserved."}


@router.post("/publish", response_model=LinkedInPublishResponse)
async def publish_to_linkedin(
    req: LinkedInPublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Guardrail 1: Confirmation flag check
    if not req.confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit user confirmation is required to publish."
        )
        
    # Guardrail 2: Verify server-side human approval on session in database
    stmt_sess = select(ContentSession).where(
        ContentSession.id == req.session_id,
        ContentSession.user_id == current_user.id
    )
    res_sess = await db.execute(stmt_sess)
    session = res_sess.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content session not found.")
        
    if not session.human_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session has not been approved by a human. Server-side explicit approval is mandatory before publishing."
        )
        
    provider = get_linkedin_provider()
    post_text = req.custom_content or session.final_post_content
    
    # Validation: Ensure content is strictly plain text
    if not isinstance(post_text, str) or not post_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content must be plain text."
        )
        
    if post_text.startswith("data:image/") or ";base64," in post_text[:100]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content must be plain text. Image and media attachments are not supported in text-only publishing mode."
        )
        
    # Guardrail 3: Official mode checks
    if settings.LINKEDIN_PROVIDER.lower() == "official":
        stmt_conn = select(LinkedInConnection).where(
            LinkedInConnection.user_id == current_user.id,
            LinkedInConnection.provider == "official",
            LinkedInConnection.is_active == True
        )
        res_conn = await db.execute(stmt_conn)
        conn = res_conn.scalar_one_or_none()
        
        if not conn or not conn.encrypted_access_token:
            session.status = "OAUTH_REQUIRED"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LinkedIn account is not connected via OAuth. Please connect your account in Settings first."
            )
            
        # Check token expiration
        if conn.token_expires_at:
            exp = conn.token_expires_at if conn.token_expires_at.tzinfo else conn.token_expires_at.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                conn.is_active = False
                session.status = "OAUTH_REQUIRED"
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="LinkedIn authorization has expired or is invalid. Please reconnect LinkedIn."
                )
                
        # Check permission scope
        if "w_member_social" not in (conn.scopes or ""):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your LinkedIn connection lacks the required 'w_member_social' permission. Please reconnect LinkedIn and grant posting permissions."
            )
            
        member_urn = conn.linkedin_member_urn or f"urn:li:person:{conn.linkedin_member_id}"
        redacted_urn = f"{member_urn[:18]}...{member_urn[-4:]}" if len(member_urn) > 22 else "urn:li:person:***"
        
        # Token age calculation
        token_age = "recent"
        if conn.connected_at:
            c_at = conn.connected_at if conn.connected_at.tzinfo else conn.connected_at.replace(tzinfo=timezone.utc)
            diff = datetime.now(timezone.utc) - c_at
            mins = int(diff.total_seconds() // 60)
            token_age = f"{mins // 60}h {mins % 60}m"
            
        # Safe Diagnostics Logging (ZERO secrets)
        logger.info(
            f"[LinkedIn Token Diagnostics]\n"
            f"Provider: official\n"
            f"OAuth connected: {conn.is_active}\n"
            f"Token present: {bool(conn.encrypted_access_token)}\n"
            f"Token expired: False\n"
            f"Token age: {token_age}\n"
            f"Scopes: {conn.scopes}\n"
            f"Authenticated member: {redacted_urn}"
        )
        
        access_token = decrypt_token(conn.encrypted_access_token)
        
        session.status = "PUBLISHING"
        await db.commit()
        
        try:
            result = await provider.publish_post(
                access_token=access_token,
                linkedin_member_urn=member_urn,
                post_text=post_text
            )
            session.status = "PUBLISHED"
            
            pub_record = PublishingHistory(
                session_id=session.id,
                user_id=current_user.id,
                linkedin_post_id=result.linkedin_post_id,
                post_content=post_text,
                status="PUBLISHED",
                provider="official",
                is_mock=False,
                published_at=datetime.now(timezone.utc)
            )
            db.add(pub_record)
            await db.commit()
            return result
        except Exception as e:
            err_msg = str(e)
            # If token is rejected or invalid, mark connection inactive to require reconnect
            if "401" in err_msg or "INVALID_ACCESS_TOKEN" in err_msg or "expired" in err_msg.lower():
                conn.is_active = False
                session.status = "OAUTH_REQUIRED"
                err_msg = "LinkedIn authorization has expired or is invalid. Please reconnect LinkedIn."
            else:
                session.status = "PUBLISH_FAILED"
                
            pub_record = PublishingHistory(
                session_id=session.id,
                user_id=current_user.id,
                post_content=post_text,
                status="PUBLISH_FAILED",
                provider="official",
                is_mock=False,
                error_message=err_msg,
                published_at=datetime.now(timezone.utc)
            )
            db.add(pub_record)
            await db.commit()
            logger.error(f"Live LinkedIn publishing error: {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )
            
    # Mock / Simulation Provider Flow
    session.status = "PUBLISHING"
    await db.commit()
    
    result = await provider.publish_post(
        access_token="mock_token",
        linkedin_member_urn="urn:li:person:simulation_member",
        post_text=post_text
    )
    session.status = "PUBLISHED"
    
    pub_record = PublishingHistory(
        session_id=session.id,
        user_id=current_user.id,
        linkedin_post_id=result.linkedin_post_id,
        post_content=post_text,
        status="PUBLISHED",
        provider="mock",
        is_mock=True,
        published_at=datetime.now(timezone.utc)
    )
    db.add(pub_record)
    await db.commit()
    return result
