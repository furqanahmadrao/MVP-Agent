# MVP Agent v2.0 - Production Roadmap (BMAD-Inspired)

**Document Version:** 2.0  
**Date:** December 28, 2025  
**Status:** Planning Phase  
**Based On:** BMAD Method, Speckit patterns, TOON format

---

## Executive Summary

This roadmap transforms MVP Agent from a hackathon prototype into a **production-ready, agent-first PRD generator** following proven patterns from:

1. **BMAD Method** - Structured agile workflow, specialized agents, agent-first outputs
2. **TOON Format** - 30-60% token reduction for agent consumption
3. **LangChain/LangGraph** - Production-ready agent orchestration

**Key Differences from Previous Plan:**
- ❌ Removed "feature suggestions" (premature, not production-focused)
- ✅ Focus on BMAD-style multi-agent workflow
- ✅ TOON format for agent-first outputs
- ✅ Correct Mermaid generation with fallbacks
- ✅ Single Dockerfile (no docker-compose)

---

## Research Findings

### 1. BMAD Method Analysis

**What is BMAD?**
- **B**reakthrough **M**ethod for **A**gile **A**I-**D**riven **D**evelopment
- Created by BMAD Code Organization
- 9 specialized agents, 15 workflow commands, structured phases
- Token-optimized (70-85% reduction via helper pattern)

**Core BMAD Agents (Adapted for Our Use):**

| BMAD Agent | Our Agent | Responsibility |
|------------|-----------|----------------|
| Business Analyst | Market Analyst | Product brief, market research |
| Product Manager | PRD Generator | Requirements, user stories, acceptance criteria |
| System Architect | Architecture Designer | Tech stack, system design, NFRs |
| Developer | Implementation Planner | Dev roadmap, implementation guidance |
| UX Designer | UX Flow Designer | User flows, wireframes, accessibility |
| Scrum Master | Sprint Planner | Sprints, story breakdown |

**BMAD Workflow Phases:**
1. **Analysis** (Product Brief) - Market, users, pain points
2. **Planning** (PRD/Tech Spec) - Requirements, user stories
3. **Solutioning** (Architecture) - System design, tech stack
4. **Implementation** (Sprints) - Development plan

**Key BMAD Patterns We'll Adopt:**
- ✅ **Helpers Pattern** - Reusable sections (70-85% token savings)
- ✅ **Structured Status Tracking** - YAML-based progress files
- ✅ **Agent-First Outputs** - Designed for AI consumption, not just humans
- ✅ **Gate Checks** - Validate outputs before proceeding
- ✅ **Phased Workflow** - Don't skip steps
- ✅ **Project Levels** - Right-size outputs (Level 0-4)

---

### 2. TOON Format Analysis

**What is TOON?**
- **T**oken-**O**riented **O**bject **N**otation
- 30-60% fewer tokens than JSON for LLMs
- Combines YAML indentation + CSV tabular format
- Python implementation: `toon_format` package

**TOON Syntax:**

```toon
# Object
name: Alice
age: 30

# Primitive Array
tags[3]: alpha,beta,gamma

# Tabular Array (uniform objects)
users[2,]{id,name,age}:
  1,Alice,30
  2,Bob,25

# Mixed Array
items[3]:
  - name: Item1
  - 42
  - hello
```

**Benefits for Agent Consumption:**
- ✅ 30-60% fewer tokens
- ✅ Array length validation `[N]`
- ✅ Tabular format for uniform data
- ✅ Minimal syntax (no braces, brackets)
- ✅ Human-readable (still Markdown-ish)

**Decision:** Use TOON for **internal agent communication** (optional feature), keep **Markdown for user outputs**. TOON is agent-first, Markdown is human-first.

---

###3. Speckit Research

**Status:** Speckit by GitHub doesn't exist as a public repo (searched `github/speckit`). This may be:
- Internal GitHub tool
- Misremembered name
- Private/enterprise product

**Alternative Research:** Studied industry-standard PRD generators:
- **ProductBoard** - Feature prioritization, roadmaps
- **Aha!** - Comprehensive PRD templates
- **Delibr** - AI-assisted PRDs

