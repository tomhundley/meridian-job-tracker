# Meridian Job Tracker API Reference

Base URL: `/api/v1`

## Authentication
- Use `X-API-Key` header on all requests.
- Admin key is configured via `settings.api_key`.
- Agent keys are created via `POST /agents` and have scoped permissions.

Example:
```bash
curl -H "X-API-Key: your-key" http://localhost:8005/api/v1/jobs
```

## Rate Limits
- Default: 100 requests/minute per client.
- Exceeding limits returns `429 Too Many Requests`.

## Error Codes
- `400` invalid input or parsing failed.
- `403` invalid API key or missing permissions.
- `404` resource not found.
- `409` conflict (duplicate job URL/ID).
- `429` rate limit exceeded.
- `500` internal server error.

## Permissions (Suggested)
- `jobs:read`, `jobs:write`, `jobs:ingest`, `jobs:update_status`, `jobs:delete`
- `cover_letters:read`, `cover_letters:write`, `cover_letters:approve`, `cover_letters:delete`
- `emails:read`, `emails:write`, `emails:delete`
- `webhooks:read`, `webhooks:write`
- `agents:write`

## Endpoints

### Jobs
`GET /jobs` (permission: `jobs:read`)
```bash
curl -H "X-API-Key: key" "http://localhost:8005/api/v1/jobs?page=1&page_size=20"
```
Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Engineer",
      "company": "Acme",
      "location": "Remote",
      "status": "saved",
      "priority": 50,
      "created_at": "2025-01-05T12:00:00Z",
      "updated_at": "2025-01-05T12:00:00Z",
      "status_changed_at": "2025-01-05T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

`POST /jobs` (permission: `jobs:write`)
```json
{
  "title": "Engineer",
  "company": "Acme",
  "location": "Remote",
  "priority": 60
}
```

`GET /jobs/{job_id}` (permission: `jobs:read`)

`PATCH /jobs/{job_id}` (permission: `jobs:write`)
```json
{
  "notes": "Referred by Alex"
}
```

`PATCH /jobs/{job_id}/status` (permission: `jobs:update_status`)
```json
{
  "status": "applied"
}
```

`DELETE /jobs/{job_id}` (permission: `jobs:delete`)

`POST /jobs/ingest` (permission: `jobs:ingest`)
```json
{
  "url": "https://linkedin.com/jobs/view/123456",
  "source": "linkedin",
  "notes": "Referred by John"
}
```
Response:
```json
{
  "id": "uuid",
  "title": "Staff Engineer",
  "company": "Acme",
  "location": "Remote",
  "status": "saved"
}
```

`POST /jobs/bulk` (permission: `jobs:ingest`)
```json
{
  "jobs": [
    { "url": "https://linkedin.com/jobs/view/1", "source": "linkedin" },
    { "url": "https://indeed.com/viewjob?jk=2", "source": "indeed" }
  ]
}
```
Response:
```json
{
  "created": [{ "id": "uuid", "title": "Engineer", "company": "Acme" }],
  "failed": [{ "url": "https://indeed.com/viewjob?jk=2", "error": "Job already exists" }]
}
```

`PATCH /jobs/bulk/status` (permission: `jobs:update_status`)
```json
{
  "job_ids": ["uuid1", "uuid2"],
  "status": "applied"
}
```
Response:
```json
{
  "updated": [{ "id": "uuid1", "status": "applied" }],
  "missing": []
}
```

### Description Management

`GET /jobs/descriptions/stats` (permission: `jobs:read`)

Returns statistics about job description completeness:
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

`GET /jobs/descriptions/incomplete` (permission: `jobs:read`)

List jobs needing full descriptions (< 500 chars):
```bash
curl "http://localhost:8005/api/v1/jobs/descriptions/incomplete?limit=10"
```
Response:
```json
[
  {
    "id": "uuid",
    "title": "VP Engineering",
    "company": "Acme",
    "url": "https://linkedin.com/jobs/view/123",
    "job_board": "linkedin",
    "job_board_id": "123",
    "description_length": 150,
    "needs_fetch": true
  }
]
```

### Job Analysis

`POST /jobs/{job_id}/analyze` (permission: `jobs:read`)

**IMPORTANT: Always use `apply_suggestions=true`**

