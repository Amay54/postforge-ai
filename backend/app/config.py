from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PostForge AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Auth & Security
    SECRET_KEY: str = "replace-with-generated-secret"
    JWT_SECRET_KEY: str = "replace-with-generated-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    TOKEN_ENCRYPTION_KEY: str = "replace-with-fernet-key"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./postforge.db"
    
    # LLM Providers
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    MOCK_LLM: bool = True
    
    # LinkedIn Official & Sandbox Config
    LINKEDIN_PROVIDER: str = "official"
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/linkedin/callback"
    LINKEDIN_API_VERSION: str = "202607"
    
    # Compatibility property
    @property
    def MOCK_LINKEDIN(self) -> bool:
        return self.LINKEDIN_PROVIDER.lower() == "mock"
    
    # Research
    MOCK_RESEARCH: bool = True
    
    # Quality Engine
    QUALITY_THRESHOLD_DEFAULT: int = 85
    MAX_ITERATIONS_DEFAULT: int = 5
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
