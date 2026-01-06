# Query Jobs in Database

Query and filter existing jobs in the Meridian job tracker.

## Instructions

Use the jobs API to search and filter your tracked jobs.

## API Endpoint

GET `http://localhost:8000/api/jobs`

## Basic Query

```bash
curl -s "http://localhost:8000/api/jobs" | jq '.items[] | {title, company, status, priority}'
```

## Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | saved, researching, ready_to_apply, applying, applied, interviewing, offer, rejected, withdrawn, archived |
| target_role | string | cto, vp, director, architect, developer |
| work_location_type | string | remote, hybrid, on_site |
| is_easy_apply | boolean | Filter Easy Apply jobs |
| is_favorite | boolean | Filter favorite jobs |
| is_perfect_fit | boolean | Filter perfect fit jobs |
| is_ai_forward | boolean | Filter AI-forward companies |
| min_priority | int | Minimum priority score (0-100) |
| min_salary | int | Minimum salary filter |
| max_salary | int | Maximum salary filter |
| max_age_days | int | Maximum posting age in days |
| company | string | Filter by company name (partial match) |
| search | string | Search title, company, description |
| sort_by | string | updated_at, created_at, priority, salary, title, company |
| sort_order | string | asc, desc |
| page | int | Page number (default 1) |
| page_size | int | Results per page (default 20, max 100) |

## Example Queries

### By Status
```bash
curl -s "http://localhost:8000/api/jobs?status=saved" | jq '.items'
curl -s "http://localhost:8000/api/jobs?status=applied" | jq '.items'
```

### By Role
```bash
curl -s "http://localhost:8000/api/jobs?target_role=vp" | jq '.items'
curl -s "http://localhost:8000/api/jobs?target_role=cto" | jq '.items'
```

### By Flags
```bash
curl -s "http://localhost:8000/api/jobs?is_easy_apply=true" | jq '.items'
curl -s "http://localhost:8000/api/jobs?is_ai_forward=true" | jq '.items'
curl -s "http://localhost:8000/api/jobs?is_favorite=true" | jq '.items'
curl -s "http://localhost:8000/api/jobs?is_perfect_fit=true" | jq '.items'
```

### By Salary
```bash
curl -s "http://localhost:8000/api/jobs?min_salary=300000" | jq '.items'
curl -s "http://localhost:8000/api/jobs?min_salary=350000&max_salary=500000" | jq '.items'
```

### By Priority
```bash
curl -s "http://localhost:8000/api/jobs?min_priority=80" | jq '.items'
```

### By Posting Age
```bash
curl -s "http://localhost:8000/api/jobs?max_age_days=7" | jq '.items'
```

### Combined Filters
```bash
# High-priority VP roles that are AI-forward and Easy Apply
curl -s "http://localhost:8000/api/jobs?target_role=vp&is_ai_forward=true&is_easy_apply=true&min_priority=70" | jq '.items'

# Remote jobs ready to apply
curl -s "http://localhost:8000/api/jobs?work_location_type=remote&status=ready_to_apply" | jq '.items'
```

### Sorting
```bash
# By priority (highest first)
curl -s "http://localhost:8000/api/jobs?sort_by=priority&sort_order=desc" | jq '.items'

# By salary (highest first)
curl -s "http://localhost:8000/api/jobs?sort_by=salary&sort_order=desc" | jq '.items'

# Most recently updated
curl -s "http://localhost:8000/api/jobs?sort_by=updated_at&sort_order=desc" | jq '.items'
```

### Search
```bash
curl -s "http://localhost:8000/api/jobs?search=AI%20startup" | jq '.items'
```

## Arguments

`/query-jobs` - List all jobs
`/query-jobs vp` - Query VP roles
`/query-jobs easy-apply` - Query Easy Apply jobs
`/query-jobs ai-forward` - Query AI-forward companies
`/query-jobs favorites` - Query favorite jobs
