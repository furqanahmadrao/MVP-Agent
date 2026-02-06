# MVP Agent v2.0 - Repository Guidelines & Agent Architecture

This document provides comprehensive information for developers, contributors, and AI agents working with the MVP Agent codebase.

---

## 🏗️ Project Structure & Module Organization

### Core Files
- **`app.py`**: Main Gradio entry point that orchestrates the UI and agent workflow
- **`.env.example`**: Template for environment configuration
- **`Dockerfile`**: Production-ready container (runs as non-root user)
- **`.dockerignore`**: Prevents secrets and unnecessary files from entering Docker builds
- **`requirements.txt`**: Python dependencies with pinned versions

### Source Directory (`src/`)

#### Core Logic
- **`workflow.py`**: LangGraph workflow orchestrator for multi-agent system
- **`agent_state.py`**: State management for workflow phases and agent communication
- **`agent_brain.py`**: Core agent intelligence and decision-making logic
- **`settings.py`**: Settings manager with UI configuration interface
- **`generation_state.py`**: Real-time state tracking for generation process

#### Agent Implementations (`src/agents/`)
Six specialized agents following the BMAD methodology:
1. **`market_analyst.py`**: Market research with Google Search grounding
2. **`financial_modeler.py`**: 3-year financial projections and unit economics
3. **`prd_generator.py`**: PRD, feature prioritization, and competitive analysis
4. **`architect.py`**: System architecture and tech stack selection
5. **`ux_designer.py`**: User flows, wireframes, and design systems
6. **`sprint_planner.py`**: Roadmap, testing strategy, and deployment guide

#### Supporting Modules
- **`prompts.py`**: Centralized prompt templates for all agents
- **`enhanced_prompts.py`**: Advanced prompt engineering utilities
- **`helpers.py`**: BMAD methodology helpers and utilities
- **`industry_templates.py`**: Industry-specific templates (SaaS, Fintech, Healthtech, etc.)
- **`toon_utils.py`**: Token optimization utilities (TOON format)
- **`validators.py`**: Input validation and sanitization
- **`error_handler.py`**: Centralized error handling
- **`file_manager.py`**: Secure file operations manager
- **`editor_page.py`**: Code editor UI components
- **`styles.py`**: Global CSS and UI styling
- **`ai_models.py`**: AI model configuration and selection
- **`google_quota.py`**: API quota management
- **`grounding_agent.py`**: Google Search grounding integration
- **`mcp_clients.py`**: MCP service client implementations
- **`mcp_http_clients.py`**: HTTP-based MCP clients
- **`mcp_process_manager.py`**: MCP service lifecycle management
- **`hf_compat.py`**: Hugging Face Spaces compatibility layer

### Tools Directory (`tools/`)

MCP (Model Context Protocol) services for secure file operations:
- **`file_manager_mcp/`**: File creation and management service (Port 8081)
  - Secure path validation
  - Input sanitization
  - Localhost-only binding
- **`markdownify_mcp/`**: Markdown formatting and validation service (Port 8082)
  - HTML to Markdown conversion
  - Format validation
  - Localhost-only binding

### Documentation Files
- **`README.md`**: User-facing documentation and quick start
- **`AGENTS.md`**: This file - developer and AI agent guidelines
- **`SECURITY_FIXES_APPLIED.md`**: Completed security fixes (Phase 1: 7/8 completed)
- **`SECURITY_REVIEW_FINDINGS.md`**: Full security audit report
- **`SECURITY_ISSUES_TRACKER.md`**: Ongoing security issues tracking
- **`LICENSE`**: MIT License

---

## 🚀 Build, Test, and Development Commands

### Initial Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Application
```bash
# Run main application (port 7860)
python app.py

# Run editor demo with sample data (port 7861)
python test_demo.py
```

### Docker Commands
```bash
# Build Docker image
docker build -t mvp-agent .

# Run container (non-root user for security)
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key_here mvp-agent

# Run with environment file
docker run -p 7860:7860 --env-file .env mvp-agent
```

### Development Workflow
```bash
# Check Python version
python --version  # Should be 3.10+

# View logs (if running)
# Logs are displayed in the Gradio terminal UI

# Manual testing
python test_demo.py
```

---

## 💻 Coding Style & Naming Conventions

### Python Style
- **Follow PEP 8** conventions with 4-space indentation
- **Use `snake_case`** for functions and variables
- **Use `PascalCase`** for classes
- **No formatter/linter** is currently enforced - keep diffs minimal and readable

