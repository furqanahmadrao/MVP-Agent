# Repository Guidelines - MVP Agent v2.0

## Project Structure & Module Organization

### Core Application Files
- **`app.py`** - Main Gradio entry point that wires the agent workflow and UI
  - Creates the Generator tab with idea input and mission control
  - Implements the Code Editor tab with file explorer
  - Manages Settings tab for API configuration
  - Handles session state and file management

### Source Code (`src/`)
The `src/` directory holds all core application logic:

#### Agent System
- **`src/agents/`** - Specialized AI agents following BMAD methodology
  - `market_analyst.py` - Conducts market research using Gemini grounding
  - `financial_modeler.py` - Creates financial projections, CAC/LTV, burn rate
  - `prd_generator.py` - Writes PRDs, tech specs, feature prioritization
  - `architect.py` - Designs system architecture and tech stack
  - `ux_designer.py` - Creates user flows and design systems
  - `sprint_planner.py` - Generates roadmaps and testing plans

#### Core Infrastructure
- **`workflow.py`** - LangGraph workflow orchestration and state management
- **`agent_brain.py`** - Agent coordination and decision-making logic
- **`agent_state.py`** - TypedDict definitions for workflow state
- **`generation_state.py`** - Thread-safe session management with per-session locks

#### AI & API
- **`ai_models.py`** - Gemini API wrapper with timeout and error handling
- **`grounding_agent.py`** - Google Search grounding implementation
- **`google_quota.py`** - API quota management and rate limiting

#### MCP & Tools
- **`mcp_clients.py`** - MCP (Model Context Protocol) client management
- **`mcp_http_clients.py`** - HTTP-based MCP communication
- **`mcp_process_manager.py`** - MCP service lifecycle management

#### UI & Presentation
- **`editor_page.py`** - Code editor interface with file explorer
- **`styles.py`** - Global CSS with animated gradients and dark theme
- **`settings.py`** - User settings management (API keys, preferences)

#### Utilities
- **`prompts.py`** - Core agent prompts following BMAD patterns
- **`enhanced_prompts.py`** - Advanced prompts for financial modeling
- **`industry_templates.py`** - SaaS, Fintech, Healthtech, E-commerce templates
- **`error_handler.py`** - Centralized error handling and recovery
- **`validators.py`** - Input validation and sanitization
- **`file_manager.py`** - File operations and ZIP creation
- **`toon_utils.py`** - TOON format for token optimization
- **`helpers.py`** - Utility functions
- **`hf_compat.py`** - Hugging Face Spaces compatibility

### Tools & MCP Services (`tools/`)
- **`tools/file_manager_mcp/`** - File operations MCP service
  - `run.py` - FastAPI server for file CRUD operations
  - Binds to `127.0.0.1:8081` for security
  - Implements path traversal protection and input validation

- **`tools/markdownify_mcp/`** - Markdown conversion MCP service
  - `run.py` - FastAPI server for HTML to Markdown conversion
  - Binds to `127.0.0.1:8082` for security

### Documentation & Configuration
- **Root-level docs:**
  - `README.md` - Main project documentation and quick start
  - `AGENTS.md` - This file, repository guidelines and standards
  - `SECURITY_REVIEW_FINDINGS.md` - Complete security audit (26 issues)
  - `SECURITY_FIXES_APPLIED.md` - Applied fixes and testing results
  - `SECURITY_ISSUES_TRACKER.md` - Ongoing security issue tracking
  - `.env.example` - Environment variable template
  - `LICENSE` - MIT License

### Configuration Files
- **`.gitignore`** - Excludes secrets, cache, outputs, and user settings
- **`.dockerignore`** - Prevents secrets and dev files in Docker images
- **`Dockerfile`** - Production-ready container with non-root user
- **`requirements.txt`** - Pinned Python dependencies

## Build, Test, and Development Commands

### Local Development
```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the main application (port 7860)
python app.py

# Access the application
# Main interface: http://localhost:7860
# Editor tab: Available in the main UI
```

