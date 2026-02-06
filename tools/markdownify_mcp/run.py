from fastapi import FastAPI
from pydantic import BaseModel
from markdownify import markdownify as md
import uvicorn

app = FastAPI(title="markdownify-mcp", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "markdownify-mcp"}


class FormatRequest(BaseModel):
    text: str


@app.post("/format")
def format_markdown(payload: FormatRequest):
    """
    Normalize content into markdown.

    If input contains HTML, markdownify will convert it.
    If it's already markdown/plain text, we return a cleaned version.
    """
    try:
        # markdownify is tolerant; if text is plain it will be returned mostly unchanged.
        markdown = md(payload.text, heading_style="ATX", bullets="*")
        return {
            "success": True,
            "markdown": markdown
        }
    except Exception as e:
        return {
            "success": False,
            "markdown": payload.text,
            "message": f"Failed to format markdown: {e}"
        }


if __name__ == "__main__":
    # Security: Bind to localhost only to prevent network exposure
    # Default port 8083 for markdownify-mcp
    uvicorn.run(app, host="127.0.0.1", port=8083)
