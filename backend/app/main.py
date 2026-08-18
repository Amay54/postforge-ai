from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db
from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.linkedin import router as linkedin_router
from app.api.dashboard import router as dashboard_router
from app.api.observability import router as observability_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="PostForge AI API",
    description="Production-grade Agentic LinkedIn Content Generation & Publishing Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Registrations
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(linkedin_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(observability_router, prefix="/api")

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "app": "PostForge AI",
        "mock_llm": settings.MOCK_LLM,
        "linkedin_provider": settings.LINKEDIN_PROVIDER,
        "mock_linkedin": settings.MOCK_LINKEDIN
    }
