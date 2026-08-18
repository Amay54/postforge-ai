# PostForge AI Environment Configuration Template
# Copy this file to .env and fill in your local credentials.

PROJECT_NAME=PostForge AI
ENVIRONMENT=development
DEBUG=true

# Security Secrets (Provide 32-byte secret and Fernet key in your local .env)
SECRET_KEY=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
TOKEN_ENCRYPTION_KEY=

# Database Connection
DATABASE_URL=sqlite+aiosqlite:///./postforge.db

# LLM Configuration (Google Gemini API)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
MOCK_LLM=true
MOCK_RESEARCH=true

# LinkedIn OAuth & Publishing Configuration
# Set LINKEDIN_PROVIDER=mock for offline simulation, or official for live publishing
LINKEDIN_PROVIDER=mock
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/linkedin/callback
LINKEDIN_API_VERSION=202607

# Editorial Quality Defaults
QUALITY_THRESHOLD_DEFAULT=85
MAX_ITERATIONS_DEFAULT=5
