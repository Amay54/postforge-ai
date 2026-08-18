# PostForge AI API Documentation

Base URL: `http://localhost:8000/api`

### 1. Posts & Workflow
- `POST /api/posts/generate`: Launch multi-agent generation pipeline.
- `GET /api/posts`: List historical content generation sessions.
- `GET /api/posts/{session_id}`: Retrieve detailed session state with revisions, reviews, and scores.
- `POST /api/posts/{session_id}/approve`: Submit explicit human approval or rejection.
- `PUT /api/posts/{session_id}/edit`: Submit manual human content edits.

### 2. LinkedIn Integration
- `GET /api/linkedin/auth-url`: Retrieve OAuth 2.0 authorization URL.
- `GET /api/linkedin/callback`: Exchange authorization code for encrypted tokens.
- `GET /api/linkedin/status`: Check connection and profile status.
- `POST /api/linkedin/publish`: Publish approved post to LinkedIn feed (requires `human_approved=true` & `confirmation=true`).

### 3. Analytics & Observability
- `GET /api/dashboard/stats`: KPI metrics for generated, approved, and published posts.
- `GET /api/dashboard/evaluation`: 10-dimension rubric averages, pass rates, and convergence distribution.
- `GET /api/observability/traces/{session_id}`: Per-step agent execution traces, token usage, and latencies.
