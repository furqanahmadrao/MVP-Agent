# MVP Agent v2.0 🚀

**AI-Powered Production-Ready PRD Generator**  
*Turn your startup idea into a comprehensive, developer-ready blueprint.*

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/AI-Gemini%202.5%20Pro%20%2F%20Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![Framework](https://img.shields.io/badge/Agent-LangGraph-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**MVP Agent v2.0** is a sophisticated multi-agent system that transforms simple startup ideas into professional **Product Requirements Documents (PRDs)** and technical specifications. 

Built on the **BMAD (Breakthrough Method for Agile AI-Driven Development)** methodology, it employs a team of specialized AI agents working in a **LangGraph** workflow to conduct market research, design architecture, and plan sprints—just like a real product team.

---

## ✨ v2.0 Key Features

*   **🤖 Multi-Agent Orchestration**: Powered by **LangGraph**, simulating a full product team:
    *   **🕵️ Market Analyst**: Conducts real-time web research using **Gemini Grounding**.
    *   **📝 PRD Generator**: Writes detailed specs following the **GitHub Spec Kit** standard.
    *   **🏗️ Architect**: Designs cloud-native systems and chooses tech stacks.
    *   **🎨 UX Designer**: Creates user flows, wireframes, and design systems.
    *   **📅 Sprint Planner**: Generates Gantt charts and testing strategies.
*   **🌍 Native Search Grounding**: No more API keys for search! Uses Gemini's built-in Google Search grounding for accurate, cited market research.
*   **💻 Code Editor UI**: A modern, IDE-like interface with a file explorer, syntax highlighting, and "Download as ZIP" functionality.
*   **📉 Token-Optimized**: Supports **TOON (Token-Oriented Object Notation)** format to reduce token usage by 30-60%.
*   **⚙️ Settings Manager**: Configure your own API keys, select models (Flash/Pro), and toggle features directly in the UI.
*   **🐳 Docker Ready**: Single-container deployment for easy hosting.

---

## 🏗️ System Architecture (BMAD Method)

The workflow follows a strict 4-phase process:

1.  **Analysis Phase**: The Market Analyst researches competitors and user pain points.
2.  **Planning Phase**: The PRD Generator creates functional requirements and user stories.
3.  **Solutioning Phase**: The Architect and UX Designer build the technical and visual foundation.
4.  **Implementation Phase**: The Sprint Planner outlines the roadmap and QA strategy.

```mermaid
graph LR
    User[User Idea] --> Analyst[Market Analyst]
    Analyst --> PRD[PRD Generator]
    PRD --> Architect[System Architect]
    Architect --> UX[UX Designer]
    UX --> Planner[Sprint Planner]
    Planner --> Output[Final Blueprint]
```

---

## 🚀 Quick Start

### Option A: Docker (Recommended)

1.  **Build the image:**
    ```bash
    docker build -t mvp-agent .
    ```
2.  **Run the container:**
    ```bash
    docker run -p 7860:7860 mvp-agent
    ```
3.  **Open in Browser:** `http://localhost:7860`

### Option B: Local Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/furqanahmadrao/MVP-Agent.git
    cd MVP-Agent
    ```

2.  **Set up Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

---

## 💻 Usage Guide

1.  **Settings**: Go to the **Settings** tab and enter your **Google Gemini API Key**.
    *   You can get one for free at [aistudio.google.com](https://aistudio.google.com/).
2.  **Generator**: Switch to the **Generator** tab.
3.  **Input**: Describe your startup idea (e.g., "A mobile app for tracking carbon footprint with gamification").
4.  **Generate**: Click "Generate Blueprint".
5.  **Watch**: Observe the "Mission Control" terminal as agents work through the phases.
6.  **Edit & Download**: Once complete, use the **Code Editor** tab to review, edit, and download your files.

---

## 📂 Generated Artifacts

| File | Agent | Description |
|------|-------|-------------|
| `product_brief.md` | Market Analyst | Market size, competitors, and vision. |
| `prd.md` | PRD Generator | Functional requirements, user stories, acceptance criteria. |
| `tech_spec.md` | PRD Generator | High-level technical approach. |
| `architecture.md` | Architect | System diagrams, database schema, tech stack. |
| `user_flow.md` | UX Designer | User journeys and wireframes. |
| `design_system.md` | UX Designer | Colors, typography, and UI components. |
| `roadmap.md` | Sprint Planner | Sprint breakdown and timeline. |
| `testing_plan.md` | Sprint Planner | QA strategy and test cases. |
| `deployment_guide.md` | Sprint Planner | Docker and CI/CD instructions. |

---

## 🔧 Configuration

You can configure the application via the UI or `.env` file:

- `GEMINI_API_KEY`: Your Google GenAI key.
- `use_toon_format`: Set to `True` to enable token optimization.
- `project_level_auto_detect`: Enable automatic complexity estimation.

---

## 🤝 Contributing

We welcome contributions! Please see `FEATURE_SUGGESTIONS.md` for our roadmap.

1.  Fork the repo.
2.  Create a feature branch.
3.  Submit a Pull Request.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