```bash
# Correct usage
curl -X POST "http://localhost:8005/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

Parameters:
- `apply_suggestions` (bool): Apply results to job record. **Always set to true.**
- `use_ai` (bool, default=true): Use Claude for semantic analysis
- `use_rag` (bool, default=true): Use Sparkles RAG for coaching insights

Response:
```json
{
  "is_ai_forward": true,
  "ai_confidence": 0.85,
  "suggested_priority": 78,
  "suggested_role": "vp",
  "is_location_compatible": true,
  "location_notes": null,
  "technologies_matched": ["Python", "AWS", "Kubernetes"],
  "technologies_missing": ["Rust"],
  "analysis_notes": "Strong match for VP role..."
}
```

When `apply_suggestions=true`, the job record is updated with:
- `priority` - Fit score (0-100)
- `is_ai_forward` - AI-forward company detection
- `target_role` - Suggested role
- `is_location_compatible` - Location validation
- `notes` - Multiple typed coaching notes (see Notes section)

### Notes

`GET /jobs/{job_id}/notes` (permission: `jobs:read`)

List notes with optional filters:
```bash
# All notes
curl "http://localhost:8005/api/v1/jobs/{id}/notes"

# Filter by type
curl "http://localhost:8005/api/v1/jobs/{id}/notes?note_type=talking_points"

# Filter by source
curl "http://localhost:8005/api/v1/jobs/{id}/notes?source=agent"
```

Response:
```json
[
  {
    "text": "**APPLY** (78/100)\n\nStrong fit...",
    "timestamp": "2025-01-07T04:00:00Z",
    "source": "agent",
    "note_type": "ai_analysis_summary",
    "metadata": {
      "priority_score": 78,
      "recommendation": "APPLY"
    }
  }
]
```

Note types:
- `general` - User-created notes
- `ai_analysis_summary` - Overall recommendation with score
- `strengths` - Key strengths for the role
- `watch_outs` - Red flags or concerns
- `talking_points` - Interview preparation points
- `study_recommendations` - Skills to brush up on
- `coaching_notes` - What to emphasize
- `rag_evidence` - Evidence from career documents

`POST /jobs/{job_id}/notes` (permission: `jobs:write`)
```json
{
  "text": "Remember to mention MDSi experience",
  "source": "user",
  "note_type": "talking_points",
  "metadata": null
}
```

### Cover Letters

`POST /jobs/{job_id}/cover-letter` (permission: `cover_letters:write`)
```json
{
  "target_role": "cto",
  "custom_instructions": "Keep it concise"
}
```

`GET /jobs/{job_id}/cover-letters` (permission: `cover_letters:read`)

### Cover Letters
`GET /cover-letters/{cover_letter_id}` (permission: `cover_letters:read`)

`PATCH /cover-letters/{cover_letter_id}/approve` (permission: `cover_letters:approve`)
```json
{ "is_approved": true }
```

`DELETE /cover-letters/{cover_letter_id}` (permission: `cover_letters:delete`)

### Emails
`GET /emails` (permission: `emails:read`)

`POST /emails` (permission: `emails:write`)
```json
{
  "from_email": "recruiter@example.com",
  "to_email": "candidate@example.com",
  "subject": "Interview",
  "body": "Let's schedule time.",
  "email_timestamp": "2025-01-05T12:00:00Z",
  "is_inbound": true
}
```

`GET /emails/{email_id}` (permission: `emails:read`)

`PATCH /emails/{email_id}/link/{job_id}` (permission: `emails:write`)

`DELETE /emails/{email_id}` (permission: `emails:delete`)

### Webhooks
`GET /webhooks` (permission: `webhooks:read`)

`POST /webhooks` (permission: `webhooks:write`)
```json
{
  "url": "https://agent.example.com/callback",
  "events": ["job.status_changed", "cover_letter.generated"],
  "secret": "webhook-secret-for-signing"
}
```

### Agents
`POST /agents` (permission: `agents:write`)
```json
{
  "name": "email-processor",
  "permissions": ["jobs:read", "jobs:update_status", "emails:write"]
}
```
Response:
```json
{
  "id": "uuid",
  "name": "email-processor",
  "api_key": "agent_xxx",
  "permissions": ["jobs:read", "jobs:update_status", "emails:write"]
}
```

### Health
`GET /health`

`GET /health/ready`

## Webhook Event Payloads
Example payload:
```json
{
  "id": "event-uuid",
  "event": "job.status_changed",
  "created_at": "2025-01-05T12:00:00Z",
  "data": {
    "job_id": "uuid",
    "status": "applied"
  }
}
```

When webhook delivery is implemented, events will be signed with:
```
X-Webhook-Signature: sha256=<hex hmac>
```

## SDK Examples

Python:
```python
import requests

resp = requests.post(
    "http://localhost:8005/api/v1/jobs",
    headers={"X-API-Key": "your-key"},
    json={"title": "Engineer", "company": "Acme"},
)
print(resp.json())
```

TypeScript:
```ts
const resp = await fetch("http://localhost:8005/api/v1/jobs", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "your-key",
  },
  body: JSON.stringify({ title: "Engineer", company: "Acme" }),
});
const data = await resp.json();
```
