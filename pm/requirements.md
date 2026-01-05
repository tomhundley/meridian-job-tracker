# Meridian Job Tracker - Requirements

## Overview

A human-in-the-loop job application system designed to streamline the job search process while maintaining full human control over all application submissions.

## Core Requirements

### Functional Requirements

#### Job Tracking
- Track job opportunities through multiple statuses (saved → applied → interviewing → offer/rejected)
- Store job descriptions, company information, and application notes
- Support priority scoring for job opportunities
- Enable tagging and categorization
- Track application history and timeline

#### Cover Letter Generation
- Generate role-specific cover letters using AI (Claude)
- Support 5 role types: CTO, VP, Director, Architect, Developer
- Pull from structured resume data for personalization
- Require human approval before use

#### Browser Automation
- Automate LinkedIn Easy Apply workflow
- Require human confirmation at critical steps
- Capture screenshots for verification
- Track application attempts and outcomes
- Support persistent browser sessions (maintain login)

#### Email Integration
- Store email correspondence related to jobs
- Link emails to specific job applications
- Support external email agent integration

### Non-Functional Requirements

#### Security
- API key authentication for all endpoints
- Secure credential storage
- No automatic submission without confirmation

#### Performance
- Async database operations
- Efficient job listing with pagination
- Fast search across job descriptions

#### Maintainability
- Modular service architecture
- Comprehensive API documentation
- Type safety (Python type hints, TypeScript)

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Framework | FastAPI | Async support, auto-generated docs, type safety |
| Database | PostgreSQL | Robust, good tooling, JSON support |
| ORM | SQLAlchemy 2.0 | Async support, mature ecosystem |
| Browser Automation | Playwright | Cross-browser, Python support, reliable |
| Frontend Framework | Next.js 15 | App Router, React 19, good DX |
| AI Provider | Anthropic Claude | Superior writing quality |

## User Stories

### Job Seeker (Primary User)

1. **Save Jobs**: "I want to save interesting job postings so I can research them later"
2. **Track Progress**: "I want to see where each application stands in the pipeline"
3. **Generate Cover Letters**: "I want AI-generated cover letters tailored to each job"
4. **Apply Efficiently**: "I want to apply to LinkedIn Easy Apply jobs quickly"
5. **Review Applications**: "I want to verify every application before submission"
6. **Search History**: "I want to search through all my tracked jobs"

### System Integration

1. **Email Agent**: "External agents can add email correspondence to the system"
2. **CLI Integration**: "Claude Code can interact with the system for automation"

## Constraints

- All application submissions require explicit human confirmation
- Resume data sourced from existing Meridian project
- Local development with Docker for database
- Frontend deployable to Vercel