### Code Organization
- **Prompts**: Keep all prompt templates centralized in `src/prompts.py` and `src/enhanced_prompts.py`
- **Long strings**: Avoid inline long strings - move to prompt files or configuration
- **Imports**: Group imports (standard library, third-party, local) with blank lines between
- **Type hints**: Use type hints where they add clarity, especially for function signatures

### Naming Patterns
```python
# Functions and variables
def generate_prd_document():
    user_input = "..."
    
# Classes
class MarketAnalystAgent:
    pass
    
# Constants
MAX_RETRIES = 3
DEFAULT_MODEL = "gemini-2.5-flash"
```

---

## 🧪 Testing Guidelines

### Current Testing Setup
- **No automated test runner** is currently configured
- **Manual testing** is the primary approach
- Tests are welcome - prefer `pytest` and name files `test_*.py`

### Manual Testing
```bash
# Test editor UI with sample data
python test_demo.py

# Test full generation workflow
python app.py
# Then use the Gradio UI to test generation
```

### Adding Tests
If you add tests:
1. Use `pytest` framework
2. Name test files with `test_` prefix
3. Place in a `tests/` directory
4. Update `.gitignore` if needed

---

## 📝 Commit & Pull Request Guidelines

### Commit Messages
- Use short, imperative summaries (e.g., "Add financial modeling agent")
- Examples from this repo:
  - "Enhance generation process with better error handling"
  - "Fix path traversal vulnerability in file manager"
  - "Update Docker configuration for security"

### Pull Request Requirements
A good PR should include:
1. **Clear description** of what changed and why
2. **Security considerations** if touching sensitive areas
3. **Screenshots or GIFs** for UI changes
4. **Testing notes** - what you tested and how

### Review Process
- PRs should be reviewed for:
  - Code quality and style consistency
  - Security implications
  - Breaking changes
  - Documentation updates

---

## 🔒 Security & Configuration

### Environment Configuration
```bash
# Required environment variables
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional settings (can also be set in UI)
use_toon_format=true
project_level_auto_detect=true
```

### Security Best Practices
1. **Never commit secrets** - always use `.env` file
2. **Keep API keys secure** - don't log or display them
3. **Validate all inputs** - use `validators.py` utilities
4. **Use secure paths** - follow patterns in `file_manager.py`
5. **Bind services locally** - MCP services use `127.0.0.1` only

### File Security
- **`.gitignore`**: Excludes `.env`, `user_settings.json`, and sensitive files
- **`.dockerignore`**: Prevents secrets from entering Docker builds
- **Path validation**: All file operations validate paths against directory traversal

---

## 🔒 Security Status & Recent Fixes

### Latest Security Update
**Date:** February 6, 2026  
**Status:** ✅ Phase 1 Critical Fixes COMPLETED (7/8 issues resolved)  
**Deployment Readiness Score:** 7.5/10 (improved from 6/10)

### Completed Security Fixes

#### 1. ✅ Path Traversal Vulnerability - FIXED
- **Severity:** CRITICAL (CVSS 9.1)
- **Location:** `tools/file_manager_mcp/run.py`
- **Fix:** Implemented proper path resolution and validation
- **Impact:** Prevents arbitrary file access outside project directory

#### 2. ✅ MCP Services Network Exposure - FIXED
- **Severity:** CRITICAL (CVSS 8.8)
- **Location:** Both MCP service files
- **Fix:** Changed binding from `0.0.0.0` to `127.0.0.1`
- **Impact:** Services only accessible from localhost

#### 3. ✅ Docker Container Running as Root - FIXED
- **Severity:** HIGH (CVSS 7.5)
- **Location:** `Dockerfile`
- **Fix:** Container now runs as non-root user `appuser`
- **Impact:** Reduced container compromise impact

#### 4. ✅ Missing .dockerignore - FIXED
- **Severity:** HIGH (CVSS 6.5)
- **Fix:** Created comprehensive `.dockerignore` file
- **Impact:** Prevents secret leakage in Docker builds

#### 5. ✅ Missing Dependencies - FIXED
- **Severity:** HIGH (CVSS 6.0)
- **Location:** `requirements.txt`
- **Fix:** Added fastapi, uvicorn, markdownify with pinned versions
- **Impact:** Proper dependency management

#### 6. ✅ Input Validation - FIXED
- **Severity:** HIGH (CVSS 7.3)
- **Location:** `tools/file_manager_mcp/run.py` and `app.py`
- **Fix:** Added comprehensive Pydantic validators
- **Impact:** Prevents injection attacks

