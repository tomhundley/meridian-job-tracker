# View Job Details

View complete details for a specific job, including data completeness check.

## API Endpoint

GET `http://localhost:8000/api/v1/jobs/{job_id}`

## Usage

### Quick View with Completeness Check

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{
  title, company, location, status,
  desc_len: (.description_raw | length),
  complete: ((.description_raw | length) > 500),
  salary_min, salary_max,
  target_role, priority,
  is_easy_apply, is_ai_forward, is_favorite, is_perfect_fit,
  work_location_type, employment_type,
  source_url, source_id,
  posted_at, applied_at
}'
```

### Full Details

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq
```

### View with Description

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{title, company, description_raw}'
```

## Completeness Check

**IMPORTANT**: Check if job data is complete before analysis or application.

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{
  title, company,
  desc_len: (.description_raw | length),
  is_complete: ((.description_raw | length) > 500),
  needs_enrichment: ((.description_raw | length) < 500),
  source_url
}'
```

### Interpretation

| desc_len | Status | Action Needed |
|----------|--------|---------------|
| < 200 | Incomplete | MUST update with browser automation |
| 200-500 | Partial | Should update for better analysis |
| 500-2000 | Adequate | Analysis will work, but more data preferred |
| 2000+ | Complete | Ready for analysis and application |

### If Job Needs Enrichment

Use `/edit-job` skill to update with full description:

1. Navigate to `source_url` with browser
2. Extract "About the job" section
3. PATCH job with full description
4. Run analysis with `apply_suggestions=true`

## Key Fields

| Field | Description |
|-------|-------------|
| `id` | Job UUID |
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `status` | saved, researching, ready_to_apply, applying, applied, etc. |
| `description_raw` | Full job description (check length!) |
| `salary_min/max` | Salary range |
| `target_role` | cto, vp, director, architect, developer |
| `priority` | 0-100 fit score |
| `is_easy_apply` | Easy Apply available |
| `is_ai_forward` | AI-forward company |
| `is_favorite` | Marked as favorite |
| `is_perfect_fit` | Marked as perfect fit |
| `work_location_type` | remote, hybrid, on_site |
| `employment_type` | full_time, contract, etc. |
| `source` | linkedin, indeed, etc. |
| `source_id` | Platform job ID |
| `source_url` | Full job URL |
| `posted_at` | When job was posted |
| `applied_at` | When you applied |
| `contact_count` | Number of linked contacts |

## List Jobs with Completeness Status

```bash
curl -s "http://localhost:8000/api/v1/jobs?limit=20" | jq '.items[] | {
  id, title, company,
  desc_len: (.description_raw | length),
  complete: ((.description_raw | length) > 500),
  priority, is_ai_forward
}'
```

## Find Incomplete Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs?limit=100" | jq '[.items[] | select((.description_raw | length) < 500)] | .[] | {id, title, company, desc_len: (.description_raw | length)}'
```

## Arguments

`/view-job {job_id}` - View complete job details with completeness check