### Docker Deployment
```bash
# Build the Docker image
docker build -t mvp-agent .

# Run the container
docker run -p 7860:7860 mvp-agent

# Run with environment variables
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key mvp-agent
```

### Testing & Quality Assurance
```bash
# Security scanning
bandit -r src/ tools/ -ll        # Find security issues
safety check                      # Check dependency vulnerabilities
semgrep --config=auto .          # Static analysis

# Code quality
flake8 src/ --max-line-length=120  # PEP 8 compliance
black src/ --check                  # Code formatting

# Manual testing
python app.py                     # Test full workflow
# Then open http://localhost:7860 and generate a blueprint
```

### MCP Services (Auto-started)
MCP services start automatically when the app runs. They bind to localhost for security:
- File Manager MCP: `http://127.0.0.1:8081`
- Markdownify MCP: `http://127.0.0.1:8082`

## Coding Style & Naming Conventions

### General Python Standards
- **Python-only repository** - No JavaScript, TypeScript, or other languages
- **PEP 8 compliance** - 4-space indentation, 120 character line limit
- **Type hints** - Use type annotations for function signatures
- **Docstrings** - Google-style docstrings for all public functions/classes

### Naming Conventions
```python
# Functions and variables: snake_case
def generate_with_grounding(prompt: str) -> Dict[str, Any]:
    api_key = get_api_key()

# Classes: PascalCase
class GenerationStateManager:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Private methods/variables: leading underscore
def _internal_helper(self):
    self._session_locks = {}
```

### Code Organization Patterns
- **Prompts**: Centralize in `src/prompts.py` and `src/enhanced_prompts.py`
- **Constants**: Define at module level, document units (bytes, seconds, etc.)
- **Imports**: Standard library → Third-party → Local, alphabetically sorted
- **Error handling**: Use custom exceptions from `src/error_handler.py`

### Security Best Practices
- **Input validation**: Always validate and sanitize user inputs
- **Path operations**: Use `Path.resolve()` and check `relative_to()` for path traversal
- **Secrets**: Never hardcode API keys, use environment variables
- **SQL/Injection**: Escape user input, use parameterized queries
- **File operations**: Validate filenames, check size limits, prevent null bytes

Example:
```python
# ✅ GOOD - Secure path handling
target = (BASE_DIR / filename).resolve()
try:
    target.relative_to(BASE_DIR)
except ValueError:
    raise SecurityError("Path traversal detected")

# ❌ BAD - Vulnerable to path traversal
target = BASE_DIR / filename  # No validation!
```

## Testing Guidelines

### Current Testing Approach
- **Manual testing** is the primary method (no automated test suite yet)
- **End-to-end testing**: Run `python app.py` and generate a full blueprint
- **Security testing**: Apply fixes from `SECURITY_FIXES_APPLIED.md` and verify

### Manual Testing Checklist
When making changes, test the following:

#### Generator Functionality
- [ ] Input validation (too short, too long, special characters)
- [ ] API key validation (missing, invalid)
- [ ] Generation process (all phases complete)
- [ ] File creation (all 13 documents generated)
- [ ] Error handling (network issues, API errors)

#### Code Editor
- [ ] File selection and display
- [ ] Syntax highlighting works
- [ ] File editing and saving
- [ ] ZIP download functionality

#### Settings
- [ ] API key save/load
- [ ] Model selection (Flash vs Pro)
- [ ] TOON format toggle
- [ ] Settings persistence

#### Security
- [ ] Path traversal attempts blocked
- [ ] MCP services on localhost only
- [ ] Input validation catches malicious input
- [ ] No secrets in logs or outputs

### Future Testing Framework
If adding automated tests, follow these conventions:
- **Framework**: Use `pytest` for test framework
- **File naming**: `test_*.py` or `*_test.py`
- **Directory**: Create `tests/` directory (excluded from Docker)
- **Coverage**: Aim for >70% code coverage
- **Fixtures**: Use `conftest.py` for shared fixtures

Example test structure:
```python
# tests/test_validators.py
import pytest
from src.validators import validate_filename

def test_validate_filename_rejects_traversal():
    with pytest.raises(ValueError):
        validate_filename("../../etc/passwd")

def test_validate_filename_accepts_valid():
    result = validate_filename("document.md")
    assert result == "document.md"
```

