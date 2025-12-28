"""
Market Analyst Agent - BMAD Analysis Phase
Generates product brief with market research, user personas, and competitor analysis
Uses Gemini Search Grounding for web research
"""

from typing import Dict, Any, List
from datetime import datetime
from ..ai_models import GeminiClient, ModelType
from ..grounding_agent import GeminiGroundingAgent
from ..helpers import BMAdHelpers, get_standard_prompt_suffix, get_mermaid_guidelines
from ..agent_state import AgentState, add_status_message


class MarketAnalystAgent:
    """
    Market Analyst - Analysis Phase
    
    Responsibilities:
    - Market research (size, trends, growth)
    - User persona identification
    - Competitor analysis
    - Pain point discovery
    - Value proposition definition
    
    Output: product_brief.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Market Analyst agent.
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        
        # Initialize clients
        self.llm = GeminiClient(api_key)
        self.grounding_agent = GeminiGroundingAgent(api_key, model_name)
    
    def generate_product_brief(self, state: AgentState) -> str:
        """
        Generate product brief document.
        
        Args:
            state: Current agent state with user idea
        
        Returns:
            Markdown formatted product brief
        """
        idea = state["idea"]
        project_level = state["project_level"]
        
        add_status_message(state, "Market Analyst: Starting market research...")
        
        # Step 1: Conduct market research
        research_data = self._conduct_market_research(idea, state)
        
        add_status_message(state, "Market Analyst: Analyzing competitors...")
        
        # Step 2: Identify competitors
        competitors = self._analyze_competitors(idea, state)
        
        add_status_message(state, "Market Analyst: Creating user personas...")
        
        # Step 3: Generate product brief
        product_brief = self._generate_brief_document(
            idea=idea,
            research_data=research_data,
            competitors=competitors,
            project_level=project_level,
            state=state
        )
        
        add_status_message(state, "Market Analyst: Product brief complete!")
        
        # Store research data in state
        state["research_results"].extend(research_data.get("results", []))
        state["citations"].extend(research_data.get("all_chunks", []))
        state["competitor_data"].extend(competitors)
        
        return product_brief
    
    def _conduct_market_research(self, idea: str, state: AgentState) -> Dict[str, Any]:
        """
        Conduct market research using Gemini Grounding.
        
        Returns:
            {
                "topic": str,
                "results": List[Dict],
                "all_chunks": List[Dict],
                "summary": str
            }
        """
        # Generate research queries
        queries = [
            f"What is the market size and growth rate for {idea}?",
            f"What are the current trends in {idea} industry?",
            f"Who are the target users for {idea}?",
            f"What are common pain points users face with {idea}?"
        ]
        
        # Track queries in state
        state["research_queries"].extend(queries)
        
        # Conduct research
        research_data = self.grounding_agent.research_topic(
            topic=idea,
            queries=queries,
            max_results_per_query=3
        )
        
        return research_data
    
    def _analyze_competitors(self, idea: str, state: AgentState) -> List[Dict[str, Any]]:
        """
        Analyze competitors using Gemini Grounding.
        
        Returns:
            List of competitor data
        """
        query = f"Who are the top 5 competitors or similar products to {idea}?"
        
        result = self.grounding_agent.search(query, max_results=5)
        
        if result["success"]:
            # Parse competitor data from answer
            competitors_prompt = f"""Based on this research about competitors for "{idea}":

{result['answer']}

Extract competitor information in this format:
1. Competitor Name
   - Strengths: ...
   - Weaknesses: ...
   - Market Position: ...

List 3-5 main competitors."""

            competitors_text = self.llm.generate(
                prompt=competitors_prompt,
                model_type=ModelType.FLASH,
                temperature=0.3
            )
            
            # Store raw competitor text (will be formatted in document)
            return [{
                "analysis": competitors_text,
                "sources": result["chunks"]
            }]
        
        return []
    
    def _generate_brief_document(
        self,
        idea: str,
        research_data: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        project_level: Any,
        state: AgentState
    ) -> str:
        """Generate the final product brief markdown document"""
        
        # Build comprehensive prompt
        prompt = f"""You are a Market Analyst creating a Product Brief for an MVP.

**Startup Idea:**
{idea}

**Project Complexity Level:** {project_level.name} (Level {project_level.value})

