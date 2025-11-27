import os
from typing import Dict, Any, List, Optional
import time

import requests


def _base_url(env_key: str, default: str) -> str:
    return os.getenv(env_key, default).rstrip("/")


def _retry_request(func, max_retries: int = 3, timeout: int = 10):
    """
    Retry wrapper with exponential backoff for HTTP requests.
    
    Args:
        func: Function that makes the HTTP request
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        Response dict or error dict
    """
    for attempt in range(max_retries):
        try:
            return func(timeout=timeout)
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException) as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                backoff = 2 ** attempt
                print(f"[MCP][RETRY] Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                print(f"[MCP][ERROR] All {max_retries} attempts failed: {e}")
                raise
    return {"success": False, "message": "Max retries exceeded"}


class FileManagerMCPClient:
    """
    HTTP client for file-manager-mcp.

    Endpoints (default base http://localhost:8081):
    - POST /create_file { filename, content }
    - POST /validate_markdown { filename }
    - POST /zip_files { source_dir?, zip_path? }
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or _base_url("FILE_MANAGER_MCP_URL", "http://localhost:8081")

    def create_file(self, filename: str, content: str) -> Dict[str, Any]:
        url = f"{self.base_url}/create_file"
        payload = {"filename": filename, "content": content}
        print(f"[MCP] → file-manager-mcp.create_file {payload['filename']}")
        
        def make_request(timeout):
            resp = requests.post(url, json=payload, timeout=timeout)
            return resp.json()
        
        try:
            return _retry_request(make_request, max_retries=3, timeout=10)
        except Exception as e:
            print(f"[MCP][ERROR] file-manager-mcp.create_file failed: {e}")
            return {"success": False, "path": filename, "message": str(e)}

    def validate_markdown(self, filename: str) -> Dict[str, Any]:
        url = f"{self.base_url}/validate_markdown"
        payload = {"filename": filename}
        print(f"[MCP] → file-manager-mcp.validate_markdown {filename}")
        
        def make_request(timeout):
            resp = requests.post(url, json=payload, timeout=timeout)
            return resp.json()
        
        try:
            return _retry_request(make_request, max_retries=3, timeout=10)
        except Exception as e:
            print(f"[MCP][ERROR] file-manager-mcp.validate_markdown failed: {e}")
            return {"success": False, "path": filename, "errors": [str(e)], "message": "Request failed"}

    def zip_files(self, source_dir: str = "outputs", zip_path: str = "outputs/mvp_package.zip") -> Dict[str, Any]:
        url = f"{self.base_url}/zip_files"
        payload = {"source_dir": source_dir, "zip_path": zip_path}
        print(f"[MCP] → file-manager-mcp.zip_files {source_dir} -> {zip_path}")
        
        def make_request(timeout):
            resp = requests.post(url, json=payload, timeout=timeout)
            return resp.json()
        
        try:
            return _retry_request(make_request, max_retries=3, timeout=20)
        except Exception as e:
            print(f"[MCP][ERROR] file-manager-mcp.zip_files failed: {e}")
            return {"success": False, "path": None, "message": str(e)}

    def create_zip_from_memory(self, files: Dict[str, str], output_filename: str) -> Dict[str, Any]:
        url = f"{self.base_url}/create_zip_from_memory"
        payload = {"files": files, "output_filename": output_filename}
        print(f"[MCP] → file-manager-mcp.create_zip_from_memory {output_filename}")
        
        def make_request(timeout):
            resp = requests.post(url, json=payload, timeout=timeout)
            return resp.json()
        
        try:
            return _retry_request(make_request, max_retries=3, timeout=30)
        except Exception as e:
            print(f"[MCP][ERROR] file-manager-mcp.create_zip_from_memory failed: {e}")
            return {"success": False, "path": None, "message": str(e)}


class GoogleSearchMCPClient:
    """
    HTTP client for google-search-mcp.

    Endpoint (default base http://localhost:8082):
    - POST /search { query, limit }
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or _base_url("GOOGLE_SEARCH_MCP_URL", "http://localhost:8082")

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        url = f"{self.base_url}/search"
        payload = {"query": query, "limit": limit}
        print(f"[MCP] → google-search-mcp.search '{query}' (limit={limit})")
        
        def make_request(timeout):
            resp = requests.post(url, json=payload, timeout=timeout)
            return resp.json()
        
        try:
            return _retry_request(make_request, max_retries=3, timeout=15)
        except Exception as e:
            print(f"[MCP][ERROR] google-search-mcp.search failed: {e}")
            return {"success": False, "results": [], "message": str(e)}


class MarkdownifyMCPClient:
    """
    HTTP client for markdownify-mcp.

    Endpoint (default base http://localhost:8083):
    - POST /format { text }
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or _base_url("MARKDOWNIFY_MCP_URL", "http://localhost:8083")

    def format_markdown(self, text: str) -> str:
        url = f"{self.base_url}/format"
        print(f"[MCP] → markdownify-mcp.format_markdown (len={len(text)})")
        
        def make_request(timeout):
            resp = requests.post(url, json={"text": text}, timeout=timeout)
            data = resp.json()
            if data.get("success") and "markdown" in data:
                return data["markdown"]
            # Fallback to original text if MCP reports failure or no markdown field.
            return text
        
        try:
            return _retry_request(make_request, max_retries=2, timeout=10)
        except Exception as e:
            print(f"[MCP][ERROR] markdownify-mcp.format_markdown failed: {e}")
            # Fallback: basic local cleanup
            return self._local_markdown_cleanup(text)
    
    def _local_markdown_cleanup(self, text: str) -> str:
        """
        Local fallback for markdown formatting when MCP fails.
        Performs basic cleanup and normalization.
        """
        import re
        
        # Remove dangerous HTML tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n')
        
        # Ensure headers have space after #
        text = re.sub(r'^(#{1,6})([^\s])', r'\1 \2', text, flags=re.MULTILINE)
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
