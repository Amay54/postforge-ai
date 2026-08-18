from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LinkedInProfileData(BaseModel):
    name: Optional[str] = None
    member_id: Optional[str] = None
    member_urn: Optional[str] = None
    email: Optional[str] = None
    picture_url: Optional[str] = None
    profile_url: Optional[str] = None

class LinkedInAuthUrlResponse(BaseModel):
    authorization_url: str
    state: str
    provider: str
    is_mock: bool = True

class LinkedInStatusResponse(BaseModel):
    provider: str # "mock" or "official"
    mode: str # "simulation" or "live"
    connected: bool
    publishing_available: bool
    profile: Optional[LinkedInProfileData] = None
    error: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkedInProfileResponse(BaseModel):
    is_connected: bool
    linkedin_user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    picture_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_mock: bool = True
    provider: str = "mock"

class LinkedInPublishRequest(BaseModel):
    session_id: str
    confirmation: bool = True
    custom_content: Optional[str] = None

class LinkedInPublishResponse(BaseModel):
    success: bool
    linkedin_post_id: Optional[str] = None
    status: str # "PUBLISHED", "PUBLISH_FAILED", "REJECTED"
    provider: str = "mock"
    is_mock: bool = True
    message: str
    published_at: Optional[datetime] = None
    error_details: Optional[str] = None
