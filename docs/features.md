# Feature Guide

MVP Agent v2.0 includes a set of product and platform capabilities designed to support rapid product planning and delivery.

## Product features

- **Multi-agent orchestration**: a deterministic workflow that simulates a full product team.
- **Market research grounding**: integrates Gemini search grounding to cite real-world context.
- **Structured PRDs**: generates PRDs following a consistent template suitable for engineering handoff.
- **Architecture planning**: creates system design guidance and high-level architecture diagrams.
- **UX deliverables**: outputs user flows and design-system suggestions for product design teams.
- **Implementation planning**: creates roadmaps, testing plans, and deployment guides.

## Platform features

- **Gradio-based UI**: fast interactive experience with a generator tab and editor tab.
- **Code editor experience**: edit generated markdown files directly in the UI.
- **ZIP downloads**: export outputs into a single archive for sharing.
- **Token optimization**: optional TOON formatting reduces token use.

## Output artifacts

Typical output files include:

- `overview.md`
- `product_brief.md`
- `prd.md`
- `architecture.md`
- `user_flow.md`
- `design_system.md`
- `roadmap.md`
- `testing_plan.md`
- `deployment_guide.md`

See the [Usage Guide](usage.md) for detailed examples.
