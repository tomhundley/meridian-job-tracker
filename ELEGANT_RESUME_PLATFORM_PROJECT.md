# Elegant Resume Platform (Meridian)

## Executive Summary

**Elegant Resume Platform** (internally codenamed "Meridian") is a revolutionary personal brand and portfolio system that reimagines how executive professionals present themselves to recruiters and hiring managers. The platform combines cutting-edge AI for recruiter engagement, a sophisticated multi-role resume system, and intelligent job description analysis—all deployed as a production website at **thomashundley.com**.

The system comprises two primary components: **Sparkles AI Agent** for intelligent recruiter conversations and resume Q&A, and the **Personal Brand Website** for comprehensive portfolio presentation, content management, and lead generation.

**Project Scope:** 62,000+ lines of production code | 299 TypeScript files | Full-stack implementation
**Development Methodology:** AI-Orchestrated Development (Vibe Coding)
**AI Orchestrator:** Tom Hundley
**Development Team:**
- Claude 4.5 Opus (Anthropic)
- Gemini 3.0 Pro (Google)
- ChatGPT Codex 5.2 (OpenAI)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Sparkles AI Agent](#sparkles-ai-agent)
3. [Personal Brand Website](#personal-brand-website)
4. [Complete Technology Stack](#complete-technology-stack)
5. [Architecture & System Design](#architecture--system-design)
6. [Database Design & Data Modeling](#database-design--data-modeling)
7. [Multi-Role Resume System](#multi-role-resume-system)
8. [Security Architecture](#security-architecture)
9. [AI/ML Integration](#aiml-integration)
10. [Role-Based Contribution Analysis](#role-based-contribution-analysis)
11. [Key Achievements & Metrics](#key-achievements--metrics)

---

## Project Overview

### The Problem

Executive professionals face a fundamental challenge in the job market: their diverse experience spans multiple potential roles (CTO, VP, Director, Architect, Senior Developer), yet traditional resumes force a one-size-fits-all presentation. This creates several pain points:

- **Role Mismatch:** A single resume can't effectively target CTO and Senior Developer positions simultaneously
- **Recruiter Friction:** Recruiters must dig through irrelevant experience to find role-specific qualifications
- **Static Engagement:** Traditional PDFs offer no interactivity or intelligent Q&A capability
- **Lost Context:** When recruiters return days later, they restart from zero
- **Manual Matching:** No automated way to see how qualifications align with specific job descriptions

### The Solution

The Elegant Resume Platform addresses these challenges through two integrated components:

1. **Sparkles AI Agent:** An intelligent conversational assistant powered by Claude 4.5 Opus that can discuss the candidate's background, answer recruiter questions, analyze job descriptions, and provide role-specific insights—all while maintaining session memory across visits.

2. **Personal Brand Website:** A comprehensive portfolio platform with multi-role resume presentation, dynamic content management, PDF generation in three formats, and integrated lead capture.

### Development Philosophy: AI-Orchestrated Engineering

This project represents a paradigm shift in software development methodology. **Tom Hundley** acted as the **AI Orchestrator**, directing a multi-model AI development team to build a production-grade platform:

**The AI Development Team:**
| Agent | Provider | Role |
|-------|----------|------|
| Claude 4.5 Opus | Anthropic | Architecture design, complex implementations, code review |
| Gemini 3.0 Pro | Google | Research, analysis, multi-file refactoring |
| ChatGPT Codex 5.2 | OpenAI | Rapid prototyping, testing, documentation |

### Multi-Model AI Development Strategy

**Claude 4.5 Opus (Anthropic)**
- Primary architect for system design decisions
- Complex multi-file implementations requiring deep context
- AI chat system architecture and prompt engineering
- Security analysis and best practice enforcement
- Database schema design and optimization

**Gemini 3.0 Pro (Google)**
- Research on RAG implementation patterns
- Large-scale refactoring across codebase
- Multi-role content system design
- Pattern detection and consistency enforcement
- Test coverage analysis

**ChatGPT Codex 5.2 (OpenAI)**
- Rapid prototyping of UI components
- Admin dashboard scaffolding
- API endpoint generation
- Documentation and code comments
- Quick iteration on styling

**Orchestration Model:**
```
Tom Hundley (AI Orchestrator)
        │
        ├──► Strategic Vision & Product Requirements
        ├──► Quality Gates & Approval Decisions
        ├──► Integration Architecture Decisions
        └──► Final Review & Production Deployment
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
            Production Website
        (thomashundley.com)
           62,000+ lines
```

---

## Sparkles AI Agent

### Overview

**Sparkles** is an intelligent AI assistant specifically designed for recruiter engagement. Unlike generic chatbots, Sparkles possesses deep knowledge of Tom Hundley's complete professional background and can engage in sophisticated conversations about experience, skills, projects, and career trajectory—all while adapting its responses based on the target role (CTO, VP, Director, Architect, or Developer).

### Core Capabilities

#### 1. Conversational Resume Q&A

**Claude 4.5 Opus Integration**

Sparkles is powered by Anthropic's most capable model, `claude-opus-4-5-20251101`, enabling nuanced, context-aware conversations.

**Conversation Features:**
- Natural language understanding of recruiter questions
- Role-specific response framing (executive vs. technical perspectives)
- Contextual awareness of previous conversation
- Proactive surfacing of relevant achievements
- Intelligent handling of follow-up questions

**Example Interactions:**
```
Recruiter: "What's Tom's experience with AI/ML?"

Sparkles (CTO Role): "Tom has been pioneering AI integration strategies
since 2023, including orchestrating a multi-model AI development team
for production applications. At ESS, he led the strategic adoption of
Claude and GPT-4 for internal productivity tools, resulting in a 40%
reduction in manual processes. His AI-first philosophy extends to
product architecture decisions..."

Sparkles (Developer Role): "Tom has hands-on experience implementing
AI systems using the Anthropic SDK, OpenAI API, and LangChain patterns.
He's built RAG systems with pgvector, implemented streaming responses,
and developed prompt engineering frameworks. Recent projects include
building a 62,000-line application with AI-assisted development..."
```

#### 2. Semantic Search (RAG Architecture)

**Retrieval-Augmented Generation Pipeline:**

```
                    ┌────────────────┐
    User Query ───► │ OpenAI         │
                    │ Embeddings     │
                    │ (1536-dim)     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ pgvector       │
                    │ Similarity     │
                    │ Search         │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Top 8 Results  │
                    │ + Metadata     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ Claude 4.5     │
                    │ Context        │
                    │ Injection      │
                    └───────┬────────┘
                            │
                            ▼
                    Streaming Response
```

**Technical Implementation:**
- **Embedding Model:** OpenAI `text-embedding-3-small` (1536 dimensions)
- **Vector Database:** Supabase PostgreSQL with pgvector extension
- **Similarity Metric:** Cosine similarity
- **Retrieval:** Top 8 results with configurable threshold (default 0.5)
- **Categories:** master-documents, interview-prep, technical deep-dives, project case studies

**RAG Search Service (343 LOC):**
```typescript
async function semanticSearch(
  query: string,
  options: {
    limit?: number;      // Default 8
    threshold?: number;  // Default 0.5
    categories?: string[];
  }
): Promise<ResumeSearchResult[]> {
  // 1. Generate query embedding
  const embedding = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });

  // 2. Execute pgvector similarity search
  const { data } = await supabase.rpc('match_resume_chunks', {
    query_embedding: embedding.data[0].embedding,
    match_threshold: options.threshold,
    match_count: options.limit,
    filter_categories: options.categories,
  });

  return data;
}
```

#### 3. Job Description Analysis Engine

**Intelligent JD Processing (753 LOC)**

When a recruiter uploads a job description, Sparkles performs sophisticated analysis to provide targeted responses.

**Supported File Formats:**
- PDF (text extraction)
- DOCX (Office Open XML parsing)
- Markdown (.md)
- Plain text (.txt)

**Analysis Capabilities:**

| Analysis Type | Description |
|--------------|-------------|
| **Technology Detection** | 100+ regex patterns across 6 categories |
| **Requirement Extraction** | Must-have vs. nice-to-have classification |
| **Seniority Detection** | Principal, Staff, Senior, Mid, Junior, Intern |
| **Experience Parsing** | Years of experience requirements |
| **Role Classification** | CTO, VP, Director, Architect, Developer scoring |
| **Match Scoring** | Strong (75+), Solid (55+), Moderate (35+), Stretch |

**Technology Pattern Groups:**
```typescript
const TECH_PATTERNS = {
  languages: [
    /\b(javascript|typescript|python|java|c\+\+|c#|ruby|go|rust|swift|kotlin)\b/gi,
    // 20+ language patterns
  ],
  frontend: [
    /\b(react|angular|vue|next\.?js|svelte|tailwind|bootstrap)\b/gi,
    // 15+ frontend patterns
  ],
  backend: [
    /\b(node\.?js|express|fastapi|django|flask|spring|rails|laravel)\b/gi,
    // 20+ backend patterns
  ],
  cloud: [
    /\b(aws|azure|gcp|kubernetes|docker|terraform|cloudformation)\b/gi,
    // 25+ cloud/infra patterns
  ],
  databases: [
    /\b(postgresql|mysql|mongodb|redis|dynamodb|elasticsearch)\b/gi,
    // 15+ database patterns
  ],
  aiml: [
    /\b(tensorflow|pytorch|openai|claude|langchain|huggingface|llm)\b/gi,
    // 10+ AI/ML patterns
  ],
};
```

**Role Detection Algorithm:**
```typescript
function detectRole(jdText: string): RoleScores {
  const scores = {
    cto: 0,
    vp: 0,
    director: 0,
    architect: 0,
    developer: 0,
  };

  // Keyword scoring with role-specific weights
  const roleKeywords = {
    cto: ['chief technology', 'cto', 'technology strategy', 'board', 'investor'],
    vp: ['vice president', 'vp engineering', 'p&l', 'department', 'executive'],
    director: ['director', 'team lead', 'people management', 'delivery'],
    architect: ['architect', 'system design', 'scalability', 'technical vision'],
    developer: ['engineer', 'developer', 'hands-on', 'coding', 'implementation'],
  };

  // Seniority level adjustments
  // Management scope indicators
  // Technical depth requirements

  return normalizedScores;
}
```

**Match Scoring Output:**
```typescript
interface JDAnalysis {
  isJobDescription: boolean;
  confidence: number;  // 0-1

  technologies: {
    languages: string[];
    frontend: string[];
    backend: string[];
    cloud: string[];
    databases: string[];
    aiml: string[];
  };

  requirements: {
    mustHave: string[];
    niceToHave: string[];
    yearsRequired: number | null;
    seniorityLevel: SeniorityLevel;
    education: string[];
  };

  roleScores: Record<RoleType, number>;
  recommendedRole: RoleType;

  matchAnalysis: {
    strongMatches: string[];
    moderateMatches: string[];
    gaps: string[];
    overallFit: 'strong' | 'solid' | 'moderate' | 'stretch';
    talkingPoints: string[];
  };
}
```

#### 4. Recruiter Memory System

**Session Persistence Architecture**

Sparkles remembers recruiters across visits without requiring login, creating a personalized experience.

**Session Data Model:**
```typescript
interface MemorySessionData {
  // Recruiter Preferences
  preferences: {
    remoteOnly: boolean;
    preferredLocation: string | null;
    companySize: 'startup' | 'midsize' | 'enterprise' | null;
    industry: string | null;
    roleType: RoleType | null;
  };

  // Conversation History
  chatHistory: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;  // Last 20 messages

  // Personal Notes
  notes: Array<{
    id: string;
    text: string;
    createdAt: string;
  }>;  // Up to 50 notes

  // Analytics
  visitCount: number;
  firstVisit: string;
  lastVisit: string;
  lastRoleViewed: RoleType;
}
```

**Session Management:**
- **Storage:** Supabase `memory_sessions` table
- **Identifier:** Cookie-based session ID (90-day expiry)
- **Security:** HMAC signature validation
- **Cleanup:** Daily cron job removes expired sessions

**Session Flow:**
```
First Visit:
  1. Generate UUID session ID
  2. Set secure cookie (90-day expiry)
  3. Create memory_sessions record
  4. Return empty preferences

Return Visit:
  1. Read session cookie
  2. Validate HMAC signature
  3. Fetch session from database
  4. Inject context into Claude prompt
  5. Update last_visit timestamp
```

#### 5. Lead Capture & Notification

**Contact Collection Modal (762 LOC)**

When recruiters express interest, Sparkles can prompt for contact information.

**Captured Fields:**
- Name (required)
- Email (required)
- Phone (optional)
- Company (optional)
- Role/Position (optional)
- Linked JD Upload (optional)

**Multi-Channel Notification:**
```
Lead Submission
      │
      ├──► Supabase: recruiter_contact_info table
      │
      ├──► Slack: #resume channel
      │    ├── Recruiter details
      │    ├── Company info
      │    └── JD analysis summary
      │
      └──► Email: Admin notification via Resend
           ├── Formatted HTML template
           └── Reply-to recruiter email
```

---

## Personal Brand Website

### Overview

The website serves as a comprehensive digital portfolio and professional presence, featuring dynamic content presentation, multi-role resume views, and sophisticated content management.

### Technology Foundation

**Framework:** Next.js 16.1.1 with App Router
**UI Framework:** React 19.2.3 (latest features including Server Components)
**Styling:** Tailwind CSS 4 with PostCSS
**Animations:** Framer Motion 12.23.26 + GSAP 3.14.2
**3D Graphics:** Three.js 0.182.0 with React Three Fiber
**Type Safety:** Full TypeScript coverage (strict mode)

### Core Features

#### 1. Multi-Role Resume Presentation

**The Innovation:** Same career history, five professional perspectives.

**Role Types:**
| Role | Perspective | Audience |
|------|-------------|----------|
| **CTO** | Board/investor/strategy | C-suite, Board members |
| **VP Engineering** | Department/P&L/hiring | Executive teams |
| **Director** | Team/people/delivery | Senior management |
| **Principal Architect** | System design/scalability | Technical leadership |
| **Senior Developer** | Hands-on/implementation | Engineering teams |

**Dynamic Content Switching:**
```typescript
// Experience bullet points adapt to role
const experience = {
  company: "ESS (Enterprise Software Solutions)",
  period: "2007 - 2015",

  roleTitles: {
    cto: [{ title: "Chief Technology Officer", period: "2012-2015" }],
    vp: [{ title: "VP of Engineering", period: "2010-2015" }],
    director: [{ title: "Director of Development", period: "2008-2012" }],
    architect: [{ title: "Principal Architect", period: "2007-2015" }],
    developer: [{ title: "Senior Software Engineer", period: "2007-2010" }],
  },

  descriptions: {
    cto: [
      "Led technology strategy for $50M revenue business unit",
      "Reported directly to CEO on digital transformation initiatives",
      "Managed $3M annual technology budget with 40% YoY efficiency gains",
    ],
    developer: [
      "Architected and implemented core billing system processing $2M daily",
      "Led migration from legacy VB6 to modern .NET architecture",
      "Mentored team of 5 developers on best practices and patterns",
    ],
    // ... other roles
  },
};
```

#### 2. Resume Section Components

**Experience Section (ExperienceSection.tsx)**
- Company cards with role-appropriate titles
- Period and location display
- Role-filtered bullet points
- Expandable detail views
- Timeline integration

**Projects Section (ProjectsSection.tsx)**
- Project showcase cards
- Technology stack tags
- Role-specific descriptions
- Image galleries
- Links to demos/repos

**Skills Section (SkillsSection.tsx)**
- Categorized skill groups
- Role relevance indicators
- Proficiency levels
- Endorsement counts
- Interactive filtering

**Education & Certifications**
- Degree information
- Professional certifications
- Continuing education
- AWS/Cloud credentials

#### 3. Interactive Timeline (1,182 LOC)

**Timeline2D Component**

A sophisticated visual timeline showing career progression with role-specific milestones.

**Features:**
- Horizontal scrolling timeline
- Company/role nodes with click-to-expand
- Milestone markers (promotions, achievements)
- Role filtering (show CTO-relevant milestones only)
- Responsive design (mobile-optimized)
- GSAP-powered smooth animations

**Timeline Data Structure:**
```typescript
interface TimelineNode {
  id: string;
  type: 'company' | 'milestone' | 'annotation';
  date: Date;
  endDate?: Date;
  title: string;
  subtitle?: string;
  description?: string;
  availableRoles: RoleType[];
  icon?: string;
  color?: string;
  children?: TimelineNode[];
}
```

#### 4. PDF Resume Generation

**Three Resume Templates:**

| Template | Pages | Use Case |
|----------|-------|----------|
| **Executive Summary** | 1-2 | Quick overview for busy executives |
| **Professional Resume** | 2-3 | ATS-optimized for job applications |
| **Complete CV** | 4-5 | Comprehensive for detailed review |

**PDF Generation Stack:**
- **Library:** @react-pdf/renderer 4.3.1
- **Fonts:** Helvetica (PDF built-in)
- **Styling:** Custom PDF stylesheet (670 LOC)
- **Components:** 10 reusable PDF sections

**PDF Component Architecture:**
```
src/lib/resume/pdf/
├── index.tsx          # PDF factory & download logic
├── config.ts          # Page dimensions, margins, fonts (647 LOC)
├── styles.ts          # PDF-specific styles (670 LOC)
├── templates/
│   ├── ExecutiveSummary.tsx
│   ├── ProfessionalResume.tsx
│   └── CompleteCV.tsx
└── components/
    ├── Header.tsx
    ├── ContactInfo.tsx
    ├── Summary.tsx
    ├── ExperienceItem.tsx
    ├── ProjectItem.tsx
    ├── SkillsGrid.tsx
    ├── Education.tsx
    ├── Certifications.tsx
    ├── PageBreak.tsx
    └── Footer.tsx
```

**ATS Optimization:**
- Clean text-based formatting (no tables for layout)
- Standard section headers
- Consistent date formatting
- Keyword-rich content
- Proper heading hierarchy
- Machine-readable structure

**Dynamic Filename Generation:**
```typescript
const filename = `Tom-Hundley-${roleLabel}-${templateName}.pdf`;
// Example: "Tom-Hundley-CTO-Executive-Summary.pdf"
```

#### 5. Admin Dashboard (Content Management System)

**Full CRUD Management for:**

| Entity | Features |
|--------|----------|
| **Jobs** | Company management, logos, periods, role visibility |
| **Positions** | Role-specific titles within companies |
| **Projects** | Detailed showcase with images, technologies |
| **Skills** | Categories, proficiency, endorsements |
| **Annotations** | Timeline markers, milestones |
| **Role Definitions** | Custom titles, headlines, colors |
| **Role Overlays** | Per-experience role customization |
| **Companies** | Client/engagement data |

**Admin UI Components:**
- **DataTable (992 LOC):** Generic table with sorting, filtering, pagination
- **Form Components:** Zod-validated forms for each entity
- **Image Upload:** Vercel Blob integration
- **Rich Text:** Markdown editor support

**Admin Authentication:**
- Supabase Auth integration
- Protected routes via middleware
- Session-based access control
- Return URL handling

#### 6. Blog Platform

**Features:**
- MDX content support
- Markdown with front matter (gray-matter)
- Reading time calculation
- Topic categorization
- RSS feed generation
- SEO metadata (Open Graph, Twitter Cards)
- Semantic search integration

**Blog Search:**
- OpenAI embeddings for semantic search
- Hybrid vector + keyword matching
- Category filtering
- Threshold-based relevance

#### 7. Photo Gallery

**Features:**
- Album organization
- Slug-based routing
- Image optimization (Next.js Image)
- Lightbox viewing
- Album metadata

#### 8. Newsletter System

**Subscription Flow:**
```
Subscribe Request
      │
      ▼
Email Validation (Zod)
      │
      ▼
Generate Verification Token (HMAC)
      │
      ▼
Send Verification Email (Resend)
      │
      ▼
User Clicks Link
      │
      ▼
Verify Token & Activate
      │
      ▼
Add to Subscriber List
```

**Daily Digest (Cron Job):**
- Runs daily via Vercel Cron
- Gathers recent blog posts (30-day lookback)
- Filters by engagement metrics
- Generates React Email template
- Sends via Resend to all verified subscribers
- Logs results to database

#### 9. Contact System

**Contact Form:**
- Multi-field form (name, email, message)
- reCAPTCHA v3 protection
- Zod schema validation
- Rate limiting (5/minute)

**Notification Pipeline:**
```
Form Submission
      │
      ├──► Supabase: contact_leads table
      │
      ├──► Slack: #contact channel
      │
      └──► Email: Admin notification
```

---

## Complete Technology Stack

### Frontend Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Next.js | 16.1.1 | React meta-framework with App Router |
| **Runtime** | Node.js | 20+ | JavaScript runtime |
| **UI** | React | 19.2.3 | Component library (Server Components) |
| **Language** | TypeScript | 5 | Full type safety |
| **Styling** | Tailwind CSS | 4 | Utility-first CSS |
| **Animation** | Framer Motion | 12.23.26 | Spring animations |
| **Animation** | GSAP | 3.14.2 | Timeline animations |
| **3D** | Three.js | 0.182.0 | WebGL 3D graphics |
| **3D React** | @react-three/fiber | 9.4.2 | React Three.js bindings |
| **3D Helpers** | @react-three/drei | 10.7.7 | Three.js utilities |
| **Charts** | Recharts | 3.6.0 | Data visualization |
| **Icons** | Lucide React | Latest | Icon library |
| **PDF** | @react-pdf/renderer | 4.3.1 | PDF generation |
| **Drag & Drop** | @dnd-kit | Latest | Modern drag-and-drop |
| **Email** | @react-email/components | 1.0.3 | Email templates |
| **Validation** | Zod | 3.25.76 | Runtime schema validation |
| **Markdown** | Marked | 16.4.2 | Markdown parsing |
| **Sanitization** | DOMPurify | 3.3.1 | XSS prevention |
| **Front Matter** | gray-matter | 4.0.3 | Markdown metadata |
| **Reading Time** | reading-time | 1.5.0 | Blog reading estimates |

### Backend & Database

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Backend** | Next.js API Routes | 16.1.1 | Serverless functions |
| **Database** | Supabase | Latest | PostgreSQL + Auth + Storage |
| **Vector Search** | pgvector | Latest | Semantic similarity search |
| **DB Client** | @supabase/supabase-js | 2.89.0 | Supabase JavaScript client |
| **SSR Support** | @supabase/ssr | 0.6.1 | Server-side rendering |
| **Raw SQL** | postgres | 3.4.7 | Direct PostgreSQL client |
| **Node PG** | pg | 8.16.3 | Node.js PostgreSQL driver |

### AI & Language Models

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Chat AI** | Claude 4.5 Opus | Latest | Conversational AI (Anthropic) |
| **SDK** | @anthropic-ai/sdk | 0.71.2 | Anthropic API client |
| **Embeddings** | OpenAI API | Latest | text-embedding-3-small |
| **SDK** | openai | 6.15.0 | OpenAI API client |

### External Services

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Email** | Resend | Transactional email delivery |
| **Notifications** | Slack Bot API | Real-time team notifications |
| **Spam Protection** | reCAPTCHA v3 | Bot prevention |
| **Analytics** | Google Tag Manager | Event tracking |
| **File Storage** | Vercel Blob | File uploads |

### Infrastructure

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Hosting** | Vercel | Serverless deployment |
| **Database** | Supabase Cloud | Managed PostgreSQL |
| **CDN** | Vercel Edge Network | Global content delivery |
| **CI/CD** | Vercel Git Integration | Automatic deployments |

---

## Architecture & System Design

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        ELEGANT RESUME PLATFORM (MERIDIAN)                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────┐    ┌────────────────────────────────────┐  │
│  │     SPARKLES AI AGENT        │    │      PERSONAL BRAND WEBSITE        │  │
│  │                              │    │                                    │  │
│  │  ┌────────────────────────┐  │    │   ┌────────────────────────────┐   │  │
│  │  │ Claude 4.5 Opus Chat   │  │    │   │    Multi-Role Resume       │   │  │
│  │  │ (Streaming Responses)  │  │    │   │    (5 Perspectives)        │   │  │
│  │  └───────────┬────────────┘  │    │   └────────────────────────────┘   │  │
│  │              │               │    │                                    │  │
│  │  ┌───────────▼────────────┐  │    │   ┌────────────────────────────┐   │  │
│  │  │ RAG Semantic Search    │  │    │   │    PDF Generation          │   │  │
│  │  │ (pgvector + OpenAI)    │  │    │   │    (3 Templates)           │   │  │
│  │  └───────────┬────────────┘  │    │   └────────────────────────────┘   │  │
│  │              │               │    │                                    │  │
│  │  ┌───────────▼────────────┐  │    │   ┌────────────────────────────┐   │  │
│  │  │ JD Analysis Engine     │  │    │   │    Admin Dashboard         │   │  │
│  │  │ (100+ Tech Patterns)   │  │    │   │    (Full CMS)              │   │  │
│  │  └───────────┬────────────┘  │    │   └────────────────────────────┘   │  │
│  │              │               │    │                                    │  │
│  │  ┌───────────▼────────────┐  │    │   ┌────────────────────────────┐   │  │
│  │  │ Session Memory         │  │    │   │    Blog + Gallery          │   │  │
│  │  │ (90-Day Persistence)   │  │    │   │    + Newsletter            │   │  │
│  │  └────────────────────────┘  │    │   └────────────────────────────┘   │  │
│  │                              │    │                                    │  │
│  └───────────────┬──────────────┘    └─────────────────┬──────────────────┘  │
│                  │                                     │                     │
│                  │        ┌─────────────────┐          │                     │
│                  └───────►│   Next.js 16    │◄─────────┘                     │
│                           │   API Routes    │                                │
│                           │   (14 endpoints)│                                │
│                           └────────┬────────┘                                │
│                                    │                                         │
│                  ┌─────────────────┼─────────────────┐                       │
│                  │                 │                 │                       │
│                  ▼                 ▼                 ▼                       │
│           ┌───────────┐    ┌─────────────┐   ┌────────────┐                  │
│           │ Supabase  │    │   Slack     │   │  Resend    │                  │
│           │ PostgreSQL│    │   Bot API   │   │  Email     │                  │
│           │ + pgvector│    │             │   │            │                  │
│           └───────────┘    └─────────────┘   └────────────┘                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### API Architecture

**14 API Endpoints across 4 Categories**

```
/api
├── Resume Chat System
│   ├── POST /resume-chat          # Claude AI conversation (829 LOC)
│   ├── POST /resume-session       # Session management
│   ├── POST /resume-lead          # Lead capture
│   └── POST /upload-jd            # JD file upload & analysis
│
├── Public Endpoints
│   ├── POST /contact              # Contact form submission
│   ├── POST /search               # Semantic blog search
│   ├── POST /newsletter           # Subscribe
│   ├── GET  /newsletter/verify    # Email verification
│   └── POST /newsletter/unsubscribe
│
├── Admin Endpoints
│   ├── POST /admin/jd-download    # Download uploaded JDs
│   └── POST /admin/slack-delete   # Manage Slack messages
│
└── Cron Jobs
    ├── POST /cron/newsletter-digest    # Daily digest
    ├── POST /cron/cleanup-sessions     # Session cleanup
    └── POST /cron/cleanup-jd-uploads   # File cleanup
```

### Data Flow Diagrams

**Resume Chat Flow:**
```
User Question
      │
      ▼
┌─────────────────┐
│ Rate Limiting   │ (20/min)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Session Lookup  │ (Cookie → DB)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RAG Search      │ (Query → Embeddings → pgvector)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Build   │ (Session + RAG + Role + JD)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Claude 4.5 Opus │ (Streaming)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Safety  │ (Stream validation)
└────────┬────────┘
         │
         ▼
Streaming Response
```

---

## Database Design & Data Modeling

### Entity-Relationship Overview

```
┌─────────────────┐
│     tenants     │ (Multi-tenancy foundation)
└────────┬────────┘
         │
    ┌────┴────┬─────────────┬──────────────┬───────────────┐
    │         │             │              │               │
    ▼         ▼             ▼              ▼               ▼
┌───────┐ ┌────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────────┐
│ jobs  │ │projects│ │  skills  │ │annotations │ │ role_definitions│
└───┬───┘ └────────┘ └──────────┘ └────────────┘ └─────────────────┘
    │
    ▼
┌───────────┐
│ positions │
└───────────┘
    │
    ▼
┌───────────┐
│  clients  │
└───────────┘
    │
    ▼
┌───────────┐
│  systems  │
└───────────┘


┌─────────────────┐        ┌────────────────────┐
│ memory_sessions │◄───────│ recruiter_contacts │
└────────┬────────┘        └────────────────────┘
         │
         ▼
┌─────────────────┐
│   jd_uploads    │
└─────────────────┘


┌─────────────────┐        ┌────────────────────┐
│ resume_chunks   │        │ newsletter_subs    │
│ (pgvector)      │        └────────────────────┘
└─────────────────┘
```

### Core Tables

#### Employment & Experience

```sql
-- Companies/Employers
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    slug TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    logo_url TEXT,
    location TEXT,
    period TEXT,  -- "2007 - 2015"
    start_date DATE,
    end_date DATE,
    description TEXT,
    available_roles TEXT[],  -- ['cto', 'vp', 'director', 'architect', 'developer']
    is_visible BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    display_sequence INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role-Specific Titles
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    role_type TEXT NOT NULL,  -- 'cto', 'vp', etc.
    title TEXT NOT NULL,
    period TEXT,
    start_date DATE,
    end_date DATE,
    exclude_from_tenure BOOLEAN DEFAULT false,
    is_visible BOOLEAN DEFAULT true
);
```

#### Session & Memory

```sql
CREATE TABLE memory_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cookie_id TEXT UNIQUE NOT NULL,
    user_data JSONB DEFAULT '{}'::jsonb,
    -- user_data contains:
    --   preferences: { remoteOnly, location, companySize, industry, roleType }
    --   chatHistory: [{ role, content, timestamp }]
    --   notes: [{ id, text, createdAt }]
    --   visitCount, firstVisit, lastVisit, lastRoleViewed
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days'),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memory_sessions_cookie ON memory_sessions(cookie_id);
CREATE INDEX idx_memory_sessions_expires ON memory_sessions(expires_at);
```

#### Vector Search (RAG)

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE resume_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    category TEXT,  -- 'master-documents', 'interview-prep', etc.
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_resume_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter_categories text[] DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    chunk_text text,
    category text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.id,
        rc.chunk_text,
        rc.category,
        rc.metadata,
        1 - (rc.embedding <=> query_embedding) as similarity
    FROM resume_chunks rc
    WHERE 1 - (rc.embedding <=> query_embedding) > match_threshold
      AND (filter_categories IS NULL OR rc.category = ANY(filter_categories))
    ORDER BY rc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create index for fast similarity search
CREATE INDEX idx_resume_chunks_embedding ON resume_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## Multi-Role Resume System

### The Innovation

The Multi-Role Resume System is a first-of-its-kind approach to professional presentation. Instead of maintaining separate resumes for different roles, a single source of truth adapts dynamically based on the target role.

### Architecture

```typescript
// Role Types
type RoleType = 'cto' | 'vp' | 'director' | 'architect' | 'developer';

// Role Definitions
interface RoleDefinition {
  type: RoleType;
  title: string;           // "Chief Technology Officer"
  headline: string;        // "Technology Executive & Strategic Leader"
  summary: string;         // Role-specific summary paragraph
  focusTags: string[];     // ["Strategy", "Board Relations", "M&A"]
  color: {
    primary: string;       // "#1e40af"
    secondary: string;     // "#3b82f6"
    glow: string;          // "rgba(30, 64, 175, 0.3)"
  };
}

// Experience with Role-Specific Content
interface Experience {
  slug: string;
  company: string;
  location: string;
  period: string;
  availableRoles: RoleType[];

  // Different titles per role
  roleTitles: Record<RoleType, {
    title: string;
    period: string;
  }[]>;

  // Different bullets per role
  descriptions: Record<RoleType, string[]>;
}
```

### Content Framing Examples

**Same Experience, Five Perspectives:**

| Role | Title | Bullet Example |
|------|-------|----------------|
| **CTO** | Chief Technology Officer | "Reported to CEO on $50M technology transformation initiative, presenting quarterly to board of directors" |
| **VP** | VP of Engineering | "Managed $3M annual budget with 12 direct reports across 3 development teams, achieving 40% efficiency gains" |
| **Director** | Director of Software Engineering | "Led team of 15 engineers through Agile transformation, reducing sprint cycle time by 35%" |
| **Architect** | Principal Solutions Architect | "Designed microservices architecture handling 10M daily transactions with 99.99% uptime" |
| **Developer** | Senior Software Engineer | "Implemented core billing engine in C# processing $2M in daily transactions with sub-100ms response times" |

### Role Switching UI

**RoleSelector Component (139 LOC)**
```typescript
const roles = [
  { type: 'cto', label: 'CTO', icon: Crown },
  { type: 'vp', label: 'VP Engineering', icon: Users },
  { type: 'director', label: 'Director', icon: Briefcase },
  { type: 'architect', label: 'Architect', icon: Building },
  { type: 'developer', label: 'Developer', icon: Code },
];

// Role selection persists in:
// 1. URL parameter (?role=cto)
// 2. Session storage (lastRoleViewed)
// 3. Cookie for return visits
```

---

## Security Architecture

### Authentication Model

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Layer 1: Rate Limiting (8,832 LOC)                                      │
│  ├── Per-endpoint configuration                                          │
│  ├── Hybrid: In-memory + Supabase persistence                            │
│  ├── Configurable windows (per minute)                                   │
│  └── Fallback-safe (works without DB)                                    │
│                                                                          │
│  Layer 2: reCAPTCHA v3                                                   │
│  ├── Score-based filtering (0.5+ threshold)                              │
│  ├── Action-specific scoring                                             │
│  └── Graceful degradation                                                │
│                                                                          │
│  Layer 3: Input Validation                                               │
│  ├── Zod schemas for all inputs                                          │
│  ├── Type coercion and sanitization                                      │
│  └── Error message standardization                                       │
│                                                                          │
│  Layer 4: Content Safety                                                 │
│  ├── Streaming content validation                                        │
│  ├── DOMPurify XSS prevention                                            │
│  └── Content policy enforcement                                          │
│                                                                          │
│  Layer 5: Session Security                                               │
│  ├── HMAC signature validation                                           │
│  ├── Cookie security flags (httpOnly, secure, sameSite)                  │
│  └── 90-day expiration with cleanup                                      │
│                                                                          │
│  Layer 6: Admin Authentication                                           │
│  ├── Supabase Auth (passwordless/OAuth)                                  │
│  ├── Middleware protection on /admin                                     │
│  └── Server-side session validation                                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Rate Limiting Configuration

| Endpoint | Limit | Window |
|----------|-------|--------|
| AI Chat | 20 | 1 minute |
| Sessions | 60 | 1 minute |
| Search | 30 | 1 minute |
| Contact Form | 5 | 1 minute |
| File Upload | 10 | 1 minute |
| Lead Capture | 5 | 1 minute |

### Content Policy Enforcement

```typescript
// Streaming content validation
async function validateStreamChunk(chunk: string): Promise<boolean> {
  // Check for suspicious patterns
  // Log anomalies
  // Allow/block based on policy
}

// Final response validation
async function validateFinalResponse(response: string): Promise<{
  safe: boolean;
  flags: string[];
}> {
  // Content policy checks
  // PII detection
  // Prompt injection detection
}
```

---

## AI/ML Integration

### Claude 4.5 Opus Configuration

**Model:** `claude-opus-4-5-20251101`

**Chat API Configuration:**
```typescript
const response = await anthropic.messages.create({
  model: 'claude-opus-4-5-20251101',
  max_tokens: 2048,
  stream: true,
  system: systemPrompt,
  messages: conversationHistory,
});
```

**System Prompt Architecture:**
```
[IDENTITY]
You are Sparkles, a professional resume assistant for Thomas Hundley...

[ROLE CONTEXT]
The recruiter is viewing Tom's profile from a {role} perspective.
Tailor your responses to emphasize {role-specific qualities}...

[RECRUITER CONTEXT]
Previous conversation: {chat_history}
Preferences: {preferences}
Notes: {notes}

[RESUME CONTEXT]
{8 semantically-retrieved resume chunks}

[JD ANALYSIS] (if uploaded)
Technologies required: {tech_list}
Strong matches: {matches}
Talking points: {talking_points}

[GUIDELINES]
- Be conversational but professional
- Reference specific achievements
- Address JD requirements proactively
- Suggest next steps naturally
```

### OpenAI Embeddings

**Model:** `text-embedding-3-small`
**Dimensions:** 1536
**Use Cases:**
- Resume chunk embeddings
- Query embeddings for RAG
- Blog content embeddings
- Semantic search

### Embedding Pipeline

```typescript
// Generate embeddings for new content
async function embedContent(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  });
  return response.data[0].embedding;
}

// Ingest new resume content
async function ingestResumeChunk(
  text: string,
  category: string,
  metadata: Record<string, any>
) {
  const embedding = await embedContent(text);

  await supabase.from('resume_chunks').insert({
    chunk_text: text,
    embedding: embedding,
    category: category,
    metadata: metadata,
  });
}
```

---

## Role-Based Contribution Analysis

### From a Developer Perspective

**Key Technical Contributions:**

1. **Full-Stack Implementation**
   - Built complete Next.js 16 application with 299 TypeScript files
   - Implemented 14 API endpoints with streaming response support
   - Created 80+ React components (7,500+ LOC)
   - Developed comprehensive Supabase integration

2. **AI Integration Development**
   - Integrated Claude 4.5 Opus for conversational AI
   - Implemented RAG pipeline with pgvector
   - Built OpenAI embeddings service
   - Created streaming response handling with content safety

3. **PDF Generation System**
   - Developed 3 resume templates with @react-pdf/renderer
   - Created 10 reusable PDF components
   - Implemented ATS-optimized formatting
   - Built dynamic role-based content injection

4. **Session & Memory System**
   - Designed cookie-based session architecture
   - Implemented HMAC signature validation
   - Built session persistence with Supabase
   - Created cleanup cron jobs

5. **Rate Limiting Infrastructure**
   - Built hybrid in-memory + database rate limiter (8,832 LOC)
   - Implemented per-endpoint configuration
   - Created fallback-safe architecture
   - Added response headers and logging

**Technical Skills Demonstrated:**
- TypeScript (strict mode, advanced types)
- React 19 (Server Components, streaming)
- Next.js 16 (App Router, API routes)
- PostgreSQL (pgvector, RLS, functions)
- AI/ML (Claude, OpenAI, RAG, embeddings)
- Real-time systems (streaming, WebSockets)
- Security (rate limiting, HMAC, XSS prevention)

---

### From a Principal Architect Perspective

**Architectural Decisions & Leadership:**

1. **System Architecture Design**
   - Designed two-component architecture (AI Agent + Website)
   - Established serverless-first approach with Vercel
   - Selected Supabase for managed PostgreSQL with pgvector
   - Created multi-tenant database foundation

2. **AI Architecture**
   - Designed RAG pipeline for semantic resume search
   - Selected embedding model and vector dimensions
   - Architected streaming response system
   - Established content safety validation layers

3. **Multi-Role Content System**
   - Invented role-based resume presentation paradigm
   - Designed flexible content model supporting 5 perspectives
   - Created role overlay architecture for customization
   - Established content inheritance patterns

4. **Data Modeling Excellence**
   - Designed normalized schema with proper relationships
   - Implemented pgvector for semantic search
   - Created JSONB patterns for flexible session data
   - Established Row Level Security policies

5. **Integration Patterns**
   - Designed multi-channel notification system
   - Established webhook patterns for Slack
   - Created file upload/processing pipeline
   - Built cron job architecture for maintenance

**Architectural Skills Demonstrated:**
- System design and decomposition
- AI/ML architecture (RAG, embeddings, LLMs)
- Database design (PostgreSQL, vectors, JSONB)
- Security architecture
- Integration patterns
- Scalability planning

---

### From a Director of Engineering Perspective

**Engineering Leadership & Delivery:**

1. **Project Execution**
   - Delivered 62,000+ lines of production code
   - Implemented 299 TypeScript files
   - Created comprehensive admin CMS
   - Deployed production website (thomashundley.com)

2. **Technical Standards**
   - Established TypeScript strict mode
   - Implemented Zod validation throughout
   - Created consistent API patterns
   - Built comprehensive error handling

3. **Quality & Security**
   - Implemented multi-layer security
   - Built rate limiting infrastructure
   - Created content safety validation
   - Established audit logging

4. **Team Enablement**
   - Created admin dashboard for content management
   - Built self-service PDF generation
   - Implemented analytics tracking
   - Established notification pipelines

5. **Operational Excellence**
   - Configured automatic deployments
   - Implemented cron jobs for maintenance
   - Built monitoring via Slack
   - Created graceful error handling

**Leadership Skills Demonstrated:**
- Project delivery and execution
- Technical standards establishment
- Security implementation
- Operational excellence
- Team tool development

---

### From a VP of Engineering Perspective

**Strategic Technical Leadership:**

1. **Technical Vision**
   - Defined AI-first approach to professional branding
   - Established multi-role resume innovation
   - Created recruiter engagement strategy
   - Designed scalable content platform

2. **Platform Strategy**
   - Built foundation for personal brand platform
   - Created AI-powered recruiter engagement
   - Established lead generation pipeline
   - Designed for content scale

3. **Technology Investment**
   - Selected cutting-edge stack (Next.js 16, React 19)
   - Invested in AI capabilities (Claude 4.5, OpenAI)
   - Chose managed services (Supabase, Vercel)
   - Built for modern deployment patterns

4. **Risk Management**
   - Implemented comprehensive rate limiting
   - Built content safety systems
   - Created session security
   - Established data protection

5. **Innovation Leadership**
   - Pioneered multi-role resume concept
   - Created AI recruiter assistant
   - Built semantic search for resumes
   - Developed JD analysis engine

**Strategic Skills Demonstrated:**
- Technical vision and strategy
- Platform architecture
- Technology investment
- Risk management
- Innovation leadership

---

### From a CTO Perspective

**Executive Technical Strategy:**

1. **AI-Orchestrated Development Innovation**
   - Pioneered "vibe coding" methodology
   - Directed multi-model AI team (Claude 4.5 Opus, Gemini 3.0 Pro, ChatGPT Codex 5.2)
   - Demonstrated human-AI collaboration at scale
   - Validated AI-driven development for complex applications

2. **Enterprise Architecture Vision**
   - Created extensible multi-tenant architecture
   - Established security-first design principles
   - Built for horizontal scalability
   - Designed integration-ready system

3. **Technology Portfolio Management**
   - Selected modern, maintainable stack
   - Balanced innovation with reliability
   - Chose AI technologies strategically
   - Built on managed services for operational efficiency

4. **Digital Transformation**
   - Transformed traditional resume into intelligent platform
   - Integrated AI for personalized engagement
   - Modernized professional branding
   - Enabled data-driven recruiter interactions

5. **Future-Ready Design**
   - Built foundation for additional AI capabilities
   - Designed for multi-tenant expansion
   - Created architecture supporting team features
   - Established patterns for continued AI integration

**Executive Technical Skills Demonstrated:**
- Strategic technology vision
- AI/ML leadership and integration
- Enterprise architecture
- Digital transformation
- Innovation portfolio management

---

## Key Achievements & Metrics

### Code Metrics

| Metric | Value |
|--------|-------|
| Total Lines of Code | 62,384+ |
| TypeScript/TSX Files | 299 |
| React Components | 80+ (7,500+ LOC) |
| API Endpoints | 14 |
| Database Tables | 15+ |
| PDF Templates | 3 |
| Resume Roles | 5 |

### Feature Metrics

| Feature | Scope |
|---------|-------|
| Role Perspectives | 5 (CTO, VP, Director, Architect, Developer) |
| PDF Templates | 3 (Executive Summary, Professional, Complete CV) |
| Tech Detection Patterns | 100+ regex patterns |
| Session Retention | 90 days |
| Notification Channels | 3 (Slack, Email, Database) |
| AI Models | 2 (Claude 4.5 Opus, OpenAI Embeddings) |

### Largest Files

| File | Lines | Purpose |
|------|-------|---------|
| project-details.ts | 5,076 | Project showcase content |
| data.ts | 2,415 | Resume data structure |
| supabase/types.ts | 1,886 | Generated DB types |
| Timeline2D.tsx | 1,182 | Interactive timeline |
| DataTable.tsx | 992 | Admin table component |
| experience-details.ts | 959 | Experience content |
| resume-chat/route.ts | 829 | AI chat endpoint |
| AIChatHero.tsx | 796 | Chat UI component |

### Architectural Achievements

- **Full Streaming AI:** Token-by-token Claude responses
- **Semantic Search:** pgvector RAG implementation
- **Multi-Role Innovation:** First-of-kind resume system
- **Session Memory:** 90-day recruiter persistence without login
- **Rate Limiting:** Hybrid 8,800+ LOC infrastructure
- **ATS Optimization:** Machine-readable PDF generation
- **Multi-Channel Notifications:** Slack + Email + Database

### Innovation Highlights

1. **Multi-Role Resume System:** Same experience, five professional perspectives
2. **Sparkles AI Agent:** Claude 4.5 Opus-powered recruiter engagement
3. **JD Analysis Engine:** 100+ pattern technology detection
4. **Recruiter Memory:** Stateful sessions without authentication
5. **RAG Implementation:** Semantic search over structured resume data
6. **AI-Orchestrated Development:** Multi-model AI team collaboration

---

## Conclusion

**Elegant Resume Platform (Meridian)** represents the future of professional branding and recruiter engagement. By combining:

- **AI-Powered Intelligence** for conversational engagement and semantic search
- **Multi-Role Presentation** allowing one resume to target multiple career paths
- **Intelligent JD Analysis** for automated requirement matching
- **Production-Grade Infrastructure** with security, rate limiting, and monitoring

The platform delivers a comprehensive solution that transforms how executive professionals present themselves to the job market.

This project demonstrates the viability of **AI-Orchestrated Development**, where strategic human direction combined with multi-model AI implementation capabilities can produce production-quality software of significant complexity (62,000+ lines) deployed to a live production environment.

---

*Project developed through AI-Orchestrated Development*
*AI Orchestrator: Tom Hundley*
*Development Team: Claude 4.5 Opus | Gemini 3.0 Pro | ChatGPT Codex 5.2*
*Total Deliverable: 62,384+ lines of production code*
*Production URL: thomashundley.com*
