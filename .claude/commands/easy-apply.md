# Filter Easy Apply Jobs

Find and manage LinkedIn Easy Apply jobs.

## Instructions

Easy Apply jobs can be applied to directly through LinkedIn with minimal effort.

## Filter Easy Apply Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs?is_easy_apply=true" | jq '.items[] | {title, company, url, status}'
```

## Easy Apply + Other Filters

VP roles with Easy Apply:
```bash
curl -s "http://localhost:8000/api/v1/jobs?is_easy_apply=true&target_role=vp" | jq '.items'
```

AI-forward Easy Apply jobs:
```bash
curl -s "http://localhost:8000/api/v1/jobs?is_easy_apply=true&is_ai_forward=true" | jq '.items'
```

Ready to apply Easy Apply jobs:
```bash
curl -s "http://localhost:8000/api/v1/jobs?is_easy_apply=true&status=ready_to_apply" | jq '.items'
```

## Mark Job as Easy Apply

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_easy_apply": true}' | jq
```

## Count Easy Apply Jobs

```bash
curl -s "http://localhost:8000/api/v1/discovery/stats" | jq '.easy_apply_jobs'
```

## Start Easy Apply Automation

Use `/apply {job_id}` to start the Easy Apply automation workflow.

## Arguments

`/easy-apply` - List all Easy Apply jobs
`/easy-apply {job_id}` - Mark a job as Easy Apply
