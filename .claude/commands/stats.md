# Job Discovery Statistics

Get statistics about discovered jobs and application status.

## Instructions

View aggregate statistics about your job search progress.

## API Endpoint

GET `http://localhost:8000/api/discovery/stats`

## Usage

```bash
curl -s "http://localhost:8000/api/discovery/stats" | jq
```

## Response Fields

- `total_jobs` - Total jobs in tracker
- `by_status` - Count by each status
  - saved, researching, ready_to_apply, applying
  - applied, interviewing, offer
  - rejected, withdrawn, archived
- `linkedin_jobs` - Jobs from LinkedIn
- `applied_jobs` - Total applications submitted
- `easy_apply_jobs` - Jobs with Easy Apply
- `application_rate` - Percentage of jobs applied to

## Example Response

```json
{
  "total_jobs": 45,
  "by_status": {
    "saved": 20,
    "researching": 8,
    "applied": 12,
    "interviewing": 3,
    "rejected": 2
  },
  "linkedin_jobs": 40,
  "applied_jobs": 15,
  "easy_apply_jobs": 25,
  "application_rate": "37.5%"
}
```

## Arguments

`/stats` - Show job discovery statistics
