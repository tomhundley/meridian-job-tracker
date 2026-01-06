# Discover and Save Jobs from LinkedIn

Bulk save jobs discovered from LinkedIn search results.

## Instructions

After searching LinkedIn with the browser, save discovered jobs to the database.

## Workflow

### Step 1: Generate Search URL

```bash
curl -s -X POST "http://localhost:8000/api/discovery/linkedin/search-url" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "VP Engineering",
    "location": "San Francisco",
    "experience_level": ["director", "executive"],
    "date_posted": "week",
    "remote": true,
    "easy_apply_only": true
  }' | jq
```

### Step 2: Browse with Playwright

Use Playwright to navigate to the search URL and extract job listings.

### Step 3: Save Discovered Jobs

```bash
curl -s -X POST "http://localhost:8000/api/discovery/linkedin/save" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_dedupe": true,
    "jobs": [
      {
        "title": "VP of Engineering",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "url": "https://linkedin.com/jobs/view/123456",
        "linkedin_job_id": "123456",
        "is_easy_apply": true,
        "posted_date": "2 days ago",
        "salary_info": "$300K - $400K"
      }
    ]
  }' | jq
```

## Search Parameters

- `keywords` - Search terms
- `location` - Location filter
- `experience_level` - entry, associate, mid_senior, director, executive
- `date_posted` - any, day, week, month
- `remote` - true for remote jobs
- `easy_apply_only` - true for Easy Apply only

## Response

```json
{
  "saved": 5,
  "skipped_duplicates": 2,
  "errors": []
}
```

## Arguments

`/discover-jobs {keywords}` - Start job discovery workflow
