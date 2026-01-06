# SoundWave AI Email Agent

## Executive Summary

**SoundWave** is an intelligent AI-powered email management agent that revolutionizes how professionals handle email overload. Built as a Claude Code MCP (Model Context Protocol) Server, SoundWave enables natural language interaction with email systems, learns user preferences through conversation, and applies a sophisticated 3-layer hybrid rules engine to automatically triage, classify, and organize emails across multiple accounts.

The system combines deterministic pattern matching, semantic search with vector embeddings, and LLM-powered classification—all while enforcing strict cost controls to prevent API spending overruns.

**Project Scope:** 9,000+ lines of production code | Python + TypeScript | MCP Server + Admin Dashboard
**Development Methodology:** AI-Orchestrated Development (Vibe Coding)
**AI Orchestrator:** Tom Hundley
**Development Team:**
- Claude 4.5 Opus (Anthropic)
- Gemini 3.0 Pro (Google)
- ChatGPT Codex 5.2 (OpenAI)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [SoundWave AI Agent](#soundwave-ai-agent)
3. [Hybrid 3-Layer Rules Engine](#hybrid-3-layer-rules-engine)
4. [Complete Technology Stack](#complete-technology-stack)
5. [Architecture & System Design](#architecture--system-design)
6. [Database Design & Data Modeling](#database-design--data-modeling)
7. [Machine Learning System](#machine-learning-system)
8. [Security Architecture](#security-architecture)
9. [Email Provider Integration](#email-provider-integration)
10. [Role-Based Contribution Analysis](#role-based-contribution-analysis)
11. [Key Achievements & Metrics](#key-achievements--metrics)

---

## Project Overview

### The Problem

Email overload is one of the most significant productivity drains for modern professionals. The average knowledge worker receives 120+ emails daily, with studies showing that email management consumes 28% of the workweek. Existing solutions fail because:

- **Rule-Based Systems Are Rigid:** Traditional email filters require technical configuration and can't adapt to changing patterns
- **AI Solutions Are Black Boxes:** Most AI email tools make opaque decisions without user control or learning
- **No Cross-Account Intelligence:** Each email account operates in isolation, duplicating configuration effort
- **Cost Unpredictability:** AI-powered solutions can generate unexpected API costs
- **One-Size-Fits-All:** Solutions don't adapt to individual work patterns and priorities

### The Solution

SoundWave addresses these challenges through an innovative architecture:

1. **Conversational Learning:** Users interact naturally through Claude Code CLI—every action teaches the system
2. **Hybrid 3-Layer Engine:** Combines free deterministic rules, low-cost semantic search, and premium LLM reasoning
3. **Budget-Aware AI:** Enforces daily/monthly spending limits with intelligent layer fallback
4. **Multi-Account Support:** Single system manages multiple email accounts with account-specific learning
5. **Confidence-Based Automation:** Progressive automation based on learned confidence levels

### Development Philosophy: AI-Orchestrated Engineering

This project was developed using the "vibe coding" methodology where **Tom Hundley** acted as the **AI Orchestrator**, directing a multi-model AI development team:

**The AI Development Team:**
| Agent | Provider | Role |
|-------|----------|------|
| Claude 4.5 Opus | Anthropic | Architecture design, MCP server implementation, rules engine |
| Gemini 3.0 Pro | Google | Research, pattern library development, integration analysis |
| ChatGPT Codex 5.2 | OpenAI | Admin dashboard, API routes, rapid prototyping |

### Multi-Model AI Development Strategy

**Claude 4.5 Opus (Anthropic)**
- Primary architect for MCP server design
- Complex async Python implementations
- Rules engine architecture with 3-layer evaluation
- Security analysis (OAuth, token encryption)
- Database schema design

**Gemini 3.0 Pro (Google)**
- Research on Microsoft Graph API patterns
- Email pattern library (300+ patterns)
- Cost optimization strategies
- pgvector integration research
- Multi-account architecture design

**ChatGPT Codex 5.2 (OpenAI)**
- Next.js admin dashboard scaffolding
- Prisma schema and API routes
- UI component generation
- Test case development
- Documentation generation

**Orchestration Model:**
```
Tom Hundley (AI Orchestrator)
        │
        ├──► Strategic Vision & Product Requirements
        ├──► Quality Gates & Approval Decisions
        ├──► Integration Architecture Decisions
        └──► Final Review & Deployment
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
Claude 4.5     Gemini 3.0     Codex 5.2
  Opus           Pro
    │               │               │
    └───────────────┴───────────────┘
                    │
                    ▼
          SoundWave MCP Server
             (9,000+ lines)
```

---

## SoundWave AI Agent

### Overview

SoundWave is an MCP (Model Context Protocol) server that integrates directly with Claude Code CLI, enabling natural language email management. Users simply talk to Claude about their email, and SoundWave handles the technical operations while learning from every interaction.

### Core Capabilities

#### 1. Natural Language Email Operations

**Conversational Interface:**
```
User: "Check my email"
Claude: [uses check_email tool]
        You have 12 new emails since yesterday:

        1. ⭐ From: john@client.com - "Q1 Project Update" (unread)
        2. From: newsletter@marketing.com - "Weekly Deals!" (unread)
        3. From: aws@amazon.com - "Your AWS Bill" (unread)
        ...

User: "Archive all the newsletters"
Claude: [uses archive_email for each newsletter]
        Done! I archived 4 newsletters and learned:
        • Emails from newsletter@marketing.com → archive [confidence: 75%]
        • Emails from digest@techcrunch.com → archive [confidence: 75%]
        Next time I see these, I'll suggest archiving them.

User: "Move John's email to my Clients folder"
Claude: [uses move_email]
        Moved to Clients/. I've also created a rule:
        • Emails from john@client.com → move to "Clients" [confidence: 100%]
```

**MCP Tools Exposed:**

| Tool | Purpose | Parameters |
|------|---------|------------|
| `check_email` | Fetch new emails | account?, folder?, limit? |
| `get_email` | Get full email content | email_id |
| `archive_email` | Move to archive | email_id |
| `delete_email` | Move to trash | email_id |
| `move_email` | Move to folder | email_id, folder |
| `mark_read` | Mark as read | email_id |
| `mark_unread` | Mark as unread | email_id |
| `list_folders` | List mail folders | account? |
| `list_accounts` | Show connected accounts | - |
| `add_account` | Start OAuth flow | provider |
| `remove_account` | Disconnect account | email |
| `set_default_account` | Change primary | email |
| `get_rules` | List learned rules | include_inactive? |
| `add_rule` | Create manual rule | name, conditions, action |
| `delete_rule` | Remove rule | rule_id |
| `record_decision` | Log user action | email_id, action, params |

#### 2. Multi-Account Management

**OAuth Flow (Microsoft 365):**
```
1. User: "Connect my work email"
2. Claude: [uses add_account provider="microsoft"]
           Opens browser → Azure AD consent page
3. User grants permissions
4. Callback captures tokens
5. Tokens encrypted with Fernet (AES-128)
6. Account ready for use
```

**Account Features:**
- Support for 10+ email accounts per user
- Account-specific learning (separate rules per account)
- Automatic token refresh with expiry management
- Encrypted token storage (Fernet encryption)
- Default account selection for quick access

**Supported Providers:**
| Provider | Status | Integration |
|----------|--------|-------------|
| Microsoft 365 | ✅ MVP | Microsoft Graph API v1.0 |
| Gmail | 🔜 Phase 2 | Gmail API v1 |
| IMAP/SMTP | 🔜 Phase 3 | Standard protocols |

#### 3. Intelligent Email Classification

**14 Email Categories:**
```python
EMAIL_CATEGORIES = [
    "urgent_client_request",    # Time-sensitive client needs
    "project_update",           # Status updates on projects
    "meeting_request",          # Calendar/scheduling requests
    "internal_announcement",    # Company-wide communications
    "vendor_communication",     # External vendor/partner emails
    "newsletter",               # Subscribed content
    "marketing",                # Promotional/sales emails
    "transactional",            # Receipts, confirmations, alerts
    "follow_up_required",       # Needs response/action
    "fyi_only",                 # Information only, no action
    "personal",                 # Non-work related
    "spam",                     # Unwanted/suspicious
    "security_alert",           # Security notifications
    "other",                    # Uncategorized
]
```

**Classification Flow:**
```
Email Received
      │
      ▼
┌─────────────────┐
│ Layer 1: Rules  │ (Deterministic, Free)
│ Pattern Match   │
└────────┬────────┘
         │
    Match? ──Yes──► Execute Action
         │
         No
         │
         ▼
┌─────────────────┐
│ Layer 2: RAG    │ (Semantic, $0.02/1M tokens)
│ Vector Search   │
└────────┬────────┘
         │
    Match? ──Yes──► Execute Action
         │
         No
         │
         ▼
┌─────────────────┐
│ Layer 3: LLM    │ (Reasoning, $0.15-3.00/1M)
│ Classification  │
└────────┬────────┘
         │
         ▼
    Classification + Confidence
         │
    Confidence ≥ 80%? ──Yes──► Execute Action
         │
         No
         │
         ▼
    Ask User → Record Decision → Learn
```

#### 4. VIP Contact System

**Priority Tiers:**
| Tier | Description | Treatment |
|------|-------------|-----------|
| 1 | Critical VIPs | Always surface, never auto-archive |
| 2 | High Priority | Surface prominently |
| 3 | Standard | Normal processing |
| 4 | Low Priority | Can batch/summarize |
| 5 | Deprioritized | Auto-archive candidates |

**VIP Features:**
- Automatic folder routing (VIP → specific folder)
- Priority scoring boost in email triage
- Relationship tracking (client, vendor, manager, colleague)
- Organization association
- Multiple email aliases per VIP

#### 5. Todo Generation

**Email → Action Item:**
```
User: "Create a todo from that email"
Claude: [extracts action items]
        Created todo:
        • Title: "Review Q1 Project Update"
        • Source: john@client.com
        • Due: (none set)
        • Priority: Medium
        • Status: Open

        Link: /todos/abc123
```

**Todo Fields:**
- Title (auto-generated from subject)
- Description (from email body)
- Status (open, in-progress, done)
- Priority (low, medium, high, urgent)
- Due date
- Linked email reference

---

## Hybrid 3-Layer Rules Engine

### Architecture Overview

The Rules Engine is SoundWave's core innovation—a cost-optimized, accuracy-maximized system that intelligently selects the cheapest effective evaluation method.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     HYBRID 3-LAYER RULES ENGINE                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 1: DETERMINISTIC PATTERN MATCHING                           │  │
│  │ Cost: FREE | Speed: <1ms | Accuracy: 100% (when matched)          │  │
│  │                                                                    │  │
│  │ Operators:                                                         │  │
│  │ • equals, not_equals                                               │  │
│  │ • contains, not_contains                                           │  │
│  │ • starts_with, ends_with                                           │  │
│  │ • matches (regex)                                                  │  │
│  │ • in_list, not_in_list                                             │  │
│  │                                                                    │  │
│  │ Fields:                                                            │  │
│  │ • from, from_domain, from_name                                     │  │
│  │ • to, cc, subject, body                                            │  │
│  │ • has_attachments, importance                                      │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                         No Match                                         │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 2: SEMANTIC SEARCH (RAG)                                    │  │
│  │ Cost: $0.02/1M tokens | Speed: ~100ms | Accuracy: High            │  │
│  │                                                                    │  │
│  │ Technology:                                                        │  │
│  │ • OpenAI text-embedding-3-small (1536 dimensions)                  │  │
│  │ • pgvector for similarity search                                   │  │
│  │ • Cosine similarity matching                                       │  │
│  │                                                                    │  │
│  │ Operators:                                                         │  │
│  │ • similar_to (threshold: 0.75 default)                             │  │
│  │ • sentiment (positive, negative, urgent, frustrated)               │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                         No Match                                         │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 3: LLM CLASSIFICATION                                       │  │
│  │ Cost: $0.15-3.00/1M tokens | Speed: ~500ms | Accuracy: Highest    │  │
│  │                                                                    │  │
│  │ Models:                                                            │  │
│  │ • GPT-4o-mini (default): $0.15/$0.60 per 1M tokens                 │  │
│  │ • GPT-4o: $2.50/$10.00 per 1M tokens                               │  │
│  │ • Claude Haiku (default): $0.25/$1.25 per 1M tokens                │  │
│  │ • Claude Sonnet: $3.00/$15.00 per 1M tokens                        │  │
│  │                                                                    │  │
│  │ Output:                                                            │  │
│  │ • Category (14 options)                                            │  │
│  │ • Confidence (0.0-1.0)                                             │  │
│  │ • Reasoning (explanation)                                          │  │
│  │ • Suggested action                                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Deterministic Pattern Matching (635 LOC)

**Pattern Library (300+ Patterns):**

```python
# Spam Indicators (auto-archive/delete)
SPAM_PREFIXES = [
    "mailer-daemon@", "postmaster@", "bounce@",
    "noreply@", "no-reply@", "donotreply@",
]

# Newsletter Patterns (auto-archive candidates)
NEWSLETTER_INDICATORS = [
    "newsletter@", "news@", "digest@", "weekly@",
    "monthly@", "bulletin@", "announce@", "updates@",
]

# Marketing Platforms (context-aware)
MARKETING_PLATFORMS = [
    "sendgrid.net", "mailchimp.com", "hubspot.com",
    "marketo.com", "pardot.com", "amazonses.com",
    "mailgun.org", "constantcontact.com",
]

# SaaS Services (transactional vs marketing)
SAAS_SERVICES = {
    "google.com": ["calendar", "docs", "drive", "meet"],
    "microsoft.com": ["teams", "sharepoint", "onedrive"],
    "github.com": ["notifications", "security"],
    "slack.com": ["notifications", "workspace"],
    "zoom.us": ["recordings", "meetings"],
    # ... 50+ more
}

# Financial Services (high priority)
FINANCIAL_SERVICES = [
    "stripe.com", "paypal.com", "square.com",
    "quickbooks.com", "xero.com", "freshbooks.com",
]
```

**Rule Evaluation:**
```python
async def evaluate_layer1(email: Email, rules: List[Rule]) -> Optional[Action]:
    """Evaluate deterministic rules. Returns action if matched."""

    for rule in sorted(rules, key=lambda r: -r.confidence):
        if not rule.is_active:
            continue

        match = True
        for condition in rule.conditions:
            field_value = get_field_value(email, condition.field)

            if condition.operator == "equals":
                match = field_value == condition.value
            elif condition.operator == "contains":
                match = condition.value.lower() in field_value.lower()
            elif condition.operator == "matches":
                match = re.match(condition.value, field_value, re.IGNORECASE)
            # ... other operators

            if not match:
                break

        if match:
            return Action(
                type=rule.action,
                params=rule.action_params,
                confidence=rule.confidence,
                source="layer1",
                rule_id=rule.id,
            )

    return None  # No match, proceed to Layer 2
```

### Layer 2: Semantic Search (407 LOC)

**Vector Embedding Pipeline:**
```python
async def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI text-embedding-3-small."""

    # Check cache first
    cache_key = hashlib.sha256(text.encode()).hexdigest()
    cached = await get_cached_embedding(cache_key)
    if cached:
        return cached

    # Generate new embedding
    response = await openai.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],  # Truncate to model limit
    )

    embedding = response.data[0].embedding

    # Cache for future use
    await cache_embedding(cache_key, embedding)

    # Track cost
    tokens = len(tiktoken.encode(text))
    await cost_tracker.record_embedding_usage(tokens)

    return embedding
```

**Similarity Search:**
```python
async def find_similar_emails(
    query_embedding: List[float],
    threshold: float = 0.75,
    limit: int = 10,
) -> List[SimilarEmail]:
    """Find similar emails using pgvector."""

    result = await db.execute("""
        SELECT
            e.id,
            e.subject,
            e.from_address,
            e.action_taken,
            1 - (ee.embedding <=> $1::vector) as similarity
        FROM email_embeddings ee
        JOIN emails e ON ee.email_id = e.id
        WHERE 1 - (ee.embedding <=> $1::vector) > $2
        ORDER BY ee.embedding <=> $1::vector
        LIMIT $3
    """, [query_embedding, threshold, limit])

    return [SimilarEmail(**row) for row in result]
```

### Layer 3: LLM Classification (437 LOC)

**Classification Prompt:**
```python
CLASSIFICATION_PROMPT = """
Analyze this email and classify it into exactly one category.

EMAIL:
From: {from_address}
Subject: {subject}
Date: {received_at}
Body Preview: {preview}

CATEGORIES:
- urgent_client_request: Time-sensitive client needs requiring immediate action
- project_update: Status updates on ongoing projects
- meeting_request: Calendar invitations or scheduling requests
- internal_announcement: Company-wide communications
- vendor_communication: External vendor/partner emails
- newsletter: Subscribed content, digests, publications
- marketing: Promotional content, sales pitches
- transactional: Receipts, confirmations, automated alerts
- follow_up_required: Requires response but not urgent
- fyi_only: Information only, no action needed
- personal: Non-work related
- spam: Unwanted, suspicious, or irrelevant
- security_alert: Security notifications, password resets
- other: Doesn't fit other categories

Respond with JSON:
{
    "category": "<category_name>",
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>",
    "suggested_action": "archive|delete|flag|none"
}
"""
```

**Classification Service:**
```python
async def classify_email(email: Email) -> Classification:
    """Classify email using LLM with budget check."""

    # Check budget before API call
    if not await cost_tracker.can_use_llm():
        raise BudgetExceededError("Daily LLM budget exhausted")

    prompt = CLASSIFICATION_PROMPT.format(
        from_address=email.from_address,
        subject=email.subject,
        received_at=email.received_at,
        preview=email.preview[:500],
    )

    # Use configured model (default: gpt-4o-mini)
    response = await openai.chat.completions.create(
        model=config.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=200,
    )

    # Track cost
    await cost_tracker.record_llm_usage(
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
    )

    result = json.loads(response.choices[0].message.content)

    return Classification(
        category=result["category"],
        confidence=result["confidence"],
        reasoning=result["reasoning"],
        suggested_action=result["suggested_action"],
    )
```

### Cost Control System (331 LOC)

**Budget Configuration:**
```python
@dataclass
class CostConfig:
    # Daily limits
    daily_embedding_budget: float = 1.00  # $1/day for embeddings
    daily_llm_budget: float = 5.00        # $5/day for LLM

    # Monthly total
    monthly_total_budget: float = 50.00   # $50/month cap

    # Per-model costs (per 1M tokens)
    embedding_cost: float = 0.02          # text-embedding-3-small
    gpt4o_mini_input: float = 0.15
    gpt4o_mini_output: float = 0.60
    gpt4o_input: float = 2.50
    gpt4o_output: float = 10.00
    claude_haiku_input: float = 0.25
    claude_haiku_output: float = 1.25
```

**Budget Enforcement:**
```python
class CostTracker:
    async def can_use_embeddings(self) -> bool:
        """Check if embedding budget allows API call."""
        usage = await self.get_daily_usage()
        return usage.embedding_cost < self.config.daily_embedding_budget

    async def can_use_llm(self) -> bool:
        """Check if LLM budget allows API call."""
        usage = await self.get_daily_usage()
        monthly = await self.get_monthly_usage()

        return (
            usage.llm_cost < self.config.daily_llm_budget and
            monthly.total_cost < self.config.monthly_total_budget
        )

    async def record_embedding_usage(self, tokens: int):
        """Record embedding API usage."""
        cost = (tokens / 1_000_000) * self.config.embedding_cost
        await self.db.execute("""
            INSERT INTO ai_usage_log (account_id, usage_date, embedding_tokens, embedding_cost_usd)
            VALUES ($1, CURRENT_DATE, $2, $3)
            ON CONFLICT (account_id, usage_date) DO UPDATE
            SET embedding_tokens = ai_usage_log.embedding_tokens + $2,
                embedding_cost_usd = ai_usage_log.embedding_cost_usd + $3
        """, [self.account_id, tokens, cost])
```

---

## Complete Technology Stack

### Backend (Python)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **MCP Framework** | mcp | >=1.0.0 | Model Context Protocol server |
| **Runtime** | Python | 3.11+ | Backend language |
| **Async** | asyncio | stdlib | Async I/O operations |
| **Email API** | msgraph-sdk | >=1.0.0 | Microsoft Graph API |
| **OAuth** | azure-identity | >=1.15.0 | Azure AD authentication |
| **HTTP** | httpx | >=0.25.0 | Async HTTP client |
| **Database** | aiosqlite | >=0.19.0 | Async SQLite |
| **Database** | asyncpg | >=0.29.0 | Async PostgreSQL |
| **Vector Search** | pgvector | >=0.2.0 | Semantic similarity |
| **Validation** | pydantic | >=2.0.0 | Data validation |
| **Settings** | pydantic-settings | >=2.0.0 | Environment config |
| **AI** | openai | >=1.0.0 | GPT models + embeddings |
| **AI** | anthropic | >=0.18.0 | Claude models |
| **Tokenization** | tiktoken | >=0.5.0 | Token counting |
| **Encryption** | cryptography | >=41.0.0 | Fernet (AES-128) |
| **Environment** | python-dotenv | >=1.0.0 | .env file loading |

### Frontend (TypeScript/Node.js)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Next.js | ^16.1.1 | React meta-framework |
| **UI** | React | ^18.3.1 | Component library |
| **Language** | TypeScript | ^5.7.2 | Type safety |
| **ORM** | Prisma | ^5.22.0 | Database ORM |
| **Styling** | Tailwind CSS | ^3.4.17 | Utility CSS |
| **Components** | Radix UI | ^1.x | Headless components |
| **Icons** | Lucide React | ^0.468.0 | Icon library |
| **Notifications** | Sonner | ^1.7.1 | Toast notifications |
| **Utilities** | clsx | ^2.1.1 | Class names |
| **Utilities** | tailwind-merge | ^2.5.5 | Merge classes |

### Infrastructure

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Database** | PostgreSQL 16 | Primary data store |
| **Vector Extension** | pgvector | Semantic search |
| **Containerization** | Docker | PostgreSQL container |
| **Admin UI** | pgAdmin | Database management |
| **Testing** | pytest | Unit testing |
| **Linting** | Ruff | Python linting |

---

## Architecture & System Design

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           SOUNDWAVE AI EMAIL AGENT                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────┐                    ┌─────────────────────────────┐   │
│  │   Claude Code CLI  │◄──── MCP Protocol ────►│    SoundWave Server     │   │
│  │   (User Interface) │                    │    (Python MCP Server)    │   │
│  └────────────────────┘                    └────────────┬────────────────┘   │
│                                                         │                    │
│                                            ┌────────────┴────────────┐       │
│                                            │                         │       │
│                                            ▼                         ▼       │
│                                   ┌─────────────────┐     ┌─────────────────┐│
│                                   │  Rules Engine   │     │ Email Provider  ││
│                                   │  (3 Layers)     │     │ (MS Graph API)  ││
│                                   └────────┬────────┘     └────────┬────────┘│
│                                            │                       │         │
│                    ┌───────────────────────┼───────────────────────┤         │
│                    │                       │                       │         │
│                    ▼                       ▼                       ▼         │
│           ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│           │   PostgreSQL    │    │    OpenAI API   │    │  Microsoft 365  │  │
│           │   + pgvector    │    │   (Embeddings)  │    │  (Email Access) │  │
│           └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                    │                                                         │
│                    ▼                                                         │
│           ┌─────────────────┐                                                │
│           │ Admin Dashboard │                                                │
│           │ (Next.js)       │                                                │
│           └─────────────────┘                                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### MCP Server Architecture

**Server Entry Point (339 LOC):**
```python
# src/server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server

# Initialize MCP server
server = Server("soundwave")

# Register tools
@server.tool()
async def check_email(
    account: Optional[str] = None,
    folder: str = "inbox",
    limit: int = 20,
) -> str:
    """Check for new emails since last sync."""
    # Implementation...

@server.tool()
async def archive_email(email_id: str) -> str:
    """Archive an email."""
    # Implementation...

# ... 14 more tools

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

### Data Flow

**Email Triage Flow:**
```
1. User: "Check my email"
              │
              ▼
2. MCP Tool: check_email()
   └─► Microsoft Graph API
       └─► Fetch messages since delta_token
           └─► Cache in local DB
               └─► Return summaries to Claude

3. User: "Archive the newsletters"
              │
              ▼
4. MCP Tool: archive_email(id)
   ├─► Execute on Graph API
   ├─► Update local cache
   └─► Record decision for learning
              │
              ▼
5. Learning System:
   ├─► Pattern detection (3+ similar decisions)
   ├─► Rule proposal (with confidence)
   └─► Confidence update (existing rules)
```

---

## Database Design & Data Modeling

### Core Schema (PostgreSQL/SQLite)

```sql
-- OAuth Accounts (encrypted tokens)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL,  -- 'microsoft', 'gmail'
    display_name TEXT,
    access_token TEXT NOT NULL,   -- Fernet encrypted
    refresh_token TEXT NOT NULL,  -- Fernet encrypted
    token_expiry TIMESTAMPTZ,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email Cache
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    message_id TEXT NOT NULL,      -- Provider's ID
    folder_id TEXT,
    from_address TEXT NOT NULL,
    from_name TEXT,
    to_addresses JSONB,
    cc_addresses JSONB,
    subject TEXT,
    preview TEXT,                   -- First 200 chars
    body_text TEXT,
    body_html TEXT,
    received_at TIMESTAMPTZ,
    is_read BOOLEAN DEFAULT false,
    has_attachments BOOLEAN DEFAULT false,
    importance TEXT DEFAULT 'normal',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, message_id)
);

CREATE INDEX idx_emails_account_received ON emails(account_id, received_at DESC);
CREATE INDEX idx_emails_folder ON emails(account_id, folder_id);

-- Learned Rules
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,      -- Array of conditions
    action TEXT NOT NULL,           -- archive, delete, move, mark_read
    action_params JSONB,            -- {folder: "Clients"}
    confidence FLOAT DEFAULT 0.5,
    times_applied INTEGER DEFAULT 0,
    times_confirmed INTEGER DEFAULT 0,
    times_overridden INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_from_decision UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rules_active_confidence ON rules(is_active, confidence DESC);

-- Decision History (Learning Data)
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    email_id UUID REFERENCES emails(id),
    email_context JSONB NOT NULL,   -- {from, subject, preview, timestamp}
    action TEXT NOT NULL,
    action_params JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_decisions_action ON decisions(action, created_at DESC);

-- VIP Contacts
CREATE TABLE vip_senders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    email TEXT NOT NULL,
    display_name TEXT,
    priority_tier INTEGER DEFAULT 3,  -- 1-5, 1=highest
    is_organization BOOLEAN DEFAULT false,
    organization_name TEXT,
    relationship TEXT,                -- client, vendor, manager, colleague
    folder_assignment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector Embeddings (pgvector)
CREATE TABLE email_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID REFERENCES emails(id) ON DELETE CASCADE,
    embedding vector(1536),           -- OpenAI text-embedding-3-small
    model TEXT DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_embeddings_vector ON email_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- AI Usage Tracking
CREATE TABLE ai_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    usage_date DATE NOT NULL,
    embedding_tokens INTEGER DEFAULT 0,
    embedding_cost_usd DECIMAL(10,6) DEFAULT 0,
    embedding_requests INTEGER DEFAULT 0,
    llm_input_tokens INTEGER DEFAULT 0,
    llm_output_tokens INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(10,6) DEFAULT 0,
    llm_requests INTEGER DEFAULT 0,
    UNIQUE(account_id, usage_date)
);
```

### Entity Relationships

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  accounts   │───┬───│   emails    │───────│ embeddings  │
└─────────────┘   │   └─────────────┘       └─────────────┘
                  │
                  ├───┌─────────────┐
                  │   │  decisions  │
                  │   └─────────────┘
                  │
                  ├───┌─────────────┐
                  │   │ vip_senders │
                  │   └─────────────┘
                  │
                  └───┌─────────────┐
                      │ ai_usage    │
                      └─────────────┘

┌─────────────┐
│    rules    │ (Global, not account-specific in MVP)
└─────────────┘
```

---

## Machine Learning System

### Learning Pipeline

```
User Action (e.g., "Archive this email")
              │
              ▼
┌─────────────────────────────────────────┐
│         Decision Recording              │
│  • Email context (from, subject, etc.)  │
│  • Action taken (archive)               │
│  • Timestamp                            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Pattern Detection               │
│  • Group by (from_domain, action)       │
│  • Count occurrences                    │
│  • Check threshold (3+ similar)         │
└────────────────┬────────────────────────┘
                 │
            Pattern Found?
                 │
        ┌────────┴────────┐
        │                 │
       Yes               No
        │                 │
        ▼                 └──► Wait for more decisions
┌─────────────────────────────────────────┐
│         Rule Proposal                   │
│  • Generate conditions from pattern     │
│  • Calculate initial confidence         │
│  • Create rule (inactive by default)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Confidence Building             │
│  • Apply rule to new emails             │
│  • Track confirmations/overrides        │
│  • Adjust confidence score              │
└────────────────┬────────────────────────┘
                 │
                 ▼
        Confidence Level?
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
  <50%        50-79%       80-99%        100%
    │            │            │            │
    ▼            ▼            ▼            ▼
  Ask         Suggest       Act &       Silent
  User        Action        Mention     Action
```

### Confidence Levels

| Level | Behavior | Example |
|-------|----------|---------|
| **<50%** | Ask without suggestion | "New email from unknown sender. What should I do?" |
| **50-79%** | Ask with suggestion | "This looks like a newsletter. Archive it?" |
| **80-99%** | Act and mention | "Archived 3 newsletters. Want to review?" |
| **100%** | Silent automation | (No message, just logs) |

### Rule Confidence Calculation

```python
def calculate_confidence(rule: Rule) -> float:
    """Calculate rule confidence from feedback."""

    if rule.times_applied == 0:
        return rule.confidence  # Initial confidence

    # Bayesian-inspired confidence update
    confirmations = rule.times_confirmed
    overrides = rule.times_overridden
    total = confirmations + overrides

    if total == 0:
        return rule.confidence

    # Base confidence from success rate
    success_rate = confirmations / total

    # Adjust for sample size (more data = more confidence)
    sample_factor = min(total / 10, 1.0)  # Max out at 10 samples

    # Blend initial confidence with learned confidence
    learned_confidence = success_rate * sample_factor
    initial_weight = 1 - sample_factor

    return (rule.confidence * initial_weight) + (learned_confidence * sample_factor)
```

---

## Security Architecture

### Token Encryption (Fernet/AES-128)

```python
# src/utils/encryption.py

from cryptography.fernet import Fernet
import os

class TokenEncryption:
    def __init__(self, key_path: str = "~/.soundwave/encryption.key"):
        self.key_path = os.path.expanduser(key_path)
        self.fernet = Fernet(self._load_or_create_key())

    def _load_or_create_key(self) -> bytes:
        """Load existing key or generate new one."""
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()

        # Generate new key
        key = Fernet.generate_key()

        # Save with restricted permissions (owner read/write only)
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        with open(self.key_path, "wb") as f:
            f.write(key)
        os.chmod(self.key_path, 0o600)

        return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

### OAuth Security (PKCE Flow)

```python
# Microsoft 365 OAuth with PKCE

class MicrosoftOAuth:
    AUTHORITY = "https://login.microsoftonline.com/{tenant}"
    SCOPES = [
        "Mail.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "MailboxSettings.ReadWrite",
        "offline_access",  # For refresh tokens
    ]

    async def start_auth_flow(self) -> str:
        """Start PKCE OAuth flow, return authorization URL."""

        # Generate PKCE challenge
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # Store verifier for callback
        await self.store_verifier(code_verifier)

        # Build authorization URL
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        return f"{self.AUTHORITY}/oauth2/v2.0/authorize?{urlencode(params)}"
```

### Security Features

| Feature | Implementation |
|---------|---------------|
| Token Storage | Fernet encryption (AES-128-CBC) |
| Key Protection | File permissions 0o600 |
| OAuth | PKCE flow (no client secret exposed) |
| API Keys | Environment variables only |
| Database | Local file with restricted access |
| Budget Limits | Prevents API cost attacks |

---

## Email Provider Integration

### Microsoft Graph API (467 LOC)

**Capabilities:**
```python
class MicrosoftProvider:
    """Microsoft 365 email provider via Graph API."""

    async def list_messages(
        self,
        folder_id: str = "inbox",
        limit: int = 20,
        delta_token: Optional[str] = None,
    ) -> Tuple[List[Email], str]:
        """Fetch messages with delta query support."""

        if delta_token:
            # Incremental sync - only new/changed messages
            url = f"/me/mailFolders/{folder_id}/messages/delta"
            params = {"$deltatoken": delta_token}
        else:
            # Full sync
            url = f"/me/mailFolders/{folder_id}/messages"
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,toRecipients,ccRecipients,"
                          "receivedDateTime,isRead,hasAttachments,importance,"
                          "bodyPreview",
            }

        response = await self.client.get(url, params=params)

        messages = [self._parse_message(m) for m in response["value"]]
        new_delta_token = response.get("@odata.deltaLink", "").split("=")[-1]

        return messages, new_delta_token

    async def move_message(self, message_id: str, folder_id: str) -> bool:
        """Move message to specified folder."""
        await self.client.post(
            f"/me/messages/{message_id}/move",
            json={"destinationId": folder_id}
        )
        return True

    async def archive_message(self, message_id: str) -> bool:
        """Move message to archive folder."""
        archive_folder = await self._get_archive_folder()
        return await self.move_message(message_id, archive_folder.id)

    async def delete_message(self, message_id: str) -> bool:
        """Move message to deleted items."""
        await self.client.post(
            f"/me/messages/{message_id}/move",
            json={"destinationId": "deleteditems"}
        )
        return True

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read."""
        await self.client.patch(
            f"/me/messages/{message_id}",
            json={"isRead": True}
        )
        return True

    async def list_folders(self) -> List[Folder]:
        """List all mail folders with hierarchy."""
        response = await self.client.get(
            "/me/mailFolders",
            params={
                "$top": 100,
                "$select": "id,displayName,parentFolderId,totalItemCount,"
                          "unreadItemCount,isHidden",
            }
        )
        return [self._parse_folder(f) for f in response["value"]]
```

### Delta Query Optimization

```python
# Efficient incremental sync using delta tokens

async def sync_folder(account_id: str, folder_id: str):
    """Sync folder using delta queries for efficiency."""

    # Get last sync state
    sync_state = await db.get_sync_state(account_id, folder_id)
    delta_token = sync_state.delta_token if sync_state else None

    # Fetch only new/changed messages
    messages, new_token = await provider.list_messages(
        folder_id=folder_id,
        delta_token=delta_token,
    )

    # Process messages
    for message in messages:
        await db.upsert_email(message)

    # Save new delta token for next sync
    await db.update_sync_state(
        account_id=account_id,
        folder_id=folder_id,
        delta_token=new_token,
        last_sync=datetime.utcnow(),
    )

    return messages
```

---

## Role-Based Contribution Analysis

### From a Developer Perspective

**Key Technical Contributions:**

1. **MCP Server Implementation**
   - Built complete MCP server with 16 tools
   - Implemented async Python architecture
   - Created stdio transport integration
   - Developed tool parameter validation

2. **3-Layer Rules Engine**
   - Designed hybrid evaluation system (635 LOC)
   - Implemented pattern matching with regex support
   - Built semantic search with pgvector
   - Integrated LLM classification service

3. **Email Provider Integration**
   - Implemented Microsoft Graph API client (467 LOC)
   - Built OAuth PKCE flow
   - Created delta query sync system
   - Developed token encryption (Fernet)

4. **Database Layer**
   - Designed async database wrapper (949 LOC)
   - Created comprehensive schema (15+ tables)
   - Implemented pgvector integration (445 LOC)
   - Built migration system

5. **Admin Dashboard**
   - Built Next.js admin interface
   - Created Prisma schema and migrations
   - Implemented REST API routes
   - Developed VIP/Todo/Contact management

**Technical Skills Demonstrated:**
- Python (async/await, MCP protocol)
- TypeScript (Next.js, Prisma)
- PostgreSQL (pgvector, advanced queries)
- API integration (Microsoft Graph, OAuth)
- Security (encryption, token management)
- AI/ML (embeddings, LLM integration)

---

### From a Principal Architect Perspective

**Architectural Decisions & Leadership:**

1. **Hybrid Rules Engine Design**
   - Invented 3-layer evaluation architecture
   - Balanced cost vs. accuracy tradeoffs
   - Designed intelligent layer fallback
   - Created budget-aware AI usage

2. **MCP Protocol Selection**
   - Chose MCP over REST for Claude integration
   - Designed tool interface for natural conversation
   - Established async-first patterns
   - Created extensible provider architecture

3. **Data Architecture**
   - Designed multi-account data model
   - Selected pgvector for semantic search
   - Created efficient delta sync patterns
   - Established encryption-at-rest strategy

4. **Cost Optimization Strategy**
   - Designed tiered AI usage (free → cheap → expensive)
   - Implemented budget enforcement
   - Created usage tracking system
   - Established fallback patterns

5. **Learning System Architecture**
   - Designed decision → pattern → rule pipeline
   - Created confidence-based automation levels
   - Established feedback loop mechanisms
   - Built pattern recognition algorithms

**Architectural Skills Demonstrated:**
- System design and cost optimization
- AI/ML architecture (embeddings, LLMs, RAG)
- Protocol selection (MCP vs REST)
- Security architecture
- Scalability planning

---

### From a Director of Engineering Perspective

**Engineering Leadership & Delivery:**

1. **Project Execution**
   - Delivered 9,000+ lines of production code
   - Implemented complete MCP server
   - Built admin dashboard
   - Created comprehensive documentation

2. **Technical Standards**
   - Established async Python patterns
   - Implemented Pydantic validation
   - Created consistent error handling
   - Built comprehensive logging

3. **Quality Assurance**
   - Implemented pytest test suite
   - Created async test patterns
   - Built database test fixtures
   - Established CI-ready structure

4. **Security Implementation**
   - Implemented Fernet encryption
   - Built OAuth PKCE flow
   - Created secure key management
   - Established budget limits

**Leadership Skills Demonstrated:**
- Project delivery
- Technical standards
- Quality assurance
- Security implementation

---

### From a VP of Engineering Perspective

**Strategic Technical Leadership:**

1. **Technical Vision**
   - Defined conversational email management paradigm
   - Established cost-optimized AI architecture
   - Created learning-first automation strategy
   - Designed multi-account platform

2. **Platform Strategy**
   - Built extensible provider architecture
   - Created future-ready integration system
   - Established scalable data model
   - Designed for enterprise readiness

3. **Technology Investment**
   - Selected MCP for Claude integration
   - Invested in pgvector for semantic search
   - Chose Fernet for encryption simplicity
   - Built on managed PostgreSQL

4. **Risk Management**
   - Implemented budget controls
   - Created confidence-based automation
   - Built fallback mechanisms
   - Established audit trail

**Strategic Skills Demonstrated:**
- Technical vision
- Platform strategy
- Technology investment
- Risk management

---

### From a CTO Perspective

**Executive Technical Strategy:**

1. **AI-Orchestrated Development Innovation**
   - Pioneered "vibe coding" for MCP server development
   - Directed multi-model AI team (Claude 4.5 Opus, Gemini 3.0 Pro, ChatGPT Codex 5.2)
   - Demonstrated human-AI collaboration on infrastructure projects
   - Validated AI-driven development for complex integrations

2. **Enterprise Architecture Vision**
   - Created extensible email platform architecture
   - Designed cost-controlled AI integration
   - Built for multi-tenant expansion
   - Established security-first patterns

3. **Technology Portfolio Management**
   - Selected MCP protocol for AI-first architecture
   - Balanced innovation with operational efficiency
   - Chose strategic AI service integrations
   - Built for maintainability

4. **Digital Transformation**
   - Transformed email management through AI
   - Created conversational interface paradigm
   - Enabled intelligent automation
   - Built learning system for continuous improvement

**Executive Technical Skills Demonstrated:**
- Strategic technology vision
- AI/ML leadership
- Enterprise architecture
- Cost management
- Innovation portfolio

---

## Key Achievements & Metrics

### Code Metrics

| Metric | Value |
|--------|-------|
| Total Python LOC | 7,129 |
| Total TypeScript LOC | ~2,000 |
| Python Modules | 31 files |
| MCP Tools | 16 |
| Database Tables | 15+ |
| Admin API Routes | 15+ |

### Component Breakdown

| Component | Lines | Purpose |
|-----------|-------|---------|
| storage/database.py | 949 | Database wrapper |
| rules/engine.py | 635 | 3-layer evaluation |
| providers/microsoft.py | 467 | Graph API client |
| storage/vectors.py | 445 | pgvector integration |
| ai/classifier.py | 437 | LLM classification |
| ai/semantic.py | 407 | Semantic search |
| storage/models.py | 404 | Data models |
| ai/embeddings.py | 402 | Embedding generation |
| tools/email.py | 384 | Email operations |
| rules/patterns.py | 347 | Pattern matching |
| server.py | 339 | MCP server entry |
| ai/cost_tracker.py | 331 | Budget enforcement |

### Feature Metrics

| Feature | Scope |
|---------|-------|
| Email Categories | 14 classification types |
| Pattern Library | 300+ recognized patterns |
| MCP Tools | 16 exposed tools |
| VIP Priority Tiers | 5 levels |
| Confidence Levels | 4 automation tiers |
| AI Models | 4 (GPT-4o-mini, GPT-4o, Claude Haiku, Claude Sonnet) |

### Architectural Achievements

- **Hybrid 3-Layer Engine:** Deterministic → Semantic → LLM evaluation
- **Budget-Aware AI:** Daily/monthly cost limits with intelligent fallback
- **Delta Sync:** Efficient incremental email fetching
- **Fernet Encryption:** Secure token storage (AES-128)
- **Confidence-Based Automation:** Progressive automation levels
- **pgvector Integration:** Semantic search with 1536-dimension embeddings
- **MCP Protocol:** Native Claude Code CLI integration

### Innovation Highlights

1. **3-Layer Hybrid Rules Engine:** Cost-optimized AI evaluation
2. **Conversational Learning:** Natural language email training
3. **Budget Enforcement:** Prevents AI cost overruns
4. **Delta Query Sync:** Efficient email synchronization
5. **Pattern Library:** 300+ email classification patterns
6. **Confidence-Based Automation:** Progressive trust building

---

## Conclusion

**SoundWave AI Email Agent** represents a new paradigm in email management—combining the power of large language models with practical cost controls and user-centric learning. By implementing:

- **Hybrid 3-Layer Architecture** balancing cost, speed, and accuracy
- **Conversational Learning** that improves with every user interaction
- **Budget-Aware AI** preventing unexpected costs
- **MCP Integration** for seamless Claude Code experience

The platform delivers intelligent email automation that adapts to individual work patterns while maintaining user control and cost predictability.

This project demonstrates the viability of **AI-Orchestrated Development** for building sophisticated infrastructure tools, with a multi-model AI team delivering 9,000+ lines of production code implementing complex integrations across email providers, AI services, and vector databases.

---

*Project developed through AI-Orchestrated Development*
*AI Orchestrator: Tom Hundley*
*Development Team: Claude 4.5 Opus | Gemini 3.0 Pro | ChatGPT Codex 5.2*
*Total Deliverable: 9,000+ lines of production code*
*Architecture: MCP Server + Admin Dashboard*
