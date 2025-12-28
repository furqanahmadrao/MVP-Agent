# MVP Agent v2.0 - Production Migration Roadmap

**Document Version:** 1.0  
**Date:** December 28, 2025  
**Status:** Planning Phase  

---

## Executive Summary

This document outlines a comprehensive, phase-by-phase migration strategy to transform MVP Agent from a hackathon prototype into a production-ready, open-source application. The migration focuses on:

1. **User-owned API keys** - Remove dependency on maintainer's API credentials
2. **Framework modernization** - Migrate from custom Python agents to LangChain
3. **Simplified search** - Replace Google Custom Search MCP with Gemini Search Grounding
4. **Enhanced UX** - Replace tabbed views with code editor-style interface
5. **Production infrastructure** - Docker containerization and deployment readiness
6. **PRD generation** - Upgrade from MVP blueprints to full Product Requirements Documents

---

## Research Findings

### 1. Gemini Search Grounding Analysis

**Key Capabilities:**
- **Built-in web search** - No separate Google API required
- **Automatic query generation** - Model decides when to search
- **Citation support** - Returns `groundingMetadata` with sources, URIs, and text segments
- **Free tier availability** - Included with Gemini API (billing starts Jan 5, 2026)
- **Supported models:** Gemini 2.5 Pro, Flash, Flash-Lite, 2.0 Flash

**Rate Limits:**
- Current Gemini API free tier: 15 RPM (requests per minute), 1500 RPD (requests per day)
- With user-provided keys, limits are per-user (much higher aggregate throughput)

**Implementation Pattern:**
```python
from google import genai
from google.genai import types

grounding_tool = types.Tool(google_search=types.GoogleSearch())
config = types.GenerateContentConfig(tools=[grounding_tool])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="research query",
    config=config
)
# Access: response.candidates[0].grounding_metadata
```

**Benefits over current Google Search MCP:**
- ✅ No separate API key/CX ID required
- ✅ Automatic query optimization by model
- ✅ Integrated citations and source tracking
- ✅ Lower barrier to entry for users
- ❌ Less control over exact queries (trade-off for simplicity)

---

### 2. LangChain Framework Analysis

**Why LangChain?**
- **Pre-built agents** - ReAct, Structured Chat, OpenAI Functions agents
- **Tool orchestration** - Native support for function calling, tools, and chains
- **Memory management** - Built-in conversation and context memory
- **Streaming support** - Real-time status updates
- **Observability** - LangSmith integration for debugging
- **RAG support** - Vector stores, retrievers, document loaders

