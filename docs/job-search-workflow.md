# Job Search Workflow Documentation

**Document Created:** January 6, 2026
**Last Updated:** January 6, 2026
**Related:** [Candidate Profile](./candidate-profile-tom-hundley.md) | [Job Search Queries](./job-search-queries.md)

---

## Overview

This document defines the workflow for the Meridian Job Tracker system. The core philosophy is **"Ingest First, Apply Later"** - maximizing opportunity capture while maintaining quality through staged evaluation.

---

## Workflow Stages

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   INGEST    │ -> │   SCORE     │ -> │ PRIORITIZE  │ -> │   TRACK     │ -> │   APPLY     │
│             │    │             │    │             │    │             │    │             │
│ Capture all │    │ Auto-match  │    │ Human       │    │ Pipeline    │    │ Execute     │
│ opportunities│   │ against     │    │ review &    │    │ management  │    │ application │
│             │    │ profile     │    │ prioritize  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Stage 1: INGEST (Capture)

### Purpose
Rapidly capture job opportunities from multiple sources without manual data entry.

### Status: `saved`

### Supported Sources

| Source | URL Pattern | Data Extracted |
|--------|-------------|----------------|
| LinkedIn | `linkedin.com/jobs/view/*` | Title, company, location, description |
| Indeed | `indeed.com/viewjob*` | Title, company, location, description |
| Greenhouse | `boards.greenhouse.io/*` | Title, company, location, description |
| Lever | `jobs.lever.co/*` | Title, company, location, description |
| Workday | `*.myworkdayjobs.com/*` | Title, company, location, description |

### Ingestion Methods

**1. Single URL Ingest**
```bash
POST /api/v1/jobs/ingest
{
  "url": "https://linkedin.com/jobs/view/123456789",
  "source": "linkedin",  # optional, auto-detected
  "notes": "Referred by John"  # optional
}
```

**2. Bulk URL Ingest**
```bash
POST /api/v1/jobs/bulk
{
  "jobs": [
    {"url": "https://linkedin.com/jobs/view/123"},
    {"url": "https://greenhouse.io/company/job/456"},
    {"url": "https://jobs.lever.co/company/789"}
  ]
}
```

**3. Manual Entry (Fallback)**
```bash
POST /api/v1/jobs
{
  "title": "VP Engineering",
  "company": "TechCorp",
  "location": "Remote",
  "url": "https://...",
  "description_raw": "..."
}
```

### Daily Workflow
1. Browse job boards (LinkedIn, Indeed, etc.)
2. Copy URLs of interesting positions
3. Batch ingest via API or UI
4. System de-duplicates automatically
5. Review queue populates

---

## Stage 2: SCORE (Auto-Match)

### Purpose
Automatically evaluate each job against Tom's profile to surface best-fit opportunities.

### Status: `saved` -> `researching` (when review begins)

### Scoring Dimensions

| Dimension | Weight | Signals |
|-----------|--------|---------|
| Role Match | 30% | Title keywords (CTO, VP, Director, Architect) |
| Tech Stack | 25% | Azure, .NET, React, TypeScript, AI/ML |
| Company Fit | 20% | Size (100-500), stage (Series B+), industry |
| Location | 15% | Remote-first, Atlanta area, no relocation |
| Compensation | 10% | $225K+ base, equity included |

### Tech Stack Matching

