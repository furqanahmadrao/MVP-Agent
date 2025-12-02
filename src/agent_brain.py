"""
Agent Brain Module - Main orchestration logic for MVP Agent
Coordinates all components: AI models, MCP clients, and prompts
"""

from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
import time

from .ai_models import GeminiClient, ModelRouter, ModelType
from .mcp_clients import get_research_orchestrator
from .prompts import PromptTemplates, get_system_prompt
from .mcp_http_clients import GoogleSearchMCPClient, MarkdownifyMCPClient
from .file_manager import sanitize_markdown

@dataclass
class AgentState:
    """Tracks the current state of the agent"""
    phase: str = "idle"
    progress: str = ""
    error: Optional[str] = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class MVPAgent:
    """
    Main agent that orchestrates the MVP generation process
    Coordinates AI models, MCP tools, and prompt templates
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize MVP Agent
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        # Initialize components
        self.gemini_client = GeminiClient(gemini_api_key)
        self.model_router = ModelRouter(self.gemini_client)
        self.research_orchestrator = get_research_orchestrator()
        self.google_search_mcp = GoogleSearchMCPClient()
        self.markdownify_mcp = MarkdownifyMCPClient()
        self.prompts = PromptTemplates()
        
        # Agent state
        self.state = AgentState()
        
        # Callbacks for UI updates
        self.status_callback: Optional[Callable[[Dict,], None]] = None

        # Metrics
        self.start_time: float = 0.0
        self.total_tokens_used: int = 0
    
    def set_status_callback(self, callback: Callable[[Dict,], None]):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def _update_status(self, message: str, type: str = "INFO", phase: str = None, details: Dict = None):
        """Update status and call callback if set"""
        if phase is None:
            phase = self.state.phase

        status_event = {
            "timestamp": time.time(),
            "elapsed_time": time.time() - self.start_time if self.start_time else 0.0,
            "message": message,
            "type": type, # INFO, WARNING, ERROR, SUCCESS, DEBUG
            "phase": phase,
            "tokens_used": self.total_tokens_used,
            "details": details if details else {}
        }
        self.state.progress = message # Keep old progress string for compatibility, though we'll use event
        if self.status_callback:
            self.status_callback(status_event)
    

    def generate_mvp(self, idea: str) -> Dict[str, str]:
        """
        Main entry point: Generate complete MVP specification
        
        Args:
            idea: The startup idea from user
            
        Returns:
            Dictionary with 8 markdown files
        """
        self.start_time = time.time()  # Initialize timer for this run
        self.total_tokens_used = 0     # Reset token count for this run
        try:
            # Phase 1: Plan research queries
            self._update_status("🤖 Understanding your idea and planning research...", phase="planning")
            self.state.phase = "planning"
            
            queries = self._generate_search_queries(idea)
            
            # Phase 2: Conduct research
            self._update_status("🔍 Researching competitor features and user feedback...", phase="research")
            self.state.phase = "research"
            
            research_results = self._conduct_research(queries)
            
            # Phase 3: Synthesize research
            self._update_status("🧠 Analyzing research and identifying insights...", phase="synthesis")
            self.state.phase = "synthesis"
            
            research_summary = self._summarize_research(idea, research_results)
            
            # Phase 4: Generate 8 MVP files
            self._update_status("✍️ Generating complete MVP specification...", phase="generation")
            self.state.phase = "generation"
            
            mvp_files = self._generate_files(idea, research_summary)
            
            # Done
            self._update_status("✅ Complete! Your MVP blueprint is ready.", type="SUCCESS", phase="complete")
            self.state.phase = "complete"
            
            return mvp_files
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self._update_status(error_msg, type="ERROR", phase="error", details={"error_details": str(e)})
            self.state.phase = "error"
            self.state.error = str(e)
            
            # Return fallback generation
            return self._generate_fallback(idea, str(e))
    
    def _generate_search_queries(self, idea: str) -> Dict[str, list]:
        """
        Phase 1: Generate search queries (Flash-Lite)

        Args:
            idea: Startup idea

        Returns:
            Dictionary with competitor_queries and pain_point_queries
        """
        self._update_status("Starting query generation (Phase 1)...", type="DEBUG", phase="planning")
        prompt = self.prompts.format_search_queries(idea)

        # Try Flash-Lite first (fastest, cheapest for simple queries)
        try:
            queries = self.model_router.route_json(
                task="search_query",  # Flash-Lite
                prompt=prompt,
                temperature=0.5
            )
            self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens
            
            # Validate structure
            if "competitor_queries" not in queries or "pain_point_queries" not in queries:
                raise ValueError("Invalid query structure")
            
            self.state.data['queries'] = queries
            self._update_status("Query generation successful (Flash-Lite).", type="SUCCESS", phase="planning")
            return queries
            
        except Exception as e1:
            self._update_status("⚠️ Retrying query generation (Flash-Lite)...", type="WARNING", phase="planning", details={"error": str(e1)})
            time.sleep(2)
            queries = self.model_router.route_json(
                task="search_query",  # Flash-Lite
                prompt=prompt,
                temperature=0.5
            )
            self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens
            if "competitor_queries" in queries and "pain_point_queries" in queries:
                self._update_status("Query generation successful (Flash-Lite fallback).", type="SUCCESS", phase="planning")
                return queries
            raise ValueError("Invalid structure from Flash-Lite")
        except Exception as e2:
            self._update_status("⚠️ Using hardcoded fallback queries...", type="WARNING", phase="planning", details={"error": str(e2)})
            return {
                "competitor_queries": [
                        f"{idea} features",
                        f"{idea} product review",
                        f"best {idea} apps"
                    ],
                    "pain_point_queries": [
                        f"{idea} problems",
                        f"{idea} complaints reddit",
                        f"what {idea} users want"
                    ]
                }
    
    def _conduct_research(self, queries: Dict[str, list]) -> Dict[str, str]:
        """
        Phase 2: Conduct research using MCP servers
        
        Args:
            queries: Dictionary with search queries
            
        Returns:
            Dictionary with web_results and social_results
        """
        self._update_status("Starting web research (Phase 2)...", type="DEBUG", phase="research")
        competitor_queries = queries.get("competitor_queries", [])
        pain_point_queries = queries.get("pain_point_queries", [])

        # Use google-search-mcp for web research (MCP call visible in logs)
        web_results_blocks = []
        all_queries = competitor_queries + pain_point_queries
        
        self._update_status(f"Executing {len(all_queries)} web searches...", type="INFO", phase="research", details={"num_queries": len(all_queries)})
        for i, q in enumerate(all_queries):
            self._update_status(f"Searching query {i+1}/{len(all_queries)}: '{q}'", type="DEBUG", phase="research")
            resp = self.google_search_mcp.search(q, limit=3)
            if resp.get("success"):
                num_results = len(resp.get("results", []))
                self._update_status(f"Found {num_results} results for query '{q}'", type="DEBUG", phase="research", details={"query": q, "num_results": num_results})
                for item in resp.get("results", []):
                    web_results_blocks.append(
                        f"- [{item.get('title','')}]({item.get('link','')}) — {item.get('snippet','')}"
                    )
            else:
                self._update_status(f"⚠️ Google Search MCP failed for query '{q}'. Falling back to legacy orchestrator.", type="WARNING", phase="research", details={"query": q, "error": resp.get("error", "unknown")})
                # Fallback: rely on existing orchestrator if MCP search fails
                break

        if web_results_blocks:
            web_results = "## Web Research (via google-search-mcp)\n\n" + "\n".join(web_results_blocks)
            self._update_status("Successfully gathered web research results via Google Search MCP.", type="INFO", phase="research")
        else:
            self._update_status("⚠️ No results from Google Search MCP. Using legacy research orchestrator.", type="WARNING", phase="research")
            # Fallback to legacy orchestrator (which now itself uses web-only research)
            legacy = self.research_orchestrator.conduct_full_research(
                competitor_queries=competitor_queries,
                pain_point_queries=pain_point_queries,
                subreddits=None,
            )
            web_results = legacy.get("web_results", "")
            self._update_status("Successfully gathered web research results via legacy orchestrator.", type="INFO", phase="research")


        # For social_results, keep compatibility but clarify web-only if using our MCP path
        social_results = "User feedback is inferred from web research and forums via MCP web search."
        self._update_status("Social media research inferred from web search results.", type="INFO", phase="research")

        results = {
            "web_results": web_results or "No web research results.",
            "social_results": social_results,
        }

        self.state.data["research_results"] = results
        self._update_status("Web research phase completed.", type="SUCCESS", phase="research")
        return results
    
    def _summarize_research(
        self,
        idea: str,
        research_results: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Phase 3: Synthesize research (Flash with fallback to Flash-Lite)

        Args:
            idea: Startup idea
            research_results: Raw research data

        Returns:
            Structured research summary
        """
        self._update_status("Starting research summarization (Phase 3)...", type="DEBUG", phase="synthesis")
        prompt = self.prompts.format_summarize_research(
            idea=idea,
            web_results=research_results.get("web_results", "No data"),
            social_results=research_results.get("social_results", "No data")
        )

        # Try Flash first (good balance of speed and quality)
        try:
            summary = self.model_router.route_json(
                task="planning",  # Flash (15 RPM)
                prompt=prompt,
                temperature=0.4
            )
            self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens

            self.state.data['research_summary'] = summary
            self._update_status("Research summarization successful (Flash).", type="SUCCESS", phase="synthesis")
            return summary

        except Exception as e1:
            # Fallback 1: Try Flash-Lite
            try:
                self._update_status("⚠️ Retrying synthesis with Flash-Lite...", type="WARNING", phase="synthesis", details={"error": str(e1)})
                time.sleep(2)
                summary = self.model_router.route_json(
                    task="simple",  # Flash-Lite
                    prompt=prompt,
                    temperature=0.4
                )
                self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens
                self._update_status("Research summarization successful (Flash-Lite fallback).", type="SUCCESS", phase="synthesis")
                return summary
            except Exception as e2:
                # Fallback 2: Hardcoded summary
                self._update_status("⚠️ Using hardcoded fallback research summary...", type="WARNING", phase="synthesis", details={"error": str(e2)})
                return {
                    "core_problem": f"Solving challenges in the {idea} space",
                    "target_audience": "General users",
                    "key_features_found": ["Basic functionality", "User interface", "Data storage"],
                    "user_complaints": ["Complexity", "Performance", "Cost"],
                    "market_gaps": ["Better UX", "Faster performance", "Lower cost"],
                    "competitive_advantages": ["Modern tech stack", "User-focused", "Scalable"]
                }
    
    def _generate_files(
        self,
        idea: str,
        research_summary: Dict[str, Any],
        tech_preference: str = "",
        platform: str = "",
        constraint: str = ""
    ) -> Dict[str, str]:
        """
        Phase 4: Generate MVP files (Pro with fallback to Flash-Lite)
        
        Args:
            idea: Startup idea
            research_summary: Synthesized research
            tech_preference: Optional tech stack preference
            platform: Optional target platform
            constraint: Optional constraints
            
        Returns:
            Dictionary with 8 markdown file contents
        """
        self._update_status(
            "Starting MVP file generation (Phase 4)...", 
            type="DEBUG", 
            phase="generation",
            details={
                "tech_preference": tech_preference,
                "platform": platform,
                "constraint": constraint
            }
        )
        prompt = self.prompts.format_generate_mvp(
            idea, 
            research_summary,
            tech_preference=tech_preference,
            platform=platform,
            constraint=constraint
        )

        # Add delay to respect rate limits (Pro: 2 RPM)
        time.sleep(7)

        # Try Pro first (better context window for large MVP generation)
        try:
            self._update_status("Generating MVP files using Pro model...", type="INFO", phase="generation")
            # First pass: generate raw files
            files = self.model_router.route_json(
                task="generation",  # Pro (2 RPM, large context)
                prompt=prompt,
                temperature=0.6
            )
            self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens
            
            # Validate all files present
            required_keys = [
                "overview_md",
                "features_md",
                "architecture_md",
                "design_md",
                "user_flow_md",
                "roadmap_md",
                "business_model_md",
                "testing_plan_md"
            ]
            
            for key in required_keys:
                if key not in files:
                    raise ValueError(f"Missing file: {key}")

            self._update_status("MVP files generated by Pro. Sanitizing markdown...", type="DEBUG", phase="generation")
            # Sanitize markdown (content from Gemini is already valid markdown)
            normalized_files = {}
            for key in required_keys:
                content = files.get(key, "")
                # Only sanitize to remove invisible characters (skip markdownify - content is already markdown)
                sanitized = sanitize_markdown(content)
                normalized_files[key] = sanitized

            self.state.data["mvp_files"] = normalized_files
            self._update_status("MVP file generation successful.", type="SUCCESS", phase="generation")
            return normalized_files
            
        except Exception as e1:
            # Fallback 1: Retry with Pro model (transient errors like network, rate limits)
            try:
                self._update_status("⚠️ Pro model failed. Retrying with Pro model (attempt 2)...", type="WARNING", phase="generation", details={"error": str(e1)})
                time.sleep(35)  # Wait 35s to respect 2 RPM rate limit (30s) + 5s buffer
                files = self.model_router.route_json(
                    task="generation",  # Pro (same model, transient errors)
                    prompt=prompt,
                    temperature=0.6
                )
                self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens

                # Validate
                required_keys = ["overview_md", "features_md", "architecture_md", "design_md", "user_flow_md", "roadmap_md", "business_model_md", "testing_plan_md"]
                for key in required_keys:
                    if key not in files:
                        raise ValueError(f"Missing {key}")

                # Sanitize markdown (content from Gemini is already valid markdown)
                normalized_files = {}
                for key in required_keys:
                    content = files.get(key, "")
                    # Only sanitize to remove invisible characters (skip markdownify - content is already markdown)
                    sanitized = sanitize_markdown(content)
                    normalized_files[key] = sanitized

                self._update_status("MVP files generated by Pro model (retry successful).", type="SUCCESS", phase="generation")
                return normalized_files
            except Exception as e2:
                # If Pro fails twice, raise to trigger main fallback (hardcoded templates)
                raise Exception(f"File generation failed after 2 Pro attempts: {str(e2)}")
    
    def _generate_fallback(self, idea: str, error: str) -> Dict[str, str]:
        """
        Last-resort fallback generation
        
        Args:
            idea: Startup idea
            error: Error message
            
        Returns:
            Dictionary with 8 basic MVP files
        """
        self._update_status("🚨 Entering emergency fallback generation...", type="ERROR", phase="fallback", details={"trigger_error": error})
        
        prompt = self.prompts.format_generate_mvp_fallback(
            idea=idea,
            context=f"Error occurred: {error}"
        )
        
        try:
            self._update_status("Trying Pro for fallback generation...", type="INFO", phase="fallback")
            # Try Pro as last resort (large context needed)
            time.sleep(3)
            files = self.model_router.route_json(
                task="generation",  # Pro
                prompt=prompt,
                temperature=0.7
            )
            self.total_tokens_used += self.gemini_client.get_token_usage() # Accumulate tokens
            self._update_status("Fallback generation successful (Pro).", type="SUCCESS", phase="fallback")
            return files
            
        except Exception as e:
            self._update_status("⚠️ Flash Lite fallback also failed. Using hardcoded templates...", type="WARNING", phase="fallback", details={"error": str(e)})
            return {
                "overview_md": f"# [Product Name] – MVP Blueprint Overview\n\n*Error occurred. Basic template provided.*\n\n## Tagline\n- One-line summary.\n\n## Purpose & Vision\n- What the product aims to achieve.\n\n## What’s Included\n- List of files.\n\n## How to Use This Blueprint\n- Instructions for humans and agents.\n\n## Style & Formatting Conventions\n- Markdown, tables, diagrams.\n\n## Glossary\n- Key terms.\n\n## References\n- Research links.",
                "features_md": f"# MVP Features for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Core Features\n- Feature 1\n- Feature 2\n- Feature 3",
                "architecture_md": f"# Architecture for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Tech Stack\n- Frontend\n- Backend\n- Database",
                "design_md": f"# Design for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Design Principles\n- Simple\n- Intuitive\n- Accessible",
                "user_flow_md": f"# User Flow for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Main Flow\n1. User lands\n2. User interacts\n3. User completes",
                "roadmap_md": f"# Roadmap for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Timeline\n- Week 1-2: Setup\n- Week 3-4: Build\n- Week 5-6: Launch",
                "business_model_md": f"# Business Model for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Executive Summary\n- Describe the business vision here.\n\n## Business Model Canvas\n| Key Partners | Key Activities | Key Resources | Value Propositions | Customer Relationships | Channels | Customer Segments | Cost Structure | Revenue Streams |\n|--------------|---------------|--------------|--------------------|-----------------------|----------|-------------------|---------------|----------------|\n| Example      | Example       | Example      | Example            | Example               | Example  | Example           | Example       | Example        |\n\n## Revenue Model\n- List revenue streams here.\n\n## Cost Structure\n- List major costs here.\n\n## Go-to-Market Strategy\n- List main strategies here.\n\n## Competitive Advantage\n- List differentiators here.\n\n## Risks & Mitigations\n- List risks and mitigations here.\n\n## Edge Cases & Fallbacks\n- List edge cases here.\n\n## Implementation Hints & Best Practices\n- List best practices here.",
                "testing_plan_md": f"# Testing Plan for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Test Strategy\n- Manual and automated\n\n## Test Cases\n- Test 1\n- Test 2\n- Test 3\n\n## Tools\n- pytest\n- Selenium\n\n## Success Criteria\n- All tests pass\n\n## Risks\n- List risks here."
            }
    
    def get_token_usage(self) -> int:
        """Get total tokens used in this session"""
        return self.gemini_client.get_token_usage()

def create_agent(gemini_api_key: str) -> MVPAgent:
    """
    Create a new MVP Agent instance
    
    Args:
        gemini_api_key: Google Gemini API key
        
    Returns:
        Configured MVPAgent instance
    """
    return MVPAgent(gemini_api_key)