## Commit & Pull Request Guidelines
- Commit history uses short, imperative summaries (e.g., “Enhance generation process…”).
- PRs should include: a concise description, what changed, and any UI impact.
- If you change UI or flows, include screenshots or a short GIF.

## Security & Configuration

### Environment Setup
1. **Create `.env` file**: Copy from `.env.example`
   ```bash
   cp .env.example .env
   ```

2. **Set API key**: Edit `.env` and add your Gemini API key
   ```bash
   GEMINI_API_KEY=your_actual_key_here
   ```

3. **Verify `.gitignore`**: Ensure `.env` is excluded (already configured)

### Secret Management Rules
- ✅ **DO**: Use environment variables for all secrets
- ✅ **DO**: Use `python-dotenv` to load `.env` files
- ✅ **DO**: Document required variables in `.env.example`
- ❌ **DON'T**: Commit `.env` files to git
- ❌ **DON'T**: Hardcode API keys in source code
- ❌ **DON'T**: Log or print API keys
- ❌ **DON'T**: Store keys in `user_settings.json` (now gitignored)

### Security Configuration
The application includes several security features:

#### File Manager MCP Security
- Binds to `127.0.0.1` (localhost only, not `0.0.0.0`)
- Path traversal protection with `Path.resolve()` and `relative_to()`
- File size limits: 10MB per file, 100MB total for ZIP
- Input validation: filename patterns, null byte checks

#### Docker Security
- Runs as non-root user (`appuser`)
- Multi-layer caching for faster builds
- `.dockerignore` prevents secret leakage
- Health checks for container monitoring

#### Application Security
- Input sanitization for user ideas
- Request timeouts (120s) to prevent hung calls
- Thread-safe state management with per-session locks
- Rate limiting ready (can be enabled in production)

### Monitoring & Logging
```python
# Logging best practices
import logging

# Configure logging (not print statements)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Good logging
logger.info("Generation started for session %s", session_id)
logger.error("API call failed: %s", str(e), exc_info=True)

# Never log secrets
# ❌ BAD: logger.info(f"API key: {api_key}")
# ✅ GOOD: logger.info("API key configured")
```

## 🔒 Security Status & Recent Improvements

**Last Security Review:** February 6, 2026
**Review Status:** Phase 1 Complete (7/8 issues resolved)
**Production Status:** ✅ Ready for Development/Staging | ⚠️ Phase 2 needed for Production
**Deployment Readiness Score:** 7.5/10 (was 6/10)

### Critical Issues Summary
See `SECURITY_REVIEW_FINDINGS.md` for complete details. Key improvements implemented:

#### ✅ Completed Security Fixes:
1. **Path Traversal Vulnerability Fixed** - File manager MCP now uses `Path.resolve()` and validates paths
2. **MCP Services Secured** - Bound to `127.0.0.1` instead of `0.0.0.0` (no network exposure)
3. **Input Validation Added** - Pydantic validators for filenames and content
4. **ZIP Bomb Protection** - 100MB total size limit, 1000 file count limit
5. **Thread Safety Implemented** - Per-session locks prevent race conditions
6. **Request Timeouts Added** - 120s timeout for Gemini API calls
7. **Dependencies Pinned** - All packages locked to specific versions
8. **Docker Hardened** - Non-root user, `.dockerignore` created

### Remaining Work
- **Input Validation in app.py** - Add rate limiting (2 concurrent generations max)
- **Phase 2 Fixes** - Error recovery, comprehensive logging, health checks
- **Phase 3 Hardening** - Monitoring, keyring for secrets, CI/CD setup

### Security Testing
Before deploying, run these security scans:
```bash
# Install security tools
pip install bandit safety semgrep

# Run security scans
bandit -r src/ tools/ -ll    # Python security issues
safety check --json          # Dependency vulnerabilities
semgrep --config=auto .      # SAST scanning
```

