"""
Gemini Grounding Agent - Web Search with Built-in Grounding
Replaces Google Custom Search MCP with Gemini's native grounding
"""

from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import time


class GeminiGroundingAgent:
    """
    Agent for web research using Gemini's built-in Search Grounding.
    
    Benefits over Google Custom Search:
    - No separate API key needed
    - Built-in citation support
    - Automatic relevance ranking
    - Free until Jan 5, 2026
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini Grounding agent.
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model (must support grounding)
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Grounding tool configuration
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        dynamic_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform web search with Gemini Grounding.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default 5)
            dynamic_threshold: Dynamic retrieval threshold (0.0-1.0)
        
        Returns:
            {
                "answer": str,           # AI-generated answer
                "chunks": List[Dict],     # Grounding chunks (sources)
                "supports": List[Dict],   # Support metadata
                "search_queries": List[str]  # Queries executed
            }
        """
        try:
            # Configure grounding
            config = types.GenerateContentConfig(
                tools=[self.grounding_tool],
                temperature=0.3,  # Lower temperature for factual accuracy
                response_modalities=["TEXT"]
            )
            
            # Add dynamic threshold if specified
            if dynamic_threshold is not None:
                config.tool_config = types.ToolConfig(
                    google_search_retrieval=types.GoogleSearchRetrievalConfig(
                        dynamic_retrieval_config=types.DynamicRetrievalConfig(
                            mode=types.DynamicRetrievalConfig.Mode.MODE_DYNAMIC,
                            dynamic_threshold=dynamic_threshold
                        )
                    )
                )
            
            # Generate response with grounding
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=query,
                config=config
            )
            
            # Extract grounding metadata
            grounding_metadata = None
            if hasattr(response.candidates[0], 'grounding_metadata'):
                grounding_metadata = response.candidates[0].grounding_metadata
            
            # Parse grounding chunks (sources)
            chunks = []
            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
                for chunk in grounding_metadata.grounding_chunks:
                    chunks.append({
                        "title": getattr(chunk.web, 'title', 'Unknown'),
                        "uri": getattr(chunk.web, 'uri', ''),
                        "snippet": getattr(chunk.web, 'snippet', '')
                    })
            
            # Parse grounding supports (citations)
            supports = []
            if grounding_metadata and hasattr(grounding_metadata, 'grounding_supports'):
                for support in grounding_metadata.grounding_supports:
                    supports.append({
                        "segment": {
                            "start_index": support.segment.start_index if hasattr(support, 'segment') else 0,
                            "end_index": support.segment.end_index if hasattr(support, 'segment') else 0,
                            "text": support.segment.text if hasattr(support, 'segment') else ""
                        },
                        "grounding_chunk_indices": support.grounding_chunk_indices if hasattr(support, 'grounding_chunk_indices') else [],
                        "confidence_scores": support.confidence_scores if hasattr(support, 'confidence_scores') else []
                    })
            
            # Extract search queries executed
            search_queries = []
            if grounding_metadata and hasattr(grounding_metadata, 'search_entry_point'):
                search_queries = getattr(grounding_metadata.search_entry_point, 'rendered_content', '')
            
            return {
                "answer": response.text,
                "chunks": chunks[:max_results],  # Limit results
                "supports": supports,
                "search_queries": [query],  # Original query
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": "",
                "chunks": [],
                "supports": [],
                "search_queries": [query],
                "success": False,
                "error": str(e)
            }
    
    def research_topic(
        self,
        topic: str,
        queries: List[str],
        max_results_per_query: int = 3
    ) -> Dict[str, Any]:
        """
        Research a topic using multiple queries.
        
        Args:
            topic: Main topic to research
            queries: List of search queries
            max_results_per_query: Max results per query
        
        Returns:
            {
                "topic": str,
                "results": List[Dict],  # Results per query
                "all_chunks": List[Dict],  # All sources combined
                "summary": str  # AI-generated summary
            }
        """
        all_results = []
        all_chunks = []
        
        for query in queries:
            result = self.search(query, max_results=max_results_per_query)
            if result["success"]:
                all_results.append({
                    "query": query,
                    "answer": result["answer"],
                    "chunks": result["chunks"]
                })
                all_chunks.extend(result["chunks"])
            
            # Rate limiting (avoid hitting API limits)
            time.sleep(0.5)
        
        # Generate summary of all findings
        summary_prompt = f"""Summarize the research findings for: {topic}

Research Results:
{self._format_research_results(all_results)}

Provide a concise summary with key insights."""

        summary_response = self.client.models.generate_content(
            model=self.model_name,
            contents=summary_prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        return {
            "topic": topic,
            "results": all_results,
            "all_chunks": all_chunks,
            "summary": summary_response.text
        }
    
    def _format_research_results(self, results: List[Dict]) -> str:
        """Format research results for summarization"""
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. Query: {result['query']}\n"
            formatted += f"   Answer: {result['answer'][:200]}...\n"
            formatted += f"   Sources: {len(result['chunks'])} found\n"
        return formatted
    
    def extract_citations(
        self,
        text: str,
        supports: List[Dict]
    ) -> str:
        """
        Format text with inline citations.
        
        Args:
            text: Original text
            supports: Grounding supports with chunk indices
        
        Returns:
            Text with [1], [2] style citations
        """
        # Sort supports by start_index (reverse order for insertion)
        sorted_supports = sorted(
            supports,
            key=lambda s: s["segment"]["start_index"],
            reverse=True
        )
        
        cited_text = text
        for support in sorted_supports:
            # Get citation numbers from chunk indices
            citations = support.get("grounding_chunk_indices", [])
            if citations:
                citation_str = f"[{','.join(str(i+1) for i in citations)}]"
                
                # Insert citation after the segment
                end_idx = support["segment"]["end_index"]
                cited_text = cited_text[:end_idx] + citation_str + cited_text[end_idx:]
        
        return cited_text
    
    def format_sources_markdown(self, chunks: List[Dict]) -> str:
        """
        Format grounding chunks as markdown citations.
        
        Returns:
            Markdown formatted source list
        """
        if not chunks:
            return ""
        
        markdown = "\n\n## 📚 Sources\n\n"
        for i, chunk in enumerate(chunks, 1):
            title = chunk.get("title", "Unknown")
            uri = chunk.get("uri", "")
            snippet = chunk.get("snippet", "")
            
            markdown += f"{i}. **{title}**\n"
            if uri:
                markdown += f"   - URL: {uri}\n"
            if snippet:
                markdown += f"   - Snippet: {snippet}\n"
            markdown += "\n"
        
        return markdown


# ===== Example Usage =====

def example_grounding_search():
    """Example of using Gemini Grounding for web search"""
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        return
    
    # Initialize agent
    agent = GeminiGroundingAgent(api_key)
    
    # Perform search
    print("🔍 Searching: What is the market size of meal planning apps?")
    result = agent.search(
        "What is the market size of meal planning apps in 2025?",
        max_results=5
    )
    
    if result["success"]:
        print("\n✅ Search successful!")
        print(f"\n📝 Answer:\n{result['answer']}\n")
        print(f"\n🔗 Found {len(result['chunks'])} sources:")
        for i, chunk in enumerate(result['chunks'], 1):
            print(f"  {i}. {chunk['title']}")
            print(f"     {chunk['uri']}")
        
        # Format as markdown
        markdown = agent.format_sources_markdown(result['chunks'])
        print(f"\n📄 Markdown:\n{markdown}")
    else:
        print(f"\n❌ Search failed: {result.get('error')}")


def example_research_topic():
    """Example of researching a topic with multiple queries"""
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        return
    
    agent = GeminiGroundingAgent(api_key)
    
    # Research with multiple queries
    print("🔬 Researching: AI-powered meal planning apps")
    result = agent.research_topic(
        topic="AI-powered meal planning apps",
        queries=[
            "What features do successful meal planning apps have?",
            "Who are the top competitors in meal planning apps?",
            "What are user pain points with meal planning apps?"
        ],
        max_results_per_query=3
    )
    
    print(f"\n✅ Research complete!")
    print(f"\n📊 Summary:\n{result['summary']}\n")
    print(f"\n🔍 Total sources found: {len(result['all_chunks'])}")


if __name__ == "__main__":
    print("=== Gemini Grounding Agent Examples ===\n")
    
    # Run examples
    example_grounding_search()
    print("\n" + "="*50 + "\n")
    example_research_topic()
