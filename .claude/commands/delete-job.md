# Delete Job

Soft delete a job from the tracker.

## Instructions

Remove a job from active tracking (soft delete - can be recovered).

## API Endpoint

DELETE `http://localhost:8000/api/jobs/{job_id}`

## Usage

```bash
curl -s -X DELETE "http://localhost:8000/api/jobs/{job_id}"
```

## Notes

- Jobs are soft-deleted (marked with deleted_at timestamp)
- Deleted jobs won't appear in normal queries
- Use `status: archived` if you want to keep the job but hide it from active lists

## Alternative: Archive Instead

If you want to keep the job record but remove from active tracking:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "archived"}' | jq
```

## Arguments

`/delete-job {job_id}` - Delete a job from the tracker
