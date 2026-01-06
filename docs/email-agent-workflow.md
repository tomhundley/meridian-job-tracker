# Email Agent Workflow

1. Agent receives email from recruiter.
2. `POST /api/v1/emails` with parsed email content.
3. System attempts to match to existing job (by company/title).
4. If matched, link email to job.
5. Agent can update job status based on email content.
6. Webhook fires to notify other systems.
