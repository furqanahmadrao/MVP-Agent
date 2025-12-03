# MVP Agent

**AI-powered MVP Blueprint Generator for MCP Hackathon 2025 – Track 2: MCP In Action (Agents)**

Transform any startup idea into a complete, production-ready MVP specification in under 2 minutes. MVP Agent combines AI reasoning with real-time market research to deliver actionable blueprints that engineering teams can implement immediately.

## ✨ What You Get

Input a single paragraph describing your startup idea. Get back **8 comprehensive, production-ready markdown files** containing **18,000+ words of detailed specifications** (50% more depth than typical MVP specs). Pure markdown, no diagram dependencies.

- **📝 Overview.md** (~1,200 words) - High-level MVP overview, usage guidance for humans and LLM agents
- **📋 Features.md** (~3,000 words) - Prioritized feature requirements (P0, P1, P2) with user personas
- **🏗️ Architecture.md** (~3,300 words) - Technical stack, component tables, API surface, and scalability plans
- **🎨 Design.md** (~2,400 words) - UI/UX guidelines, design system, accessibility standards
- **🗺️ User Flow.md** (~2,000 words) - Complete user journeys (numbered, step-by-step) with decision trees
- **📅 Roadmap.md** (~3,000 words) - Detailed launch plan, technical debt management, and milestones
- **💼 Business_model.md** (~1,800 words) - Business model specification, unit economics, and go-to-market
- **🧪 Testing_plan.md** (~1,800 words) - Testing strategy, test cases, and quality gates
- **📦 ZIP Download** - All files packaged for your team

### 🌟 Quality Highlights
- **Production-Grade:** Specifications ready for implementation by senior devs or AI agents
- **AI-Friendly:** Structured formatting optimized for Cursor, Windsurf, and Claude Code
- **Comprehensive:** Covers user, business, and technical perspectives in depth
- **No Dependencies:** Pure markdown tables and text - no broken mermaid diagrams

All outputs are **opinionated**, **implementation-ready**, and use **structured markdown** for clarity.

---

## 🎬 Demo & Resources

