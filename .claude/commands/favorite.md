# Mark Job as Favorite

Toggle the favorite flag on a job.

## Instructions

Mark jobs you're particularly interested in as favorites for easy filtering.

## API Endpoint

PATCH `http://localhost:8000/api/v1/jobs/{job_id}`

## Usage

Mark as favorite:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_favorite": true}' | jq '.title, .company, .is_favorite'
```

Remove favorite:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_favorite": false}' | jq
```

## Filter Favorite Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs?is_favorite=true" | jq '.items[] | {title, company}'
```

## Arguments

`/favorite {job_id}` - Toggle favorite status on a job
