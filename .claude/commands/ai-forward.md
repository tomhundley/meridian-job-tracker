# Mark Job as AI-Forward

Toggle the AI-forward flag on a job.

## Instructions

Mark jobs at AI-forward companies or for AI-focused roles.

## API Endpoint

PATCH `http://localhost:8000/api/jobs/{job_id}`

## Usage

Mark as AI-forward:
```bash
curl -s -X PATCH "http://localhost:8000/api/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_ai_forward": true}' | jq '.title, .company, .is_ai_forward'
```

## Auto-Detection

Jobs are automatically analyzed for AI-forward status during ingestion.
Use `/analyze-job` to re-analyze:

```bash
curl -s -X POST "http://localhost:8000/api/jobs/{job_id}/analyze?apply_suggestions=true" | jq '.is_ai_forward, .ai_confidence'
```

## Filter AI-Forward Jobs

```bash
curl -s "http://localhost:8000/api/jobs?is_ai_forward=true" | jq '.items[] | {title, company, priority}'
```

## AI-Forward Detection Keywords

The system detects AI-forward companies based on:
- AI/ML technologies: TensorFlow, PyTorch, LangChain, OpenAI, etc.
- Culture indicators: "AI-first", "AI-native", "building AI products"
- Job requirements: ML engineering, prompt engineering, etc.

## Arguments

`/ai-forward {job_id}` - Toggle AI-forward status on a job
