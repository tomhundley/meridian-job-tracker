# Agent Integration Guide

Instructions for AI agents working with the Meridian Job Tracker. Keep concise and update when workflows change.

> **Detailed Documentation**: See [docs/ANALYSIS_SYSTEM.md](docs/ANALYSIS_SYSTEM.md) for full analysis system details.

## Part of the Meridian Ecosystem

This project integrates with:
- **[trh-meridian](https://github.com/ElegantSoftwareSolutions/trh-meridian)** - Resume site + Sparkles RAG (260+ career documents)
- **[meridian-linkedIn](https://github.com/tomhundley/meridian-linkedIn)** - LinkedIn MCP Server

---

## CRITICAL RULES

### Rule 1: Complete Descriptions Required

**Every job MUST have `description_raw` > 500 characters (ideally 2000+) before analysis.**

The job scraper uses `httpx` which cannot execute JavaScript. LinkedIn renders descriptions via JavaScript, resulting in only ~150 characters from meta tags.

**ALWAYS use browser automation** to extract full job descriptions.

### Rule 2: Always Apply Suggestions

**ALWAYS use `apply_suggestions=true` when analyzing jobs.**

```bash
# CORRECT - always use this
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"

# WRONG - never do this
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze"
```

---

## Job Workflow

### Step 1: Extract Job Data (Browser Automation Required)

```bash
# Navigate to job page
mcp__chrome-devtools__navigate_page  # or mcp__playwright__browser_navigate

# Take snapshot and extract "About the job" section
mcp__chrome-devtools__take_snapshot  # or mcp__playwright__browser_snapshot

# Write extracted data to JSON file (avoids shell escaping issues)
Write to /tmp/{company}-job.json
```

### Step 2: Create/Update Job

```bash
# Create new job
cat /tmp/job.json | curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @-

# Or update existing job
cat /tmp/update.json | curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{id}" \
  -H "Content-Type: application/json" -d @-
```

### Step 3: Run Analysis (Always with apply_suggestions=true)

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

This updates:
- `priority` - Fit score (0-100)
- `is_ai_forward` - AI-forward company detection
- `ai_confidence` - Confidence score (0-1)
- `target_role` - Suggested role (cto/vp/director/architect/developer)
- `is_location_compatible` - Location validation for GA-based candidate
- `notes` - Multiple typed coaching notes

---

## Required Data Fields

| Field | Required | How to Extract |
|-------|----------|----------------|
| `title` | YES | Job header |
| `company` | YES | Company link |
| `description_raw` | YES | "About the job" section (2000+ chars) |
| `location` | YES | Location badge |
| `work_location_type` | YES | remote/hybrid/on_site badge |
| `employment_type` | YES | full_time/contract/etc |
| `source` | YES | "linkedin" or other |
| `source_id` | YES | Job ID from URL |
| `source_url` | YES | Full URL |
| `is_easy_apply` | YES | Easy Apply badge present |
| `salary_min/max` | If shown | Salary badge |

---

## Typed Notes System

Analysis generates multiple categorized notes automatically:

| Note Type | Content |
|-----------|---------|
| `ai_analysis_summary` | Overall recommendation (APPLY/SKIP) with score |
| `strengths` | Key strengths for this role |
| `watch_outs` | Red flags or concerns |
| `talking_points` | Interview preparation points |
| `study_recommendations` | Skills to brush up on |
| `coaching_notes` | What to emphasize in applications |
| `rag_evidence` | Evidence from career documents |

### Filter Notes by Type

```bash
# Get all notes
curl -s "http://localhost:8000/api/v1/jobs/{id}/notes"

# Filter by type
curl -s "http://localhost:8000/api/v1/jobs/{id}/notes?note_type=talking_points"

# Filter by source
curl -s "http://localhost:8000/api/v1/jobs/{id}/notes?source=agent"
```

### Add a Note

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Remember to mention the MDSi experience",
    "source": "user",
    "note_type": "talking_points"
  }'
```

---

## RAG Integration (Sparkles)

RAG is enabled by default. The system matches job requirements against 260+ career documents from Sparkles.

### Check RAG Status

```bash
# Get description statistics
curl -s "http://localhost:8000/api/v1/jobs/descriptions/stats"

# Returns:
# {
#   "total_jobs": 62,
#   "complete_descriptions": 43,
#   "incomplete_descriptions": 19,
#   "needs_fetch": 19
# }
```

### List Incomplete Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs/descriptions/incomplete?limit=10"
```

### Disable RAG (Rarely Needed)

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true&use_rag=false"
```

---

## Location Validation

The system validates job locations for a GA-based candidate:

- **Remote US** with state restrictions → Checks if GA is allowed
- **Remote US** without restrictions → Compatible
- **Hybrid/On-site** anywhere in US → Compatible (candidate travels)

When location is incompatible:
- Sets `is_location_compatible = false`
- Sets `status = archived`
- Adds explanation to `decline_notes`

---

## API Quick Reference

| Endpoint | Description |
|----------|-------------|
| `POST /jobs` | Create job |
| `PATCH /jobs/{id}` | Update job |
| `POST /jobs/{id}/analyze?apply_suggestions=true` | **Run AI analysis** |
| `GET /jobs/{id}/notes` | List notes |
| `POST /jobs/{id}/notes` | Add note |
| `GET /jobs/descriptions/stats` | Description statistics |
| `GET /jobs/descriptions/incomplete` | Jobs needing descriptions |

---

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://...
API_KEY=your-api-key
ANTHROPIC_API_KEY=sk-ant-...

# For RAG (from meridian/.env.local)
OPENAI_API_KEY=sk-proj-...
SPARKLES_SUPABASE_URL=https://xxx.supabase.co
SPARKLES_SUPABASE_SERVICE_KEY=eyJ...
```

---

## Common Patterns

### Recruiting Firms

Jobs posted by staffing agencies (Staffing Science, Albert Bow, BrainWorks, etc.):
- Still extract full description - contains actual role details
- Note the actual hiring company if mentioned in description

### Verifying Description Completeness

```bash
curl -s "http://localhost:8000/api/v1/jobs/{id}" | jq '{
  title,
  company,
  desc_len: (.description_raw | length),
  analyzed: (.priority != null)
}'
```

If `desc_len < 500`: Job needs full description via browser automation.

---

## Key Files

- `backend/src/services/ai_analysis_service.py` - AI analysis + coaching
- `backend/src/services/sparkles_client.py` - RAG integration
- `backend/src/services/location_service.py` - Location validation
- `backend/src/schemas/job_note.py` - Note types
- `docs/ANALYSIS_SYSTEM.md` - Full documentation
