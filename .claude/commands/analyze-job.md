# Analyze Job Fit

Analyze a job for AI-forward status, fit score, and role suggestions.

## Instructions

Analyze a job in the database to determine:
- **is_ai_forward**: Whether this is an AI-forward company/role
- **ai_confidence**: Confidence score (0-1) for AI-forward detection
- **suggested_priority**: Fit score (0-100) based on skills match
- **suggested_role**: Recommended target role (CTO, VP, Director, etc.)
- **technologies_matched/missing**: Tech requirements vs resume skills

## API Endpoint

POST `http://localhost:8000/api/jobs/{job_id}/analyze`

## Usage

Analyze a job (read-only):
```bash
curl -s -X POST "http://localhost:8000/api/jobs/{job_id}/analyze" | jq
```

Analyze and apply suggestions to job:
```bash
curl -s -X POST "http://localhost:8000/api/jobs/{job_id}/analyze?apply_suggestions=true" | jq
```

## Arguments

`/analyze-job {job_id}` - Analyze a specific job by ID

## Response Fields

- `is_ai_forward` - Boolean indicating AI-forward company
- `ai_confidence` - 0-1 confidence score
- `suggested_priority` - 0-100 fit score
- `suggested_role` - cto, vp, director, architect, developer
- `technologies_matched` - Skills you have that match
- `technologies_missing` - Required skills you're missing
- `years_experience_required` - Years of experience needed
- `seniority_level` - Detected seniority level
- `analysis_notes` - Detailed analysis notes
