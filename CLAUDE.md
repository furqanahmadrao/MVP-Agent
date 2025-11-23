# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Tasks

### Setup and Installation
- **Create Virtual Environment:** `python -m venv venv`
- **Activate Virtual Environment (Windows):** `venv\Scripts\activate`
- **Activate Virtual Environment (macOS/Linux):** `source venv/bin/activate`
- **Install Dependencies:** `pip install -r requirements.txt`

### Running the Application
- **Run the main application:** `python app.py` (This will start all 3 internal MCP servers and expose the Gradio UI)

### Testing
- **Run MCP Health Check:** `python tests/mcp_health_check.py` (Verifies all 3 MCP servers are running and responding correctly.)
- **Manual Testing Flow:**
    1. Run `python app.py`
    2. Enter a sample startup idea into the Gradio UI.
    3. Click "🎯 Generate MVP Blueprint".
    4. Verify status updates, tab population, markdown rendering, and ZIP download functionality.

## High-Level Code Architecture and Structure

The MVP Agent is a **multi-phase autonomous agent** powered by Google Gemini and custom MCP servers.

### Core Components:
- **`app.py`**: The main Gradio application that serves as the entry point and UI.
- **`src/`**: Contains the core logic for the agent.
    - **`agent_brain.py`**: Orchestrates the multi-phase agent logic (Intent Understanding, Market Research, Analysis & Synthesis, Blueprint Generation).
    - **`ai_models.py`**: Handles interactions with the Gemini API.
    - **`mcp_http_clients.py`**: Clients for interacting with the internal MCP servers.
    - **`mcp_process_manager.py`**: Manages the lifecycle of the internal MCP servers.
    - **`file_manager.py`**: Handles file operations, though generated markdown files are primarily in-memory.
    - **`prompts.py`**: Stores AI prompts used for blueprint generation.
    - **`validators.py`**: For input validation.
    - **`error_handler.py`**: Centralized error handling.
    - **`google_quota.py`**: Manages API quota for Google services.
    - **`hf_compat.py`**: Contains compatibility code for Hugging Face Spaces deployment.
- **`tools/`**: Houses the internal Model Context Protocol (MCP) servers. These are auto-started by `app.py`.
    - **`file_manager_mcp/`**: MCP for file creation, markdown validation, and ZIP packaging.
    - **`google_search_mcp/`**: MCP for performing Google Custom Search queries and returning structured market data.
    - **`markdownify_mcp/`**: MCP for markdown formatting.
- **`logs/`**: Directory for MCP server logs (gitignored).

### Data Flow and Storage:
- All generated MVP blueprint markdown files (`overview.md`, `features.md`, `architecture.md`, `design.md`, `user_flow.md`, `roadmap.md`, `business_model.md`, `testing_plan.md`) are created and held **in memory only**, never written to disk persistently.
- When a user requests a download, a ZIP file is temporarily created in the system's temporary directory.
- These temporary ZIP files are automatically deleted after 30 minutes by a background thread, ensuring stateless operation and efficient resource usage, especially for multi-user environments like Hugging Face Spaces.

### Environment Variables:
- **`GEMINI_API_KEY`**: Required for Gemini API access.
- **`GOOGLE_API_KEY`**: Optional, for enhanced Google Custom Search capabilities.
- **`GOOGLE_SEARCH_ENGINE_ID`**: Optional, for enhanced Google Custom Search capabilities. These are typically managed via Hugging Face Spaces "Secrets" feature in deployment.

## Project Context and Goals

This project is an autonomous AI agent built for the MCP Hackathon 2025. It transforms startup ideas into complete MVP specifications.

### Core Technologies
- **Frontend:** Gradio 6.0 (orange/black theme)
- **AI Models:** Gemini 2.5 Pro, Flash, Flash-8B
- **MCP Servers:** 3 custom servers (web-search, reddit, markdownify)
- **Deployment:** Hugging Face Spaces
- **Language:** Python 3.10+

### Current Status & Next Steps
- **Status:** The project is implementation-complete and ready for testing and enhancement, followed by deployment.
- **Immediate Focus:**
    1.  **Test with real API keys:** Add `GEMINI_API_KEY` to `.env` and verify local generation.
    2.  **(Optional) Enable real MCP servers:** Add API keys for search and other services if full functionality is needed.
    3.  **Deploy to Hugging Face Spaces:** Create the space, upload files, configure secrets, and test the live deployment.
    4.  **Create Demo Video:** Record a 1-3 minute demo for submission.

### Key Guidance for AI Agents
- **Key Design Decisions:**
    - Use a multi-model approach for cost optimization (Pro for complex tasks, Flash for simple ones).
    - Use 3 MCP servers to demonstrate orchestration without excessive complexity.
    - Use Gradio for its rapid prototyping and native Hugging Face Spaces support.
- **Common Pitfalls to Avoid:**
    - Do not start coding before reading the architecture documentation in the `.docs/` folder.
    - Never hardcode API keys; use environment variables.
    - Implement robust error handling and fallbacks for all external API/MCP calls.
    - Add comprehensive logging to trace agent behavior.

### Troubleshooting Guide
- **If MCP servers fail:**
    1. Check API keys in environment variables.
    2. Verify network connectivity and check for rate limits.
    3. The system should fall back to heuristic/mock data mode.
- **If Gemini API fails:**
    1. Check API key validity, quota, and billing.
    2. Check for rate limits.
    3. The system should use a fallback model (e.g., Flash instead of Pro).
- **If Gradio won't start:**
    1. Check for port conflicts.
    2. Verify all dependencies in `requirements.txt` are installed.
    3. Ensure the Python version is 3.10+.
