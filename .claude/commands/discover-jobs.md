# Discover and Save Jobs from LinkedIn

Bulk discover jobs from LinkedIn search results and save with complete data.

## CRITICAL: Full Data Extraction Required

**Every discovered job MUST have complete description extracted via browser automation.**

The discovery workflow has two phases:
1. **Discovery**: Find jobs from search results (basic info only)
2. **Enrichment**: Extract full description for each job (REQUIRED)

## Complete Workflow

### Phase 1: Search and Discover

#### Step 1: Generate Search URL

```bash
curl -s -X POST "http://localhost:8000/api/v1/discovery/linkedin/search-url" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "VP Engineering",
    "location": "United States",
    "experience_level": ["director", "executive"],
    "date_posted": "week",
    "remote": true,
    "easy_apply_only": true
  }' | jq '.search_url'
```

#### Step 2: Navigate with Browser

```
mcp__chrome-devtools__navigate_page with the search URL
mcp__chrome-devtools__take_snapshot
```

#### Step 3: Extract Job Listings from Search Results

From the snapshot, extract for each job:
- Job title
- Company name
- LinkedIn job ID (from URL)
- Location
- Easy Apply badge
- Salary (if shown)

### Phase 2: Enrich Each Job (MANDATORY)

**For EACH discovered job, you MUST:**

#### Step 1: Navigate to Job Page

```
mcp__chrome-devtools__navigate_page with url: "https://www.linkedin.com/jobs/view/{job_id}/"
```

#### Step 2: Extract Full Description

```
mcp__chrome-devtools__take_snapshot
```

Find the "About the job" section and extract complete description (2000+ chars).

#### Step 3: Save with Complete Data

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "VP of Engineering",
    "company": "TechCorp",
    "description_raw": "Full 2000+ char description...",
    "location": "San Francisco, CA (Remote)",
    "work_location_type": "remote",
    "employment_type": "full_time",
    "source": "linkedin",
    "source_id": "123456789",
    "source_url": "https://linkedin.com/jobs/view/123456789/",
    "is_easy_apply": true
  }' | jq
```

#### Step 4: Run Analysis

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true" | jq
```

## Search Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `keywords` | string | Search terms (e.g., "VP Engineering") |
| `location` | string | Location filter |
| `experience_level` | array | entry, associate, mid_senior, director, executive |
| `date_posted` | string | any, day, week, month |
| `remote` | boolean | Filter for remote jobs |
| `easy_apply_only` | boolean | Filter for Easy Apply only |

## Validation Checklist

For EACH discovered job:
- [ ] Full description extracted (2000+ chars)
- [ ] `source_url` and `source_id` set
- [ ] `work_location_type` set
- [ ] `is_easy_apply` set
- [ ] Analysis run with `apply_suggestions=true`

## DO NOT Use Bulk Save Without Enrichment

The bulk save endpoint creates jobs with incomplete data:

```bash
# DO NOT USE without enrichment phase
curl -s -X POST "http://localhost:8000/api/v1/discovery/linkedin/save" ...
```

Jobs saved this way will have truncated descriptions and analysis will fail.

## Arguments

`/discover-jobs {keywords}` - Start job discovery workflow with full enrichment
