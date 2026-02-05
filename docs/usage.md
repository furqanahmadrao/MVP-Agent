# Usage Guide

This guide covers the main user workflow, supported inputs, and output artifacts.

## Generate a blueprint

1. Open the app in your browser.
2. Go to **Settings** and add your Gemini API key.
3. Navigate to **Generator**.
4. Enter a clear description of your startup idea.
5. (Optional) Adjust project complexity level.
6. Click **Generate Blueprint**.

## Monitor progress

The **Mission Control** panel shows status updates as the workflow progresses through the analysis, planning, solutioning, and implementation phases.

## Edit outputs

The **Code Editor** tab provides:

- File explorer for generated markdown artifacts
- In-browser editing for quick revisions
- Download button for ZIP export

## Example prompt

> "A mobile app that helps families coordinate shared calendars, chores, and shopping lists with real-time notifications."

## Output package

The generated package is a ZIP file containing markdown artifacts. A typical run includes:

- `overview.md` (summary)
- `product_brief.md` (market research)
- `prd.md` (product requirements)
- `architecture.md` (system design)
- `user_flow.md` (UX flow)
- `design_system.md` (UI guidelines)
- `roadmap.md` (implementation plan)
- `testing_plan.md` (QA strategy)
- `deployment_guide.md` (ops guidance)

## Tips for better results

- Use specific target users and problems.
- Mention constraints (budget, timeline, platform).
- Provide inspiration apps or competitors.

For configuration details, see [Configuration](configuration.md).
