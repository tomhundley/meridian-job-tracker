# Job Search Queries Documentation

**Document Created:** January 6, 2026
**Last Updated:** January 6, 2026
**Related:** [Candidate Profile](./candidate-profile-tom-hundley.md) | [Job Search Workflow](./job-search-workflow.md)

---

## Overview

This document defines the recommended queries for the Meridian Job Tracker system, optimized for Tom Hundley's executive job search ($225K-$350K, CTO/VP level, AI-focused).

---

## API Endpoints

### Base URL
```
/api/v1/jobs
```

### Available Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | enum | Job status in pipeline |
| `target_role` | enum | CTO, VP, Director, Architect, Developer |
| `company` | string | Company name (partial match) |
| `search` | string | Full-text search on title, company, description |
| `page` | int | Pagination (default: 1) |
| `page_size` | int | Results per page (default: 20, max: 100) |

---

## Core Queries

### 1. Pipeline Overview (Funnel View)

**Purpose:** See distribution of jobs across pipeline stages

**API Call:**
```
GET /api/v1/jobs?page_size=100
```

**SQL Equivalent:**
```sql
SELECT
    status,
    COUNT(*) as count,
    ROUND(AVG(priority), 1) as avg_priority
FROM jobs
WHERE deleted_at IS NULL
GROUP BY status
ORDER BY CASE status
    WHEN 'saved' THEN 1
    WHEN 'researching' THEN 2
    WHEN 'ready_to_apply' THEN 3
    WHEN 'applying' THEN 4
    WHEN 'applied' THEN 5
    WHEN 'interviewing' THEN 6
    WHEN 'offer' THEN 7
    WHEN 'rejected' THEN 8
    WHEN 'withdrawn' THEN 9
    WHEN 'archived' THEN 10
END;
```

**Expected Output:**
```
| status          | count | avg_priority |
|-----------------|-------|--------------|
| saved           | 15    | 50.0         |
| researching     | 8     | 65.0         |
| ready_to_apply  | 5     | 75.0         |
| applying        | 3     | 80.0         |
| applied         | 45    | 70.0         |
| interviewing    | 2     | 90.0         |
```

---

### 2. Jobs by Target Role

**Purpose:** Filter jobs matching specific resume variant

**API Call:**
```
GET /api/v1/jobs?target_role=cto&status=saved
GET /api/v1/jobs?target_role=vp&status=saved
GET /api/v1/jobs?target_role=director&status=saved
GET /api/v1/jobs?target_role=architect&status=saved
```

**SQL Equivalent:**
```sql
SELECT * FROM jobs
WHERE target_role = 'cto'  -- or 'vp', 'director', 'architect', 'developer'
  AND status IN ('saved', 'researching', 'ready_to_apply')
  AND deleted_at IS NULL
ORDER BY priority DESC, created_at DESC;
```

**Role Distribution Analysis:**
```sql
SELECT
    target_role,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'applied') as applied,
    COUNT(*) FILTER (WHERE status = 'interviewing') as interviewing
FROM jobs
WHERE deleted_at IS NULL
GROUP BY target_role;
```

---

### 3. High-Priority Jobs (Action Required)

**Purpose:** Surface jobs needing immediate attention

**API Call:**
```
GET /api/v1/jobs?status=ready_to_apply&page_size=50
```

**SQL Equivalent:**
```sql
SELECT * FROM jobs
WHERE status IN ('ready_to_apply', 'applying')
  AND deleted_at IS NULL
ORDER BY
    priority DESC,
    status_changed_at ASC  -- Oldest first (don't let them go stale)
LIMIT 20;
```

---

### 4. Tech Stack Matching

**Purpose:** Find jobs matching Tom's core technologies

**Tom's Primary Stack:**
- Azure, C#, .NET, React, TypeScript, Next.js, Cosmos DB, SQL Server
- AI/ML: OpenAI, RAG, LLMs

**API Call (search parameter):**
```
GET /api/v1/jobs?search=azure
GET /api/v1/jobs?search=react%20typescript
GET /api/v1/jobs?search=openai%20ai
```

**SQL Equivalent:**
```sql
-- High-match jobs (multiple tech keywords)
SELECT
    *,
    (CASE WHEN description_raw ILIKE '%azure%' THEN 1 ELSE 0 END +
     CASE WHEN description_raw ILIKE '%c#%' OR description_raw ILIKE '%.net%' THEN 1 ELSE 0 END +
     CASE WHEN description_raw ILIKE '%react%' THEN 1 ELSE 0 END +
     CASE WHEN description_raw ILIKE '%typescript%' THEN 1 ELSE 0 END +
     CASE WHEN description_raw ILIKE '%ai%' OR description_raw ILIKE '%openai%' THEN 1 ELSE 0 END
    ) as tech_match_score
FROM jobs
WHERE status NOT IN ('rejected', 'withdrawn', 'archived')
  AND deleted_at IS NULL
ORDER BY tech_match_score DESC, priority DESC;
```

---

### 5. Company Research Queue

**Purpose:** Jobs in "researching" status needing company deep-dive

**API Call:**
```
GET /api/v1/jobs?status=researching
```

**SQL Equivalent:**
```sql
SELECT
    j.*,
    EXTRACT(DAY FROM NOW() - j.status_changed_at) as days_in_research
FROM jobs j
WHERE j.status = 'researching'
  AND j.deleted_at IS NULL
ORDER BY j.status_changed_at ASC;  -- Oldest first
```

---

### 6. Application Velocity

**Purpose:** Track application rate and outcomes

