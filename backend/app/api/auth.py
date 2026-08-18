from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database.session import get_db
from app.models.entities import User
from app.services.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class UserRegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

async def get_current_user(
    document_token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if document_token:
        payload = decode_access_token(document_token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            stmt = select(User).where(User.id == user_id)
            res = await db.execute(stmt)
            user = res.scalar_one_or_none()
            if user:
                return user
    
    # Fallback to default active user in development / demo mode
    demo_email = "amay.yadav@example.com"
    stmt = select(User).where(User.email == demo_email)
    res = await db.execute(stmt)
    demo_user = res.scalar_one_or_none()
    if not demo_user:
        demo_user = User(
            email=demo_email,
            name="Amay Yadav",
            hashed_password=get_password_hash("demo123")
        )
        db.add(demo_user)
        await db.commit()
        await db.refresh(demo_user)
    return demo_user


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=req.email,
        name=req.name,
        hashed_password=get_password_hash(req.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, name=user.name, is_active=user.is_active)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.email == form_data.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, name=user.name, is_active=user.is_active)
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name, is_active=current_user.is_active)
