"Market Analyst Agent - BMAD Analysis Phase
Conducts market research using Gemini Grounding and generates Product Brief.
"

from typing import Dict, Any, Tuple
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..toon_utils import ToonFormatter
from ..agent_state import AgentState, add_status_message

class MarketAnalystAgent:
    """
    Market Analyst - Analysis Phase
    
    Responsibilities:
    - Conduct web research (Competitors, Trends, Pain Points) using Gemini Grounding
    - Synthesize research into a Product Brief
    - Output structured data for next phase
    
    Output: product_brief.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Market Analyst agent"""
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
    
    def generate_product_brief(self, state: AgentState) -> Tuple[str, Dict[str, Any]]:
        """
        Generate product brief using Gemini Grounding.
        
        Args:
            state: Agent state
        
        Returns:
            Tuple[product_brief_markdown, research_data_dict]
        """
        idea = state["idea"]
        add_status_message(state, "Market Analyst: Conducting grounded research...")
        
        # Step 1: Research & Synthesis (Gemini Grounding)
        research_prompt = f"""
{self.helpers.get_role_definition("market_analyst")}

**Objective:**
Analyze the startup idea below. Use Google Search to find:
1. Market Size & Trends (CAGR, TAM/SAM/SOM estimates)
2. Top 3 Competitors (Names, Strengths, Weaknesses)
3. Key User Pain Points (from forums, reviews)
4. Unique Value Proposition opportunities

**Startup Idea:**
{idea}

**Output:**
Provide a comprehensive market analysis.
{get_standard_prompt_suffix()}
"""
        
        # Call Gemini with Grounding
        research_result = self.llm.generate_with_grounding(research_prompt, model_name=self.model_name)
        research_text = research_result["text"]
        citations = research_result.get("citations", [])
        
        add_status_message(state, f"Market Analyst: Found {len(citations)} sources.")
        
        # Step 2: Format Product Brief (Markdown)
        format_prompt = f"""
{self.helpers.get_role_definition("market_analyst")}

**Objective:**
Create a structured **Product Brief** based on the research provided.

**Research Data:**
{research_text}

**Structure:**
# Product Brief: {idea}

## 1. Executive Summary
[Concise vision statement]

## 2. Market Analysis
- **Market Size:** [Data from research]
- **Trends:** [Key trends]

## 3. Competitive Landscape
| Competitor | Strengths | Weaknesses |
|------------|-----------|------------|
| [Name] | ... | ... |

## 4. User Personas
- **Primary:** [Description + Needs]
- **Secondary:** [Description + Needs]

## 5. Unique Value Proposition
[What makes this different?]

## 6. Success Metrics
- [Metric 1]
- [Metric 2]

---
**Rationale:**
Explain why this product concept is viable based on the research.

**Agent Guidance:**
The next agent (PRD Generator) should focus on features that solve the identified pain points: [List top 3 pain points].

**Citations:**
{self._format_citations(citations)}
"""
        
        brief_result = self.llm.generate_with_grounding(format_prompt, model_name=self.model_name)
        product_brief = brief_result["text"]
        
        # Step 3: Create Structured Data (TOON/JSON) for next agents
        structured_data = {
            "market_size": "Extracted from research", # In a real agent, we'd extract this specifically
            "competitors": ["Extracted competitor list"],
            "pain_points": ["Extracted pain points"],
            "citations": citations
        }
        
        return product_brief, structured_data

    def _format_citations(self, citations: list) -> str:
        if not citations:
            return "No citations available."
        
        formatted = "\n**Sources:**\n"
        for i, c in enumerate(citations, 1):
            formatted += f"{i}. [{c.get('title', 'Source')}]({c.get('uri', '#')})\n"
        return formatted