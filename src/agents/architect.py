"""
Architecture Designer Agent - BMAD Solutioning Phase
Generates system architecture, tech stack, database schema, and NFR coverage
"""

from typing import Dict, Any
from datetime import datetime
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..agent_state import AgentState, add_status_message

class ArchitectureDesignerAgent:
    """
    Architecture Designer - Solutioning Phase
    
    Responsibilities:
    - System component design
    - Tech stack selection with justification
    - Database schema design
    - API architecture
    - NFR coverage validation (≥90%)
    - Security architecture
    - Scalability strategy
    
    Output: architecture.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Architecture Designer agent"""
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
    
    def generate_architecture(self, state: AgentState) -> str:
        """
        Generate architecture document.
        
        Args:
            state: Agent state with PRD and requirements
        
        Returns:
            Markdown formatted architecture document
        """
        idea = state["idea"]
        prd = state["prd"]
        tech_spec = state.get("tech_spec", "")
        # In a full implementation, requirements would be parsed into objects
        # For now, we assume simple list or empty
        requirements = state.get("requirements", [])
        
        add_status_message(state, "Architect: Designing system architecture...")
        
        prompt = f"""
{self.helpers.get_role_definition("architect")}

**Objective:**
Generate a comprehensive **Architecture Document** based on the PRD and Tech Spec.
Address Functional and Non-Functional Requirements.

**Input - PRD:**
{prd[:2000]}... [truncated for context]

**Input - Tech Spec:**
{tech_spec}

**Structure:**
# System Architecture: {idea}

## 1. System Overview
[High-level design description]

## 2. Component Architecture (Mermaid)
{self.helpers.get_mermaid_guidelines()}
```mermaid
graph TB
    Client[Client App] --> API[API Gateway]
    API --> Auth[Auth Service]
    API --> Core[Core Service]
    Core --> DB[(Database)]
```
(If Mermaid fails, provide text description)

## 3. Technology Stack
| Layer | Choice | Rationale | NFR Addressed |
|-------|--------|-----------|---------------|
| Frontend | ... | ... | ... |
| Backend | ... | ... | ... |
| Database | ... | ... | ... |

## 4. Database Schema
[ER Diagram or Text Description]

## 5. API Design
- **Style:** [REST/GraphQL]
- **Key Endpoints:**
  - `GET /resource`
  - `POST /resource`

## 6. NFR Coverage
- **Performance:** [Strategy]
- **Security:** [Strategy]
- **Scalability:** [Strategy]

---
**Rationale:**
Explain why this architecture was chosen (e.g., monolith vs microservices).

**Agent Guidance:**
Next step is UX Design. The User Flows must align with this API structure.
"""
        
        # Use PRO model for architecture if possible, or fall back to configured
        # For now, rely on configured model_name (likely Flash for speed)
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        architecture = result["text"]
        
        # Add NFR coverage calculation (simulation)
        coverage, uncovered = self.helpers.calculate_nfr_coverage(requirements, architecture)
        add_status_message(state, f"Architect: NFR coverage check: {coverage:.1f}%")
        
        return architecture