# Edit Job Details

Update job information like description, salary, notes, priority, etc.

## Common Use Case: Fix Incomplete Descriptions

**Many jobs have incomplete descriptions** (only ~150 chars from meta tags). This skill is commonly used to update jobs with full descriptions extracted via browser automation.

### Check If Job Needs Update

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{
  title, company,
  desc_len: (.description_raw | length),
  source_url, source_id
}'
```

If `desc_len < 500`: Job has incomplete data and needs updating.

### Update with Full Description

#### Step 1: Navigate to Job Page

```
mcp__chrome-devtools__navigate_page with url from source_url
```

Or search LinkedIn: `https://www.linkedin.com/jobs/search/?keywords="Company Name"`

#### Step 2: Extract Full Data

```
mcp__chrome-devtools__take_snapshot
```

Extract from "About the job" section (2000+ chars).

#### Step 3: Write JSON File

Write to `/tmp/{company}-update.json`:

```json
{
  "description_raw": "Full description from About the job section...",
  "salary_min": 300000,
  "salary_max": 400000,
  "salary_currency": "USD",
  "work_location_type": "remote",
  "location": "San Francisco, CA (Remote)",
  "source_id": "4354665921",
  "source_url": "https://www.linkedin.com/jobs/view/4354665921/",
  "is_easy_apply": true
}
```

#### Step 4: PATCH Job

```bash
cat /tmp/{company}-update.json | curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" -d @- | jq '{title, company, desc_len: (.description_raw | length)}'
```

#### Step 5: Run Analysis

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze?apply_suggestions=true" | jq
```

## API Endpoint

PATCH `http://localhost:8000/api/v1/jobs/{job_id}`

## Editable Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Job title |
| `company` | string | Company name |
| `description_raw` | string | Full job description (2000+ chars) |
| `location` | string | Job location |
| `work_location_type` | enum | remote, hybrid, on_site |
| `salary_min` | int | Minimum salary |
| `salary_max` | int | Maximum salary |
| `salary_currency` | string | Currency code (USD, EUR, etc.) |
| `employment_type` | enum | full_time, contract, etc. |
| `target_role` | enum | cto, vp, director, architect, developer |
| `priority` | int | 0-100 fit score |
| `notes` | string | Personal notes |
| `tags` | array | Array of tags |
| `source` | string | linkedin, indeed, etc. |
| `source_id` | string | Platform job ID |
| `source_url` | string | Full job URL |
| `is_easy_apply` | bool | Easy Apply available |
| `is_favorite` | bool | Marked as favorite |
| `is_perfect_fit` | bool | Marked as perfect fit |
| `is_ai_forward` | bool | AI-forward company |

## Usage Examples

### Update Salary

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"salary_min": 350000, "salary_max": 450000, "salary_currency": "USD"}' | jq
```

### Update Priority and Notes

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"priority": 85, "notes": "Great culture fit, talked to former employee"}' | jq
```

### Update Target Role

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"target_role": "vp"}' | jq
```

### Mark as Favorite

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_favorite": true}' | jq
```

## Shell Escaping Note

For fields with special characters (like `description_raw` with apostrophes), always use the JSON file approach:

```bash
# Write JSON to file first
Write to /tmp/update.json

# Then use file
cat /tmp/update.json | curl -s -X PATCH "..." -d @-
```

## Arguments

`/edit-job {job_id}` - Edit job details (prompts for what to update)