**Market Research Data:**
{research_data.get('summary', 'No research data available')}

**Competitor Analysis:**
{competitors[0]['analysis'] if competitors else 'No competitor data available'}

**Your Task:**
Generate a comprehensive Product Brief with the following sections:

1. **Executive Summary** (2-3 paragraphs)
   - Clear problem statement
   - Proposed solution
   - Target market
   - Unique value proposition

2. **Market Analysis**
   - Market size and growth projections
   - Key trends
   - Market segmentation
   - Opportunity gaps

3. **User Personas** (3-5 personas)
   Create a table with columns:
   | Persona Name | Description | Demographics | Pain Points | Goals | Tech Savviness |
   
   Make personas realistic and specific.

4. **Pain Points & User Needs**
   - List 5-8 key pain points users currently face
   - For each pain point, explain why it matters
   - Prioritize by severity (Critical/High/Medium)

5. **Competitor Landscape**
   Create a comparison table:
   | Competitor | Strengths | Weaknesses | Market Position | Differentiation Opportunity |
   
   Include 3-5 main competitors.

6. **Unique Value Proposition**
   - What makes this solution different?
   - Why should users choose this over competitors?
   - Key differentiators (3-5 points)

7. **Success Metrics** (KPIs)
   - User acquisition targets
   - Engagement metrics
   - Revenue/business metrics
   - Market penetration goals

8. **Market Segmentation Diagram** (Mermaid)
   Create a quadrantChart showing market segments by:
   - User sophistication (x-axis)
   - Willingness to pay (y-axis)
   
   If Mermaid diagram fails, provide a text-based description of market segments.

{get_standard_prompt_suffix()}

{get_mermaid_guidelines()}

**Important:**
- Use data from the research provided
- Be specific with numbers and projections
- Use tables for structured comparisons
- Include rationale for key decisions
- Add agent guidance at the end for the PRD Generator

**Document Header:**
Use this format:
# Product Brief: [Project Name]

**Subtitle:** Market Analysis & Product Strategy  
**Version:** 1.0  
**Generated By:** MVP Agent - Market Analyst  
**Date:** {datetime.now().strftime('%Y-%m-%d')}

---

Generate the complete Product Brief now.
"""
        
        # Generate document
        product_brief = self.llm.generate(
            prompt=prompt,
            model_type=ModelType.PRO,  # Use Pro for comprehensive analysis
            temperature=0.7
        )
        
        # Add sources section
        if research_data.get("all_chunks"):
            sources_markdown = self.grounding_agent.format_sources_markdown(
                research_data["all_chunks"][:10]  # Limit to top 10 sources
            )
            product_brief += sources_markdown
        
        # Add agent guidance
        agent_guidance = self.helpers.generate_agent_guidance(
            guidance="""**For PRD Generator:**
1. Use the identified user personas as the basis for user stories
2. Address all pain points listed in this brief with functional requirements
3. Ensure features align with the unique value proposition
4. Reference competitors when defining "Must-Have" vs "Should-Have" features
5. Target the market segments identified in this brief

**Key Data to Reference:**
- User personas (names, pain points, goals)
- Pain point priorities (Critical/High/Medium)
- Competitor weaknesses (opportunities for differentiation)
- Success metrics (will inform acceptance criteria)""",
            next_phase="Planning (PRD Generation)"
        )
        
        product_brief += agent_guidance
        
        return product_brief


# ===== Example Usage =====

if __name__ == "__main__":
    import os
    from ..agent_state import create_initial_state, ProjectLevel
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        exit(1)
    
    # Create test state
    state = create_initial_state(
        idea="An AI-powered meal planning app that helps busy professionals eat healthier by generating personalized weekly meal plans based on dietary preferences, budget, and available time.",
        api_key=api_key,
        project_level=ProjectLevel.MEDIUM
    )
    
    # Initialize agent
    agent = MarketAnalystAgent(api_key)
    
    # Generate product brief
    print("🔬 Generating Product Brief...")
    product_brief = agent.generate_product_brief(state)
    
    print("\n" + "="*50)
    print(product_brief)
    print("="*50)
    
    print(f"\n✅ Product Brief generated ({len(product_brief)} characters)")
    print(f"📊 Research queries: {len(state['research_queries'])}")
    print(f"🔗 Citations: {len(state['citations'])}")
