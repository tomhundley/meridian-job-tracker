# Add Job from URL

Ingest a job into the tracker from a LinkedIn or other job board URL.

## CRITICAL: Browser Automation Required

**The `/ingest` API alone will NOT get complete job descriptions from LinkedIn.**

LinkedIn renders job descriptions via JavaScript. The scraper uses httpx (no JS execution), resulting in only ~150 characters from meta tags instead of 2000+ characters of actual content.

**You MUST use browser automation to extract full job data.**

## Required Workflow

### Step 1: Navigate to Job Page

```
# Using Chrome DevTools MCP (preferred)
mcp__chrome-devtools__navigate_page with url: "https://www.linkedin.com/jobs/view/{job_id}/"

# OR using Playwright MCP
mcp__playwright__browser_navigate with url: "https://www.linkedin.com/jobs/view/{job_id}/"
```

### Step 2: Extract Job Data

```
# Take snapshot
mcp__chrome-devtools__take_snapshot

# Find and extract from snapshot:
# - Job title (heading near top)
# - Company name (link near title)
# - Location and work type badges
# - Salary badge (if present)
# - Easy Apply badge (if present)
# - "About the job" section - THIS IS THE FULL DESCRIPTION
```

### Step 3: Create JSON File

Write extracted data to `/tmp/{company}-update.json`:

```json
{
  "title": "VP of Engineering",
  "company": "TechCorp",
  "description_raw": "Full job description from 'About the job' section... (2000+ chars)",
  "location": "San Francisco, CA (Remote)",
  "work_location_type": "remote",
  "employment_type": "full_time",
  "salary_min": 300000,
  "salary_max": 400000,
  "salary_currency": "USD",
  "source": "linkedin",
  "source_id": "4354665921",
  "source_url": "https://www.linkedin.com/jobs/view/4354665921/",
  "is_easy_apply": true
}
```

### Step 4: Create Job via API

```bash
cat /tmp/{company}-update.json | curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @- | jq '{id, title, company, desc_len: (.description_raw | length)}'
```

### Step 5: Run Analysis

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true" | jq
```

## Validation Checklist

Before considering a job "added":
- [ ] `description_raw` is 2000+ characters (minimum 500)
- [ ] `source_url` is set
- [ ] `source_id` is set
- [ ] `work_location_type` is set (remote/hybrid/on_site)
- [ ] Analysis has been run with `apply_suggestions=true`

## Supported Sources

- LinkedIn: `linkedin.com/jobs/view/*` (REQUIRES browser automation)
- Indeed: `indeed.com/viewjob*`
- Greenhouse: `boards.greenhouse.io/*`
- Lever: `jobs.lever.co/*`
- Workday: `*.myworkdayjobs.com/*`

## What Gets Extracted

| Field | Required | Source |
|-------|----------|--------|
| `title` | YES | Job header |
| `company` | YES | Company link |
| `description_raw` | YES | "About the job" (2000+ chars) |
| `location` | YES | Location badge |
| `work_location_type` | YES | remote/hybrid/on_site badge |
| `employment_type` | YES | full_time/contract/etc |
| `salary_min/max` | If shown | Salary badge |
| `source_id` | YES | Job ID from URL |
| `source_url` | YES | Full URL |
| `is_easy_apply` | YES | Easy Apply badge |

## After Analysis

Analysis sets:
- `is_ai_forward` - AI-forward company detection
- `ai_confidence` - Confidence score (0-1)
- `priority` - Fit score (0-100)
- `target_role` - cto/vp/director/architect/developer

## Example

```
/add-job https://www.linkedin.com/jobs/view/4354665921
```

This triggers the full workflow: browser navigation, data extraction, job creation, and analysis.
