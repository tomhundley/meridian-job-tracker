# Meridian Job Tracker

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A human-in-the-loop job application tracking system with LinkedIn browser automation, AI-powered cover letter generation, and a modern web dashboard.

> **Part of the Meridian Suite**
> - [trh-meridian](https://github.com/ElegantSoftwareSolutions/trh-meridian) - Resume & Portfolio Site
> - [meridian-linkedIn](https://github.com/tomhundley/meridian-linkedIn) - LinkedIn MCP Server
> - **meridian-job-tracker** - Job Application Tracker (this repo)

## Features

- **Job Pipeline Tracking** - Track opportunities from discovery to offer
- **AI Cover Letters** - Generate role-specific cover letters with Claude
- **LinkedIn Automation** - Streamline Easy Apply with human-in-the-loop confirmation
- **Email Integration** - Link correspondence to job applications
- **Agent APIs & Webhooks** - Scoped API keys, bulk ingestion, and notifications
- **Modern Dashboard** - Next.js 15 with real-time updates

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Dashboard     │     │   Claude CLI    │     │  Email Agent    │
│   (Next.js)     │     │  (Automation)   │     │   (External)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    FastAPI Backend     │
                    │  • Jobs API            │
                    │  • Cover Letter Gen    │
                    │  • LinkedIn Automation │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  PostgreSQL Database   │
                    └────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Anthropic API key (for cover letters)

### 1. Clone & Setup

```bash
git clone https://github.com/tomhundley/meridian-job-tracker.git
cd meridian-job-tracker
```

### 2. Start Database

```bash
cd database
docker-compose up -d
```

### 3. Start Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python -m src.main
```

API available at http://localhost:8005/docs

### 4. Start Frontend

```bash
cd frontend

npm install
cp .env.example .env.local
npm run dev
```

Dashboard available at http://localhost:3005

## Project Structure

```
meridian-job-tracker/
├── backend/                    # Python FastAPI
│   ├── src/
│   │   ├── api/routes/        # REST endpoints
│   │   ├── automation/        # Playwright LinkedIn
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── schemas/           # Pydantic models
│   │   └── services/          # Business logic
│   ├── scripts/               # Utilities
│   └── tests/                 # Test suite
├── database/                   # Docker PostgreSQL
│   ├── docker-compose.yml
│   └── init.sql
├── frontend/                   # Next.js 15
│   └── src/
│       ├── app/               # App Router pages
│       └── components/        # React components
├── docs/                       # Documentation
│   └── progress_tracker.md
└── pm/                         # Project management
    ├── requirements.md
    └── architecture.md
```

## API Reference

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/jobs` | List jobs with filters |
| POST | `/api/v1/jobs` | Create job |
| POST | `/api/v1/jobs/ingest` | Ingest job from URL |
| POST | `/api/v1/jobs/bulk` | Bulk ingest jobs |
| PATCH | `/api/v1/jobs/bulk/status` | Bulk status update |
| GET | `/api/v1/jobs/{id}` | Get job details |
| PATCH | `/api/v1/jobs/{id}` | Update job |
| PATCH | `/api/v1/jobs/{id}/status` | Update status |
| DELETE | `/api/v1/jobs/{id}` | Soft delete job |
| POST | `/api/v1/jobs/{id}/cover-letter` | Generate cover letter |
| GET | `/api/v1/jobs/{id}/cover-letters` | List job cover letters |

### Cover Letters

| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/api/v1/cover-letters/{id}/approve` | Approve for use |
| DELETE | `/api/v1/cover-letters/{id}` | Delete |

### Emails

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/emails` | List emails |
| POST | `/api/v1/emails` | Create record |
| PATCH | `/api/v1/emails/{id}/link/{job_id}` | Link to job |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/webhooks` | List webhooks |
| POST | `/api/v1/webhooks` | Register webhook |

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents` | Create agent API key |

## Documentation

- `docs/api-reference.md` - Full API reference
- `docs/agent-integration.md` - AI agent workflows
- `docs/mcp-integration.md` - LinkedIn MCP integration
- `docs/email-agent-workflow.md` - Email agent flow

## Job Statuses

| Status | Description |
|--------|-------------|
| `saved` | Initial save from job board |
| `researching` | Gathering company info |
| `ready_to_apply` | Materials prepared |
| `applying` | Application in progress |
| `applied` | Successfully submitted |
| `interviewing` | In interview process |
| `offer` | Received offer |
| `rejected` | Application rejected |
| `withdrawn` | Candidate withdrew |
| `archived` | No longer tracking |

## Role Types

Resume data adapts to target role:

| Role | Title |
|------|-------|
| `cto` | Chief Technology Officer |
| `vp` | VP of Software Development |
| `director` | Director of Software Engineering |
| `architect` | Principal Solutions Architect |
| `developer` | Senior Software Engineer |

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `API_KEY` | API authentication key |
| `ANTHROPIC_API_KEY` | Claude API key |
| `RESUME_DATA_PATH` | Path to Meridian resume data |

### Frontend (`.env.local`)

| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Backend API URL |

## Development

```bash
# Backend
cd backend
pytest                    # Run tests
ruff check .             # Lint
mypy src                 # Type check

# Frontend
cd frontend
npm run dev              # Development server
npm run build            # Production build
npm run lint             # Lint
npm run test             # Component tests
```

## Deployment

### Frontend → Vercel

1. Connect GitHub repo to Vercel
2. Set root directory to `frontend`
3. Configure `BACKEND_URL` environment variable

### Backend → Railway/Render

1. Deploy with Python 3.11+ runtime
2. Provision PostgreSQL database
3. Set environment variables
4. Run `python -m src.main`

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- **[trh-meridian](https://github.com/ElegantSoftwareSolutions/trh-meridian)** - Personal resume and portfolio site with role-specific content
- **[meridian-linkedIn](https://github.com/tomhundley/meridian-linkedIn)** - LinkedIn MCP server for Claude Code integration