### Quick Wins (Completed)
- ✅ Created `.dockerignore` file
- ✅ Added `user_settings.json` to `.gitignore`
- ✅ Pinned all dependencies in `requirements.txt`
- ✅ Changed MCP services to bind to `127.0.0.1`
- ✅ Added missing dependencies (fastapi, uvicorn, markdownify)

**⚠️ For production deployment, complete Phase 2 reliability fixes first.**

For detailed findings, remediation steps, and code examples, see:
- `SECURITY_REVIEW_FINDINGS.md` - Complete audit with 26 issues documented
- `SECURITY_FIXES_APPLIED.md` - All applied fixes with code examples
- `SECURITY_ISSUES_TRACKER.md` - Ongoing tracking of remaining issues

---

## 🏗️ Architecture Overview

### Multi-Agent System (BMAD Methodology)
The application uses a **LangGraph-based workflow** where specialized agents work in sequence:

```
User Idea → Market Analyst → Financial Modeler → PRD Generator →
Architect → UX Designer → Sprint Planner → Final Blueprint
```

#### Agent Roles:
1. **Market Analyst** (`src/agents/market_analyst.py`)
   - Uses Gemini Grounding for real-time web research
   - Identifies competitors, market size, user personas
   - Outputs: `product_brief.md`

2. **Financial Modeler** (`src/agents/financial_modeler.py`) ⭐ NEW
   - Creates 3-year revenue projections
   - Calculates CAC, LTV, burn rate, runway
   - Outputs: `financial_model.md`

3. **PRD Generator** (`src/agents/prd_generator.py`)
   - Writes functional requirements and user stories
   - Creates feature prioritization (RICE scores)
   - Conducts competitive analysis
   - Outputs: `prd.md`, `tech_spec.md`, `feature_prioritization.md`, `competitive_analysis.md`

4. **Architect** (`src/agents/architect.py`)
   - Designs system architecture and database schema
   - Selects tech stack and infrastructure
   - Outputs: `architecture.md`

5. **UX Designer** (`src/agents/ux_designer.py`)
   - Creates user flows and wireframes
   - Designs UI components and style guide
   - Outputs: `user_flow.md`, `design_system.md`

6. **Sprint Planner** (`src/agents/sprint_planner.py`)
   - Generates 6-week roadmap with sprint breakdown
   - Creates testing strategy and QA plan
   - Outputs: `roadmap.md`, `testing_plan.md`, `deployment_guide.md`

### State Management
- **`GenerationStateManager`** - Thread-safe session storage with per-session locks
- **`AgentState`** - TypedDict for LangGraph workflow state
- **Session isolation** - Each generation has unique session ID

### MCP (Model Context Protocol)
Two FastAPI services provide file operations:
- **File Manager MCP** - Create/read/validate/zip markdown files
- **Markdownify MCP** - Convert HTML to Markdown

Services auto-start when app launches and bind to localhost for security.

---

## 🎨 UI Architecture

### Three-Tab Interface
1. **Generator Tab** - Input idea, configure complexity, start generation
2. **Code Editor Tab** - Browse files, edit content, download ZIP
3. **Settings Tab** - API key management, model selection

### Real-Time Progress
- **Mission Control** - Live logs with emoji indicators
- **Phase Indicators** - Visual progress through 4 BMAD phases
- **Session Tracking** - Unique session IDs for concurrent users

### Styling
- **VS Code-inspired theme** - Dark mode with syntax highlighting
- **Animated gradients** - Professional look with smooth transitions
- **Responsive design** - Works on desktop and tablet
- **CSS in `src/styles.py`** - Centralized styling for maintainability

---

## 📦 Dependencies & Versioning

All dependencies are **pinned to specific versions** for reproducibility:

### Core Dependencies
```txt
gradio==5.49.1              # UI framework
python-dotenv==1.0.1        # Environment variables
google-generativeai==0.8.3  # Gemini API
langchain==0.3.10           # LLM framework
langchain-google-genai==2.0.7
langgraph==0.2.60           # Agent orchestration
```

