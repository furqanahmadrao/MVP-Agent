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
