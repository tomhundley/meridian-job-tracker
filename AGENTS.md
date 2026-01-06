# Agent Notes

This file is for AI agents working in this repo. Keep it concise and update when workflows change.

## Project Overview
- Backend: FastAPI + async SQLAlchemy (`backend/src`)
- Frontend: Next.js 15 (`frontend/`)
- Database: PostgreSQL via Docker (`database/`)
- Auth: `X-API-Key` header (admin key in `settings.api_key`; agent keys via `/api/v1/agents`)

## Key Commands
Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m src.main
pytest
```

Frontend:
```bash
cd frontend
npm install
npm run dev
npm run test
```

Database:
```bash
cd database
docker-compose up -d
```

## Environment
Backend `.env`:
- `DATABASE_URL` (asyncpg connection string)
- `API_KEY` (admin key)
- `ANTHROPIC_API_KEY` (cover letters)
- `RESUME_DATA_PATH` (Meridian resume data)

Frontend `.env.local`:
- `BACKEND_URL`

## Tests
- Backend tests skip unless `TEST_DATABASE_URL` is set.
- Frontend uses Vitest (`frontend/vitest.config.ts`).

## Important Files
- API routes: `backend/src/api/routes/*`
- Auth/permissions: `backend/src/api/deps.py`
- Job scraper: `backend/src/services/job_scraper.py`
- Models: `backend/src/models/*`
- Migrations: `backend/alembic/*` (keep in sync with `database/init.sql`)
- Docs: `docs/api-reference.md`, `docs/agent-integration.md`

## API Permissions (Suggested)
- jobs:read, jobs:write, jobs:ingest, jobs:update_status, jobs:delete
- cover_letters:read, cover_letters:write, cover_letters:approve, cover_letters:delete
- emails:read, emails:write, emails:delete
- webhooks:read, webhooks:write
- agents:write
