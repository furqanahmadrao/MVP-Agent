# Repository Guidelines

## Project Structure & Module Organization
- `app.py` is the main Gradio entry point that wires the agent workflow and UI.
- `src/` holds the core logic (agents, prompts, settings, helpers, and UI pages).
- `tools/` contains MCP utilities (e.g., markdown formatting and file manager services).
- `scripts/` is for one-off maintenance scripts.
- `test_demo.py` launches a demo editor session for manual UI verification.
- Docs and roadmaps live at the repo root (e.g., `README.md`, `PRODUCTION_ROADMAP_V2.md`).

## Build, Test, and Development Commands
- `python -m venv venv` and `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux): create and activate a virtual environment.
- `pip install -r requirements.txt`: install Python dependencies.
- `python app.py`: run the main application locally on port 7860.
- `python test_demo.py`: start the editor demo UI on port 7861 with sample data.
- `docker build -t mvp-agent .` and `docker run -p 7860:7860 mvp-agent`: build and run the Docker image.

## Coding Style & Naming Conventions
- Python-only repo; follow PEP 8 conventions with 4-space indentation.
- Use `snake_case` for functions/variables and `PascalCase` for classes.
- Keep prompts and long template strings centralized in `src/prompts.py` and `src/enhanced_prompts.py`.
- No formatter/linter is enforced; keep diffs minimal and readable.

## Testing Guidelines
- There is no automated test runner configured in this repository.
- Use `python test_demo.py` for manual UI checks and `python app.py` for end-to-end runs.
- If you add tests, prefer `pytest` and name files `test_*.py`.

## Commit & Pull Request Guidelines
- Commit history uses short, imperative summaries (e.g., “Enhance generation process…”).
- PRs should include: a concise description, what changed, and any UI impact.
- If you change UI or flows, include screenshots or a short GIF.

## Security & Configuration Tips
- Copy `.env.example` to `.env` and set `GEMINI_API_KEY` before running.
- Keep API keys out of commits and logs; never hardcode secrets.

## 🔒 Known Issues & Security Review

**Last Security Review:** February 5, 2026  
**Review Status:** 26 issues identified (11 Critical/High, 15 Medium/Low)  
**Production Status:** ⚠️ NOT READY - Critical security vulnerabilities must be fixed

### Critical Issues Summary
See `SECURITY_REVIEW_FINDINGS.md` for complete details. Top priority fixes:

1. **Path Traversal Vulnerability** in `tools/file_manager_mcp/run.py` - allows arbitrary file access
2. **MCP Services Exposed to Network** without authentication on 0.0.0.0
3. **Docker Container Running as Root** - security risk
4. **Missing .dockerignore** - potential secret leakage
5. **Missing Dependencies** - fastapi, uvicorn, markdownify not in requirements.txt
6. **Thread Safety Issues** in `GenerationStateManager` - data corruption risk
7. **Input Validation Missing** - injection attack vectors
8. **ZIP Bomb Risk** - no size limits on file uploads

### Remediation Plan
- **Phase 1 (Week 1):** Critical security fixes - path traversal, authentication, Docker hardening
- **Phase 2 (Week 2):** High priority reliability - thread safety, rate limiting, error recovery
- **Phase 3 (Week 3):** Production hardening - multi-stage builds, monitoring, documentation
- **Phase 4 (Week 4):** Testing & quality assurance - security audit, load testing

**Current Deployment Readiness Score:** 6/10  
**Target Score for Production:** 9/10

### Quick Wins (Can fix in ~40 minutes)
1. Create `.dockerignore` file
2. Add `user_settings.json` to `.gitignore`
3. Pin all dependencies in `requirements.txt`
4. Change MCP services to bind to `127.0.0.1` instead of `0.0.0.0`
5. Add missing dependencies to `requirements.txt`

**⚠️ DO NOT deploy to production until Phase 1 and Phase 2 fixes are complete.**

For detailed findings, remediation steps, and code examples, see: `SECURITY_REVIEW_FINDINGS.md`