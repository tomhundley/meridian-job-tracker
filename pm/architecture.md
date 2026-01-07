# Meridian Job Tracker - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  Next.js        │    │  Claude Code    │    │  External   │ │
│  │  Dashboard      │    │  CLI            │    │  Email      │ │
│  │  (Vercel)       │    │  (Automation)   │    │  Agent      │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬──────┘ │
└───────────┼──────────────────────┼────────────────────┼────────┘
            │                      │                    │
            ▼                      ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Jobs API    │  │ Cover       │  │ Email       │             │
│  │ Routes      │  │ Letter API  │  │ API         │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│  ┌──────┴────────────────┴────────────────┴──────┐             │
│  │              Service Layer                     │             │
│  ├────────────────────────────────────────────────┤             │
│  │ • AI Analysis Service   • Cover Letter Service │             │
│  │ • Sparkles RAG Client   • Location Service     │             │
│  │ • JD Analyzer           • Description Fetcher  │             │
│  │ • Resume Service        • Analysis Cache       │             │
│  │ • Note Service (typed)  • Contact Service      │             │
│  └─────────────┬──────────────────┬───────────────┘             │
│                │                  │                             │
│  ┌─────────────┴──────────────────┴───────────────┐             │
│  │         SQLAlchemy Async ORM                   │             │
│  └────────────────────────┬───────────────────────┘             │
└───────────────────────────┼─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐
│ PostgreSQL      │  │ Sparkles RAG │  │ External APIs   │
│ Database        │  │ (Supabase)   │  │ • Claude (AI)   │
│                 │  │ 260+ docs    │  │ • OpenAI (embed)│
└─────────────────┘  └──────────────┘  └─────────────────┘
```

## Component Architecture

### Backend (`/backend`)

```
backend/
├── src/
│   ├── api/
│   │   ├── deps.py           # Dependency injection (auth, db)
│   │   └── routes/           # API endpoint handlers
│   │       ├── jobs.py       # Job CRUD + cover letter generation
│   │       ├── cover_letters.py
│   │       ├── emails.py
│   │       └── health.py
│   ├── automation/
│   │   ├── browser.py        # Playwright session management
│   │   └── linkedin_apply.py # LinkedIn Easy Apply automation
│   ├── config/
│   │   ├── database.py       # SQLAlchemy async setup
│   │   └── settings.py       # Pydantic settings
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/
│   │   ├── resume_service.py # Access Meridian resume data
│   │   ├── jd_analyzer.py    # Job description parsing
│   │   └── cover_letter_service.py
│   └── main.py               # FastAPI application
├── scripts/
│   └── seed_resume_data.py   # Import resume from TypeScript
└── tests/
```

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/login/     # Authentication page
│   │   ├── (dashboard)/      # Protected dashboard routes
│   │   │   ├── page.tsx      # Job list
│   │   │   ├── jobs/[id]/    # Job detail
│   │   │   ├── jobs/new/     # New job form
│   │   │   ├── search/       # Search page
│   │   │   └── settings/     # Settings page
│   │   └── api/              # API route handlers (proxy to backend)
│   ├── components/
│   │   ├── jobs/             # Job-specific components
│   │   └── layout/           # Layout components
│   └── middleware.ts         # Auth middleware
```

### Database (`/database`)

```
database/
├── docker-compose.yml        # PostgreSQL container config
└── init.sql                  # Schema initialization
```

## Data Flow

### Job Creation Flow

```
User → Dashboard → POST /api/jobs → Backend → Database
                                      │
                                      └→ Resume Service (for analysis)
```

### Cover Letter Generation Flow

```
User → Dashboard → POST /api/jobs/{id}/cover-letter
                                │
                                ▼
                          Backend API
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
              Resume Service         JD Analyzer
                    │                       │
                    └───────────┬───────────┘
                                ▼
                     Cover Letter Service
                                │
                                ▼
                         Claude API
                                │
                                ▼
                            Database
```

### AI Analysis Flow

```
User → POST /api/jobs/{id}/analyze?apply_suggestions=true
                                │
                                ▼
                         Check Description
                      (min 500 chars required)
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             JD Analyzer              Sparkles RAG
          (extract requirements)   (match career docs)
                    │                       │
                    └───────────┬───────────┘
                                ▼
                         Claude AI
                    (semantic analysis +
                     coaching insights)
                                │
                                ▼
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
              Update Job Fields      Generate Typed Notes
            (priority, ai_forward,   (summary, strengths,
             target_role, etc.)      watch_outs, etc.)
```

### LinkedIn Automation Flow

```
Claude CLI → POST /api/jobs/{id}/apply → Backend
                                           │
                                           ▼
                                    LinkedIn Automation
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                              │
                    ▼                                              ▼
            Navigate to Job                               Fill Form Fields
                    │                                              │
                    ▼                                              ▼
        [PAUSE - Human Confirmation]                  [PAUSE - Human Review]
                    │                                              │
                    ▼                                              ▼
              Click Apply                                    Submit
                    │                                              │
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼
                                     Record Attempt
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│        jobs         │       │    cover_letters    │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │───┐   │ id (PK)             │
│ title               │   │   │ job_id (FK)         │───┐
│ company             │   │   │ content             │   │
│ location            │   │   │ target_role         │   │
│ work_location_type  │   │   │ is_approved         │   │
│ description_raw     │   │   │ created_at          │   │
│ status              │   │   └─────────────────────┘   │
│ target_role         │   │                             │
│ priority            │   │   ┌─────────────────────┐   │
│ is_ai_forward       │   │   │       emails        │   │
│ ai_confidence       │   │   ├─────────────────────┤   │
│ is_location_compat  │   └──▶│ id (PK)             │   │
│ is_easy_apply       │       │ job_id (FK)         │◀──┘
│ source / source_id  │       │ from_email          │
│ notes (JSON array)  │       │ subject             │
│ applied_at          │       │ body                │
│ created_at          │       │ timestamp           │
└─────────────────────┘       └─────────────────────┘
         │
         │    ┌─────────────────────────┐
         │    │  application_attempts   │
         │    ├─────────────────────────┤
         └───▶│ id (PK)                 │
              │ job_id (FK)             │
              │ method                  │
              │ success                 │
              │ error_message           │
              │ screenshot_path         │
              │ created_at              │
              └─────────────────────────┘
```

### Typed Notes (JSON Array in jobs.notes)

```json
[
  {
    "text": "**APPLY** (78/100) - Strong fit...",
    "timestamp": "2025-01-07T04:00:00Z",
    "source": "agent",
    "note_type": "ai_analysis_summary",
    "metadata": {"priority_score": 78}
  }
]
```

Note types: `general`, `ai_analysis_summary`, `strengths`, `watch_outs`, `talking_points`, `study_recommendations`, `coaching_notes`, `rag_evidence`

## Security Model

### Authentication
- API key authentication via `X-API-Key` header
- Keys stored in environment variables
- Frontend stores key in httpOnly cookie

### Authorization
- Single-user system (API key grants full access)
- All dashboard routes protected by middleware

### Data Protection
- No automatic data deletion
- Soft delete for jobs
- Audit trail via timestamps
