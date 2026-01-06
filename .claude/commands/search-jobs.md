# Search for Jobs on LinkedIn

Search LinkedIn for relevant job postings using browser automation.

## Instructions

Use Playwright browser automation to search LinkedIn for jobs matching your criteria.

## Step 1: Generate Search URL

```bash
curl -s -X POST "http://localhost:8000/api/discovery/linkedin/search-url" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "$ARGUMENTS",
    "location": "United States",
    "experience_level": ["director", "executive"],
    "date_posted": "week",
    "remote": true,
    "easy_apply_only": true
  }' | jq '.search_url'
```

## Step 2: Navigate with Playwright

Use the MCP Playwright tools to:
1. Navigate to the search URL
2. Take a snapshot of job listings
3. Extract job details (title, company, URL, etc.)

## Search Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| keywords | string | Search terms (e.g., "VP Engineering") |
| location | string | Location filter |
| experience_level | array | entry, associate, mid_senior, director, executive |
| date_posted | string | any, day, week, month |
| remote | boolean | Filter for remote jobs |
| easy_apply_only | boolean | Filter for Easy Apply only |

## Common Searches

VP roles:
```
/search-jobs VP Engineering
```

CTO roles:
```
/search-jobs CTO Chief Technology Officer
```

AI-focused roles:
```
/search-jobs VP AI ML Engineering
```

## Step 3: Save Discovered Jobs

After extracting jobs from Playwright, save them:
```bash
curl -s -X POST "http://localhost:8000/api/discovery/linkedin/save" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_dedupe": true,
    "jobs": [
      {
        "title": "VP of Engineering",
        "company": "TechCorp",
        "url": "https://linkedin.com/jobs/view/123456",
        "linkedin_job_id": "123456",
        "is_easy_apply": true
      }
    ]
  }' | jq
```

## Arguments

`/search-jobs {keywords}` - Search LinkedIn for jobs with given keywords
