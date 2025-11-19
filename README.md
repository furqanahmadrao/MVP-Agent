---
title: MVP Agent - AI-Powered Blueprint Generator
emoji: "🚀"
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
tags:
   - mcp-in-action-track
   - agents
   - mvp
   - market-research
   - gemini
   - mcp
   - startup
   - product-management
models:
   - google/gemini-2.5-pro
   - google/gemini-2.5-flash
short_description: AI agent that generates MVP blueprints and roadmaps
---
# 🚀 MVP Agent

**AI-powered MVP Blueprint Generator for MCP Hackathon 2025 – Track 2: MCP In Action (Agents)**

Transform any startup idea into a complete, production-ready MVP specification in under 2 minutes. MVP Agent combines AI reasoning with real-time market research to deliver actionable blueprints that engineering teams can implement immediately.

## ✨ What You Get

Input a single paragraph describing your startup idea. Get back:

- **📋 Features.md** - Prioritized feature requirements (P0, P1, P2)
- **🏗️ Architecture.md** - Technical stack, database schema, API design (with Mermaid diagrams)
- **🎨 Design.md** - UI/UX guidelines, design system, accessibility standards
- **🗺️ User Flow.md** - Complete user journeys (with Mermaid flowcharts)
- **📅 Roadmap.md** - 6-week launch plan with milestones
- **📦 ZIP Download** - All files packaged for your team

All outputs are **opinionated**, **implementation-ready**, and include **rendered Mermaid diagrams**.

---

## 🎬 Demo & Resources

- **📹 Demo Video:** [Watch on YouTube](https://youtube.com/your-demo-video) *(Update with your video link)*
- **📝 Blog Post:** [Read the full story](https://your-blog.com/mvp-agent) *(Update with your blog link)*
- **💼 LinkedIn Post:** [Join the discussion](https://linkedin.com/posts/your-post) *(Update with your LinkedIn post link)*

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
- Analyzes your idea to identify target users, core problems, and success metrics
- Generates strategic research queries

### Phase 2: Market Research 🔍
- Uses **Google Custom Search MCP** to research competitors and market trends
- Gathers real user feedback and pain points from the web
- Synthesizes insights from multiple sources

### Phase 3: Analysis & Synthesis 📊
- Identifies market gaps and opportunities
- Maps feature requirements to user needs
- Determines optimal technical architecture

### Phase 4: Blueprint Generation ✨
- Creates 5 detailed markdown documents
- Generates Mermaid diagrams for architecture and user flows
- Packages everything into a downloadable ZIP

**Total time:** ~60-90 seconds per blueprint

---

## 🏗️ Architecture

MVP Agent runs **3 internal MCP servers** (auto-started, no manual setup needed):

1. **file-manager-mcp** (Port 8081)
   - Handles file creation, markdown validation, ZIP packaging
   - Endpoints: `/create_file`, `/validate_markdown`, `/zip_files`

2. **google-search-mcp** (Port 8082)
   - Performs Google Custom Search queries
   - Returns structured competitor and market data

3. **markdownify-mcp** (Port 8083)
   - Handles markdown formatting and rendering
   - Endpoints: `/format_markdown`, `/render_mermaid`

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/furqanahmadrao/MVP-Agent.git
    cd MVP-Agent
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the root directory or set them directly in your shell:
    ```
    GEMINI_API_KEY=your_gemini_api_key
    GOOGLE_API_KEY=your_google_cloud_api_key  # Optional, for enhanced search
    GOOGLE_SEARCH_ENGINE_ID=your_custom_search_engine_id # Optional, for enhanced search
    ```
    -   **GEMINI_API_KEY**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).
    -   **GOOGLE_API_KEY** (Optional): Get from [Google Cloud Console](https://console.cloud.google.com/).
    -   **GOOGLE_SEARCH_ENGINE_ID** (Optional): Create at [Google Programmable Search](https://programmablesearchengine.google.com/).
        *Note: Without Google Search API, the agent uses placeholder data but still generates valid blueprints.*

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The app will:
    1.  ✅ Start all 3 MCP servers (file-manager-mcp, google-search-mcp, markdownify-mcp)
    2.  ✅ Launch the Gradio UI in your browser (usually at `http://127.0.0.1:7860`)
---
## 🌐 Deploy on Hugging Face Spaces

This repository is **ready for one-click deployment** to HF Spaces:

### Steps:
1. **Fork/Clone** this Space or create a new Space from this repository.
2. **Set up Secrets:** In your Hugging Face Space settings, add the following as secrets:
    - `GEMINI_API_KEY` (Required): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
    - `GOOGLE_API_KEY` (Optional, for enhanced search): Get from [Google Cloud Console](https://console.cloud.google.com/)
    - `GOOGLE_SEARCH_ENGINE_ID` (Optional, for enhanced search): Create at [Google Programmable Search](https://programmablesearchengine.google.com/)
        *Note: Without Google Search API, the agent uses placeholder data but still generates valid blueprints.*
3. **Deploy** - HF will automatically:
   - Install dependencies from `requirements.txt`
   - Run `app.py`
   - Start all MCP servers
   - Expose the Gradio UI


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
- **Orange/Black Theme** - High contrast, modern design
- **Real-time Status Updates** - See the agent's reasoning process
- **Tabbed Output** - Easy navigation between documents
- **Mermaid Diagram Rendering** - Architecture and user flows visualized
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

### Optional (for enhanced search):
```bash
GOOGLE_API_KEY=your_google_cloud_api_key
GOOGLE_SEARCH_ENGINE_ID=your_custom_search_engine_id
```

### Default Quotas:
- Google Custom Search: 100 queries/day (free tier)
- Gemini API: Check your Google Cloud quota
- Configurable via `src/google_quota.py`

### Troubleshooting Mermaid Diagrams
- If you see "Syntax error in text" in the Architecture/User Flow tab, open `logs/mermaid/` to see the original diagram plus AI fix attempts.
- You can run the validator locally to test a Mermaid block:
```bash
python -c "from src.mermaid_utils import validate_mermaid_block; print(validate_mermaid_block('graph TD\nA --> B'))"
```
- If you want to reproduce the original issue without auto-fixes, run the agent locally and inspect `logs/mermaid/` (AI fix attempts are logged). There isn't currently an env var to disable fixes; the logs let you compare original vs fixed output.

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
   - ✅ All 5 tabs populate with content
   - ✅ Mermaid diagrams render correctly
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
- ✅ Production-ready outputs (5 markdown files + ZIP)
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