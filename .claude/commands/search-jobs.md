# Search for Jobs on LinkedIn

Search LinkedIn for relevant job postings using browser automation.

## CRITICAL: Extract Full Data for Each Result

**When saving jobs from search results, you MUST navigate to each job page to extract the full description.**

Search results only show: title, company, location, and a brief snippet. The full job description (required for analysis) is only available on the individual job page.

## Complete Workflow

### Step 1: Generate Search URL

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

### Step 2: Navigate to Search Results

```
mcp__chrome-devtools__navigate_page with the search URL
mcp__chrome-devtools__take_snapshot
```

### Step 3: For EACH Interesting Job

You MUST do the following for each job you want to save:

#### 3a. Navigate to Job Page

```
mcp__chrome-devtools__navigate_page with url: "https://www.linkedin.com/jobs/view/{job_id}/"
```

#### 3b. Take Snapshot

```
mcp__chrome-devtools__take_snapshot
```

#### 3c. Extract Complete Data

From the snapshot, extract:
- Job title (from header)
- Company name (from company link)
- Location (from badge)
- Work location type: remote/hybrid/on_site (from badge)
- Salary (from badge, if shown)
- Easy Apply status (badge present or not)
- **FULL DESCRIPTION** from "About the job" section (2000+ chars)

#### 3d. Save Job

Write to `/tmp/{company}-job.json` then:

```bash
cat /tmp/{company}-job.json | curl -s -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @- | jq
```

#### 3e. Run Analysis

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

## Common Searches

VP roles:
```
/search-jobs VP Engineering
```

CTO roles:
```
/search-jobs CTO Chief Technology Officer
```

AI-focused roles:
```
/search-jobs VP AI ML Engineering
```

Director roles:
```
/search-jobs Director of Engineering
```

## Required Data for Each Job

| Field | Source |
|-------|--------|
| `title` | Job header |
| `company` | Company link |
| `description_raw` | "About the job" section (2000+ chars) |
| `location` | Location badge |
| `work_location_type` | remote/hybrid/on_site badge |
| `employment_type` | Job details |
| `source_id` | Job ID from URL |
| `source_url` | Full job URL |
| `is_easy_apply` | Easy Apply badge |
| `salary_min/max` | Salary badge (if shown) |

## Validation

Before considering a job saved:
- [ ] `description_raw` is 2000+ characters
- [ ] `source_url` and `source_id` set
- [ ] `work_location_type` set
- [ ] Analysis run with `apply_suggestions=true`

## Arguments

`/search-jobs {keywords}` - Search LinkedIn and save jobs with full data