### MCP & Utilities
```txt
fastapi==0.115.12           # MCP service framework
uvicorn==0.34.0             # ASGI server
markdownify==0.14.1         # HTML to Markdown
aiohttp==3.11.11            # Async HTTP client
orjson==3.10.13             # Fast JSON serialization
pydantic==2.9.2             # Data validation
```

### Special Dependencies
```txt
toon-format==0.9.0b1        # Token optimization (BETA)
requests>=2.31.0            # HTTP library
```

**Note:** `toon-format` is a **beta package**. Monitor for stable release.

---

## 🚀 Deployment Guide

### Local Development
Best for testing and development:
```bash
python app.py
# Access at http://localhost:7860
```

### Docker (Recommended for Production)
Production-ready container with security hardening:
```bash
# Build image
docker build -t mvp-agent .

# Run container
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key mvp-agent

# Run with volume for outputs (optional)
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key \
  -v $(pwd)/outputs:/home/appuser/app/outputs mvp-agent
```

### Environment Variables
- `GEMINI_API_KEY` - **Required** - Your Gemini API key
- `GRADIO_SERVER_NAME` - Default: `0.0.0.0` (all interfaces)
- `GRADIO_SERVER_PORT` - Default: `7860`
- `PYTHONUNBUFFERED` - Default: `1` (for logging)

### Hugging Face Spaces
To deploy on HF Spaces:
1. Fork repository
2. Create new Space (Gradio app)
3. Add `GEMINI_API_KEY` as a secret
4. Push code to Space
5. App auto-deploys

**Note:** MCP services work on HF Spaces with localhost binding.

---

## 🔧 Troubleshooting

### Common Issues

#### "API Key not found"
**Solution:**
```bash
# Set in .env file
echo "GEMINI_API_KEY=your_key" > .env

# Or set in UI Settings tab
```

#### "MCP Service Connection Failed"
**Solution:**
```bash
# MCP services auto-start. Check if ports are in use:
netstat -an | grep 8081
netstat -an | grep 8082

# Kill conflicting processes if needed
```

#### "Generation Hangs at 'Analysis' phase"
**Solution:**
- Check internet connection (Gemini Grounding needs web access)
- Verify API key is valid
- Check Gemini API quota at https://aistudio.google.com/

#### "Docker Build Fails"
**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t mvp-agent .
```

#### "Import Error: No module named 'fastapi'"
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

## 📖 Additional Resources

### Documentation
- [Gemini API Docs](https://ai.google.dev/docs)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [BMAD Methodology](https://github.com/bmad-code-org/BMAD-METHOD)

### Tools & Utilities
- [Get Gemini API Key](https://aistudio.google.com/)
- [RICE Scoring Model](https://www.productplan.com/glossary/rice-scoring-model/)
- [GitHub Spec Kit](https://github.com/github/github-spec-kit)

### Community
- [GitHub Issues](https://github.com/furqanahmadrao/MVP-Agent/issues)
- [GitHub Discussions](https://github.com/furqanahmadrao/MVP-Agent/discussions)

---

## ✅ Pre-Deployment Checklist

Before deploying to production, verify:

### Security
- [ ] All dependencies updated and scanned for vulnerabilities
- [ ] `.env` file not committed to git
- [ ] API keys stored securely (not in code)
- [ ] MCP services bound to `127.0.0.1`
- [ ] Input validation enabled
- [ ] Rate limiting configured

### Testing
- [ ] Generate complete blueprint (all 13 files)
- [ ] Test with different project complexity levels
- [ ] Verify ZIP download works
- [ ] Test error handling (invalid API key, network issues)
- [ ] Security scan passes (bandit, safety)

### Configuration
- [ ] Environment variables documented
- [ ] Docker image builds successfully
- [ ] Health checks configured
- [ ] Logging enabled
- [ ] Monitoring set up (if applicable)

### Documentation
- [ ] README.md updated
- [ ] AGENTS.md reflects current structure
- [ ] Security docs reviewed
- [ ] Deployment guide tested

---

**Last Updated:** February 6, 2026
**Document Version:** 2.1
**Contributors:** MVP Agent Development Team