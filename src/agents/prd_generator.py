"""
PRD Generator Agent - BMAD Planning Phase
Generates Product Requirements Document with FR/NFR, user stories, and MoSCoW prioritization
"""

from typing import Dict, Any, List
from datetime import datetime
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..agent_state import AgentState, add_status_message


class PRDGeneratorAgent:
    """
    PRD Generator - Planning Phase
    
    Responsibilities:
    - Define functional requirements (FR-001, FR-002, ...)
    - Define non-functional requirements (NFR-001, NFR-002, ...)
    - Create user stories with acceptance criteria
    - MoSCoW prioritization
    - Requirements traceability
    
    Output: prd.md, tech_spec.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize PRD Generator agent"""
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
    
    def generate_prd(self, state: AgentState) -> str:
        """
        Generate Product Requirements Document.
        
        Args:
            state: Agent state with product brief
        
        Returns:
            Markdown formatted PRD
        """
        idea = state["idea"]
        product_brief = state["product_brief"]
        personas = state.get("personas", [])
        
        add_status_message(state, "PRD Generator: Defining requirements...")
        
        # Generate PRD
        prompt = f"""You are a Product Manager creating a comprehensive PRD (Product Requirements Document).

**Startup Idea:**
{idea}

**Product Brief Context:**
{product_brief[:2000]}... [truncated for brevity]

**Your Task:**
Generate a detailed PRD with structured requirements following BMAD patterns.

**Document Structure:**

# Product Requirements Document: [Project Name]

**Version:** 1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Author:** MVP Agent - PRD Generator

---

## 1. Functional Requirements

For each functional requirement, use this format:

### FR-001: [Requirement Title]
**Description:** Clear description of what the system must do  
**User Story:** As a [persona], I want to [action] so that [benefit]  
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Priority:** Must-Have | Should-Have | Could-Have | Won't-Have  
**Story Points:** [1-13, Fibonacci]  
**Dependencies:** None | FR-XXX, FR-YYY  
**Rationale:** Why this requirement is important

**Create 12-20 functional requirements** covering:
- User authentication & profiles
- Core features (based on value proposition)
- Data management
- Integrations
- User interactions

## 2. Non-Functional Requirements

### NFR-001: [Requirement Title]
**Description:** Quality attribute or constraint  
**Metric:** Measurable target (e.g., response time <200ms, 99.9% uptime)  
**Priority:** Must-Have | Should-Have  
**Test Strategy:** How to verify this requirement  
**Rationale:** Why this NFR matters

**Create 8-12 NFRs** covering:
- Performance
- Security
- Scalability
- Reliability
- Usability
- Accessibility (WCAG 2.1)

## 3. User Stories Grouped by Epics

### Epic 1: [Epic Name] (EP-001)
**Description:** High-level feature group  
**User Stories:**
- [FR-001] Story Title (5 points)
- [FR-002] Story Title (3 points)
**Total Points:** 8

**Create 4-6 epics** grouping related FRs.

## 4. MoSCoW Prioritization

**Must-Have** (MVP Blockers):
| ID | Title | Story Points | Rationale |
|----|-------|--------------|-----------|
| FR-001 | ... | 5 | Critical for core value |

**Should-Have** (Important, not blocking):
| ID | Title | Story Points | Rationale |
|----|-------|--------------|-----------|

**Could-Have** (Nice to have):
| ID | Title | Story Points | Rationale |
|----|-------|--------------|-----------|

**Won't-Have** (Explicitly excluded from v1.0):
| Feature | Reason for Exclusion |
|---------|---------------------|

## 5. Success Metrics & KPIs

Define how to measure success:
- User Acquisition: [target]
- Engagement: [metric and target]
- Retention: [metric and target]
- Business: [revenue/cost targets]

## 6. Out of Scope

Explicitly state what is NOT included in v1.0.

{get_standard_prompt_suffix()}

**Requirements Naming:**
- FR-001, FR-002 (Functional)
- NFR-001, NFR-002 (Non-Functional)
- EP-001, EP-002 (Epics)
- US-001, US-002 (User Stories, if separate from FRs)

**Story Points Scale:** Use Fibonacci (1, 2, 3, 5, 8, 13)
- 1-2: Simple task, <4 hours
- 3-5: Medium task, 1-2 days
- 8-13: Complex task, 3-5 days

Generate the complete PRD now.
"""
        
        prd = self.llm.generate(
            prompt=prompt,
            model_type=ModelType.PRO,
            temperature=0.5
        )
        
        # Parse requirements and store in state
        requirements = self.helpers.parse_requirements(prd)
        state["requirements"].extend(requirements)
        
        # Add agent guidance
        agent_guidance = self.helpers.generate_agent_guidance(
            guidance="""**For Architecture Designer:**
1. Address ALL NFRs in your system design (aim for ≥90% coverage)
2. Use the MoSCoW prioritization to guide technology choices
3. Design for the most complex user stories (8-13 points) first
4. Reference specific FR/NFR IDs in architecture decisions
5. Ensure scalability for projected user metrics

**Critical NFRs to Address:**
- Performance requirements (response times, throughput)
- Security requirements (authentication, authorization, encryption)
- Scalability targets (concurrent users, data volume)
- Availability/reliability (uptime, disaster recovery)

**Requirements Traceability:**
All architecture components must map to specific FR/NFR IDs.""",
            next_phase="Solutioning (Architecture Design)"
        )
        
        prd += agent_guidance
        
        add_status_message(state, f"PRD Generator: {len(requirements)} requirements defined!")
        
        return prd
    
    def generate_tech_spec(self, state: AgentState) -> str:
        """
        Generate Technical Specification (detailed technical requirements).
        
        Args:
            state: Agent state with PRD
        
        Returns:
            Markdown formatted tech spec
        """
        prd = state["prd"]
        requirements = state.get("requirements", [])
        
        add_status_message(state, "PRD Generator: Creating technical specification...")
        
        prompt = f"""You are a Technical Product Manager creating a Technical Specification document.

**Context:**
You have a PRD with {len(requirements)} requirements. Now create detailed technical specifications.

**PRD Summary:**
{prd[:1500]}... [truncated]

**Your Task:**
Generate a Technical Specification document.

# Technical Specification: [Project Name]

**Version:** 1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## 1. Technical Requirements

### Data Models
Define key data entities:
- User
- [Core entities from FRs]
- Relationships

### API Specifications
For each major feature:
- Endpoints (REST/GraphQL)
- Request/Response formats
- Authentication requirements

### Integration Requirements
Third-party services needed:
- Authentication (OAuth, etc.)
- Payments
- Email/SMS
- Storage
- Analytics

## 2. Performance Requirements

Map NFR-xxx to technical specs:
- Database query optimization strategies
- Caching requirements
- CDN usage
- Load balancing

## 3. Security Requirements

Map security NFRs to implementation:
- Authentication flow
- Authorization model (RBAC, ABAC)
- Data encryption (at rest, in transit)
- API security
- OWASP Top 10 mitigations

## 4. Scalability Design

- Horizontal vs vertical scaling strategy
- Database sharding approach
- Microservices boundaries (if applicable)
- Queue/message broker requirements

## 5. Technology Constraints

- Browser support
- Mobile OS versions
- Third-party API rate limits
- Budget constraints

{get_standard_prompt_suffix()}

Generate the complete Technical Specification now.
"""
        
        tech_spec = self.llm.generate(
            prompt=prompt,
            model_type=ModelType.FLASH,
            temperature=0.5
        )
        
        add_status_message(state, "PRD Generator: Technical specification complete!")
        
        return tech_spec


# ===== Example Usage =====

if __name__ == "__main__":
    import os
    from ..agent_state import create_initial_state, ProjectLevel
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        exit(1)
    
    # Create test state with mock product brief
    state = create_initial_state(
        idea="An AI-powered meal planning app",
        api_key=api_key,
        project_level=ProjectLevel.MEDIUM
    )
    state["product_brief"] = "Mock product brief with market analysis..."
    
    # Initialize agent
    agent = PRDGeneratorAgent(api_key)
    
    # Generate PRD
    print("📋 Generating PRD...")
    prd = agent.generate_prd(state)
    
    print(f"\n✅ PRD generated ({len(prd)} characters)")
    print(f"📊 Requirements extracted: {len(state['requirements'])}")
