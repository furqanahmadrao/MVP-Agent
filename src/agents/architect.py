"""
Architecture Designer Agent - BMAD Solutioning Phase
Generates system architecture, tech stack, database schema, and NFR coverage
"""

from typing import Dict, Any
from datetime import datetime
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix, get_mermaid_guidelines
from ..agent_state import AgentState, add_status_message, RequirementType


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
        requirements = state.get("requirements", [])
        
        # Get NFRs for coverage tracking
        nfrs = [r for r in requirements if r.get("type") == RequirementType.NON_FUNCTIONAL]
        
        add_status_message(state, f"Architect: Designing system for {len(requirements)} requirements...")
        
        prompt = f"""You are a System Architect designing the technical architecture for an MVP.

**Startup Idea:**
{idea}

**Requirements Context:**
- Total Requirements: {len(requirements)}
- Non-Functional Requirements: {len(nfrs)}
- Must address ≥90% of NFRs in architecture

**PRD Summary:**
{prd[:1500]}... [truncated]

**Tech Spec:**
{tech_spec[:1000] if tech_spec else 'Not provided'}

**Your Task:**
Generate a comprehensive Architecture Document.

# System Architecture: [Project Name]

**Version:** 1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Architect:** MVP Agent - Architecture Designer

---

## 1. System Overview

### High-Level Architecture Diagram (Mermaid)
```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web App]
        Mobile[Mobile App]
    end
    
    subgraph "API Gateway"
        Gateway[API Gateway]
    end
    
    subgraph "Application Layer"
        Auth[Auth Service]
        Core[Core Service]
        Jobs[Background Jobs]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Cache)]
        Storage[Object Storage]
    end
    
    Web --> Gateway
    Mobile --> Gateway
    Gateway --> Auth
    Gateway --> Core
    Core --> DB
    Core --> Cache
    Core --> Storage
    Jobs --> DB
```

If Mermaid fails, describe the architecture in text.

### Architecture Principles
- Scalability strategy
- Security-first approach
- Cost optimization
- Developer experience

## 2. Technology Stack

Create a detailed table:

| Category | Technology | Version | Justification | NFR Mapping |
|----------|----------|---------|--------------|-------------|
| Frontend | React | 18.x | Component reusability, ecosystem | NFR-XXX (Performance) |
| Backend | Node.js/Express | 20.x | ... | NFR-XXX |
| Database | PostgreSQL | 15.x | ... | NFR-XXX |
| Cache | Redis | 7.x | ... | NFR-XXX |
| Auth | Auth0 | Latest | ... | NFR-XXX (Security) |
| Hosting | AWS/Vercel | - | ... | NFR-XXX (Scalability) |

**Important:** Map each technology choice to specific NFR-XXX IDs.

### Alternative Considerations
For each major technology choice, mention alternatives considered and why rejected.

## 3. Database Schema

### Entity Relationship Diagram (Mermaid)
```mermaid
erDiagram
    USER ||--o{ SESSION : has
    USER ||--o{ PROFILE : has
    USER {
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
    }
    PROFILE {
        uuid id PK
        uuid user_id FK
        string name
        json preferences
    }
```

If Mermaid fails, use text-based schema.

### Data Models
For each entity:
- Fields with types
- Indexes
- Constraints
- Relationships

## 4. API Architecture

### API Design Principles
- RESTful vs GraphQL (with justification)
- Versioning strategy
- Rate limiting
- Pagination

### Key Endpoints
Create a table:

| Endpoint | Method | Auth Required | Request | Response | FR Mapping |
|----------|--------|--------------|---------|----------|------------|
| /api/v1/users | POST | No | UserCreateDTO | UserDTO | FR-001 |
| /api/v1/profile | GET | Yes | - | ProfileDTO | FR-002 |

Map endpoints to FR-XXX IDs.

## 5. NFR Coverage Report

**CRITICAL:** For each NFR, show how it's addressed in architecture.

### NFR-001: Performance
**Requirement:** Response time <200ms (p95)  
**Architecture Solutions:**
- Redis caching for frequent queries
- CDN for static assets
- Database indexing strategy
- Connection pooling

### NFR-002: Security
**Requirement:** Industry-standard authentication  
**Architecture Solutions:**
- OAuth 2.0 with Auth0
- HTTPS everywhere
- API key rotation
- SQL injection prevention (parameterized queries)

[Repeat for ALL NFRs]

### Coverage Summary
**Total NFRs:** {len(nfrs)}  
**Covered in Architecture:** [count]  
**Coverage Percentage:** [calculate]  
**Uncovered NFRs:** [list any, if <90%]

## 6. Security Architecture

### Authentication Flow Diagram (Mermaid sequenceDiagram)

### Authorization Model
- RBAC (Role-Based Access Control)
- Permission matrix

### Data Security
- Encryption at rest
- Encryption in transit
- PII handling
- GDPR compliance

### OWASP Top 10 Mitigations
For each OWASP risk, show mitigation strategy.

## 7. Scalability Strategy

### Horizontal Scaling
- Load balancer configuration
- Stateless application design
- Database read replicas

### Vertical Scaling
- Resource allocation
- When to scale up

### Bottleneck Analysis
Identify potential bottlenecks and solutions.

## 8. Monitoring & Observability

- Application Performance Monitoring (APM)
- Logging strategy
- Alerting rules
- Health checks

## 9. Deployment Architecture

### CI/CD Pipeline
- Build → Test → Deploy flow
- Blue-green deployment
- Rollback strategy

### Infrastructure as Code
- Tools (Terraform, CloudFormation)
- Environment parity (dev/staging/prod)

{get_standard_prompt_suffix()}
{get_mermaid_guidelines()}

**CRITICAL REQUIREMENTS:**
1. Address ≥90% of NFRs (calculate and show percentage)
2. Map every tech choice to NFR-XXX IDs
3. Map every API endpoint to FR-XXX IDs
4. Include Mermaid diagrams with text fallbacks
5. Show explicit NFR coverage report

Generate the complete Architecture Document now.
"""
        
        architecture = self.llm.generate(
            prompt=prompt,
            model_type=ModelType.PRO,
            temperature=0.6
        )
        
        # Calculate NFR coverage
        coverage, uncovered = self.helpers.calculate_nfr_coverage(nfrs, architecture)
        
        add_status_message(state, f"Architect: Architecture complete! NFR coverage: {coverage:.1f}%")
        
        # Add agent guidance
        agent_guidance = self.helpers.generate_agent_guidance(
            guidance=f"""**For UX Designer:**
1. User flows must align with API endpoints defined in this architecture
2. Design for the authentication flow specified in Security Architecture
3. Consider performance constraints (page load times, API response times)
4. Address accessibility NFRs in wireframe designs
5. Follow mobile-first approach if specified in architecture

**For Developer:**
1. Tech stack is locked - use technologies specified in this document
2. Database schema is the source of truth
3. API endpoints must match specifications exactly
4. Follow security patterns defined in Security Architecture
5. Implement monitoring as specified

**NFR Coverage:** {coverage:.1f}% ({len(nfrs) - len(uncovered)}/{len(nfrs)} NFRs addressed)  
**Uncovered NFRs:** {', '.join(uncovered) if uncovered else 'None'}""",
            next_phase="Solutioning (UX Design) & Implementation (Development)"
        )
        
        architecture += agent_guidance
        
        # Store tech stack in state
        state["tech_stack"] = {
            "frontend": ["React"],
            "backend": ["Node.js"],
            "database": ["PostgreSQL"],
            "cache": ["Redis"]
        }
        
        return architecture


if __name__ == "__main__":
    import os
    from ..agent_state import create_initial_state, ProjectLevel, Requirement, RequirementType
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        exit(1)
    
    # Create test state
    state = create_initial_state(
        idea="An AI-powered meal planning app",
        api_key=api_key,
        project_level=ProjectLevel.MEDIUM
    )
    state["prd"] = "Mock PRD..."
    state["requirements"] = [
        {"id": "NFR-001", "type": RequirementType.NON_FUNCTIONAL, "title": "Performance"},
        {"id": "NFR-002", "type": RequirementType.NON_FUNCTIONAL, "title": "Security"},
    ]
    
    # Initialize agent
    agent = ArchitectureDesignerAgent(api_key)
    
    # Generate architecture
    print("🏗️ Generating Architecture...")
    architecture = agent.generate_architecture(state)
    
    print(f"\n✅ Architecture generated ({len(architecture)} characters)")
