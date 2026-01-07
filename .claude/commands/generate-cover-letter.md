# Generate Cover Letter

Generate a personalized, RAG-enhanced cover letter for a job.

## Arguments

```
/generate-cover-letter {job_id} [--role <role>] [--emphasis "<points>"] [--tone <professional|conversational>]
```

### Required
- `{job_id}` - UUID or partial ID of the job

### Optional Flags
- `--role <role>` - Target role (cto/vp/director/architect/developer)
- `--emphasis "<points>"` - Key points to emphasize (in quotes)
- `--tone <professional|conversational>` - Letter tone (default: professional)

## Workflow

### Step 1: Validate Job

1. Fetch job from API:
   ```bash
   curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq '{title, company, target_role, desc_len: (.description_raw | length)}'
   ```

2. **Check description length** - must be > 500 characters for quality output
   - If too short: "Job description is too short for cover letter. Add full description first."

### Step 2: Determine Role

1. If `--role` flag provided: use that role
2. Else if job has `target_role`: use job's target role
3. Else: **Prompt user interactively** using AskUserQuestion:
   - "Which role should I target for this cover letter?"
   - Options: CTO, VP Engineering, Director, Architect, Developer

### Step 3: Handle Emphasis (Optional)

1. If `--emphasis` flag provided: use as `custom_instructions`
2. Else: Optionally ask user "Any specific points to emphasize?" (can skip)

### Step 4: Generate Cover Letter

```bash
# Write request to file to avoid shell escaping issues
cat > /tmp/cover-letter-request.json << 'EOF'
{
  "target_role": "{role}",
  "tone": "{tone}",
  "custom_instructions": "{emphasis or null}"
}
EOF

# Generate via API (RAG is enabled by default)
curl -s -X POST "http://localhost:8000/api/v1/jobs/{job_id}/cover-letter" \
  -H "Content-Type: application/json" \
  -d @/tmp/cover-letter-request.json | jq
```

### Step 5: Display Formatted Output

Format the response as:

```markdown
## Cover Letter Generated

**Job:** {title} at {company}
**Role:** {target_role}
**Tone:** {tone}
**Version:** {version}
**ID:** {cover_letter_id}

---

{cover letter content}

---

### RAG Evidence Used

| Requirement | Match | Evidence |
|-------------|-------|----------|
| {requirement} | {match_strength} | "{evidence_snippet}" |
| ... | ... | ... |

*Note: RAG evidence shows how your career documents matched the job requirements.*
```

If no RAG evidence (rag_context_used = false):
```
*RAG context was not available for this generation.*
```

## Response Fields

| Field | Description |
|-------|-------------|
| `id` | Cover letter UUID |
| `content` | Generated cover letter text |
| `target_role` | Role used for generation |
| `version` | Version number (increments each generation) |
| `is_current` | Whether this is the latest version |
| `model_used` | AI model used (claude-sonnet-4-20250514) |
| `rag_context_used` | Whether RAG was used |
| `rag_evidence` | Array of matched requirements with evidence |

## Target Roles

| Role | Description |
|------|-------------|
| `cto` | Chief Technology Officer |
| `vp` | VP of Engineering |
| `director` | Director of Engineering |
| `architect` | Principal/Staff Architect |
| `developer` | Senior Developer |

## Examples

### Basic (uses job's target_role)
```
/generate-cover-letter abc123
```

### With specific role
```
/generate-cover-letter abc123 --role vp
```

### With emphasis
```
/generate-cover-letter abc123 --role director --emphasis "highlight cloud migration experience"
```

### Conversational tone
```
/generate-cover-letter abc123 --tone conversational
```

### Full example
```
/generate-cover-letter abc123 --role cto --tone professional --emphasis "AI/ML leadership and startup scaling"
```

## List Cover Letters for Job

```bash
curl -s "http://localhost:8000/api/v1/jobs/{job_id}/cover-letters" | jq '.[] | {id, version, is_current, target_role, rag_context_used}'
```

## Get Specific Cover Letter

```bash
curl -s "http://localhost:8000/api/v1/cover-letters/{cover_letter_id}" | jq
```