- **📹 Demo Video:** [Watch on YouTube](https://youtu.be/rA8rnS_nzEg)
 - **📝 Blog Post:** [Read the full story](https://dev.to/furqanahmadrao/mvp-agent-ai-powered-mvp-blueprints-gradio-gemini-mcp-2mp5)
 - **💼 LinkedIn Post:** [Join the discussion](https://www.linkedin.com/posts/furqanahmadrao_mcp1stbirthday-ai-hackathon-activity-7393878758564339712-mvaq?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFNc81MBkk13VySrZD_UKhkgv7SAtdCaV48)

---

## 🎯 Live Demo

**Example ideas to test:**
- "An AI-powered meal planning app that helps busy professionals eat healthier by generating personalized weekly meal plans based on dietary restrictions and cooking skill level"
- "A vertical SaaS platform for managing compliance workflows for fintech startups, with automated audit trails and real-time regulatory updates"
- "A mobile app that uses AI to analyze your daily habits and suggest micro-optimizations for productivity, sleep, and mental health"

---

## 🧠 How It Works

MVP Agent is a **multi-phase autonomous agent** powered by Google Gemini and custom MCP servers:

### Phase 1: Intent Understanding 🧠
- **Model:** Gemini 2.5 Flash-Lite (fastest, cheapest for simple queries)
- Analyzes your idea to identify target users, core problems, and success metrics
- Generates strategic research queries (7 high-quality, focused queries)
- **Fallback:** Flash-Lite retry → Hardcoded queries

### Phase 2: Market Research 🔍
- **Model:** N/A (MCP server calls only)
- Uses **Google Custom Search MCP** to research competitors and market trends
- Gathers real user feedback and pain points from the web
- **Fallback:** Legacy research orchestrator

### Phase 3: Analysis & Synthesis 📊
- **Model:** Gemini 2.5 Flash (good balance of speed and quality)
- Identifies market gaps and opportunities
- Maps feature requirements to user needs
- Determines optimal technical architecture
- **Fallback:** Flash-Lite → Hardcoded summary

### Phase 4: Blueprint Generation ✨
- **Model:** Gemini 2.5 Pro (large context window for comprehensive MVP files)
- Creates 8 detailed markdown documents (overview, features, architecture, design, user_flow, roadmap, business_model, testing_plan)
- Generates structured tables and step-by-step flows
- Sanitizes markdown (removes invisible characters)
- Packages everything into a downloadable ZIP via **File Manager MCP**
- **Fallback:** Pro retry (35s delay for rate limits) → Hardcoded templates

**Total time:** ~60-90 seconds per blueprint

### 🤖 Model Selection Strategy

MVP Agent uses **intelligent model routing** to balance quality, speed, and cost:

| Phase | Primary Model | Fallback | Rationale |
|-------|--------------|----------|-----------|
| **Query Generation** | Flash-Lite | Flash-Lite retry | Simple task, needs speed |
| **Research** | N/A (MCP) | N/A | External API calls only |
| **Synthesis** | Flash | Flash-Lite | Good balance of speed & quality |
| **Generation** | **Pro** | Pro retry (35s wait) | Large context needed (18K+ words) |

**Why Pro for Generation?**
- Flash's context window is too small for generating 8 comprehensive files (~18,000 words)
- Pro handles large outputs in a single API call (no chunking needed)
- Pro has 2 RPM limit, but we generate all 8 files in **one request** (well under limit)
- Eliminates failed Flash attempts, saving ~15 seconds per generation

**Why Retry Same Model Instead of Downgrading?**
- If Pro fails, it's usually due to: transient network errors, rate limits, or API timeouts
- Downgrading to Flash-Lite makes no sense: if Pro (most capable) can't do it, Flash-Lite (least capable) definitely can't
- Retrying Pro after 35s delay respects the 2 RPM rate limit (30s minimum between calls)
- If Pro fails twice, we skip to hardcoded templates (no pointless downgrades)

---

## 🏗️ Architecture

MVP Agent runs **3 internal MCP servers** (auto-started, no manual setup needed):

1. **file-manager-mcp** (Port 8081)
   - Handles file creation, markdown validation, and robust ZIP packaging from in-memory content (fully integrated with agent logic)
   - Endpoints: `/create_file`, `/validate_markdown`, `/zip_files`, `/create_zip_from_memory`

2. **google-search-mcp** (Port 8082)
   - Performs Google Custom Search queries
   - Returns structured competitor and market data

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# GOOGLE_SEARCH_ENGINE_ID=your_cse_id (optional)

# Run the app
```

The app will:
1. ✅ Start all 3 MCP servers
---
## 🌐 Deploy on Hugging Face Spaces

This repository is **ready for one-click deployment** to HF Spaces:

### Steps:
1. **Fork/Clone** this Space or create a new Space from this repository
   ```
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_API_KEY=your_google_api_key (optional)
   GOOGLE_SEARCH_ENGINE_ID=your_cse_id (optional)
   ```
3. **Deploy** - HF will automatically:
   - Install dependencies from `requirements.txt`
   - Run `app.py`
   - Start all MCP servers
   - Expose the Gradio UI

### Required Secrets:
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optional Secrets (for full search capabilities):
- `GOOGLE_API_KEY` - Get from [Google Cloud Console](https://console.cloud.google.com/)
- `GOOGLE_SEARCH_ENGINE_ID` - Create at [Google Programmable Search](https://programmablesearchengine.google.com/)

**Note:** Without Google Search API, the agent uses placeholder data but still generates valid blueprints.

---

### Hugging Face Spaces — Best Practices

- Store API keys with the Spaces "Secrets" feature instead of in the repo or `.env` file.
- Pin package versions in `requirements.txt` for consistent builds across deployments.
- Use `share=False` for private spaces; set `share=True` only for public demos.
- Consider `Flash-Lite` for routine tasks to reduce token usage and cost.
- Limit concurrency or add batching for high-traffic Spaces to avoid API quota exhaustion.
- Add a short `short_description` and `tags` in README front-matter to improve discoverability (done).


---

## 🎨 UI Features

### Clean, Professional Interface
- **Orange/Black Theme** - High contrast, modern design with enhanced header typography
- **Real-time Status Updates** - See the agent's reasoning process with accurate elapsed time tracking
- **Tabbed Output** - Easy navigation between documents
- **Structured Markdown** - Clear tables and step-by-step flows
- **One-Click Download** - Get all files as ZIP

### Mobile Responsive
- Works perfectly on tablets and phones
- Touch-friendly controls
- Readable on all screen sizes

---

## 🔐 Environment Variables

### Required:
```bash
GEMINI_API_KEY=your_gemini_api_key
```
**Important:** Ensure these are correctly set in a `.env` file in the project root, or as secrets in your deployment environment. `load_dotenv()` is explicitly called to load these.

### Optional (for enhanced search):
```bash
GOOGLE_API_KEY=your_google_cloud_api_key
GOOGLE_SEARCH_ENGINE_ID=your_custom_search_engine_id
```

### API Rate Limits & Quotas:

**Gemini API (Free Tier):**
- **Flash-Lite:** 15 RPM (requests per minute)
- **Flash:** 15 RPM
- **Pro:** 2 RPM ⚠️

**Our Usage Pattern:**
- Phase 1: 1-2 Flash-Lite calls (query generation)
- Phase 3: 1 Flash call (synthesis)
- Phase 4: 1 Pro call (generation of all 8 files)
- **Total:** ~1 Pro call per blueprint = well within 2 RPM limit

**Google Custom Search (Free Tier):**
- 100 queries/day
- Configurable via `src/google_quota.py`

---

## 🧪 Testing

### MCP Health Check
```bash
python tests/mcp_health_check.py
```
Verifies all 3 MCP servers are running and responding correctly.

### Manual Testing Flow
1. Run `python app.py`
2. Enter a sample startup idea
3. Click "🎯 Generate MVP Blueprint"
4. Verify:
   - ✅ Status updates stream in real-time
   - ✅ All tabs populate with content (Overview first)
   - ✅ Structured markdown renders correctly
   - ✅ ZIP download appears and works

---

## 📂 Project Structure

```
mvp-agent/
├── app.py                    # Main Gradio application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── README.md                # This file
│
├── src/                     # Source code
│   ├── agent_brain.py       # Core agent logic
│   ├── ai_models.py         # Gemini API client
│   ├── mcp_http_clients.py  # MCP server HTTP clients
│   ├── mcp_process_manager.py # MCP server lifecycle
│   ├── file_manager.py      # File operations
│   ├── prompts.py           # AI prompts
│   ├── validators.py        # Input validation
│   ├── error_handler.py     # Error handling
│   ├── google_quota.py      # API quota management
│   └── hf_compat.py         # HF Spaces compatibility
│
├── tools/                   # Internal MCP servers
│   ├── file_manager_mcp/    # File operations MCP
│   ├── google_search_mcp/   # Search MCP
│   └── markdownify_mcp/     # Markdown formatting MCP
│
└── logs/                    # MCP server logs (gitignored)
```

---

## 🚀 Performance

- **Generation Time:** 60-90 seconds per blueprint
- **Concurrent Users:** ✅ Fully supports multiple simultaneous generations (no file conflicts)
- **Memory Usage:** ~500MB average per generation
- **Token Usage:** ~15,000-25,000 tokens per blueprint (varies by idea complexity)
- **Storage:** Zero persistent storage for markdown files; ZIPs are auto-deleted after 30 minutes

---

## 💾 Storage Architecture

**Optimized for Hugging Face Spaces and Multi-User Environments:**

- **In-Memory Markdown Generation:** All MVP files (features.md, architecture.md, etc.) are created and held in memory only—never written to disk.
 - **In-Memory Markdown Generation:** All MVP files (`overview.md`, `features.md`, `architecture.md`, `design.md`, `user_flow.md`, `roadmap.md`, `business_model.md`, `testing_plan.md`) are created and held in memory only—never written to disk.
- **Temporary ZIP Storage:** When a user requests a download, a ZIP file is created in the system temp directory.
- **Timeout-Based Cleanup:** ZIP files are automatically deleted 30 minutes after creation by a background thread. No persistent storage is used.
- **Concurrent-Safe:** Multiple users can generate and preview MVPs simultaneously without file conflicts or race conditions.
- **Preview Window:** Users can view and re-download their blueprint for up to 30 minutes before the ZIP is deleted.
- **Stateless Operation:** If the app/server restarts, unsaved work is lost—this is standard for stateless web apps and ensures efficient resource usage.

This architecture eliminates:
- ❌ Disk space issues
- ❌ Race conditions between users
- ❌ Manual cleanup requirements
- ❌ Storage quota concerns

---

## 🧹 File Cleanup & Retention

- All generated markdown files are kept in memory and never written to disk.
- ZIP files for download are stored in the system temp directory and deleted automatically after 30 minutes.
- This ensures users can preview and download their blueprints for a reasonable window, while preserving disk space and supporting multi-user concurrency.

---

---

## 🤝 Contributing

Contributions welcome! Ideas for improvement:

- [ ] Add more MCP tools (pricing intelligence, analytics)
- [ ] Support PDF/DOCX export formats
- [ ] Implement caching for research results
- [ ] Add user authentication and saved projects
- [ ] Extend to non-SaaS product types

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

Copyright (c) 2025 Furqan Ahmad (huggingface.co/furqanahmadrao)  
All rights reserved until November 30, 2025.  

This project is proprietary until that date and may not be copied, redistributed, or modified without permission.  
After November 30 2025, it will be released under the MIT License, allowing anyone to use, modify, and distribute it with proper attribution.


---

## 🏆 MCP 1st Birthday

This project was built for the **Model Context Protocol (MCP) 1st Birthday Hackathon 2025 - Track 2: MCP In Action (Agents)**.

**Track Requirements Met:**
- ✅ Gradio-based UI
- ✅ Multiple MCP server integration (3 custom servers)
- ✅ Planning → Reasoning → Execution flow
- ✅ Visible reasoning traces (real-time status updates)
- ✅ Production-ready outputs (overview.md + features.md + architecture.md + design.md + user_flow.md + roadmap.md + business_model.md + testing_plan.md)
- ✅ Good UX/UI (orange/black theme, mobile-friendly)
- ✅ Autonomous agent behavior
- ✅ Complete documentation

**Tag:** `mcp-in-action-track`

---

## 📞 Support

- **Issues:** Report bugs or request features via GitHub Issues
- **Questions:** Ask in the Community tab on Hugging Face
- **Demo:** Watch the demo video (coming soon)

---

**Built with ❤️ using Google Gemini, Gradio, and Model Context Protocol**

---

# December 2025 Update — README Sync with Current Codebase

This appendix brings the README fully in sync with the repository’s current state as of December 3, 2025. It documents the live code paths, MCP servers, environment variables, UI flows, agent orchestration, error handling, and health checks. It complements the sections above without removing them, so prior links continue to work.

If you are new, you can start here; otherwise, treat this as the authoritative delta against earlier README content.

## Tech Stack Overview
- Runtime/UI: Python 3.10+, Gradio 5.x (dark orange/black theme)
- LLMs: Google Gemini 2.5 models via google-generativeai (Pro, Flash, Flash-Lite)
- MCP-style internal tools: FastAPI + Uvicorn HTTP servers
  - file-manager-mcp (port 8081)
  - google-search-mcp (port 8082)
  - markdownify-mcp (port 8083)
- HTTP clients with retry/backoff: requests
- Async web search client and quota tracking: aiohttp + custom quota tracker
- Env management: python-dotenv

Key modules (src/):
- agent_brain.py — Orchestrates the 4 phases; model routing; fallbacks; status events
- ai_models.py — Gemini integration; JSON extraction; model router
- mcp_http_clients.py — HTTP clients for the three MCP servers with retries and local fallbacks
- mcp_process_manager.py — Starts/stops MCP servers and checks health before launching UI
- mcp_clients.py — Legacy research orchestrator (web-only), quota/caching policies
- file_manager.py — In-memory ZIP packaging with MCP-first, local fallback
- prompts.py — All prompt templates and formats for each phase
- validators.py — Input and output validators; sanitization
- error_handler.py — Structured logging, user-friendly errors, categories and severities
- google_quota.py — Daily quota tracking for Google Custom Search
- hf_compat.py — Shim for HF Hub OAuth imports across gradio/hf versions

Internal MCP servers (tools/):
- tools/file_manager_mcp: /health, /create_file, /validate_markdown, /zip_files, /create_zip_from_memory (8081)
- tools/google_search_mcp: /health, /search (8082)
- tools/markdownify_mcp: /health, /format (8083)

## Setup (Local)
1) Create a virtual environment and install deps

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure environment variables (create a .env at repo root)

Required:
```bash
GEMINI_API_KEY=your_gemini_api_key
```
Optional (enable real search and fine-tune quotas):
```bash
GOOGLE_API_KEY=your_google_cloud_api_key
GOOGLE_SEARCH_ENGINE_ID=your_cse_id
# Quota knobs for google custom search (used by src/google_quota.py)
GOOGLE_DAILY_QUOTA=100
GOOGLE_MAX_RESULTS_PER_REQUEST=10
GOOGLE_MAX_REQUESTS_PER_TASK=5
GOOGLE_RETRY_ATTEMPTS=3

# Override local MCP URLs if ports differ from defaults
FILE_MANAGER_MCP_URL=http://127.0.0.1:8081
GOOGLE_SEARCH_MCP_URL=http://127.0.0.1:8082
MARKDOWNIFY_MCP_URL=http://127.0.0.1:8083
```

3) Run the app
```bash
python app.py
```
The app will start three MCP servers automatically, verify their health, and then launch Gradio. If any server fails, the app exits with a clear message and log path.

## UI/UX Flow
- Inputs: Startup Idea (textbox), plus optional Advanced Configuration: Target Platform (dropdown), Preferred Tech Stack (textbox), Key Constraints (textbox)
- Status: Live “Agent Status - Mission Control” shows current phase, elapsed time, token usage, and a scrolling activity log with event levels (INFO/WARNING/ERROR/SUCCESS/DEBUG)
- Outputs: Eight tabs render the generated markdown files; a ZIP download button appears when complete

Note: The input label currently displays “estimated time: 8-10 min.” Actual runs typically complete faster on a healthy network and API (often ~1–3 minutes), but allow for retries/rate limits.

## Agent Workflow & Fallbacks
1) Planning — Generate 7 high-quality research queries (Gemini Flash-Lite; retry Flash-Lite → hardcoded queries)
2) Research — Web search via google-search-mcp; if unavailable, fall back to legacy orchestrator (web-only)
3) Synthesis — Summarize findings (Gemini Flash; fallback Flash-Lite → hardcoded summary)
4) Generation — Produce 8 markdown files in one shot (Gemini Pro); on failure, retry Pro after ~35s; final fallback provides basic templates

Model routing is defined in src/ai_models.py::ModelRouter, and token usage is tracked via GeminiClient. Status events with timestamps/elapsed seconds are emitted throughout src/agent_brain.py.

## Architecture
- app.py bootstraps MCP servers using MCPManager before serving the Gradio UI
- MCPManager starts tools/* MCP servers as subprocesses and performs HTTP health checks with log-tail diagnostics on failure
- All MCP servers expose /health and simple JSON endpoints; see tools/*/run.py for exact shapes
- File packaging: src/file_manager.py first attempts /create_zip_from_memory on file-manager-mcp; if that fails, it writes a temp ZIP locally and returns the path. No persistent markdown files are written.

Default ports:
- file-manager-mcp — 8081
- google-search-mcp — 8082
- markdownify-mcp — 8083

## Environment Variables (Complete)
Required
- GEMINI_API_KEY

Optional — Search & Quotas
- GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID
- GOOGLE_DAILY_QUOTA, GOOGLE_MAX_RESULTS_PER_REQUEST, GOOGLE_MAX_REQUESTS_PER_TASK, GOOGLE_RETRY_ATTEMPTS

Optional — MCP URLs (override defaults if needed)
- FILE_MANAGER_MCP_URL, GOOGLE_SEARCH_MCP_URL, MARKDOWNIFY_MCP_URL

## Error Handling & Logging
- Structured error classes with categories (API, VALIDATION, FILESYSTEM, NETWORK, PARSING, CONFIGURATION, UNKNOWN) and severities (LOW→CRITICAL) in src/error_handler.py
- Daily log file written to logs/mvp_agent_YYYYMMDD.log; MCP server logs written to logs/file-manager-mcp.log, logs/google-search-mcp.log, logs/markdownify-mcp.log
- User-facing errors include helpful guidance; technical details captured in logs for diagnostics

## Health Checks
If the UI fails to start, check MCP health endpoints directly in another terminal:
```bash
curl -s http://127.0.0.1:8081/health
curl -s http://127.0.0.1:8082/health
curl -s http://127.0.0.1:8083/health
```
If any are unhealthy, see the tail of their logs under logs/*.log as reported by MCPManager error messages.

## Testing (Manual)
There is no tests/ directory in this repo at present. Use this quick manual flow instead:
1) Run: python app.py
2) Enter a sample idea and click “Generate MVP Blueprint”
3) Verify: status events stream; all eight tabs populate; the ZIP download appears; ZIP contains 9 files (8 markdown + a readme for the bundle)
4) If Google keys are set, confirm that research steps mention google-search-mcp with non-empty results; without keys, placeholder research will be used

## Hugging Face Spaces
- Works out of the box; set required/optional secrets (GEMINI_API_KEY, GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID) in Space settings
- The app is single-process: Spaces will run app.py, which starts child MCP servers and exposes the UI
- For public Spaces, consider API rate limits (Pro ~2 RPM). The code already spaces calls and retries Pro after ~35s when necessary.

## Differences vs Previous README
- Corrected MCP server list and documented all three with default ports and endpoints
- Clarified environment overrides for MCP URLs and Google Custom Search quota tuning
- Replaced reference to a non-existent tests/ directory with actionable manual checks
- Documented current UI inputs (Platform, Tech Preference, Constraints) and live status metrics
- Made ZIP packaging details explicit (in-memory first; local temp fallback)
- Added logging/error handling section with file paths and categories
- Reiterated model-routing and fallbacks exactly as implemented in src/agent_brain.py and src/ai_models.py

---

This section is maintained to reflect the code as of 2025-12-03. If you change ports, env keys, MCP endpoints, or UI flows, please update this appendix accordingly.
