import os
from typing import List, Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

app = FastAPI(title="google-search-mcp", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "google-search-mcp"}


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


# Load .env so this server can be run standalone (e.g. via `python tools/google_search_mcp/run.py`)
load_dotenv()

BASE_URL = "https://www.googleapis.com/customsearch/v1"


@app.post("/search")
def search(payload: SearchRequest):
    """
    MCP-style wrapper around Google Custom Search.
    Returns structured JSON: { success, results: [{title,snippet,link}], message }.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return {
            "success": False,
            "results": [],
            "message": "Google Custom Search not configured. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID."
        }

    limit = max(1, min(payload.limit or 10, 10))
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": payload.query,
        "num": limit,
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return {
                "success": False,
                "results": [],
                "message": f"Google API error {resp.status_code}: {resp.text[:200]}"
            }

        data = resp.json()
        items = data.get("items", []) or []
        results: List[dict] = []
        for item in items:
            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                }
            )

        return {
            "success": True,
            "results": results,
            "message": f"Fetched {len(results)} results for query."
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "message": f"Exception during Google search: {e}"
        }


if __name__ == "__main__":
    # Default port 8082 for google-search-mcp
    uvicorn.run(app, host="0.0.0.0", port=8082)
