# LinkedIn MCP Integration

The `meridian-linkedIn` MCP server can integrate with the Meridian Job Tracker API to automate job creation and application flows.

## Capabilities
- Create jobs from LinkedIn job view URLs.
- Trigger LinkedIn Easy Apply automation.
- Update job status after application.

## Suggested Flow
1. MCP server detects a LinkedIn job URL.
2. `POST /api/v1/jobs/ingest` with `{ "url": "...", "source": "linkedin" }`.
3. If the job is ready, call the CLI `meridian apply <job_id>` or invoke the LinkedIn automation service.
4. Update status using `PATCH /api/v1/jobs/{job_id}/status` with `applied` or `interviewing`.

## Required Permissions
Create an agent with:
- `jobs:ingest`
- `jobs:update_status`
- `jobs:read`

## Example
```bash
curl -X POST http://localhost:8005/api/v1/jobs/ingest \
  -H "X-API-Key: agent-key" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://linkedin.com/jobs/view/123","source":"linkedin"}'
```
