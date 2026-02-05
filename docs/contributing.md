# Contributing

Thanks for your interest in contributing to MVP Agent v2.0! This guide outlines how to get started and submit high-quality changes.

## Development setup

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies.
3. Run the app locally:

```bash
python app.py
```

## Branching and pull requests

- Create feature branches from `main` (or the default branch).
- Keep changes focused and scoped to a single feature or fix.
- Write clear commit messages.
- Ensure documentation updates accompany UI or workflow changes.

## Code quality expectations

- Follow existing coding patterns in the codebase.
- Prefer clear, explicit functions over implicit behavior.
- Keep markdown and documentation consistent with the `docs/` structure.

## Adding new agents

When adding a new agent:

1. Implement it in `src/agents/`.
2. Add it to the workflow in `src/workflow.py`.
3. Ensure outputs are written into `AgentState`.
4. Update the documentation to include the new artifact or phase.

## Reporting issues

Please include:

- Steps to reproduce
- Expected vs actual behavior
- Logs or screenshots if applicable

## License

By contributing, you agree that your contributions will be licensed under the project's MIT license.