**Common Patterns:**
- Requirements traceability (FR-001, NFR-001)
- MoSCoW prioritization (Must/Should/Could/Won't)
- User stories with acceptance criteria
- System diagrams (architecture, user flows)
- Gate checks before implementation

---

### 4. Mermaid Diagram Best Practices

**Current Issues:**
- Mermaid syntax errors cause rendering failures
- No validation before showing diagrams
- Breaks user experience

**Production Solution:**
1. **Validate** Mermaid syntax before outputting
2. **Fallback** to text descriptions if validation fails
3. **Hide** diagrams with errors (don't show broken diagrams)
4. **Optional** - Use Mermaid CLI for server-side validation

**Validation Strategy:**
```python
def validate_mermaid(diagram: str) -> bool:
    """Validate Mermaid diagram syntax"""
    try:
        # Basic syntax validation
        if not diagram.strip().startswith(('graph', 'sequenceDiagram', 'classDiagram', 'erDiagram', 'gantt', 'pie', 'quadrantChart', 'flowchart')):
            return False
        
        # Check for balanced braces/brackets
        if diagram.count('[') != diagram.count(']'):
            return False
        if diagram.count('(') != diagram.count(')'):
            return False
        if diagram.count('{') != diagram.count('}'):
            return False
        
        return True
    except Exception:
        return False

def generate_with_fallback(diagram: str, fallback_text: str) -> str:
    """Generate diagram or fallback to text"""
    if validate_mermaid(diagram):
        return f"```mermaid\n{diagram}\n```\n\n"
    else:
        return f"**Diagram unavailable** (validation failed)\n\n{fallback_text}\n\n"
```

---

## Production Architecture (BMAD-Inspired)

### Agent Orchestration (LangGraph)

```python
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    """Shared state across all agents"""
    idea: str
    project_level: int  # 0-4 (BMAD levels)
    product_brief: str
    prd: str
    architecture: str
    user_flows: str
    roadmap: str
    business_model: str
    testing_plan: str
    research_data: dict
    status: str
    errors: list

# Define workflow graph
workflow = StateGraph(AgentState)

# Add nodes (agents)
workflow.add_node("market_analyst", market_analyst_agent)
workflow.add_node("prd_generator", prd_generator_agent)
workflow.add_node("architect", architecture_agent)
workflow.add_node("ux_designer", ux_flow_agent)
workflow.add_node("sprint_planner", roadmap_agent)

# Define edges (workflow)
workflow.set_entry_point("market_analyst")
workflow.add_edge("market_analyst", "prd_generator")
workflow.add_edge("prd_generator", "architect")
workflow.add_edge("architect", "ux_designer")
workflow.add_edge("ux_designer", "sprint_planner")
workflow.add_edge("sprint_planner", END)

# Compile
app = workflow.compile()
```

**Benefits:**
- Clear workflow visualization
- Parallel agent execution (where possible)
- Built-in error handling and retries
- State management across phases

---

## Phase-by-Phase Implementation

### **Phase 1: Core Infrastructure** ⏱️ 3-4 days

**Goal:** Set up production-ready foundation with LangGraph + TOON support.

**Tasks:**
1. **Set up LangGraph environment**
   ```txt
   langchain==0.3.10
   langchain-google-genai==2.0.7
   langgraph==0.2.60
   toon-format==0.9.0  # TOON support
   ```

2. **Create agent state structure**
   - Define `AgentState` TypedDict
   - YAML-based status tracking (BMAD pattern)
   - Project level detection (0-4)

3. **Implement helpers system** (BMAD pattern)
   - Create `src/helpers.py` with reusable sections
   - Load Global Config
   - Generate YAML Status
   - Parse Requirements
   - 70-85% token savings

4. **Add TOON format support** (optional)
   - TOON encoder/decoder for agent outputs
   - Fallback to JSON if TOON fails
   - Settings toggle (TOON vs. JSON)

**Deliverables:**
- ✅ LangGraph workflow skeleton
- ✅ Agent state management
- ✅ Helpers system
- ✅ TOON format support (optional)

---

### **Phase 2: API Key Management & Settings** ⏱️ 2-3 days

**Goal:** User-provided API keys, remove dependency on maintainer's keys.

**Tasks:**
1. **Create settings UI** (`src/settings.py`)
   - API key input (masked password field)
   - Model selection (Pro/Flash/Flash-Lite)
   - Rate limit display
   - TOON format toggle
   - Save to Gradio persistent state

2. **Update `app.py`**
   - Add "Settings" tab
   - Load API key from settings (fallback to env)
   - Validate API key on save

3. **Update agent initialization**
   - Pass API key to all agents
   - Remove hardcoded env var dependency

**Deliverables:**
- ✅ Settings page with API key input
- ✅ Persistent storage (Gradio state)
- ✅ API key validation

---

### **Phase 3: Gemini Search Grounding** ⏱️ 2-3 days

**Goal:** Replace Google Custom Search MCP with Gemini Grounding.

**Tasks:**
1. **Remove Google Search MCP**
   - Delete `tools/google_search_mcp/`
   - Remove from `src/mcp_process_manager.py`
   - Remove env vars from `.env.example`

2. **Implement Gemini Grounding agent**
   ```python
   from google.genai import types
   
   grounding_tool = types.Tool(google_search=types.GoogleSearch())
   config = types.GenerateContentConfig(tools=[grounding_tool])
   
   response = client.models.generate_content(
       model="gemini-2.5-flash",
       contents="research query",
       config=config
   )
   
   # Extract citations
   citations = response.candidates[0].grounding_metadata
   ```

3. **Update Market Analyst agent**
   - Use Gemini Grounding for research
   - Extract `groundingChunks` and `groundingSupports`
   - Format citations in markdown

**Deliverables:**
- ✅ Google Search MCP removed
- ✅ Gemini Grounding integrated
- ✅ Citation support in outputs

---

### **Phase 4: BMAD-Style Agent Implementation** ⏱️ 7-10 days

**Goal:** Implement 6 specialized agents following BMAD patterns.

**Agents to Implement:**

#### **Agent 1: Market Analyst** (2 days)
- **Input:** User idea
- **Output:** `product_brief.md`
- **Sections:**
  - Executive Summary
  - Market Analysis (Gemini Grounding)
  - User Personas
  - Pain Points
  - Competitor Analysis
  - Unique Value Proposition
- **Mermaid:** Market segmentation diagram (with fallback)
- **Gate Check:** Validate completeness

#### **Agent 2: PRD Generator** (2 days)
- **Input:** Product brief
- **Output:** `prd.md`
- **Sections:**
  - Functional Requirements (FR-001, FR-002...)
  - Non-Functional Requirements (NFR-001, NFR-002...)
  - User Stories (grouped by epics)
  - Acceptance Criteria
  - MoSCoW Prioritization (Must/Should/Could/Won't)
  - Success Metrics
- **Format:** TOON for internal agent use (optional), Markdown for users
- **Mermaid:** User story map (with fallback)

#### **Agent 3: Architecture Designer** (2 days)
- **Input:** PRD
- **Output:** `architecture.md`
- **Sections:**
  - System Components
  - Tech Stack (with justifications)
  - Database Schema
  - API Specifications
  - NFR Coverage (traceability to NFR-001, etc.)
  - Security Architecture
  - Scalability Strategy
- **Mermaid:** System architecture diagram, ERD (with fallbacks)
- **Gate Check:** ≥90% NFR coverage

#### **Agent 4: UX Flow Designer** (2 days)
- **Input:** PRD, Architecture
- **Output:** `user_flow.md`
- **Sections:**
  - User Flows (numbered steps, decision points)
  - Wireframes (ASCII art or structured descriptions)
  - WCAG 2.1 Accessibility
  - Design Tokens (colors, typography)
  - Component Library
- **Mermaid:** User flow diagrams (with fallbacks)

#### **Agent 5: Sprint Planner** (1 day)
- **Input:** PRD, Architecture
- **Output:** `roadmap.md`
- **Sections:**
  - Sprint Breakdown (MVP, v1.0, v2.0)
  - Story Estimates (points/hours)
  - Dependencies
  - Timeline (Gantt chart)
  - Milestones
- **Mermaid:** Gantt chart (with fallback)

#### **Agent 6: Business Model Designer** (1 day)
- **Input:** Product brief, PRD
- **Output:** `business_model.md`
- **Sections:**
  - Revenue Streams
  - Cost Structure
  - Pricing Model
  - Go-to-Market Strategy
  - Unit Economics (CAC, LTV, LTV:CAC)
  - Break-Even Analysis

**Deliverables:**
- ✅ 6 specialized agents (LangChain tools)
- ✅ BMAD-style outputs (agent-first + human-readable)
- ✅ Gate checks between phases
- ✅ Mermaid diagrams with fallbacks

---

### **Phase 5: Code Editor UI** ⏱️ 4-5 days

**Goal:** Replace tabbed view with code editor-style interface.

**Tasks:**
1. **Implement file browser sidebar**
   - Collapsible file tree (11 markdown files)
   - Active file highlighting
   - File icons

2. **Implement code editor pane**
   - Use `gr.Code` component (Gradio)
   - Syntax highlighting (Markdown)
   - Read-only mode
   - Line numbers
   - Copy to clipboard button

3. **Update generation flow**
   - **During generation:** Show terminal-style status (Phase 1)
   - **After completion:** Hide status, show editor UI (Phase 2)
   - Default to `overview.md` opened
   - "Download All as ZIP" button

4. **Add export options**
   - Download individual file
   - Download all as ZIP
   - Copy to clipboard

**Deliverables:**
- ✅ Code editor-style interface
- ✅ File browser sidebar
- ✅ Syntax-highlighted Markdown
- ✅ Individual file download

---

### **Phase 6: Mermaid Validation & Fallbacks** ⏱️ 2-3 days

**Goal:** Ensure only valid Mermaid diagrams are shown.

**Tasks:**
1. **Implement Mermaid validator**
   ```python
   def validate_mermaid(diagram: str) -> tuple[bool, str]:
       """Validate Mermaid syntax, return (is_valid, error_msg)"""
       # Check diagram type
       # Check balanced braces/brackets
       # Check basic syntax
       # Optional: Use Mermaid CLI for validation
   ```

2. **Add fallback system**
   - If validation fails, use text description
   - Hide diagram (don't show broken syntax)
   - Log error for debugging

3. **Update all diagram generation prompts**
   - Provide text fallback in prompt
   - Tell agent to validate before outputting
   - Include common Mermaid pitfalls

**Deliverables:**
- ✅ Mermaid validation function
- ✅ Fallback to text descriptions
- ✅ No broken diagrams shown to users

---

### **Phase 7: Docker Containerization** ⏱️ 2-3 days

**Goal:** Single Docker container for easy deployment.

**Tasks:**
1. **Create Dockerfile** (single container, no compose)
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   # Copy requirements
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy source
   COPY . .
   
   # Expose Gradio port
   EXPOSE 7860
   
   # Run app
   CMD ["python", "app.py"]
   ```

2. **Optimize Docker image**
   - Multi-stage build
   - Minimize layers
   - Use `.dockerignore`
   - Target size: <500MB

3. **Add environment variable support**
   - Pass API keys via env vars
   - Document in README

4. **Test deployment**
   - Build image locally
   - Test on Linux, macOS, Windows/WSL
   - Verify all features work

**Deliverables:**
- ✅ Dockerfile (single container)
- ✅ Optimized image (<500MB)
- ✅ Deployment documentation

---

### **Phase 8: Production Hardening** ⏱️ 3-4 days

**Goal:** Production-ready features: error handling, logging, monitoring.

**Tasks:**
1. **Enhanced error handling**
   - Retry logic with exponential backoff
   - User-friendly error messages
   - Graceful degradation (fallbacks)
   - Error recovery (resume from last phase)

2. **Structured logging**
   - JSON format logs
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Rotate log files
   - Correlation IDs for tracing

3. **Rate limiting** (per-user, based on API key)
   - Track API calls per user
   - Display remaining quota
   - Queue system for high load

4. **Security hardening**
   - Input sanitization (prevent prompt injection)
   - API key encryption at rest
   - HTTPS enforcement
   - CORS configuration

5. **Performance optimization**
   - Async I/O for API calls
   - Caching for repeated queries
   - Lazy loading for UI components

**Deliverables:**
- ✅ Production-grade error handling
- ✅ Structured logging
- ✅ Rate limiting
- ✅ Security best practices

---

### **Phase 9: Publishing & CI/CD** ⏱️ 2-3 days

**Goal:** Publish Docker image and set up CI/CD.

**Tasks:**
1. **Publish to Docker registries**
   - GitHub Container Registry: `ghcr.io/furqanahmadrao/mvp-agent`
   - Docker Hub: `furqanahmadrao/mvp-agent`

2. **Set up GitHub Actions**
   ```yaml
   # .github/workflows/docker-publish.yml
   name: Docker Publish
   on:
     push:
       branches: [main]
       tags: ['v*']
   
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: docker/build-push-action@v5
           with:
             push: true
             tags: ghcr.io/furqanahmadrao/mvp-agent:latest
   ```

3. **Automated testing**
   - Unit tests (pytest)
   - Integration tests (end-to-end PRD generation)
   - Coverage reporting

4. **Documentation**
   - Update README with Docker instructions
   - Add deployment guides (AWS, GCP, Azure)
   - API documentation (if exposing API)

**Deliverables:**
- ✅ Published Docker images
- ✅ CI/CD pipeline
- ✅ Automated testing
- ✅ Comprehensive documentation

---

## Technology Stack Summary

### Core Stack
- **Language:** Python 3.10+
- **UI:** Gradio (with Monaco/Code editor)
- **AI:** Google Gemini 2.5 (Pro/Flash/Flash-Lite)
- **Framework:** LangChain + LangGraph
- **Search:** Gemini Search Grounding (built-in)
- **Format:** TOON (agent-first)
- **Deployment:** Docker (single container)

### Dependencies
```txt
# Core
gradio==5.49.1
python-dotenv==1.0.1

# AI & Agents
langchain==0.3.10
langchain-google-genai==2.0.7
langgraph==0.2.60
google-generativeai==0.8.3

# Data & Formats
pydantic==2.9.2
pyyaml==6.0.1
toon-format==0.9.0  # Optional, for agent-first outputs

# Utilities
aiohttp==3.10.5
orjson==3.10.7

# Optional: Mermaid validation
# mermaid-cli (requires Node.js, skip if not needed)
```

### MCP Servers Status
- ❌ **Google Search MCP** - REMOVED (replaced by Gemini Grounding)
- ⚠️ **File Manager MCP** - CONVERT to LangChain tool
- ⚠️ **Markdownify MCP** - CONVERT to LangChain tool

---

## Output Format Specification

### Project Levels (BMAD-Inspired)

| Level | Complexity | Story Count | Documents | Workflow |
|-------|------------|-------------|-----------|----------|
| 0 | Prototype | 1 | Minimal (brief + tech spec) | Quick start |
| 1 | Small | 1-10 | Light (brief + PRD + arch) | Standard |
| 2 | Medium | 5-15 | Standard (all 11 docs) | Full workflow |
| 3 | Large | 12-40 | Comprehensive (+ sprints) | Agile |
| 4 | Enterprise | 40+ | Enterprise (+ governance) | Full BMAD |

**Auto-Detection Logic:**
- Analyze idea complexity
- Estimate feature count
- Detect keywords (SaaS, marketplace, platform → Level 2+)
- User can override

---

### Document Structure (11 Files)

#### 1. `product_brief.md` (Market Analyst)
```markdown
# Product Brief: [Project Name]

## Executive Summary
[2-3 paragraphs]

## Market Analysis
[Gemini Grounding research]
- Market size
- Growth trends
- Key players

## User Personas
| Persona | Description | Pain Points |
|---------|-------------|-------------|
| ... | ... | ... |

## Competitor Analysis
[2,]{competitor,strengths,weaknesses}:
  Competitor A,Feature-rich,Complex UI
  Competitor B,Simple,Limited features

## Unique Value Proposition
[What makes us different]

## Success Metrics
- Metric 1
- Metric 2

---
**Rationale:** [Why these choices]
**Agent Guidance:** Next step is PRD generation. Focus on features that address identified pain points.
```

#### 2. `prd.md` (PRD Generator)
```markdown
# Product Requirements Document

## Functional Requirements
### FR-001: User Authentication
**Description:** [Detailed description]
**User Story:** As a [user], I want to [action] so that [benefit]
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
**Priority:** Must-Have
**Story Points:** 5

[Repeat for all FRs]

## Non-Functional Requirements
### NFR-001: Performance
**Description:** System must handle 1000 concurrent users
**Metric:** Response time <200ms (p95)
**Priority:** Must-Have

[Repeat for all NFRs]

## User Stories (Epics)
### Epic 1: User Management
- [FR-001] User Authentication (5 points)
- [FR-002] User Profile (3 points)

## MoSCoW Prioritization
**Must-Have:** FR-001, FR-002, NFR-001
**Should-Have:** FR-003, FR-004
**Could-Have:** FR-005
**Won't-Have:** FR-006 (v2.0)

---
**Rationale:** [Why these features]
**Agent Guidance:** Next step is architecture. Ensure all NFRs are addressed in system design.
```

**(Continue for all 11 documents...)**

**All documents follow BMAD pattern:**
- Structured sections
- Requirements traceability (FR-001, NFR-001)
- Agent guidance at end
- Mermaid diagrams (with fallbacks)
- TOON format for internal agent use (optional)

---

## File Structure Changes

### New Files
```
MVP-Agent/
├── src/
│   ├── agents/                   # NEW: LangGraph agents
│   │   ├── market_analyst.py
│   │   ├── prd_generator.py
│   │   ├── architect.py
│   │   ├── ux_designer.py
│   │   ├── sprint_planner.py
│   │   └── business_model.py
│   ├── helpers.py                # NEW: BMAD helpers pattern
│   ├── settings.py               # NEW: Settings UI
│   ├── validators.py             # NEW: Mermaid validation
│   └── toon_utils.py             # NEW: TOON format (optional)
├── Dockerfile                    # NEW: Single container
├── .dockerignore                 # NEW
├── .github/
│   └── workflows/
│       └── docker-publish.yml    # NEW: CI/CD
└── PRODUCTION_ROADMAP_V2.md      # THIS FILE
```

### Modified Files
```
MVP-Agent/
├── app.py                        # Add settings tab, editor UI
├── src/
│   ├── agent_brain.py            # Refactor to use LangGraph
│   ├── ai_models.py              # Add Gemini Grounding
│   ├── prompts.py                # Update for BMAD patterns
│   └── file_manager.py           # Add TOON support (optional)
├── requirements.txt              # Add LangChain, TOON
└── README.md                     # Update for v2.0
```

### Removed Files
```
MVP-Agent/
└── tools/
    └── google_search_mcp/        # DELETE (replaced by Gemini Grounding)
        ├── run.py
        └── server.json
```

---

## Testing Strategy

### Unit Tests
- API key validation
- Gemini Grounding parsing
- LangChain tool execution
- Mermaid validation
- TOON encoding/decoding
- File export (ZIP)

### Integration Tests
- End-to-end PRD generation
- Settings persistence
- Editor UI interactions
- Docker container startup

### Performance Tests
- Response time per agent (<5s per phase)
- Token usage tracking
- Rate limit compliance
- Memory footprint (Docker)

### Manual QA
- Generate 5 sample PRDs (different industries)
- Verify all Mermaid diagrams render or fallback
- Test Docker deployment on 3 platforms

---

## Timeline Estimate

| Phase | Duration | Completion Date (Est.) |
|-------|----------|------------------------|
| Phase 1: Core Infrastructure | 3-4 days | Jan 3, 2026 |
| Phase 2: API Key Management | 2-3 days | Jan 6, 2026 |
| Phase 3: Gemini Grounding | 2-3 days | Jan 9, 2026 |
| Phase 4: BMAD Agents | 7-10 days | Jan 20, 2026 |
| Phase 5: Code Editor UI | 4-5 days | Jan 26, 2026 |
| Phase 6: Mermaid Validation | 2-3 days | Jan 29, 2026 |
| Phase 7: Docker | 2-3 days | Feb 1, 2026 |
| Phase 8: Production Hardening | 3-4 days | Feb 5, 2026 |
| Phase 9: Publishing & CI/CD | 2-3 days | Feb 8, 2026 |

**Total Estimated Time:** 27-38 days (5-7 weeks)  
**Target Public Release:** Early February 2026

---

## Success Metrics

### Technical Metrics
- ⏱️ **Generation time:** <5 minutes per PRD
- 💾 **Docker image size:** <500MB
- 📊 **Token efficiency:** TOON: 30-60% reduction (agent-first), Markdown: human-readable
- ⚡ **Rate limit compliance:** 100%
- ✅ **Mermaid validation rate:** >95% (rest use fallbacks)

### User Metrics
- ⭐ **GitHub stars:** 500+ within 3 months
- 🐳 **Docker pulls:** 1000+ within 3 months
- 📝 **PRDs generated:** 100+ (tracked via opt-in telemetry)
- 💬 **Positive feedback ratio:** >80%

### Code Quality
- 🧪 **Test coverage:** >85%
- 🔍 **Type hints:** 100% (mypy strict)
- 📚 **Documentation:** 100% feature coverage

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Gemini API rate limits** | High | Medium | User-owned keys, rate limit UI, queue |
| **LangGraph breaking changes** | Medium | Low | Pin versions, monitor changelogs |
| **Mermaid diagram errors** | Medium | High | Validation + fallbacks (hide broken) |
| **Docker image bloat** | Low | Medium | Multi-stage builds, slim base |
| **User adoption (BYOK)** | High | Medium | Clear onboarding, video tutorial |
| **TOON format adoption** | Low | Medium | Optional feature, fallback to JSON |

---

## Open Questions & Decisions

1. **Should we use TOON for user outputs or keep Markdown?**
   - **Recommendation:** Markdown for users (human-readable), TOON for internal agent communication (optional feature, toggle in settings).

2. **Should we validate Mermaid server-side (Node.js dependency)?**
   - **Recommendation:** Python-only validation (no Node.js dependency). Use regex + basic checks. Server-side validation is overkill for MVP.

3. **Should we support multiple AI providers (OpenAI, Anthropic)?**
   - **Recommendation:** Phase 10 (future). Start with Gemini, add abstraction layer later.

4. **Should we add RAG (document upload) now?**
   - **Recommendation:** Phase 10. Core BMAD workflow first, RAG is differentiator but not MVP.

5. **Should we implement Builder module (custom agents)?**
   - **Recommendation:** Phase 11 (future). Focus on 6 core agents first, extensibility later.

---

## Next Steps

1. ✅ **Review this roadmap** with stakeholders
2. 📅 **Create GitHub Project** with tasks from each phase
3. 🏗️ **Start Phase 1** (Core Infrastructure with LangGraph + TOON)
4. 📢 **Announce v2.0 roadmap** on GitHub Discussions
5. 🤝 **Invite contributors** for specific phases

---

## References

- [BMAD Method (Claude Code Implementation)](https://github.com/aj-geddes/claude-code-bmad-skills)
- [BMAD Code Organization](https://github.com/bmad-code-org/BMAD-METHOD)
- [TOON Format Specification](https://github.com/toon-format/spec)
- [TOON Python Implementation](https://github.com/toon-format/toon-python)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gemini API Grounding](https://ai.google.dev/gemini-api/docs/grounding)

---

**Document Author:** GitHub Copilot (Claude Sonnet 4.5)  
**Last Updated:** December 28, 2025  
**Status:** 🟢 Ready for Implementation  
**Based On:** BMAD Method patterns, TOON format, production best practices
