# Job Statistics

Get statistics about jobs, descriptions, and application status.

## Quick Commands

```bash
# Description completeness statistics
curl -s "http://localhost:8000/api/v1/jobs/descriptions/stats" | jq

# Discovery statistics (if endpoint exists)
curl -s "http://localhost:8000/api/v1/discovery/stats" | jq
```

## Description Statistics

Shows job description completeness:

```bash
curl -s "http://localhost:8000/api/v1/jobs/descriptions/stats" | jq
```

Response:
```json
{
  "total_jobs": 62,
  "with_descriptions": 60,
  "complete_descriptions": 43,
  "incomplete_descriptions": 17,
  "missing_descriptions": 2,
  "needs_fetch": 19,
  "min_length_threshold": 500,
  "target_length": 2000
}
```

| Field | Description |
|-------|-------------|
| `total_jobs` | Total jobs in tracker |
| `complete_descriptions` | Jobs with 2000+ char descriptions |
| `incomplete_descriptions` | Jobs with < 500 char descriptions |
| `needs_fetch` | Jobs needing browser automation to fetch full description |

## List Incomplete Jobs

```bash
curl -s "http://localhost:8000/api/v1/jobs/descriptions/incomplete?limit=20" | jq
```

## Job Count by Status

```bash
curl -s "http://localhost:8000/api/v1/jobs" | jq '{
  total: .total,
  by_status: (.items | group_by(.status) | map({(.[0].status): length}) | add)
}'
```

## AI Analysis Statistics

```bash
curl -s "http://localhost:8000/api/v1/jobs?limit=100" | jq '{
  total: .total,
  analyzed: [.items[] | select(.priority != null)] | length,
  ai_forward: [.items[] | select(.is_ai_forward == true)] | length,
  location_compatible: [.items[] | select(.is_location_compatible == true)] | length,
  avg_priority: ([.items[] | select(.priority != null) | .priority] | add / length)
}'
```

## Arguments

`/stats` - Show job statistics including description completeness
