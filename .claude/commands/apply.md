# LinkedIn Easy Apply

Start LinkedIn Easy Apply automation for a job.

## Instructions

Automate the LinkedIn Easy Apply process using browser automation.

## CLI Command

```bash
cd backend && python -m src.cli apply {job_id} --dry-run
```

## Options

- `--dry-run` - Preview without submitting (default: true)
- `--no-dry-run` - Actually submit the application

## Prerequisites

1. Job must have a LinkedIn URL
2. LinkedIn must be logged in via browser automation
3. Job must be an Easy Apply job

## Workflow

1. Opens the job URL in browser
2. Clicks Easy Apply button
3. Fills in application fields
4. Reviews before submission
5. Submits (if not dry-run)

## Check if Job is Easy Apply

```bash
curl -s "http://localhost:8000/api/jobs/{job_id}" | jq '.is_easy_apply'
```

## Filter Easy Apply Jobs

```bash
curl -s "http://localhost:8000/api/jobs?is_easy_apply=true" | jq '.items[] | {title, company, url}'
```

## Arguments

`/apply {job_id}` - Start Easy Apply for a job (dry-run mode)
