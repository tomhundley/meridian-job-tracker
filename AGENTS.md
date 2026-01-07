# Agent Notes

This file is for AI agents working in this repo. Keep it concise and update when workflows change.

> **Comprehensive Documentation**: See [ELEGANT_JOB_TRACKER_PROJECT.md](ELEGANT_JOB_TRACKER_PROJECT.md) for full project details, architecture, and implementation patterns.

## Part of the Meridian Ecosystem

This project integrates with other Meridian ecosystem components. Central documentation for all projects is available at [trh-meridian/docs/projects](https://github.com/ElegantSoftwareSolutions/trh-meridian/tree/main/docs/projects).

---

## CRITICAL: Job Data Quality Rules

**Every job MUST have complete data before analysis can work properly.**

### The Problem
The job scraper uses `httpx` + `BeautifulSoup` which **cannot execute JavaScript**. LinkedIn and many job boards render descriptions via JavaScript, resulting in only ~150 characters from meta tags instead of 2000+ characters of actual content.

### Required Workflow for LinkedIn Jobs

1. **NEVER rely solely on the `/ingest` API for LinkedIn jobs** - it will get truncated descriptions
2. **ALWAYS use browser automation** (Chrome DevTools MCP or Playwright) to extract full job data
3. **Verify description length** - must be 500+ characters for analysis to work, ideally 2000+
4. **Run analysis AFTER confirming full description** - analysis fails silently with incomplete data

### Browser Automation Workflow

```bash
# 1. Navigate to job page
mcp__chrome-devtools__navigate_page or mcp__playwright__browser_navigate

# 2. Take snapshot to extract "About the job" section
mcp__chrome-devtools__take_snapshot or mcp__playwright__browser_snapshot

# 3. Write extracted data to JSON file (avoids shell escaping issues)
Write to /tmp/{company}-update.json

# 4. PATCH the job with full data
cat /tmp/file.json | curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{id}" \
  -H "Content-Type: application/json" -d @-

# 5. Run analysis ONLY after full description is confirmed
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

### Data Fields to Extract

| Field | Required | Source |
|-------|----------|--------|
| `description_raw` | **YES** | "About the job" section (2000+ chars) |
| `salary_min/max` | If shown | Salary badge or description |
| `work_location_type` | YES | remote/hybrid/on_site badge |
| `employment_type` | YES | full_time/contract/etc. |
| `location` | YES | Location text |
| `source_id` | YES | LinkedIn job ID from URL |
| `source_url` | YES | Full LinkedIn URL |
| `is_easy_apply` | YES | Easy Apply badge present |

### Validation Checklist

Before marking a job as "complete":
- [ ] `description_raw` length > 500 characters (ideally 2000+)
- [ ] `source_url` is set
- [ ] `source_id` is set
- [ ] `work_location_type` is set
- [ ] Analysis has been run with `apply_suggestions=true`

### Common Patterns

**Recruiting firms** (job is via intermediary):
- Staffing Science, Albert Bow, Wellington Steele, BrainWorks, Jobgether, etc.
- Still extract full description - contains actual role details
- Note the actual hiring company if mentioned

**Company pages unavailable**:
- Search LinkedIn with company name in quotes: `"Company Name"`
- Use job ID from existing `source_url` if available

---

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
