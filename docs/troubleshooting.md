# Troubleshooting

This guide lists common issues and recommended fixes.

## App fails to start

**Symptoms**
- `ModuleNotFoundError`
- `ImportError`

**Resolution**
- Verify you installed dependencies with `pip install -r requirements.txt`.
- Ensure Python 3.10+ is active.

## "Gemini API Key not found"

**Symptoms**
- Error in the Mission Control panel
- Generation stops immediately

**Resolution**
- Add a key in **Settings** or set `GEMINI_API_KEY`.
- Restart the app after modifying environment variables.

## Generation is slow

**Symptoms**
- Long wait times in the Mission Control panel

**Resolution**
- Choose a faster model (e.g., `gemini-2.5-flash`).
- Reduce the complexity level.

## ZIP download missing files

**Symptoms**
- ZIP archive missing one or more documents

**Resolution**
- Regenerate the blueprint.
- Ensure generation completed successfully before downloading.

## "Port already in use"

**Symptoms**
- Gradio reports the port 7860 is occupied

**Resolution**
- Stop the conflicting process or run with a different port by editing `app.py`.

## Still stuck?

Open an issue with logs and steps to reproduce. Include your OS, Python version, and any error output.
