# Getting Started

This guide helps you generate your first MVP blueprint in minutes.

## Prerequisites

- Python 3.10+
- A Gemini API key (create one at https://aistudio.google.com/)
- Optional: Docker for containerized runs

## Quick start (local)

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app.py
```

Open `http://localhost:7860` in your browser.

## Quick start (Docker)

```bash
docker build -t mvp-agent .
docker run -p 7860:7860 mvp-agent
```

## First run

1. Open the app in your browser.
2. Go to **Settings** and paste your Gemini API key.
3. Open **Generator**, describe your idea, and click **Generate Blueprint**.
4. Review results in the **Code Editor** tab.
5. Download the ZIP for handoff or archival.

## What gets generated

MVP Agent produces a package of markdown files such as `overview.md`, `prd.md`, `architecture.md`, `roadmap.md`, and more. See the [Usage Guide](usage.md) for details and examples.
