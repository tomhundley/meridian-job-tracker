# Edit Job Details

Update job information like salary, notes, priority, etc.

## Instructions

Modify job fields after creation.

## API Endpoint

PATCH `http://localhost:8000/api/jobs/{job_id}`

## Editable Fields

- `title` - Job title
- `company` - Company name
- `location` - Job location
- `work_location_type` - remote, hybrid, on_site
- `salary_min`, `salary_max` - Salary range
- `salary_currency` - Currency code (USD, EUR, etc.)
- `employment_type` - full_time, contract, etc.
- `target_role` - cto, vp, director, architect, developer
- `priority` - 0-100 fit score
- `notes` - Personal notes
- `tags` - Array of tags
- `is_easy_apply`, `is_favorite`, `is_perfect_fit`, `is_ai_forward` - Boolean flags

## Usage

Update salary:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"salary_min": 350000, "salary_max": 450000}' | jq
```

Update priority and notes:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"priority": 85, "notes": "Great culture fit, talked to former employee"}' | jq
```

Update target role:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"target_role": "vp"}' | jq
```

Set work location type:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"work_location_type": "remote"}' | jq
```

## Arguments

`/edit-job {job_id}` - Edit job details
