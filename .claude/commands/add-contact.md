# Add Job Contact

Add a contact (recruiter, hiring manager, etc.) to a job.

## Instructions

Track hiring team members, recruiters, and other contacts for each job.

## API Endpoint

POST `http://localhost:8000/api/v1/jobs/{job_id}/contacts`

## Usage

```bash
curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "title": "VP of Engineering",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "email": "jane@company.com",
    "contact_type": "hiring_manager",
    "is_job_poster": true,
    "notes": "Met at conference last year"
  }' | jq
```

## Contact Types

- `recruiter` - External or internal recruiter
- `hiring_manager` - The person you'd report to
- `hr` - HR representative
- `team_member` - Potential colleague
- `executive` - C-level or VP
- `other` - Other contact type

## List Contacts for Job

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}/contacts" | jq
```

## Update Contact

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}/contacts/{contact_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Had initial call, very responsive"
  }' | jq
```

## Delete Contact

```bash
curl -s -X DELETE "http://localhost:8000/api/v1/jobs/{job_id}/contacts/{contact_id}"
```

## Arguments

`/add-contact {job_id}` - Add a contact to a job
