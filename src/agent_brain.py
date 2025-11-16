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
from .mermaid_utils import (
    extract_mermaid_blocks,
    validate_mermaid_block,
    validate_markdown_mermaid,
    log_mermaid_attempt,
    fix_common_mermaid_errors
)

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
        self.status_callback: Optional[Callable[[str], None]] = None
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def _update_status(self, message: str):
        """Update status and call callback if set"""
        self.state.progress = message
        if self.status_callback:
            self.status_callback(message)
    
    def _fix_mermaid_diagram(self, mermaid_code: str, error_reason: str, max_attempts: int = 3) -> tuple[str, bool]:
        """
        Attempt to fix a broken Mermaid diagram using AI
        
        Args:
            mermaid_code: The invalid Mermaid code
            error_reason: Description of the error
            max_attempts: Maximum fix attempts
            
        Returns:
            Tuple of (fixed_code, is_valid)
        """
        current_code = mermaid_code
        
        for attempt in range(max_attempts):
            try:
                # Create fix prompt
                fix_prompt = self.prompts.format_fix_mermaid(current_code, error_reason)
                
                # Call AI to fix (use Flash-Lite for speed)
                time.sleep(2)  # Rate limit protection
                response = self.gemini_client.generate(
                    prompt=fix_prompt,
                    model_type=ModelType.FLASH_LITE,
                    temperature=0.3  # Low temperature for precise fixes
                )
                
                # Extract the mermaid block from response
                blocks = extract_mermaid_blocks(response)
                if not blocks:
                    # Try to extract without fences
                    current_code = response.strip()
                else:
                    current_code = blocks[0]
                
                # Validate the fix
                is_valid, new_error = validate_mermaid_block(current_code)
                
                if is_valid:
                    return current_code, True
                else:
                    # Update error reason for next attempt
                    error_reason = new_error
                    
            except Exception as e:
                # Log error and continue to next attempt
                print(f"Mermaid fix attempt {attempt+1} failed: {e}")
                continue
        
        # If all attempts failed, try automatic fixes
        try:
            auto_fixed = fix_common_mermaid_errors(current_code)
            is_valid, _ = validate_mermaid_block(auto_fixed)
            if is_valid:
                return auto_fixed, True
        except Exception:
            pass
        
        return current_code, False
    
    def _validate_and_fix_mermaid_in_markdown(self, markdown: str, file_type: str) -> str:
        """
        Validate and fix all Mermaid diagrams in a markdown file
        
        Args:
            markdown: Full markdown content
            file_type: Type of file (for logging)
            
        Returns:
            Markdown with fixed Mermaid diagrams
        """
        # Extract all Mermaid blocks
        blocks = extract_mermaid_blocks(markdown)
        
        if not blocks:
            # No Mermaid blocks found - nothing to fix
            return markdown
        
        # Log original attempt
        for i, block in enumerate(blocks):
            is_valid, error = validate_mermaid_block(block)
            log_mermaid_attempt(file_type, 0, block, is_valid, error)
            
            if not is_valid:
                self._update_status(f"🔧 Fixing Mermaid diagram {i+1} in {file_type}...")
                
                # Try to fix
                fixed_block, success = self._fix_mermaid_diagram(block, error)
                
                if success:
                    self._update_status(f"✅ Fixed Mermaid diagram {i+1} in {file_type}")
                    # Replace the broken block with fixed one
                    markdown = markdown.replace(
                        f"```mermaid\n{block}\n```",
                        f"```mermaid\n{fixed_block}\n```"
                    )
                    # Log successful fix
                    log_mermaid_attempt(file_type, 1, fixed_block, True, "")
                else:
                    self._update_status(f"⚠️  Could not auto-fix Mermaid diagram {i+1} in {file_type}")
                    # Log failed fix attempt
                    log_mermaid_attempt(file_type, 1, fixed_block, False, "max attempts reached")
        
        return markdown
    
    def generate_mvp(self, idea: str) -> Dict[str, str]:
        """
        Main entry point: Generate complete MVP specification
        
        Args:
            idea: The startup idea from user
            
        Returns:
            Dictionary with 5 markdown files
        """
        try:
            # Phase 1: Plan research queries
            self._update_status("🤖 Understanding your idea and planning research...")
            self.state.phase = "planning"
            
            queries = self._generate_search_queries(idea)
            
            # Phase 2: Conduct research
            self._update_status("🔍 Researching competitor features and user feedback...")
            self.state.phase = "research"
            
            research_results = self._conduct_research(queries)
            
            # Phase 3: Synthesize research
            self._update_status("🧠 Analyzing research and identifying insights...")
            self.state.phase = "synthesis"
            
            research_summary = self._summarize_research(idea, research_results)
            
            # Phase 4: Generate MVP files
            self._update_status("✍️ Generating complete MVP specification...")
            self.state.phase = "generation"
            
            mvp_files = self._generate_files(idea, research_summary)
            
            # Done
            self._update_status("✅ Complete! Your MVP blueprint is ready.")
            self.state.phase = "complete"
            
            return mvp_files
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self._update_status(error_msg)
            self.state.phase = "error"
            self.state.error = str(e)
            
            # Return fallback generation
            return self._generate_fallback(idea, str(e))
    
    def _generate_search_queries(self, idea: str) -> Dict[str, list]:
        """
        Phase 1: Generate search queries (Flash Lite with fallback)
        
        Args:
            idea: Startup idea
            
        Returns:
            Dictionary with competitor_queries and pain_point_queries
        """
        prompt = self.prompts.format_search_queries(idea)
        
        # Try Flash Lite first
        try:
            queries = self.model_router.route_json(
                task="planning",  # Flash Lite
                prompt=prompt,
                temperature=0.5
            )
            
            # Validate structure
            if "competitor_queries" not in queries or "pain_point_queries" not in queries:
                raise ValueError("Invalid query structure")
            
            self.state.data['queries'] = queries
            return queries
            
        except Exception as e1:
            # Fallback 1: Try Flash
            try:
                self._update_status("⚠️  Retrying query generation...")
                time.sleep(2)
                queries = self.model_router.route_json(
                    task="generation",  # Flash
                    prompt=prompt,
                    temperature=0.5
                )
                if "competitor_queries" in queries and "pain_point_queries" in queries:
                    return queries
                raise ValueError("Invalid structure from Flash")
            except Exception as e2:
                # Fallback 2: Hardcoded queries
                self._update_status("⚠️  Using fallback queries...")
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
        competitor_queries = queries.get("competitor_queries", [])
        pain_point_queries = queries.get("pain_point_queries", [])

        # Use google-search-mcp for web research (MCP call visible in logs)
        web_results_blocks = []
        for q in competitor_queries:
            resp = self.google_search_mcp.search(q, limit=5)
            if resp.get("success"):
                for item in resp.get("results", []):
                    web_results_blocks.append(
                        f"- [{item.get('title','')}]({item.get('link','')}) — {item.get('snippet','')}"
                    )
            else:
                # Fallback: rely on existing orchestrator if MCP search fails
                break

        if web_results_blocks:
            web_results = "## Web Research (via google-search-mcp)\n\n" + "\n".join(web_results_blocks)
        else:
            # Fallback to legacy orchestrator (which now itself uses web-only research)
            legacy = self.research_orchestrator.conduct_full_research(
                competitor_queries=competitor_queries,
                pain_point_queries=pain_point_queries,
                subreddits=None,
            )
            web_results = legacy.get("web_results", "")

        # For social_results, keep compatibility but clarify web-only if using our MCP path
        social_results = "User feedback is inferred from web research and forums via MCP web search."

        results = {
            "web_results": web_results or "No web research results.",
            "social_results": social_results,
        }

        self.state.data["research_results"] = results
        return results
    
    def _summarize_research(
        self,
        idea: str,
        research_results: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Phase 3: Synthesize research (Flash with fallback)
        
        Args:
            idea: Startup idea
            research_results: Raw research data
            
        Returns:
            Structured research summary
        """
        prompt = self.prompts.format_summarize_research(
            idea=idea,
            web_results=research_results.get("web_results", "No data"),
            social_results=research_results.get("social_results", "No data")
        )
        
        # Try Flash first
        try:
            summary = self.model_router.route_json(
                task="planning",  # Flash (15 RPM)
                prompt=prompt,
                temperature=0.4
            )
            
            self.state.data['research_summary'] = summary
            return summary
            
        except Exception as e1:
            # Fallback 1: Try Flash-Lite
            try:
                self._update_status("⚠️  Retrying synthesis...")
                time.sleep(2)
                summary = self.model_router.route_json(
                    task="query",  # Flash Lite
                    prompt=prompt,
                    temperature=0.4
                )
                return summary
            except Exception as e2:
                # Fallback 2: Hardcoded summary
                self._update_status("⚠️  Using fallback research summary...")
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
        research_summary: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Phase 4: Generate MVP files (Flash with fallback to Pro)
        
        Args:
            idea: Startup idea
            research_summary: Synthesized research
            
        Returns:
            Dictionary with 5 markdown file contents
        """
        prompt = self.prompts.format_generate_mvp(idea, research_summary)
        
        # Add delay to respect rate limits
        time.sleep(7)
        
        # Try Flash first
        try:
            # First pass: generate raw files
            files = self.model_router.route_json(
                task="generation",  # Flash (15 RPM)
                prompt=prompt,
                temperature=0.6
            )
            
            # Validate all files present
            required_keys = [
                "features_md",
                "architecture_md",
                "design_md",
                "user_flow_md",
                "roadmap_md"
            ]
            
            for key in required_keys:
                if key not in files:
                    raise ValueError(f"Missing file: {key}")

            # Normalize markdown via markdownify-mcp (MCP call visible in logs)
            normalized_files = {}
            for key in required_keys:
                content = files.get(key, "")
                # First, normalize via MCP
                normalized = self.markdownify_mcp.format_markdown(content)
                
                # Then sanitize to remove invisible characters
                sanitized = sanitize_markdown(normalized)
                
                # Validate and fix Mermaid blocks if this file should contain them
                if key in ["architecture_md", "user_flow_md"]:
                    # These files SHOULD have Mermaid diagrams
                    file_type = key.replace("_md", "")
                    sanitized = self._validate_and_fix_mermaid_in_markdown(sanitized, file_type)
                    
                    # Final validation check
                    is_valid, error_msg = validate_markdown_mermaid(sanitized)
                    if not is_valid:
                        self._update_status(f"⚠️  Warning: {key} still has Mermaid issues: {error_msg}")
                        print(f"Mermaid validation warning for {key}: {error_msg}")
                
                normalized_files[key] = sanitized

            self.state.data["mvp_files"] = normalized_files
            return normalized_files
            
        except Exception as e1:
            # Fallback 1: Try Pro model (better quality, lower RPM)
            try:
                self._update_status("⚠️  Retrying with Pro model...")
                time.sleep(5)
                files = self.model_router.route_json(
                    task="synthesis",  # Pro
                    prompt=prompt,
                    temperature=0.6
                )
                
                # Validate
                for key in ["features_md", "architecture_md", "design_md", "user_flow_md", "roadmap_md"]:
                    if key not in files:
                        raise ValueError(f"Missing {key}")
                
                return files
            except Exception as e2:
                # If both fail, raise to trigger main fallback
                raise Exception(f"File generation failed with both Flash and Pro: {str(e2)}")
    
    def _generate_fallback(self, idea: str, error: str) -> Dict[str, str]:
        """
        Last-resort fallback generation
        
        Args:
            idea: Startup idea
            error: Error message
            
        Returns:
            Dictionary with basic MVP files
        """
        self._update_status("⚠️  Using emergency fallback generation...")
        
        prompt = self.prompts.format_generate_mvp_fallback(
            idea=idea,
            context=f"Error occurred: {error}"
        )
        
        try:
            # Try Flash Lite as last resort
            time.sleep(3)
            files = self.model_router.route_json(
                task="generation",
                prompt=prompt,
                temperature=0.7
            )
            
            return files
            
        except Exception as e:
            # Absolute last resort: Hardcoded templates
            self._update_status("⚠️  Using basic templates...")
            return {
                "features_md": f"# MVP Features for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Core Features\n- Feature 1\n- Feature 2\n- Feature 3",
                "architecture_md": f"# Architecture for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Tech Stack\n- Frontend\n- Backend\n- Database",
                "design_md": f"# Design for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Design Principles\n- Simple\n- Intuitive\n- Accessible",
                "user_flow_md": f"# User Flow for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Main Flow\n1. User lands\n2. User interacts\n3. User completes",
                "roadmap_md": f"# Roadmap for: {idea}\n\n*Error occurred. Basic template provided.*\n\n## Timeline\n- Week 1-2: Setup\n- Week 3-4: Build\n- Week 5-6: Launch"
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
