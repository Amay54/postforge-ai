# PostForge AI ? Setup & Installation Guide

## 1. Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

## 2. Environment Setup
Copy the template configuration:
```bash
cp .env.example .env
```

Fill in your configuration in `.env`:
```env
PROJECT_NAME="PostForge AI"
ENVIRONMENT=development
DEBUG=true

SECRET_KEY=your_generated_secret_key
JWT_SECRET_KEY=your_generated_jwt_secret
TOKEN_ENCRYPTION_KEY=your_generated_fernet_key

DATABASE_URL=sqlite+aiosqlite:///./postforge.db

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
MOCK_LLM=true
MOCK_RESEARCH=true

LINKEDIN_PROVIDER=mock # or official
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/linkedin/callback
LINKEDIN_API_VERSION=202607
```

## 3. Running the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 4. Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
