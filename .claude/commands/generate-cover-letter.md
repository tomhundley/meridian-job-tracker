# Generate Cover Letter

Generate a personalized cover letter for a job.

## Instructions

Generate an AI-powered cover letter tailored to the job description and target role.

## API Endpoint

POST `http://localhost:8000/api/jobs/{job_id}/cover-letter`

## Usage

```bash
curl -s -X POST "http://localhost:8000/api/jobs/{job_id}/cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "target_role": "vp"
  }' | jq
```

## With Custom Instructions

```bash
curl -s -X POST "http://localhost:8000/api/jobs/{job_id}/cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "target_role": "cto",
    "custom_instructions": "Emphasize AI/ML experience and startup scaling"
  }' | jq
```

## Target Roles

- `cto` - Chief Technology Officer
- `vp` - VP of Engineering
- `director` - Director of Engineering
- `architect` - Principal/Staff Architect
- `developer` - Senior Developer

## List Cover Letters for Job

```bash
curl -s "http://localhost:8000/api/jobs/{job_id}/cover-letters" | jq
```

## Response Fields

- `id` - Cover letter UUID
- `content` - Generated cover letter text
- `target_role` - Role used for generation
- `version` - Version number (increments each generation)
- `is_current` - Whether this is the current/latest version
- `model_used` - AI model used for generation

## Arguments

`/generate-cover-letter {job_id} {role}` - Generate for a specific job and role
