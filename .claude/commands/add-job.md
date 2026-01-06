# Add Job from URL

Ingest a job into the tracker from a LinkedIn or other job board URL.

## Instructions

Use the job ingest API to scrape and add a job from a URL.

## API Endpoint

POST `http://localhost:8000/api/v1/jobs/ingest`

## Usage

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/ingest" \
  -H "Content-Type: application/json" \
  -d '{"url": "$ARGUMENTS"}'
```

## Supported Sources

- LinkedIn: `linkedin.com/jobs/view/*`
- Indeed: `indeed.com/viewjob*`
- Greenhouse: `boards.greenhouse.io/*`
- Lever: `jobs.lever.co/*`
- Workday: `*.myworkdayjobs.com/*`

## What Gets Auto-Extracted

- Title, company, location, description
- Salary range (if available)
- Employment type (full-time, contract, etc.)
- Work location type (remote, hybrid, on-site)
- Posted date
- Easy Apply status (LinkedIn)
- AI-forward analysis
- Priority/fit score
- Target role suggestion

## Example

`/add-job https://www.linkedin.com/jobs/view/123456789`
