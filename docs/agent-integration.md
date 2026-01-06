# Agent Integration Guide

## Register as an Agent
Use the admin API key to create an agent with scoped permissions.

```bash
curl -X POST http://localhost:8005/api/v1/agents \
  -H "X-API-Key: admin-key" \
  -H "Content-Type: application/json" \
  -d '{"name":"email-processor","permissions":["jobs:read","jobs:update_status","emails:write"]}'
```

The response includes the agent `api_key`. Store it securely.

## Recommended Workflows

### Email Processing → Job Update
1. Agent receives inbound recruiter email.
2. `POST /emails` to store the email.
3. Match to a job (company/title).
4. `PATCH /jobs/{id}/status` to update status.
5. (Optional) Register webhook to notify other agents.

### Job Discovery → Ingest → Follow-up
1. Call `POST /jobs/ingest` for each discovered posting.
2. If needed, call `PATCH /jobs/{id}/status` to move to `ready_to_apply`.
3. Generate cover letter via `POST /jobs/{id}/cover-letter`.

## Idempotency Keys
For retriable requests, include `Idempotency-Key` and retry safely. The API deduplicates jobs by `job_board` + `job_board_id` when available, returning `409` on duplicates. Keep your own retry log to avoid replaying non-idempotent calls.

## Batch Processing Patterns
- Use `POST /jobs/bulk` to ingest many job URLs at once.
- Use `PATCH /jobs/bulk/status` to update many jobs in one call.
- Keep batches small (25-100) to avoid timeouts and rate limits.

## Rate Limits
Default limit is 100 requests/minute. If you need higher limits for automation, request a dedicated agent key or adjust server configuration.
