# Update Job Status

Update the status of a job in the tracker.

## Instructions

Change a job's status through the application workflow.

## API Endpoint

PATCH `http://localhost:8000/api/v1/jobs/{job_id}/status`

## Job Statuses

- `saved` - Initial state, job saved for review
- `researching` - Researching company/role
- `ready_to_apply` - Ready to submit application
- `applying` - Application in progress
- `applied` - Application submitted
- `interviewing` - In interview process
- `offer` - Received offer
- `rejected` - Rejected by company
- `withdrawn` - Withdrew application
- `archived` - No longer considering

## Usage

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "applied"}' | jq
```

## With Decline Reasons

When marking as rejected or withdrawn:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "company_decline_reasons": ["salary_mismatch", "overqualified"],
    "decline_notes": "They wanted someone more junior"
  }' | jq
```

## Bulk Status Update

Update multiple jobs at once:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/bulk/status" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["uuid1", "uuid2"],
    "status": "archived"
  }' | jq
```

## Arguments

`/update-status {job_id} {status}` - Update status for a job
