# View Job Details

View complete details for a specific job.

## Instructions

Get all information about a job including contacts, status, and analysis.

## API Endpoint

GET `http://localhost:8000/api/jobs/{job_id}`

## Usage

```bash
curl -s "http://localhost:8000/api/jobs/{job_id}" | jq
```

## Key Fields

```bash
curl -s "http://localhost:8000/api/jobs/{job_id}" | jq '{
  title, company, location, status,
  salary_min, salary_max,
  target_role, priority,
  is_easy_apply, is_ai_forward, is_favorite, is_perfect_fit,
  work_location_type, employment_type,
  posted_at, applied_at,
  contact_count
}'
```

## View with Description

```bash
curl -s "http://localhost:8000/api/jobs/{job_id}" | jq '{title, company, description_raw}'
```

## Arguments

`/view-job {job_id}` - View complete job details