**SQL Query:**
```sql
-- Weekly application rate
SELECT
    DATE_TRUNC('week', applied_at) as week,
    COUNT(*) as applications,
    COUNT(*) FILTER (WHERE status = 'interviewing') as interviews,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejections
FROM jobs
WHERE applied_at IS NOT NULL
  AND deleted_at IS NULL
GROUP BY DATE_TRUNC('week', applied_at)
ORDER BY week DESC;
```

**Response Rate Calculation:**
```sql
SELECT
    COUNT(*) as total_applied,
    COUNT(*) FILTER (WHERE status = 'interviewing') as interviews,
    COUNT(*) FILTER (WHERE status IN ('offer', 'interviewing')) as positive_responses,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status IN ('offer', 'interviewing')) /
        NULLIF(COUNT(*), 0),
        1
    ) as response_rate_pct
FROM jobs
WHERE status NOT IN ('saved', 'researching', 'ready_to_apply', 'applying')
  AND deleted_at IS NULL;
```

---

### 7. Decline Analysis

**Purpose:** Understand why opportunities don't work out

**API Call:**
```
GET /api/v1/decline-reasons/user      -- Why Tom passed
GET /api/v1/decline-reasons/company   -- Why they rejected
```

**SQL Equivalent:**
```sql
-- User decline reasons (why Tom withdrew)
SELECT
    unnest(user_decline_reasons) as reason,
    COUNT(*) as count
FROM jobs
WHERE status = 'withdrawn'
  AND user_decline_reasons IS NOT NULL
  AND deleted_at IS NULL
GROUP BY unnest(user_decline_reasons)
ORDER BY count DESC;

-- Company decline reasons
SELECT
    unnest(company_decline_reasons) as reason,
    COUNT(*) as count
FROM jobs
WHERE status = 'rejected'
  AND company_decline_reasons IS NOT NULL
  AND deleted_at IS NULL
GROUP BY unnest(company_decline_reasons)
ORDER BY count DESC;
```

---

### 8. Stale Jobs Detection

**Purpose:** Find jobs stuck in pipeline too long

**SQL Query:**
```sql
SELECT
    *,
    EXTRACT(DAY FROM NOW() - status_changed_at) as days_stale
FROM jobs
WHERE status IN ('saved', 'researching', 'ready_to_apply')
  AND status_changed_at < NOW() - INTERVAL '7 days'
  AND deleted_at IS NULL
ORDER BY status_changed_at ASC;
```

---

### 9. Interview Pipeline

**Purpose:** Active interview tracking

**API Call:**
```
GET /api/v1/jobs?status=interviewing
```

**SQL Equivalent:**
```sql
SELECT
    j.*,
    EXTRACT(DAY FROM NOW() - j.status_changed_at) as days_in_interview
FROM jobs j
WHERE j.status = 'interviewing'
  AND j.deleted_at IS NULL
ORDER BY j.priority DESC, j.status_changed_at DESC;
```

---

### 10. Source Analysis

**Purpose:** Track which job sources yield best results

**SQL Query (requires `job_board` field):**
```sql
SELECT
    COALESCE(job_board, 'unknown') as source,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'applied') as applied,
    COUNT(*) FILTER (WHERE status = 'interviewing') as interviews,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'interviewing') /
        NULLIF(COUNT(*) FILTER (WHERE status = 'applied'), 0),
        1
    ) as interview_rate_pct
FROM jobs
WHERE deleted_at IS NULL
GROUP BY job_board
ORDER BY total DESC;
```

---

## Future Query Enhancements

### Salary Range Filtering (Requires Schema Update)

```sql
-- Add to jobs table:
ALTER TABLE jobs ADD COLUMN salary_min INTEGER;
ALTER TABLE jobs ADD COLUMN salary_max INTEGER;

-- Query:
SELECT * FROM jobs
WHERE (salary_min >= 200000 OR salary_max >= 225000)
  AND status NOT IN ('rejected', 'withdrawn', 'archived')
ORDER BY salary_max DESC NULLS LAST;
```

### Company Size Filtering (Requires Schema Update)

```sql
-- Add to jobs table:
ALTER TABLE jobs ADD COLUMN company_size VARCHAR(20);
ALTER TABLE jobs ADD COLUMN company_stage VARCHAR(20);
ALTER TABLE jobs ADD COLUMN industry VARCHAR(100);

-- Query for target profile (100-500 employees, growth stage):
SELECT * FROM jobs
WHERE company_size IN ('100-500', '500-1000')
  AND company_stage IN ('series-b', 'series-c', 'growth')
  AND industry IN ('Healthcare Tech', 'Enterprise SaaS', 'AI/ML')
ORDER BY priority DESC;
```

### Semantic Search (Using Embeddings)

```sql
-- Requires vector extension and embeddings
SELECT * FROM jobs
ORDER BY embedding <=> (
    SELECT embedding FROM resume_embeddings
    WHERE content_type = 'skills'
    LIMIT 1
)
LIMIT 10;
```

---

## API Response Format

All job queries return:

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "VP Engineering",
      "company": "TechCorp",
      "location": "Remote",
      "status": "saved",
      "target_role": "vp",
      "priority": 75,
      "url": "https://...",
      "created_at": "2026-01-06T12:00:00Z",
      "status_changed_at": "2026-01-06T12:00:00Z",
      "user_decline_reasons": null,
      "company_decline_reasons": null,
      "decline_notes": null
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## Related Documentation

- [Candidate Profile: Tom Hundley](./candidate-profile-tom-hundley.md)
- [Job Search Workflow](./job-search-workflow.md)
- [Schema Reference](../database/init.sql)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-06 | 1.0 | Initial query documentation |
