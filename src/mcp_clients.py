"""
MCP Clients Module - Integration with MCP servers
Handles all MCP server communications for web search, Reddit, etc.
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import math
import time
from .google_quota import get_quota_config, can_reserve_requests, increment_usage, get_daily_usage

@dataclass
class SearchResult:
    """Data class for search results"""
    title: str
    url: str
    snippet: str
    source: str = "web"

class MCPWebSearchClient:
    """
    Client for Web Search with Google Custom Search API
    Falls back to placeholder data if API is not configured
    
    Required Environment Variables:
    - GOOGLE_API_KEY: Your Google Cloud API key
    - GOOGLE_SEARCH_ENGINE_ID: Your Custom Search Engine ID
    """
    
    def __init__(self):
        """Initialize web search client"""
        self.server_name = "google-custom-search"
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.available = bool(self.api_key and self.search_engine_id)
        
        # Quota configuration
        env = dict(os.environ)  # copy to plain dict for type compatibility
        cfg = get_quota_config(env)
        self.daily_quota = cfg["DAILY_QUOTA"]
        self.max_results_per_request = cfg["MAX_RESULTS_PER_REQUEST"]
        self.max_requests_per_task = cfg["MAX_REQUESTS_PER_TASK"]
        self.retry_attempts = cfg["RETRY_ATTEMPTS"]
        
        if self.available:
            print(f"✅ Web Search: Google Custom Search API configured (daily quota={self.daily_quota})")
        else:
            print("ℹ️  Web Search: Using placeholder data (API keys not configured)")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Perform web search using Google Custom Search API or fallback
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Try Google Custom Search API if configured
        if self.available:
            try:
                # Determine how many Google API calls are needed
                per_request = max(1, self.max_results_per_request)
                requests_needed = math.ceil(num_results / per_request)
                
                # Check quota
                if not can_reserve_requests(requests_needed, self.daily_quota):
                    print(f"⚠️  Not enough Google quota for {requests_needed} requests (used: {get_daily_usage()} / {self.daily_quota})")
                    print("ℹ️  Falling back to placeholder data due to quota limits...")
                    return self._get_placeholder_results(query)
                
                results = await self._search_google_api(query, num_results)
                
                # On success, increment usage by number of requests actually made
                actual_requests = math.ceil(len(results) / per_request) if results else 0
                if actual_requests > 0:
                    increment_usage(actual_requests)
                
                return results
            except Exception as e:
                print(f"⚠️  Google Search API error: {e}")
                print("ℹ️  Falling back to placeholder data...")
        
        # Fallback to placeholder data
        return self._get_placeholder_results(query)
    
    async def _search_google_api(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using Google Custom Search API with paging and retries
        
        Args:
            query: Search query
            num_results: Total number of results desired
            
        Returns:
            List of SearchResult objects
        """
        per_call = max(1, self.max_results_per_request)
        collected: List[SearchResult] = []
        start_index = 1  # Google CSE start index is 1-based
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while len(collected) < num_results:
                to_fetch = min(per_call, num_results - len(collected))
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': query,
                    'num': to_fetch,
                    'start': start_index
                }
                
                attempt = 0
                last_exception = None
                while attempt <= self.retry_attempts:
                    try:
                        async with session.get(self.base_url, params=params) as response:
                            text = await response.text()
                            if response.status == 200:
                                # Parse JSON safely
                                try:
                                    data = await response.json()
                                except Exception:
                                    import json as _json
                                    data = _json.loads(text)
                                items = data.get('items', [])
                                if not items:
                                    # No more results available
                                    return collected
                                for item in items:
                                    collected.append(SearchResult(
                                        title=item.get('title', 'No title'),
                                        url=item.get('link', ''),
                                        snippet=item.get('snippet', 'No description available'),
                                        source="google_custom_search"
                                    ))
                                print(f"✅ Google Search: Retrieved {len(items)} items for '{query}' (start={start_index})")
                                break  # success for this page
                            elif response.status in (429, 500, 502, 503, 504):
                                attempt += 1
                                last_exception = Exception(f"HTTP {response.status}")
                                backoff = 2 ** (attempt - 1)
                                print(f"⚠️ Google API returned {response.status}. Retrying in {backoff}s (attempt {attempt}/{self.retry_attempts})")
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                raise Exception(f"API returned status {response.status}: {text}")
                    except Exception as e:
                        attempt += 1
                        last_exception = e
                        if attempt > self.retry_attempts:
                            # Exhausted retries
                            raise
                        backoff = 2 ** (attempt - 1)
                        print(f"⚠️ Google API request failed: {e}. Retrying in {backoff}s (attempt {attempt}/{self.retry_attempts})")
                        await asyncio.sleep(backoff)
                
                # Prepare for next page
                start_index += per_call
                # Google CSE has practical limits on start index; stop if too far
                if start_index > 100:
                    break
        
        print(f"✅ Google Search: Found {len(collected)} total results for '{query}'")
        return collected
    
    def _get_placeholder_results(self, query: str) -> List[SearchResult]:
        """
        Generate placeholder results when API is not available
        
        Args:
            query: Search query
            
        Returns:
            List of placeholder SearchResult objects
        """
        results = []
        
        results.append(SearchResult(
            title=f"Market Analysis: {query}",
            url="https://example.com/analysis",
            snippet=f"Industry research shows growing demand for solutions in this space. Key competitors are implementing similar features with positive user feedback.",
            source="web_placeholder"
        ))
        
        results.append(SearchResult(
            title=f"Feature Comparison: {query}",
            url="https://example.com/features",
            snippet=f"Leading platforms in this category typically include core features like user authentication, data management, and mobile responsiveness.",
            source="web_placeholder"
        ))
        
        return results
    
    def search_sync(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Synchronous wrapper for search"""
        return asyncio.run(self.search(query, num_results))

# Reddit integration removed.
# The project is configured to use web search only. Reddit-specific client and placeholder data
# have been removed to simplify deployment (Hugging Face Spaces compatibility).
# If Reddit integration is required in the future, re-add a dedicated client with its own quota/caching logic.

class ResearchOrchestrator:
    """
    Orchestrates research across multiple MCP servers
    Combines web search and social media research
    """
    
    def __init__(self):
        """Initialize research orchestrator"""
        self.web_client = MCPWebSearchClient()
        # Reddit integration removed — web-only research
    
    def research_competitor_features(self, queries: List[str]) -> str:
        """
        Research competitor features using web search
        
        Args:
            queries: List of search queries
            
        Returns:
            Formatted string with research results
        """
        all_results = []
        
        for query in queries:
            try:
                results = self.web_client.search_sync(query, num_results=5)
                all_results.extend(results)
            except Exception as e:
                print(f"Web search error for '{query}': {e}")
        
        # Format results
        if not all_results:
            return "No web search results found."
        
        formatted = "## Competitor Feature Research\n\n"
        for i, result in enumerate(all_results, 1):
            formatted += f"### Result {i}: {result.title}\n"
            formatted += f"**URL:** {result.url}\n"
            formatted += f"**Summary:** {result.snippet}\n\n"
        
        return formatted
    
    def research_user_feedback(
        self,
        queries: List[str],
        subreddits: Optional[List[str]] = None
    ) -> str:
        """
        Research user feedback (Reddit integration removed)

        Returns:
            Informative placeholder explaining Reddit was disabled.
        """
        # Reddit integration removed to keep the app compatible with Hugging Face Spaces.
        # Use web-based research instead; surface user feedback by searching review sites and forums.
        return "Reddit integration is disabled. Web search results and review sites are used for user feedback."
    
    def conduct_full_research(
        self,
        competitor_queries: List[str],
        pain_point_queries: List[str],
        subreddits: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Conduct full research across web and social media
        
        Args:
            competitor_queries: Queries for competitor research
            pain_point_queries: Queries for user pain points
            subreddits: Subreddits to search
            
        Returns:
            Dictionary with 'web_results' and 'social_results'
        """
        web_results = self.research_competitor_features(competitor_queries)
        social_results = self.research_user_feedback(pain_point_queries, subreddits)
        
        return {
            "web_results": web_results,
            "social_results": social_results
        }

# Singleton instance
_orchestrator = None

def get_research_orchestrator() -> ResearchOrchestrator:
    """Get or create the research orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResearchOrchestrator()
    return _orchestrator
