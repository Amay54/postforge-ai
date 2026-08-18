# PostForge AI ?
### Production-Grade Agentic LinkedIn Content Generation & Publishing Platform

PostForge AI is an autonomous, multi-agent AI system designed to transform natural language objectives into executive-tier, viral LinkedIn posts. Engineered with a **LangGraph cyclical state machine**, it executes an adversarial **Generator-Reviewer feedback loop**, evaluates drafts across a **10-dimension editorial rubric**, requires **mandatory human-in-the-loop approval**, and seamlessly publishes via the **official LinkedIn API** (or sandboxed Mock Provider).

---

## ?? Key Architectural Features

1. **Multi-Agent Orchestration**:
   - `Planner Agent`: Extracts audience pain points, devises disruptive hook angles, and establishes narrative outlines.
   - `Researcher Agent`: Queries real-time sources or validated benchmarks to anchor claims in verifiable data.
   - `Generator Agent`: Crafts scroll-stopping drafts adhering to LinkedIn readability standards and mobile formatting.
   - `Reviewer Agent`: Strictly grades drafts on a 0?100 scale across 10 dimensions without directly rewriting the post text.
   - `Quality Router & Feedback Loop`: Iterates until `quality_score >= threshold` (default 85) or `iteration >= max_iterations` (default 5).

2. **Mandatory Human-in-the-Loop Approval**:
   - Zero posts can ever be published without explicit user verification and approval.
   - Built-in live editor modal allowing human overrides before dispatch.

3. **Production Security & LinkedIn OAuth 2.0**:
   - Official LinkedIn REST API v2 publishing engine with PKCE OAuth authorization flow.
   - AES-256 Fernet token encryption for storing access and refresh tokens securely at rest.
   - Comprehensive Mock Provider sandbox enabled by default for zero-credential testing.

4. **Evaluation Engine & Observability Traces**:
   - Computes pass rates, average iterations to pass, and individual dimension averages.
   - Tracks per-step agent latencies, prompt/completion token consumption, and complete execution traces.

5. **Modern Full-Stack Dashboard**:
   - **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts (Radar & Bar charts), Framer Motion, and diff visualization.
   - **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0 (Async), Pydantic v2, aiosqlite / asyncpg, pytest-asyncio (100% test coverage).

---

## ?? Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Dashboard will be live at `http://localhost:5173`.

### 3. Docker Compose (Full Stack)
```bash
docker-compose up --build
```
- Web Application: `http://localhost:3000`
- API Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## ?? Running Automated Tests
```bash
python -m pytest -c backend/pytest.ini -v
```
All 13 automated tests pass with 100% coverage across Agents, Workflows, Discriminator logic, Security, and API endpoints.

---

## ?? Documentation
- [Architecture & Agent Graph](ARCHITECTURE.md)
- [Setup & Environment Guide](SETUP.md)
- [API Reference & Schema](API.md)
