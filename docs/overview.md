# Overview

**MVP Agent v2.0** is a production-ready, multi-agent system that transforms startup ideas into detailed Product Requirements Documents (PRDs) and supporting technical plans. It uses a structured, multi-phase workflow inspired by the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology.

## What the product does

MVP Agent ingests a user idea and produces a complete blueprint package containing:

- Market research and competitive positioning
- PRDs and technical specifications
- Architecture diagrams and system design guidance
- UX flows and design-system recommendations
- Roadmap, testing strategy, and deployment guidance

The output can be reviewed and edited directly in the web UI and downloaded as a ZIP for handoff to engineering teams.

## Who this is for

- **Founders** wanting a fast, structured path from idea to product plan.
- **Product managers** needing a consistent PRD and roadmap template.
- **Engineering teams** requiring architecture and QA planning as inputs to implementation.
- **Accelerators and studios** that need repeatable, high-quality documentation across startups.

## Core workflow phases

1. **Analysis**: Researches market landscape and synthesizes a product brief.
2. **Planning**: Produces PRDs and technical requirements.
3. **Solutioning**: Generates architecture and UX artifacts.
4. **Implementation**: Builds roadmap, testing plan, and deployment guidance.

## Key capabilities

- **Multi-agent orchestration** using LangGraph to enforce a deterministic workflow.
- **Gemini-native grounding** for market research without external search API keys.
- **Token-optimized output** via TOON format for efficiency.
- **IDE-like editing experience** with built-in file explorer and markdown editor.

## High-level system components

- **Gradio UI** (app.py): interactive interface for generation and editing.
- **Workflow engine** (src/workflow.py): LangGraph state machine coordinating agents.
- **Agent suite** (src/agents/): specialized agents for research, PRDs, architecture, UX, and sprints.
- **Settings manager** (src/settings.py): manages API keys and feature flags.
- **File manager** (src/file_manager.py): prepares output ZIPs for download.

For a deeper technical dive, see the [Architecture Overview](architecture.md).
