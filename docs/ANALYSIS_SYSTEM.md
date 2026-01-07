# AI Job Analysis System

Enhanced AI-powered job analysis with Sparkles RAG integration for personalized coaching and preparation guidance.

## Overview

The analysis system provides:
1. **Claude-powered semantic analysis** - Comprehensive job fit assessment
2. **Sparkles RAG integration** - Match job requirements against 260+ career documents
3. **Multiple typed notes** - Structured coaching advice, talking points, study recommendations
4. **Description fetcher** - Identify and track jobs needing full descriptions

## Architecture

```
                    Job Analysis Request
                            |
                            v
                  +-------------------+
                  | Check description |
                  |   length < 500?   |
                  +--------+----------+
                           |
               Yes         |         No
               v           |          |
    +------------------+   |          |
    | Flag for fetch   |   |          |
    | (Manual browser  |--+          |
    |  automation)     |              |
    +------------------+              |
                                      v
                          +---------------------+
                          | Extract Requirements |
                          | (JD Analyzer)        |
                          +----------+----------+
                                     |
                                     v
                          +---------------------+
                          | SparklesClient      |
                          | matchJDRequirements |
                          +----------+----------+
                                     |
                                     v
                          +---------------------+
                          | Build RAG Context   |
                          | for Claude          |
                          +----------+----------+
                                     |
                                     v
                          +---------------------+
                          | Claude Analysis +   |
                          | Coaching Insights   |
                          +----------+----------+
                                     |
                                     v
                          +---------------------+
                          | Generate 5-10 Typed |
                          | Notes               |
                          +---------------------+
```

## Components

### 1. AI Analysis Service

**File:** `backend/src/services/ai_analysis_service.py`

The core analysis service using Claude for semantic job analysis.

```python
from src.services import ai_analysis_service, analyze_job_with_ai

# Basic analysis
analysis, ai_result = analyze_job_with_ai(job, use_ai=True)

# Generate typed notes from results
notes = generate_typed_notes(ai_result, coaching_insights, requirement_matches)
```

**Key Features:**
- Role classification (CTO, VP, Director, Architect, Developer)
- AI-forward company detection (building_ai, using_ai, ai_curious, traditional)
- Skills alignment analysis
- Location compatibility checking
- Priority scoring (0-100)

### 2. Sparkles RAG Client

**File:** `backend/src/services/sparkles_client.py`

Connects to Sparkles Supabase database for semantic search over career documents.

```python
from src.services import sparkles_client

# Check if configured
if sparkles_client.is_configured:
    # Match job requirements against resume
    matches = await sparkles_client.match_jd_requirements(
        requirements=["Python experience", "Team leadership"],
        threshold=0.40,
        limit_per_req=3,
    )

    # General semantic search
    results = await sparkles_client.search_resume_context(
        query="enterprise integration experience",
        categories=["master-documents", "career-analysis"],
        limit=5,
    )
```

**Configuration:**

Set these environment variables:
```bash
SPARKLES_SUPABASE_URL=https://your-project.supabase.co
SPARKLES_SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=your-openai-key  # For embeddings
```

**RAG Settings (in settings.py):**
```python
rag_similarity_threshold: float = 0.5
rag_max_results: int = 8
rag_timeout_seconds: int = 5
```

### 3. Typed Notes System

**File:** `backend/src/schemas/job_note.py`

Notes are now categorized by type for better organization:

| Type | Purpose | Example |
|------|---------|---------|
| `general` | Default type | Any user/agent note |
| `ai_analysis_summary` | Overall fit assessment | "APPLY (78/100) - Strong fit..." |
| `coaching_notes` | What to emphasize | "Lead with MDSi CTO experience" |
| `talking_points` | Interview prep | "Your Comcast integration scaled to..." |
| `study_recommendations` | Gaps to fill | "Review Kubernetes orchestration" |
| `strengths` | What to highlight | "3M+ lines AI-generated code" |
| `watch_outs` | Red flags | "50% travel may be excessive" |
| `rag_evidence` | Supporting docs | "From MDSi case study: ..." |

**Note Structure:**
```python
class JobNoteEntry(BaseModel):
    text: str
    timestamp: datetime
    source: NoteSource  # "user" | "agent"
    note_type: NoteType  # One of the types above
    metadata: dict | None  # Optional structured data
```

### 4. Description Fetcher

**File:** `backend/src/services/description_fetcher.py`

Identifies jobs with incomplete descriptions and tracks fetch status.

```python
from src.services import description_fetcher

# Get statistics
stats = await description_fetcher.get_stats(db)
# Returns: {total_jobs, complete_descriptions, incomplete_descriptions, needs_fetch, ...}

# Get jobs needing descriptions
incomplete = await description_fetcher.get_incomplete_jobs(db, limit=20)
for job in incomplete:
    url = description_fetcher.build_fetch_url(job)
    # Use browser automation to fetch from url
```

