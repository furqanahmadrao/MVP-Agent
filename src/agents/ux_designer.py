"""
UX Flow Designer Agent - BMAD Solutioning Phase
Generates user flows, design system, and wireframes.
"""

from typing import Dict, Any, Tuple
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..agent_state import AgentState, add_status_message

class UXFlowDesignerAgent:
    """
    UX Flow Designer - Solutioning Phase
    
    Responsibilities:
    - Create user flows (Mermaid)
    - Define Design System (Typography, Colors, Components)
    - Draft Wireframes (Text/ASCII)
    
    Output: user_flow.md, design_system.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
        
    def generate_user_flows(self, state: AgentState) -> str:
        """Generate User Flows document."""
        prd = state["prd"]
        architecture = state["architecture"]
        add_status_message(state, "UX Designer: Designing user flows...")
        
        prompt = f"""
{self.helpers.get_role_definition("ux_designer")}

**Objective:**
Create detailed **User Flows** and **Wireframes** based on the PRD and Architecture.

**Input - PRD:**
{prd[:1500]}...

**Input - Architecture:**
{architecture[:1500]}...

**Structure:**
# User Flows & UX Design

## 1. Primary User Journey
**Goal:** [Main user goal]
**Steps:**
1. [Step 1]
2. [Step 2]
...

## 2. User Flow Diagram (Mermaid)
{self.helpers.get_mermaid_guidelines()}
```mermaid
sequenceDiagram
    participant User
    participant App
    participant System
    User->>App: Action
    App->>System: API Call
    System-->>App: Response
    App-->>User: Feedback
```

## 3. Wireframes
### Screen: Dashboard
[Layout description]
- Header: ...
- Main Content: ...
- Sidebar: ...

## 4. Accessibility (WCAG)
- [Requirement 1]
- [Requirement 2]

---
**Agent Guidance:**
Ensure designs account for error states defined in the Architecture.
"""
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]

    def generate_design_system(self, state: AgentState) -> str:
        """Generate Design System document."""
        add_status_message(state, "UX Designer: creating design system...")
        
        prompt = f"""
{self.helpers.get_role_definition("ux_designer")}

**Objective:**
Create a **Design System** specification.

**Structure:**
# Design System

## 1. Design Principles
- [Principle 1]
- [Principle 2]

## 2. Typography
- **Headings:** [Font Family]
- **Body:** [Font Family]

## 3. Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #... | Main actions |
| Secondary | #... | Accents |
| Error | #... | Alerts |

## 4. Components
- **Buttons:** [Variants]
- **Cards:** [Style]
- **Inputs:** [States]

---
**Agent Guidance:**
Consistent styling ensures professional implementation.
"""
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]