**Migration Strategy:**
- Replace `src/agent_brain.py` orchestration with `LangGraph` (LangChain's agent framework)
- Convert MCP tools to LangChain `Tool` objects
- Use `ConversationBufferMemory` for multi-phase context
- Implement streaming callbacks for real-time UI updates

**Current vs. Future Architecture:**

| Current (Custom) | Future (LangChain) |
|------------------|-------------------|
| Custom phase orchestration | LangGraph state machine |
| Manual prompt construction | Prompt templates + chains |
| Custom tool calling | `@tool` decorators |
| Manual token tracking | Built-in callbacks |
| Custom retry logic | Exponential backoff utilities |

---

### 3. PRD Best Practices Research

**Industry Standard PRD Components:**

1. **Executive Summary**
   - Product vision and goals
   - Success metrics
   - Target audience

2. **Problem Statement**
   - User pain points
   - Market opportunity
   - Competitive landscape

3. **Proposed Solution**
   - Feature specifications (detailed)
   - User stories and use cases
   - Acceptance criteria

4. **Technical Architecture**
   - System diagrams (Mermaid)
   - Tech stack rationale
   - Database schema
   - API specifications

5. **UX/UI Design**
   - User flows (step-by-step)
   - Wireframes (textual descriptions)
   - Design system guidelines
   - Accessibility requirements

6. **Development Roadmap**
   - Phased releases (MVP, v1.0, v2.0)
   - Sprint planning
   - Resource allocation

7. **Business Model**
   - Revenue streams
   - Cost structure
   - Go-to-market strategy

8. **Testing & QA Strategy**
   - Test cases
   - Performance benchmarks
   - Security considerations

9. **Risk Assessment**
   - Technical risks
   - Market risks
   - Mitigation strategies

10. **Appendix**
    - Research citations
    - Glossary
    - Mermaid diagrams

**Additions to Current MVP Agent Output:**
- Add Mermaid diagrams (architecture, user flows, database schemas)
- Add acceptance criteria for each feature
- Add API specifications (if applicable)
- Add security/compliance section
- Add risk assessment matrix

---

### 4. Community Pain Points (Reddit Research)

**Top Issues with MVP/PRD Generators:**

1. **Generic, templated output** - "Sounds like ChatGPT wrote it" feedback
2. **Lack of market validation** - No real competitor data or user pain points
3. **Missing financial modeling** - Revenue projections, CAC, LTV calculations
4. **No iteration support** - Can't refine or regenerate specific sections
5. **Poor export formats** - PDF exports lose formatting, no version control
6. **No collaboration features** - Can't share or co-edit with team members
7. **Overpromising on scope** - MVPs try to do too much (scope creep)

**Opportunities for Differentiation:**
- ✅ **Real web research** (already doing this, enhance with Gemini Grounding)
- ✅ **Editable outputs** (new code editor interface)
- ✅ **Version control ready** (markdown + Git-friendly)
- 🆕 **Iteration support** (regenerate single sections)
- 🆕 **Export options** (PDF, Notion, Markdown, JSON)
- 🆕 **Collaboration** (shareable links, team workspaces - future)

---

## Phase-by-Phase Migration Plan

### **Phase 1: API Key Management & Settings UI** ⏱️ 2-3 days

**Goal:** Allow users to provide their own Gemini API key via settings page.

**Tasks:**
1. **Create settings page** (`src/settings.py`)
   - API key input field (password-masked)
   - Model selection (Pro/Flash/Flash-Lite)
   - Rate limit configuration
   - Save to browser localStorage (Gradio persistent state)

2. **Update `app.py`**
   - Add "Settings" tab to Gradio interface
   - Load API key from settings (fallback to env var for testing)
   - Display current API key status (masked)

3. **Update `src/agent_brain.py`**
   - Accept API key as constructor parameter
   - Remove hardcoded env var dependency

4. **Add validation**
   - Test API key on save
   - Show error if invalid
   - Display rate limit status

**Deliverables:**
- ✅ Settings page with API key input
- ✅ Persistent API key storage (local)
- ✅ API key validation
- ✅ Updated README with "Bring Your Own Key" instructions

---

### **Phase 2: Gemini Search Grounding Migration** ⏱️ 2-3 days

**Goal:** Replace Google Custom Search MCP with Gemini Search Grounding.

**Tasks:**
1. **Remove Google Search MCP**
   - Delete `tools/google_search_mcp/`
   - Remove from `src/mcp_process_manager.py`
   - Remove Google API env vars from `.env.example`

2. **Implement Gemini Grounding**
   - Update `src/ai_models.py` to support `google_search` tool
   - Create `generate_with_grounding()` method
   - Parse `groundingMetadata` and extract sources

3. **Update research phase** (`src/agent_brain.py`)
   - Replace MCP search calls with Gemini Grounding
   - Format grounding results for synthesis phase
   - Add citation tracking

4. **Update prompts** (`src/prompts.py`)
   - Remove explicit search query generation prompt
   - Add guidance for grounding-based research
   - Ensure citations are included in outputs

**Deliverables:**
- ✅ Google Search MCP removed
- ✅ Gemini Grounding integrated
- ✅ Citation support in generated documents
- ✅ Reduced API key complexity (one key vs. three)

---

### **Phase 3: Code Editor UI** ⏱️ 4-5 days

**Goal:** Replace tabbed file view with Monaco/CodeMirror-style editor interface.

**Tasks:**
1. **Research Gradio code editor options**
   - Evaluate `gr.Code` component
   - Consider custom HTML/JS with Monaco Editor
   - Plan sidebar + editor layout

2. **Implement file browser sidebar**
   - Collapsible file tree (8 markdown files)
   - Active file highlighting
   - File icons (markdown icon)

3. **Implement code editor pane**
   - Syntax highlighting (Markdown)
   - Read-only mode (user can copy/edit locally)
   - Line numbers
   - Search/replace within editor

4. **Update generation flow**
   - Show terminal-style status during generation (Phase 1)
   - On completion, hide status and show editor UI (Phase 2)
   - Default to `overview.md` opened
   - Add "Download All as ZIP" button in editor view

5. **Add export options**
   - Download individual file
   - Download all as ZIP
   - Copy to clipboard
   - (Future: Export to Notion, Google Docs)

**Deliverables:**
- ✅ Code editor-style interface
- ✅ File browser sidebar
- ✅ Syntax-highlighted Markdown preview
- ✅ Individual file download
- ✅ Seamless transition from generation to editor view

---

### **Phase 4: LangChain Migration** ⏱️ 5-7 days

**Goal:** Migrate from custom orchestration to LangChain/LangGraph.

**Tasks:**
1. **Set up LangChain environment**
   - Add `langchain`, `langchain-google-genai`, `langgraph` to `requirements.txt`
   - Create `src/langchain_agent.py`

2. **Define LangChain tools**
   - Convert Markdownify MCP to `@tool` decorator
   - Convert File Manager to LangChain tool
   - Define Gemini Grounding as tool

3. **Implement LangGraph agent**
   - Define state nodes: `plan`, `research`, `synthesize`, `generate`
   - Add conditional edges (error handling, retry logic)
   - Implement streaming callbacks for UI updates

4. **Migrate prompts to LangChain**
   - Convert `src/prompts.py` to `ChatPromptTemplate`
   - Use `MessagesPlaceholder` for context

5. **Update `src/agent_brain.py`**
   - Replace custom orchestration with LangGraph runner
   - Keep existing public API (`generate_mvp()`)
   - Add streaming support

6. **Testing & validation**
   - Compare outputs with old system
   - Verify token usage tracking
   - Test error scenarios

**Deliverables:**
- ✅ LangChain-based agent orchestration
- ✅ Tool integration (Gemini, File Manager)
- ✅ Streaming status updates
- ✅ Backward-compatible public API

---

### **Phase 5: PRD Enhancement & Mermaid Diagrams** ⏱️ 3-4 days

**Goal:** Upgrade from MVP blueprints to full PRD-compliant documents.

**Tasks:**
1. **Update document templates** (`src/prompts.py`)
   - Add sections: Acceptance Criteria, Risk Assessment, API Specs
   - Enhance existing sections with PRD best practices
   - Add Mermaid diagram requirements

2. **Implement Mermaid diagram generation**
   - Add to `architecture.md`: System architecture diagram
   - Add to `user_flow.md`: User flow diagrams (per persona)
   - Add to `roadmap.md`: Gantt chart
   - Add to new `database_schema.md`: ERD

3. **Add new PRD documents**
   - `api_specification.md` (if applicable)
   - `security_compliance.md`
   - `risk_assessment.md`
   - Total: 11 files (up from 8)

4. **Enhance research synthesis**
   - Extract financial modeling data (pricing, CAC, LTV)
   - Add competitive feature matrix
   - Include SWOT analysis

5. **Add diagram validation**
   - Use Mermaid CLI to validate syntax (optional)
   - Provide rendering instructions in README

**Deliverables:**
- ✅ 11 PRD-compliant markdown files
- ✅ 4-5 Mermaid diagrams per project
- ✅ Enhanced research synthesis
- ✅ Financial modeling section

---

### **Phase 6: Docker Containerization** ⏱️ 2-3 days

**Goal:** Create single-container Docker image for easy deployment.

**Tasks:**
1. **Create Dockerfile**
   - Base image: `python:3.10-slim`
   - Install dependencies
   - Copy source files
   - Expose Gradio port (7860)
   - Set entrypoint to `python app.py`

2. **Optimize Docker image**
   - Multi-stage build
   - Minimize layers
   - Use `.dockerignore`
   - Target size: <500MB

3. **Create docker-compose.yml**
   - Single service definition
   - Environment variable passthrough
   - Volume mounts for logs
   - Port mapping

4. **Update documentation**
   - Add Docker setup instructions to README
   - Provide docker-compose example
   - Document environment variables

5. **Publish to registries**
   - GitHub Container Registry: `ghcr.io/furqanahmadrao/mvp-agent`
   - Docker Hub: `furqanahmadrao/mvp-agent`
   - Add automatic builds (GitHub Actions)

**Deliverables:**
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ Published Docker images
- ✅ Deployment documentation

---

### **Phase 7: Production Hardening** ⏱️ 3-4 days

**Goal:** Add production-ready features: error handling, logging, monitoring.

**Tasks:**
1. **Enhanced error handling**
   - Retry logic with exponential backoff
   - User-friendly error messages
   - Error recovery (fallback to cached data)
   - Graceful degradation

2. **Logging & monitoring**
   - Structured logging (JSON format)
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Rotate log files
   - Optional: OpenTelemetry integration

3. **Rate limiting**
   - Per-user rate limiting (based on API key)
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
- ✅ Comprehensive logging
- ✅ Rate limiting
- ✅ Security best practices

---

### **Phase 8: Advanced Features (Optional)** ⏱️ 5-7 days

**Goal:** Add differentiated features based on community feedback.

**Tasks:**
1. **Iteration support**
   - "Regenerate Section" button per document
   - Provide context from other documents
   - Version history (local storage)

2. **Multi-format export**
   - PDF generation (with Mermaid diagrams rendered)
   - Notion import format
   - JSON export (structured data)

3. **Templates & presets**
   - Industry-specific templates (SaaS, E-commerce, Mobile App)
   - Pre-configured tech stacks
   - Customizable output structure

4. **RAG enhancement**
   - Upload existing documents (competitor PRDs, research)
   - Vector store for context retrieval
   - Reference existing projects

5. **Collaboration (future)**
   - Shareable project links
   - Team workspaces
   - Comment threads (per section)

**Deliverables:**
- ✅ Section regeneration
- ✅ PDF export
- ✅ Industry templates
- ✅ RAG support (optional)

---

## Technology Stack Summary

### Current Stack
- **Language:** Python 3.10+
- **UI:** Gradio 5.49.1
- **AI:** Google Gemini (via `google-generativeai`)
- **Tools:** Custom MCP servers (Python FastAPI)
- **Deployment:** Local Python script

### Future Stack (v2.0)
- **Language:** Python 3.10+
- **UI:** Gradio (with Monaco Editor integration)
- **AI:** Google Gemini + LangChain
- **Framework:** LangChain + LangGraph
- **Search:** Gemini Search Grounding (built-in)
- **Deployment:** Docker container
- **Diagrams:** Mermaid.js
- **Storage:** Gradio persistent state (local), future: SQLite/PostgreSQL

---

## Dependency Changes

### Packages to Add
```txt
# LangChain ecosystem
langchain==0.3.10
langchain-google-genai==2.0.7
langgraph==0.2.60
langchain-community==0.3.10

# Diagram rendering (optional, for validation)
mermaid-py==0.3.0

# PDF generation (Phase 8)
weasyprint==62.3
markdown2==2.5.0
```

### Packages to Remove
```txt
# No longer needed with Gemini Grounding
# (None - Google Search MCP was custom code)
```

### MCP Servers Status
- ❌ **Google Search MCP** - REMOVED (replaced by Gemini Grounding)
- ⚠️ **File Manager MCP** - MIGRATE to LangChain tool (keep functionality)
- ⚠️ **Markdownify MCP** - MIGRATE to LangChain tool (keep functionality)

*Alternative:* Instead of removing MCPs entirely, convert them to LangChain tools. This maintains modularity while gaining LangChain benefits.

---

## File Structure Changes

### New Files
```
MVP-Agent/
├── src/
│   ├── langchain_agent.py       # NEW: LangGraph orchestration
│   ├── langchain_tools.py        # NEW: Tool definitions
│   ├── settings.py               # NEW: Settings page logic
│   ├── export_utils.py           # NEW: PDF/Notion export
│   └── templates.py              # NEW: Industry templates
├── Dockerfile                    # NEW
├── docker-compose.yml            # NEW
├── .dockerignore                 # NEW
└── MIGRATION_ROADMAP.md          # THIS FILE
```

### Modified Files
```
MVP-Agent/
├── app.py                        # Add settings tab, editor UI
├── src/
│   ├── agent_brain.py            # Refactor to use LangChain
│   ├── ai_models.py              # Add Gemini Grounding support
│   ├── prompts.py                # Enhance for PRD, Mermaid
│   ├── file_manager.py           # Add export functions
│   └── mcp_process_manager.py    # Remove Google Search MCP
├── requirements.txt              # Add LangChain, remove unused
└── README.md                     # Update for v2.0 features
```

### Removed Files
```
MVP-Agent/
└── tools/
    └── google_search_mcp/        # DELETE entire directory
        ├── run.py
        └── server.json
```

---

## Testing Strategy

### Unit Tests
- API key validation
- Gemini Grounding parsing
- LangChain tool execution
- Mermaid diagram syntax validation
- File export (ZIP, PDF, JSON)

### Integration Tests
- End-to-end MVP/PRD generation
- Settings persistence
- Editor UI interactions
- Docker container startup

### Performance Tests
- Response time per phase
- Token usage tracking
- Rate limit compliance
- Memory footprint (Docker)

### User Acceptance Tests
- Generate 5 sample PRDs (different industries)
- Compare output quality (v1 vs. v2)
- Verify all Mermaid diagrams render
- Test Docker deployment on 3 platforms (Linux, macOS, Windows/WSL)

---

## Rollout Plan

### Stage 1: Alpha (Internal Testing)
- Complete Phases 1-4
- Deploy to local Docker container
- Generate 10 test PRDs
- Collect feedback

### Stage 2: Beta (Limited Release)
- Complete Phases 5-7
- Publish to GitHub Container Registry
- Invite 20 beta testers
- Iterate based on feedback

### Stage 3: Public Release
- Complete Phase 8 (optional features)
- Publish to Docker Hub
- Announce on Reddit, Product Hunt, Hacker News
- Monitor GitHub Issues

### Stage 4: Iteration
- Implement community feature requests
- Add integrations (Notion, Figma, Jira)
- Explore SaaS offering (hosted version)

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Gemini API rate limits** | High | Medium | User-owned keys, rate limit UI, queue system |
| **LangChain breaking changes** | Medium | Low | Pin versions, monitor changelogs |
| **Mermaid diagram errors** | Low | Medium | Syntax validation, fallback to text |
| **Docker image bloat** | Medium | Medium | Multi-stage builds, alpine base |
| **User adoption (BYOK)** | High | Medium | Clear onboarding, video tutorial |
| **Output quality regression** | High | Low | A/B testing, user feedback loop |

---

## Success Metrics

### Technical Metrics
- ⏱️ **Generation time:** <5 minutes per PRD (down from 10 minutes)
- 💾 **Docker image size:** <500MB
- 📊 **Token efficiency:** <50k tokens per PRD (with grounding)
- ⚡ **Rate limit compliance:** 100% (no user-reported errors)

### User Metrics
- ⭐ **GitHub stars:** 500+ within 3 months
- 🐳 **Docker pulls:** 1000+ within 3 months
- 📝 **PRDs generated:** 100+ (tracked via optional telemetry)
- 💬 **Positive feedback ratio:** >80% (GitHub Issues + Reddit)

### Community Metrics
- 🔧 **Contributors:** 5+ active contributors
- 🐛 **Issues closed:** <48 hour avg response time
- 📚 **Documentation:** 100% feature coverage
- 🌍 **Translations:** 3+ languages (future)

---

## Open Questions & Decisions Needed

1. **Should we keep File Manager & Markdownify as MCPs or convert to LangChain tools?**
   - **Recommendation:** Convert to LangChain tools for simplicity. MCPs add deployment complexity.

2. **Should we support multiple AI providers (OpenAI, Anthropic, local models)?**
   - **Recommendation:** Phase 9 (future). Start with Gemini, add abstraction layer later.

3. **Should we build a hosted SaaS version or keep it self-hosted only?**
   - **Recommendation:** Start self-hosted (open source), evaluate SaaS based on demand.

4. **Should we add user authentication (for saving projects)?**
   - **Recommendation:** Phase 9. Start with local storage (Gradio state), add auth later.

5. **Should we implement RAG now or defer to Phase 8?**
   - **Recommendation:** Defer to Phase 8. Core features first, RAG is differentiator but not MVP.

---

## Timeline Estimate

| Phase | Duration | Dependencies | Completion Date (Est.) |
|-------|----------|--------------|------------------------|
| Phase 1: API Key Management | 2-3 days | None | Jan 2, 2026 |
| Phase 2: Gemini Grounding | 2-3 days | Phase 1 | Jan 5, 2026 |
| Phase 3: Code Editor UI | 4-5 days | Phase 2 | Jan 11, 2026 |
| Phase 4: LangChain Migration | 5-7 days | Phase 3 | Jan 19, 2026 |
| Phase 5: PRD Enhancement | 3-4 days | Phase 4 | Jan 23, 2026 |
| Phase 6: Docker | 2-3 days | Phase 5 | Jan 26, 2026 |
| Phase 7: Production Hardening | 3-4 days | Phase 6 | Jan 30, 2026 |
| Phase 8: Advanced Features | 5-7 days | Phase 7 | Feb 7, 2026 |

**Total Estimated Time:** 26-36 days (4-6 weeks)  
**Target Public Release:** Early February 2026

---

## Next Steps

1. ✅ **Review this document** with stakeholders
2. 📅 **Create GitHub Project** with tasks from each phase
3. 🏗️ **Start Phase 1** (API Key Management)
4. 📢 **Announce v2.0 roadmap** on GitHub Discussions
5. 🤝 **Invite contributors** for specific phases

---

## References

- [Gemini API Grounding Documentation](https://ai.google.dev/gemini-api/docs/grounding)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [PRD Best Practices - ProductPlan](https://www.productplan.com/glossary/product-requirements-document/)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [Gradio Custom Components](https://www.gradio.app/guides/custom-components-in-five-minutes)

---

**Document Author:** GitHub Copilot (Claude Sonnet 4.5)  
**Last Updated:** December 28, 2025  
**Status:** 🟢 Ready for Review
