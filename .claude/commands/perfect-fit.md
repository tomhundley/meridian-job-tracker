# Mark Job as Perfect Fit

Toggle the perfect fit flag on a job.

## Instructions

Mark jobs that are an ideal match as "perfect fit" for prioritization.

## API Endpoint

PATCH `http://localhost:8000/api/v1/jobs/{job_id}`

## Usage

Mark as perfect fit:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_perfect_fit": true}' | jq '.title, .company, .is_perfect_fit'
```

Remove perfect fit:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_perfect_fit": false}' | jq
```

## Filter Perfect Fit Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs?is_perfect_fit=true" | jq '.items[] | {title, company, priority}'
```

## Combined Filters

Find AI-forward perfect fits:
```bash
curl -s "http://localhost:8000/api/v1/jobs?is_perfect_fit=true&is_ai_forward=true" | jq '.items'
```

## Arguments

`/perfect-fit {job_id}` - Toggle perfect fit status on a job
