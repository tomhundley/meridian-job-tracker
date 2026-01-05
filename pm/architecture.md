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
│  │ • Resume Service    • Cover Letter Service     │             │
│  │ • JD Analyzer       • LinkedIn Automation      │             │
│  └────────────────────────┬───────────────────────┘             │
│                           │                                     │
│  ┌────────────────────────┴───────────────────────┐             │
│  │         SQLAlchemy Async ORM                   │             │
│  └────────────────────────┬───────────────────────┘             │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
├─────────────────────────────────────────────────────────────────┤
│  jobs │ cover_letters │ emails │ application_attempts          │
└─────────────────────────────────────────────────────────────────┘
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
│ url                 │   │   │ is_approved         │   │
│ description_raw     │   │   │ created_at          │   │
│ status              │   │   └─────────────────────┘   │
│ target_role         │   │                             │
│ priority            │   │   ┌─────────────────────┐   │
│ notes               │   │   │       emails        │   │
│ tags                │   │   ├─────────────────────┤   │
│ applied_at          │   └──▶│ id (PK)             │   │
│ created_at          │       │ job_id (FK)         │◀──┘
│ updated_at          │       │ from_email          │
│ deleted_at          │       │ subject             │
└─────────────────────┘       │ body                │
         │                    │ timestamp           │
         │                    └─────────────────────┘
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
