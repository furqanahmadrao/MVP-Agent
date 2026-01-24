# Features

The MVP Agent is packed with features designed to streamline the process of creating Product Requirements Documents (PRDs) and technical specifications.

## Core Features

- **Multi-Agent Orchestration:** Powered by LangGraph, the MVP Agent simulates a full product team, including a Market Analyst, PRD Generator, System Architect, UX Designer, and Sprint Planner. Each agent is a specialized AI model that has been trained to perform a specific task, ensuring that the generated documents are of the highest quality.
- **Native Search Grounding:** The Market Analyst agent uses Gemini's built-in Google Search grounding to conduct real-time web research. This ensures that the generated documents are based on the latest market trends and data, and that all sources are properly cited.
- **Code Editor UI:** The application features a modern, IDE-like interface with a file explorer, syntax highlighting, and "Download as ZIP" functionality. This makes it easy to review and edit the generated documents, and to download them for use in other applications.
- **Token-Optimized:** The system supports TOON (Token-Oriented Object Notation) format, which can reduce token usage by 30-60%. This makes it more affordable to generate large, complex documents.
- **Settings Manager:** Users can configure their own API keys, select models (Flash/Pro), and toggle features directly in the UI. This makes it easy to customize the application to meet your specific needs.
- **Docker Ready:** The application is containerized for easy deployment and hosting. This means that you can run it on any platform that supports Docker, including your local machine, a cloud server, or a managed hosting service.

## Generated Artifacts

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
