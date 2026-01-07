# Claude Code Project Rules

Project-specific rules and conventions for Claude Code when working in this repository.

## API Configuration

- **Backend URL**: `http://localhost:8000/api/v1/`
- **Frontend URL**: `http://localhost:3005`
- **Database**: PostgreSQL via Docker at `localhost:5434`

## Job Data Quality - MANDATORY

### The #1 Rule

**Every job added to the system MUST have a complete description (2000+ chars) extracted via browser automation.**

The built-in job scraper (`/ingest` endpoint) uses httpx which cannot execute JavaScript. LinkedIn and most job boards require JavaScript to render full descriptions. Without browser automation, you only get ~150 characters from meta tags.

### Before ANY Job Operation

1. **Check description length**: `curl -s "http://localhost:8000/api/v1/jobs/{id}" | jq '{title, company, desc_len: (.description_raw | length)}'`
2. If `desc_len < 500`: Job is INCOMPLETE - must update with browser automation
3. If `desc_len < 2000`: Job may be incomplete - verify with source

### Adding Jobs - Required Steps

```bash
# Step 1: Use browser to navigate to job page
# Chrome DevTools MCP or Playwright

# Step 2: Take snapshot and extract "About the job" section

# Step 3: Create JSON file with all extracted data
# Write to /tmp/{company}-update.json to avoid shell escaping issues

# Step 4: Create or update job via API
cat /tmp/file.json | curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @-

# Step 5: Run analysis with apply_suggestions=true
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

### Required Fields for Every Job

| Field | Description | How to Get |
|-------|-------------|------------|
| `title` | Job title | From job header |
| `company` | Company name | From job header |
| `description_raw` | Full job description | "About the job" section - MUST BE 2000+ CHARS |
| `location` | Job location | From location badge |
| `work_location_type` | remote/hybrid/on_site | From location badge |
| `employment_type` | full_time/contract/etc | From job details |
| `source` | "linkedin" or other | Based on URL |
| `source_id` | Platform job ID | From URL (e.g., 4354665921) |
| `source_url` | Full job URL | Browser URL |
| `is_easy_apply` | Boolean | Easy Apply badge present |

### Optional But Recommended

| Field | Description |
|-------|-------------|
| `salary_min` | Minimum salary |
| `salary_max` | Maximum salary |
| `salary_currency` | "USD" typically |
| `posted_at` | When job was posted |

## Analysis Requirements - MANDATORY

### The Analysis Rule

**ALWAYS run analysis with `apply_suggestions=true`.** This is not optional.

```bash
# CORRECT - always use this
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"

# WRONG - never analyze without applying suggestions
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze"
```

The job analysis endpoint (`/analyze`) requires:
- `description_raw` > 500 characters to generate meaningful results
- Without sufficient description, analysis returns low-confidence defaults

With `apply_suggestions=true`, the system auto-updates:
- `is_ai_forward` - Whether company/role is AI-forward
- `ai_confidence` - Confidence score (0-1)
- `priority` - Fit score (0-100)
- `target_role` - Suggested role (cto/vp/director/architect/developer)
- `is_location_compatible` - Whether job location is compatible with user
- `notes` - Multiple typed notes with coaching insights

### RAG-Enhanced Analysis

RAG is enabled by default (`use_rag=true`). The system fetches context from Sparkles career documents (260+ documents) to provide personalized coaching:

```bash
# Standard analysis (RAG enabled by default)
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"

# Explicitly enable RAG (same as above)
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true&use_rag=true"

# Disable RAG (rarely needed)
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true&use_rag=false"
```

### Typed Notes

Analysis with `apply_suggestions=true` generates multiple categorized notes:

| Note Type | Purpose |
|-----------|---------|
| `ai_analysis_summary` | Overall recommendation (APPLY/SKIP/etc) with score |
| `strengths` | Key strengths identified in the match |
| `watch_outs` | Red flags or concerns |
| `talking_points` | Interview preparation points |
| `study_recommendations` | Skills/topics to brush up on |
| `coaching_notes` | What to emphasize in applications |
| `rag_evidence` | Evidence from career documents |

Filter notes by type:
```bash
curl -s "http://localhost:8000/api/v1/jobs/{id}/notes?note_type=talking_points"
```

### Incomplete Descriptions

Check for jobs needing full descriptions:
```bash
# Get statistics
curl -s "http://localhost:8000/api/v1/jobs/descriptions/stats"

