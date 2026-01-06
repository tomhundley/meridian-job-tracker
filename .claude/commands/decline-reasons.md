# Decline Reasons

View and apply decline reasons when rejecting or withdrawing from jobs.

## Instructions

Track why jobs didn't work out - either you declined or the company declined.

## List User Decline Reasons

Reasons for when YOU decline/withdraw:
```bash
curl -s "http://localhost:8000/api/v1/decline-reasons/user" | jq
```

## List Company Decline Reasons

Reasons for when the COMPANY rejects you:
```bash
curl -s "http://localhost:8000/api/v1/decline-reasons/company" | jq
```

## Apply Decline Reasons

When marking a job as rejected:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "company_decline_reasons": ["experience_mismatch", "salary_expectations"],
    "decline_notes": "They wanted someone with more fintech experience"
  }' | jq
```

When withdrawing:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "withdrawn",
    "user_decline_reasons": ["better_offer", "salary_too_low"],
    "decline_notes": "Accepted offer at another company"
  }' | jq
```

## Common User Decline Reason Codes

- `salary_too_low` - Compensation below expectations
- `not_remote` - Required in-office when seeking remote
- `culture_mismatch` - Company culture concerns
- `better_offer` - Accepted another offer
- `role_mismatch` - Role not as described
- `timeline_mismatch` - Start date didn't work

## Common Company Decline Reason Codes

- `experience_mismatch` - Experience level mismatch
- `salary_expectations` - Salary expectations too high
- `skills_mismatch` - Missing required skills
- `overqualified` - Deemed overqualified
- `position_filled` - Position already filled
- `no_feedback` - No specific feedback given

## Arguments

`/decline-reasons` - List all decline reason categories