**High-Priority Keywords (Tom's Core Stack):**
```
Azure, C#, .NET, React, TypeScript, Next.js,
Cosmos DB, SQL Server, OpenAI, AI, ML, LLM, RAG
```

**Bonus Keywords:**
```
Python, Docker, Kubernetes, Terraform,
FastAPI, Node.js, PostgreSQL
```

**Red Flag Keywords:**
```
Java-only, PHP, WordPress, entry-level,
no remote, on-site required, C2C only
```

### Scoring Algorithm (Proposed)
```python
def calculate_job_score(job, profile):
    score = 0

    # Role match (30 points max)
    role_keywords = ['cto', 'vp', 'vice president', 'director', 'architect']
    if any(kw in job.title.lower() for kw in role_keywords):
        score += 30

    # Tech stack (25 points max)
    tech_matches = count_tech_keywords(job.description, profile.tech_stack)
    score += min(tech_matches * 5, 25)

    # Remote/Location (15 points max)
    if 'remote' in job.location.lower():
        score += 15
    elif 'atlanta' in job.location.lower():
        score += 10

    # Company signals (20 points max)
    # - Check company size, funding, industry

    # Compensation (10 points max)
    # - Parse salary if available

    return score
```

---

## Stage 3: PRIORITIZE (Human Review)

### Purpose
Human evaluation of scored jobs to make final prioritization decisions.

### Status Progression
- `saved` - Newly ingested, unreviewed
- `researching` - Under active evaluation
- `ready_to_apply` - Approved for application
- `withdrawn` - Declined by user (with reasons)

### Review Checklist

**Company Research:**
- [ ] Company website review
- [ ] Glassdoor reviews (culture, interview process)
- [ ] LinkedIn company page (size, growth, funding)
- [ ] Recent news (layoffs, acquisitions, funding)
- [ ] Tech blog/engineering culture

**Role Evaluation:**
- [ ] Does title match target roles?
- [ ] Are responsibilities aligned with goals?
- [ ] Is there room for growth/impact?
- [ ] Is the tech stack compatible?

**Red Flag Check:**
- [ ] Recent layoffs?
- [ ] Negative Glassdoor trends?
- [ ] C2C/contractor only?
- [ ] Relocation required?
- [ ] Below target compensation?

### Decline Tracking

When declining a job, record reasons for future analysis:

**User Decline Reasons:**
- Compensation: `salary_too_low`, `benefits_inadequate`, `no_equity`
- Location: `not_remote`, `wrong_location`, `relocation_required`
- Role Fit: `underqualified`, `overqualified`, `wrong_responsibilities`
- Company: `culture_concerns`, `bad_reviews`, `financial_instability`
- Other: `found_better`, `timing_not_right`, `lost_interest`

---

## Stage 4: TRACK (Pipeline Management)

### Purpose
Active management of opportunities through the application funnel.

### Status Progression
```
ready_to_apply -> applying -> applied -> interviewing -> offer
                                    \-> rejected (by company)
                                    \-> withdrawn (by user)
```

### Pipeline Metrics

| Metric | Target | Tracking |
|--------|--------|----------|
| Weekly Applications | 10-15 | `applied_at` timestamps |
| Response Rate | >10% | Applied -> Interviewing |
| Interview Conversion | >30% | Interviewing -> Offer |
| Time in Stage | <7 days | `status_changed_at` |

### Stale Job Detection

Jobs requiring attention:
```sql
-- Jobs stuck in early stages > 7 days
SELECT * FROM jobs
WHERE status IN ('saved', 'researching', 'ready_to_apply')
  AND status_changed_at < NOW() - INTERVAL '7 days';
```

---

## Stage 5: APPLY (Execute)

### Purpose
Execute high-quality applications with appropriate materials.

### Status: `applying` -> `applied`

### Application Components

**1. Resume Selection**
Select role-appropriate resume variant:

| Job Title Pattern | Resume Variant |
|-------------------|----------------|
| CTO, Chief Technology | `cto` |
| VP Engineering, VP Technology | `vp` |
| Director of Engineering | `director` |
| Principal/Staff Architect | `architect` |
| Senior Engineer | `developer` |

**2. Cover Letter Generation**
```bash
POST /api/v1/jobs/{job_id}/cover-letter
{
  "target_role": "vp",
  "custom_instructions": "Emphasize AI experience"
}
```

**3. Application Execution**
- Submit via job board
- Record `applied_at` timestamp
- Update status to `applied`
- Set follow-up reminder

### Post-Application Tracking

**On Response:**
- Positive: Move to `interviewing`
- Negative: Move to `rejected`, record `company_decline_reasons`
- No response (30 days): Consider `rejected` with `ghosted`

---

## API Workflow Examples

### Complete Ingest-to-Apply Flow

```bash
# 1. Ingest new job
POST /api/v1/jobs/ingest
{"url": "https://linkedin.com/jobs/view/123456789"}
# Returns: job_id = "abc-123"

# 2. Review and prioritize
PATCH /api/v1/jobs/abc-123
{
  "target_role": "vp",
  "priority": 85,
  "notes": "Strong AI focus, good culture signals"
}

# 3. Move to research queue
PATCH /api/v1/jobs/abc-123/status
{"status": "researching"}

# 4. After research, ready to apply
PATCH /api/v1/jobs/abc-123/status
{"status": "ready_to_apply"}

# 5. Generate cover letter
POST /api/v1/jobs/abc-123/cover-letter
{"target_role": "vp"}

# 6. Mark as applying
PATCH /api/v1/jobs/abc-123/status
{"status": "applying"}

# 7. After submission, mark applied
PATCH /api/v1/jobs/abc-123/status
{"status": "applied"}
# Note: applied_at timestamp set automatically
```

### Bulk Status Updates

```bash
# Move multiple jobs through pipeline
PATCH /api/v1/jobs/bulk/status
{
  "job_ids": ["abc-123", "def-456", "ghi-789"],
  "status": "applied"
}
```

### Decline with Reasons

```bash
# User declining opportunity
PATCH /api/v1/jobs/abc-123/status
{
  "status": "withdrawn",
  "user_decline_reasons": ["salary_too_low", "not_remote"],
  "decline_notes": "Compensation 30% below target"
}

# Company rejection
PATCH /api/v1/jobs/abc-123/status
{
  "status": "rejected",
  "company_decline_reasons": ["selected_other"],
  "decline_notes": "Went with internal candidate"
}
```

---

## Daily/Weekly Workflows

### Daily (15-30 min)

1. **Ingest New Jobs**
   - Browse job boards
   - Bulk ingest interesting URLs
   - Quick triage of new entries

2. **Pipeline Review**
   - Check for stale jobs (>7 days in stage)
   - Follow up on pending applications
   - Update statuses as needed

### Weekly (1-2 hours)

1. **Deep Research Session**
   - Move 5-10 jobs through research queue
   - Company deep-dives
   - Prioritization decisions

2. **Application Batch**
   - Process `ready_to_apply` queue
   - Generate cover letters
   - Submit applications

3. **Analytics Review**
   - Application velocity (target: 10-15/week)
   - Response rates
   - Decline reason patterns

---

## Future Enhancements

### Phase 2: Automated Scoring
- AI-powered job description analysis
- Automatic tech stack extraction
- Company data enrichment (LinkedIn, Crunchbase)

### Phase 3: Smart Prioritization
- ML-based fit scoring
- Similar-job recommendations
- Optimal application timing

### Phase 4: Application Automation
- Auto-fill common fields
- One-click apply integration
- Smart follow-up scheduling

---

## Related Documentation

- [Candidate Profile: Tom Hundley](./candidate-profile-tom-hundley.md)
- [Job Search Queries](./job-search-queries.md)
- [Schema Reference](../database/init.sql)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-06 | 1.0 | Initial workflow documentation |