#### 7. ✅ User Settings in Git - FIXED
- **Severity:** MEDIUM (CVSS 5.3)
- **Location:** `.gitignore`
- **Fix:** Added `user_settings.json` and `*.json` to gitignore
- **Impact:** Prevents accidental secret commits

### Remaining Issues (1)
1. **Thread Safety** in `GenerationStateManager` - In progress

### Security Documentation
For detailed information, see:
- **`SECURITY_FIXES_APPLIED.md`**: Complete list of fixes with code examples
- **`SECURITY_REVIEW_FINDINGS.md`**: Full security audit (26 issues identified)
- **`SECURITY_ISSUES_TRACKER.md`**: Ongoing issues and remediation plan

---

## 🤖 Agent Architecture (BMAD Methodology)

### The 6 Specialized Agents

#### Phase 1: Analysis (20% of workflow)
1. **Market Analyst Agent** (`src/agents/market_analyst.py`)
   - Conducts real-time market research using Google Search grounding
   - Identifies competitors and user pain points
   - Outputs: `product_brief.md`

2. **Financial Modeler Agent** (`src/agents/financial_modeler.py`)
   - Creates 3-year revenue projections
   - Calculates unit economics (CAC, LTV, payback period)
   - Analyzes burn rate and funding requirements
   - Outputs: `financial_model.md`

#### Phase 2: Planning (25% of workflow)
3. **PRD Generator Agent** (`src/agents/prd_generator.py`)
   - Writes detailed product requirements
   - Creates RICE-scored feature prioritization
   - Performs competitive feature analysis
   - Outputs: `prd.md`, `tech_spec.md`, `feature_prioritization.md`, `competitive_analysis.md`

#### Phase 3: Solutioning (30% of workflow)
4. **Architect Agent** (`src/agents/architect.py`)
   - Designs system architecture and database schema
   - Selects appropriate tech stack
   - Creates architecture diagrams
   - Outputs: `architecture.md`

5. **UX Designer Agent** (`src/agents/ux_designer.py`)
   - Maps user flows and journeys
   - Creates wireframe descriptions
   - Defines design system (colors, typography, components)
   - Outputs: `user_flow.md`, `design_system.md`

#### Phase 4: Implementation (25% of workflow)
6. **Sprint Planner Agent** (`src/agents/sprint_planner.py`)
   - Creates sprint breakdown and roadmap
   - Develops QA and testing strategy
   - Writes deployment and CI/CD guide
   - Outputs: `roadmap.md`, `testing_plan.md`, `deployment_guide.md`

### Workflow Orchestration
- **Framework:** LangGraph for agent state management
- **State:** Shared `AgentState` object passed between agents
- **Gates:** Phase validation ensures quality before proceeding
- **Progress:** Real-time updates via `GenerationStateManager`

### AI Models Used
- **Default:** Google Gemini 2.5 Flash (fast, cost-effective)
- **Optional:** Google Gemini 2.5 Pro (higher quality, more expensive)
- **Grounding:** Native Google Search grounding for market research
- **Optimization:** TOON format reduces token usage by 30-60%

---

## 🛠️ MCP Services (Model Context Protocol)

### What are MCP Services?
MCP services are FastAPI-based microservices that provide specialized functionality to the agents.

### File Manager MCP (Port 8081)
**Location:** `tools/file_manager_mcp/run.py`

**Capabilities:**
- Create and write files securely
- Validate markdown syntax
- Create ZIP archives of generated files
- Path traversal protection
- Input validation and sanitization

**Security Features:**
- Localhost-only binding (`127.0.0.1:8081`)
- Path validation against directory traversal
- File size limits (10MB per file)
- Filename validation (no special characters)
- Content validation (no null bytes)

### Markdown Formatter MCP (Port 8082)
**Location:** `tools/markdownify_mcp/run.py`

**Capabilities:**
- Convert HTML to Markdown
- Validate markdown syntax
- Format markdown consistently
- Handle code blocks and tables

**Security Features:**
- Localhost-only binding (`127.0.0.1:8082`)
- Input size limits
- Safe HTML parsing

### Usage in Code
```python
from src.mcp_http_clients import FileManagerHTTPClient

# Create file via MCP
client = FileManagerHTTPClient()
result = client.create_file("output/prd.md", content)
```

---

## 📦 Dependencies

