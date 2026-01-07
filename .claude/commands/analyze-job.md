# Analyze Job Fit

Analyze a job for AI-forward status, fit score, and role suggestions.

## MANDATORY: Always Apply Suggestions

**ALWAYS use `apply_suggestions=true` when analyzing jobs.** This is not optional.

```bash
# CORRECT - always use this
curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze?apply_suggestions=true" | jq

# WRONG - never do this
curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze" | jq
```

## PREREQUISITE: Complete Description Required

**Analysis requires `description_raw` > 500 characters to generate meaningful results.**

Before running analysis, verify description length:
```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{title, company, desc_len: (.description_raw | length)}'
```

If `desc_len < 500`: Job has incomplete data. Use browser automation to extract full description first. See `/add-job` or `/edit-job` skills.

## What Analysis Does

With `apply_suggestions=true`, analysis updates the job with:

| Field | Description |
|-------|-------------|
| `is_ai_forward` | Whether this is an AI-forward company/role |
| `ai_confidence` | Confidence score (0-1) for AI-forward detection |
| `priority` | Fit score (0-100) based on skills match |
| `target_role` | Recommended target role (CTO, VP, Director, etc.) |
| `is_location_compatible` | Whether location is compatible (GA-based) |
| `notes` | Multiple typed notes with coaching insights |

### RAG-Enhanced Coaching

RAG is enabled by default. The system matches job requirements against 260+ career documents from Sparkles to generate:

| Note Type | Content |
|-----------|---------|
| `ai_analysis_summary` | Overall recommendation with score |
| `strengths` | Key strengths for this role |
| `watch_outs` | Red flags or concerns |
| `talking_points` | Interview preparation points |
| `study_recommendations` | Skills to brush up on |
| `rag_evidence` | Evidence from career documents |

## API Endpoint

POST `http://localhost:8000/api/v1/jobs/{job_id}/analyze?apply_suggestions=true`

## Workflow for Incomplete Jobs

If description is too short:

1. Get job source URL:
   ```bash
   curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{source_url, source_id}'
   ```

2. Use browser to navigate to job page and extract full description

3. Update job with full description:
   ```bash
   cat /tmp/update.json | curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}" \
     -H "Content-Type: application/json" -d @-
   ```

4. Run analysis:
   ```bash
   curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze?apply_suggestions=true" | jq
   ```

## Arguments

`/analyze-job {job_id}` - Analyze a specific job by ID

## Response Fields

```json
{
  "is_ai_forward": true,
  "ai_confidence": 0.75,
  "suggested_priority": 85,
  "suggested_role": "vp",
  "technologies_matched": ["Python", "AWS", "Kubernetes"],
  "technologies_missing": ["Rust"],
  "years_experience_required": 10,
  "seniority_level": "VP",
  "analysis_notes": "Strong match for VP role. AI-forward company with ML focus."
}
```

## Common Issues

### Low Confidence Results

If analysis returns `ai_confidence: 0.1` and `suggested_priority < 50`:
- Check `description_raw` length - likely incomplete
- Use browser automation to get full description
- Re-run analysis after updating

### Analysis Appears Wrong

The analysis depends on:
1. Complete job description (2000+ chars ideal)
2. Resume data at `RESUME_DATA_PATH` environment variable
3. Skills matching algorithm

If results seem off, verify description completeness first.
