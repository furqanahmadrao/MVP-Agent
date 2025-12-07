
# 🤖 Copilot Instructions for MVP Agent

## Project Overview
MVP Agent is a multi-phase autonomous agent that converts startup ideas into detailed, implementation-ready MVP blueprints. It uses Python 3.10+, Gradio UI, Google Gemini (Pro/Flash), and three custom Model Context Protocol (MCP) servers. All outputs are structured markdown files (overview, features, architecture, design, user_flow, roadmap, business_model, testing_plan) held in memory and packaged as a ZIP for download.

## Architecture & Key Components
- **Entry Point:** `app.py` (starts Gradio UI and all MCP servers)
- **Core Logic:** `src/agent_brain.py` (orchestrates agent phases: intent, research, synthesis, blueprint)
- **AI Model Integration:** `src/ai_models.py` (Gemini API), `src/prompts.py` (prompt templates, agent guidance)
- **MCP Servers:**
  - `tools/file_manager_mcp/` (file ops, markdown validation, ZIP)
  - `tools/google_search_mcp/` (web search, competitor data)
  - `tools/markdownify_mcp/` (markdown formatting)
- **Server Management:** `src/mcp_process_manager.py`, `src/mcp_http_clients.py`
- **Other:** `src/error_handler.py`, `src/validators.py`, `src/google_quota.py`, `src/hf_compat.py`

## Developer Workflows
- **Setup:**
  - `python -m venv venv` → `venv\Scripts\activate` → `pip install -r requirements.txt`
  - Set `GEMINI_API_KEY` (required), `GOOGLE_API_KEY`/`GOOGLE_SEARCH_ENGINE_ID` (optional) as env vars or Hugging Face Spaces secrets.
- **Run App:** `python app.py` (auto-starts all MCP servers, launches Gradio UI)
- **Test MCP Health:** `python tests/mcp_health_check.py`
- **Manual Test:**
  1. Start app, enter idea, generate blueprint
  2. Verify real-time status, tabbed outputs, ZIP download

## Project-Specific Patterns & Conventions
- **Blueprint Generation:**
  - All markdown files are generated in-memory, never written to disk except for temporary ZIPs (auto-deleted after 30 min).
  - Each markdown file follows strict templates (see `src/prompts.py`), with rationale and explicit agent guidance after major sections. Example: after a table, add a "Rationale" and "Agent Guidance" subsection.
  - Outputs are designed for both human and LLM agent consumption (tables, numbered lists, agent instructions, edge cases, fallback strategies).
- **User Flow Formatting:**
  - User flows must use numbered lists, explicit decision points, and rationale/agent guidance after each major flow (see `src/prompts.py`).
- **Error Handling:**
  - All external API/MCP calls must have robust error handling and fallbacks (see `src/error_handler.py`).
  - If APIs fail, fallback templates are used (see `_generate_fallback` in `agent_brain.py`).
- **Environment Variables:**
  - Never hardcode API keys; always use env vars or deployment secrets.
- **Logging:**
  - Add detailed logs for agent actions and errors (see `logs/`, `src/error_handler.py`).
- **Testing:**
  - Use the provided health check and manual UI flow for validation.

## Integration & External Dependencies
- **Gemini API:** via `src/ai_models.py` (requires `GEMINI_API_KEY`)
- **Google Custom Search:** via `tools/google_search_mcp/` (optional, requires `GOOGLE_API_KEY`/`GOOGLE_SEARCH_ENGINE_ID`)
- **Gradio UI:** for user interaction and output display
- **Hugging Face Spaces:** supported via `src/hf_compat.py` (use Spaces secrets for keys)

## Key Files & References
- `src/prompts.py`: All prompt templates and agent guidance patterns
- `docs/`: Architecture, UI/UX, and agent behavior specs
- `README.md`, `CLAUDE.md`: High-level architecture, setup, and agent-specific guidance

---

**For more details, see:**
- `docs/00_project_overview.md`, `docs/02_architecture.md`, `docs/07_agent_behavior_spec.md`
- `README.md` (setup, workflows, project structure)
- `CLAUDE.md` (AI agent guidance, troubleshooting)

---

*Last updated: November 24, 2025*
