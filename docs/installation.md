# Installation & Setup

This guide covers installation options, dependencies, and environment configuration for MVP Agent v2.0.

## System requirements

- **Python**: 3.10 or higher
- **Operating system**: macOS, Linux, or Windows
- **Memory**: 4 GB+ recommended
- **Network**: outbound access to Gemini API endpoints

## Dependencies

Core dependencies are listed in `requirements.txt` and include:

- Gradio (UI)
- LangGraph (workflow orchestration)
- LangChain + Google GenAI (model integration)
- TOON format (token optimization)

Install with:

```bash
pip install -r requirements.txt
```

## Environment variables

MVP Agent reads environment variables from `.env` (via python-dotenv):

- `GEMINI_API_KEY`: Gemini API key used for generation

You can also set the key through the in-app **Settings** tab, which stores it in `user_settings.json`.

## Running the application

```bash
python app.py
```

The Gradio server starts at `http://localhost:7860` by default.

## Docker deployment

```bash
docker build -t mvp-agent .
docker run -p 7860:7860 mvp-agent
```

## Troubleshooting installation

- If dependencies fail to install, verify your Python version (`python --version`).
- If the UI does not load, confirm the port is open and no other process uses `7860`.
- For API errors, validate your key and usage quotas.

For additional help, see the [Troubleshooting](troubleshooting.md) guide.