**API Endpoints:**

```bash
# Get description statistics
GET /api/v1/jobs/descriptions/stats

# List jobs needing full descriptions
GET /api/v1/jobs/descriptions/incomplete?limit=20
```

## API Usage

### Analyze a Job

```bash
# Basic analysis with AI
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze"

# Analysis with suggestions applied and RAG enabled
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/analyze?apply_suggestions=true&use_rag=true"
```

**Parameters:**
- `apply_suggestions` (bool): Apply priority/role/ai_forward to job record
- `use_ai` (bool, default true): Use Claude for semantic analysis
- `use_rag` (bool, default true): Use Sparkles RAG for coaching insights

### List Job Notes

```bash
# All notes
curl "http://localhost:8000/api/v1/jobs/{job_id}/notes"

# Filter by type
curl "http://localhost:8000/api/v1/jobs/{job_id}/notes?note_type=talking_points"

# Filter by source
curl "http://localhost:8000/api/v1/jobs/{job_id}/notes?source=agent"
```

### Add a Note

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Remember to mention the AI-generated code stats",
    "source": "user",
    "note_type": "talking_points"
  }'
```

## Generated Notes

When analysis runs with `apply_suggestions=true`, the system generates multiple typed notes:

1. **AI Analysis Summary** - Overall recommendation and score
2. **Strengths** - Key strengths identified in the match
3. **Watch-outs** - Concerns or potential issues
4. **Location Issues** (if incompatible) - Location restriction details
5. **RAG Evidence** (if RAG enabled) - JD requirement matches with evidence

If Sparkles RAG is configured and finds matches:
6. **Talking Points** - Specific interview points with evidence
7. **Coaching Notes** - What to emphasize in applications
8. **Study Recommendations** - Skills/topics to brush up on

## Configuration

### Environment Variables

```bash
# Required for AI analysis
ANTHROPIC_API_KEY=your-claude-api-key

# Required for RAG (optional feature)
SPARKLES_SUPABASE_URL=https://your-project.supabase.co
SPARKLES_SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=your-openai-key

# Optional: Customize RAG behavior
RAG_SIMILARITY_THRESHOLD=0.5
RAG_MAX_RESULTS=8
RAG_TIMEOUT_SECONDS=5
```

### Description Thresholds

In `description_fetcher.py`:
- `MIN_DESCRIPTION_LENGTH = 500` - Jobs below this need fetching
- `TARGET_DESCRIPTION_LENGTH = 2000` - Ideal description length

## Workflow for Claude Code Agents

### Adding Jobs with Full Descriptions

1. Use browser automation to navigate to job URL
2. Extract full description from page
3. Create/update job via API with full description
4. Run analysis with `apply_suggestions=true`

```bash
# Step 1-2: Use Chrome DevTools or Playwright MCP to extract

# Step 3: Create job
cat /tmp/job.json | curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" -d @-

# Step 4: Analyze
curl -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

### Batch Processing Incomplete Descriptions

1. Get list of incomplete jobs:
```bash
curl "http://localhost:8000/api/v1/jobs/descriptions/incomplete?limit=10"
```

2. For each job, use browser automation to fetch full description

3. Update job with PATCH:
```bash
cat /tmp/update.json | curl -X PATCH "http://localhost:8000/api/v1/jobs/{id}" \
  -H "Content-Type: application/json" -d @-
```

4. Re-run analysis:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/{id}/analyze?apply_suggestions=true"
```

## Cost & Performance

| Operation | Cost | Latency |
|-----------|------|---------|
| AI Analysis (Claude) | ~$0.03 | 3-5s |
| RAG Search (Sparkles) | Free* | <500ms |
| Embedding (OpenAI) | ~$0.0001 | 200ms |
| Description Fetch | Free | 5-10s |

*Same Supabase instance - no additional API cost

## Troubleshooting

### RAG Not Working

1. Check configuration:
```python
from src.services import sparkles_client
print(sparkles_client.is_configured)  # Should be True
```

2. Verify environment variables are set
3. Check logs for `sparkles_search_error` or `rag_context_failed`

### Incomplete Descriptions

1. Check stats:
```bash
curl "http://localhost:8000/api/v1/jobs/descriptions/stats"
```

2. List incomplete:
```bash
curl "http://localhost:8000/api/v1/jobs/descriptions/incomplete"
```

3. Use browser automation to fetch full descriptions

### Analysis Returns Low Confidence

- Ensure description is > 500 characters
- Check that description contains actual job requirements
- Verify the job URL is accessible and description was fully extracted