# List incomplete jobs
curl -s "http://localhost:8000/api/v1/jobs/descriptions/incomplete?limit=10"
```

## User Location & Validation

### User Location
- **State**: Georgia (GA)
- **City**: Alpharetta
- **Travel**: Willing to travel anywhere in the US for hybrid/on-site roles

### Location Validation Rules

When analyzing jobs with `apply_suggestions=true`:

1. **Remote jobs**: Check if location allows Georgia
   - "Remote US (CT, MA, NH, NJ, NY)" → **Incompatible** (GA not listed)
   - "Remote US" or "Remote" → **Compatible** (all states allowed)

2. **Hybrid/On-site jobs**: Always **Compatible** (user travels anywhere US)

3. **Auto-rejection behavior** (when location incompatible):
   - Sets `is_location_compatible = false`
   - Sets `status = archived`
   - Adds `location_restricted` to `user_decline_reasons`
   - Adds explanation to `decline_notes`

### Location String Patterns

The location service parses these formats:
- `"Remote US (CT, MA, NH, NJ, NY)"` → Requires one of: CT, MA, NH, NJ, NY
- `"Remote - CT, MA, NH, NJ, NY only"` → Same as above
- `"Remote in: CT | MA | NH"` → Same pattern with pipe separator
- `"Remote US"` or `"Fully Remote"` → All states allowed

## Shell Command Patterns

### Avoid Shell Escaping Issues

Job descriptions contain apostrophes, quotes, and special characters. Never pass them directly in shell commands.

**WRONG:**
```bash
curl -d '{"description_raw": "We're looking..."}'  # Apostrophe breaks shell
```

**RIGHT:**
```bash
# Write to file first
Write JSON to /tmp/job-update.json

# Then use file
cat /tmp/job-update.json | curl -s -X PATCH "..." -d @-
```

### curl Patterns

```bash
# GET job
curl -s "http://localhost:8000/api/v1/jobs/{id}" | jq

# PATCH job (from file)
cat /tmp/update.json | curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{id}" \
  -H "Content-Type: application/json" -d @- | jq

# POST new job (from file)
cat /tmp/job.json | curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @- | jq

# Analyze job
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true" | jq
```

## Browser Automation

### Chrome DevTools MCP (Preferred)

```
mcp__chrome-devtools__navigate_page - Navigate to URL
mcp__chrome-devtools__take_snapshot - Get page content
mcp__chrome-devtools__click - Click elements by uid
```

### Playwright MCP (Alternative)

```
mcp__playwright__browser_navigate - Navigate to URL
mcp__playwright__browser_snapshot - Get page content
mcp__playwright__browser_click - Click elements
```

### LinkedIn Job Extraction

1. Navigate to `https://www.linkedin.com/jobs/view/{job_id}/`
2. Take snapshot
3. Find "About the job" section (usually uid contains heading "About the job")
4. Extract all StaticText and LineBreak content under that section
5. Preserve formatting with `\n` for line breaks

## Skills (Slash Commands)

All skills are in `.claude/commands/`. Key skills:

| Skill | Purpose |
|-------|---------|
| `/add-job {url}` | Add job from URL (uses browser automation) |
| `/analyze-job {id}` | Analyze job fit and AI-forward status |
| `/search-jobs {keywords}` | Search LinkedIn for jobs |
| `/discover-jobs {keywords}` | Bulk discover and save jobs |
| `/view-job {id}` | View job details |
| `/edit-job {id}` | Edit job fields |
| `/apply {id}` | Start application workflow |

## Testing

```bash
# Backend tests (uses main database with transaction rollback)
cd backend
source .venv/bin/activate
pytest

# Frontend tests
cd frontend
npm run test
```

## Common Gotchas

1. **Truncated descriptions**: Always verify `description_raw` length after ingestion
2. **Shell escaping**: Use JSON files for any data containing special characters
3. **Analysis fails silently**: Check description length if analysis returns defaults
4. **Recruiting firms**: Company may be recruiter, not actual employer - extract both
5. **curl with @file**: Use `cat file | curl -d @-` not `curl -d @file` for reliability