### Core Dependencies (requirements.txt)
```
gradio==5.49.1              # Web UI framework
python-dotenv==1.0.1         # Environment variable management
google-generativeai==0.8.3   # Google Gemini AI
langchain==0.3.10            # LangChain framework
langchain-google-genai==2.0.7 # Gemini integration for LangChain
langgraph==0.2.60            # Agent workflow orchestration
toon-format==0.9.0b1         # Token optimization
pydantic==2.9.2              # Data validation
aiohttp==3.11.11             # Async HTTP client
orjson==3.10.13              # Fast JSON serialization
fastapi==0.115.12            # MCP services framework
uvicorn==0.34.0              # ASGI server for MCP services
markdownify==0.14.1          # HTML to Markdown conversion
requests>=2.31.0             # HTTP requests
```

### Python Version
- **Required:** Python 3.10 or higher
- **Tested on:** Python 3.10, 3.11

---

## 🎨 UI Components & Styling

### Gradio Interface
- **Main app:** `app.py` - Three tabs (Generator, Editor, Settings)
- **Editor:** `src/editor_page.py` - Code editor with file tree
- **Styles:** `src/styles.py` - Global CSS with animations

### UI Features
- Animated gradients and transitions
- Syntax highlighting for code
- Real-time terminal output ("Mission Control")
- File tree with expand/collapse
- Download as ZIP functionality
- Responsive design

### Customization
- All CSS is in `src/styles.py` as `GLOBAL_CSS`
- Gradio theme is default with custom CSS overlay
- Colors follow a modern gradient scheme

---

## 🚀 Deployment

### Docker Deployment (Recommended)
```bash
# Build
docker build -t mvp-agent .

# Run with API key
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key mvp-agent

# Run with .env file
docker run -p 7860:7860 --env-file .env mvp-agent
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export GEMINI_API_KEY=your_key

# Run
python app.py
```

### Hugging Face Spaces
- Compatible with HF Spaces (see `src/hf_compat.py`)
- Set `GEMINI_API_KEY` in Spaces secrets
- Use the Gradio SDK

### Production Considerations
- Use Gemini 2.5 Flash for cost efficiency
- Enable TOON format to reduce token usage
- Monitor Google API quotas (`src/google_quota.py`)
- Set up proper logging and monitoring
- Consider rate limiting for public deployments

---

## 🤝 Contributing

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes following the guidelines above
4. **Test** your changes thoroughly
5. **Commit** with clear messages
6. **Push** to your branch
7. **Open** a Pull Request

### What We're Looking For
- Security improvements
- Performance optimizations
- New agent capabilities
- Better error handling
- Documentation improvements
- UI/UX enhancements

### Areas That Need Help
- Automated testing infrastructure
- Performance benchmarks
- Additional industry templates
- Internationalization (i18n)
- Accessibility improvements

---

## 📚 Additional Resources

### Key Documents
- **User Guide:** See `README.md` for end-user documentation
- **Security:** See `SECURITY_FIXES_APPLIED.md` and `SECURITY_REVIEW_FINDINGS.md`
- **License:** MIT License - see `LICENSE` file

### External Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev/)
- [Gradio Docs](https://www.gradio.app/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

## 🎯 Quick Reference for AI Agents

### When Working on This Codebase:
1. ✅ **Read this file** (`AGENTS.md`) for guidelines
2. ✅ **Check security docs** before touching sensitive areas
3. ✅ **Follow naming conventions** (snake_case, PascalCase)
4. ✅ **Validate inputs** using `validators.py` patterns
5. ✅ **Test manually** with `python test_demo.py`
6. ✅ **Update docs** if you change structure or features
7. ✅ **Consider security** for every change
8. ✅ **Keep changes minimal** and focused

### Important File Locations:
- **Agents:** `src/agents/*.py` (6 agent files)
- **Prompts:** `src/prompts.py`, `src/enhanced_prompts.py`
- **Workflow:** `src/workflow.py` (LangGraph orchestration)
- **UI:** `app.py`, `src/editor_page.py`, `src/styles.py`
- **Security:** `tools/file_manager_mcp/run.py` (path validation examples)
- **Config:** `.env.example`, `src/settings.py`

### Common Tasks:
- **Add a new agent:** Create in `src/agents/`, add to `workflow.py`
- **Modify prompts:** Edit `src/prompts.py` or `src/enhanced_prompts.py`
- **Change UI:** Edit `app.py` or `src/styles.py`
- **Fix security issue:** Check `SECURITY_REVIEW_FINDINGS.md` for patterns
- **Update dependencies:** Edit `requirements.txt` with pinned versions

---

**Last Updated:** February 6, 2026  
**Version:** 2.0  
**Status:** Phase 1 Security Fixes Complete ✅
