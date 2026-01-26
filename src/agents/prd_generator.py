"""
PRD Generator Agent - BMAD Planning Phase
Generates PRD and Tech Spec using GitHub Spec Kit structure.
"""

import re
from typing import Dict, Any, Tuple, List
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..agent_state import AgentState, add_status_message

class PRDGeneratorAgent:
    """
    PRD Generator - Planning Phase
    
    Responsibilities:
    - Translate Product Brief into Functional/Non-Functional Requirements
    - Define User Stories and Acceptance Criteria (Spec Kit style)
    - Prioritize features (MoSCoW)
    - Generate Technical Specification
    
    Output: prd.md, tech_spec.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize PRD Generator agent"""
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
    
    def generate_prd(self, state: AgentState) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate PRD based on Product Brief.
        
        Args:
            state: Agent state
        
        Returns:
            Tuple[prd_markdown, requirements_list]
        """
        product_brief = state["product_brief"]
        add_status_message(state, "PRD Generator: Defining requirements and user stories...")
        
        prompt = f"""
{self.helpers.get_role_definition("prd_generator")}

**Objective:**
Create a comprehensive **Product Requirements Document (PRD)** based on the Product Brief.
Follow the **GitHub Spec Kit** methodology (Goals, Functional Requirements, User Stories, Acceptance Criteria).

**Input - Product Brief:**
{product_brief}

**Structure:**
# Product Requirements Document (PRD)

## 1. Goals & Objectives
[High-level goals from Spec Kit]

## 2. Functional Requirements
### FR-001: [Feature Name]
**Description:** [Detailed description]
**User Story:** As a [persona], I want [action] so that [benefit].
**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
**Priority:** [Must/Should/Could]

[Repeat for 5-7 core features]

## 3. Non-Functional Requirements (NFRs)
### NFR-001: [Category]
**Requirement:** [Specific metric or constraint]
**Priority:** Must-Have

[Include Performance, Security, Scalability, Accessibility]

## 4. User Stories (Epics)
- **Epic 1:** [Description]
  - Story 1.1: ...
  - Story 1.2: ...

## 5. Success Metrics
- [Metric 1]
- [Metric 2]

---
**Rationale:**
Explain why these features were prioritized.

**Agent Guidance:**
Next step is Architecture. Ensure all NFRs are feasible with standard web technologies.
"""
        
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        prd = result["text"]
        
        # Extract requirements into a structured list
        requirements = self._parse_requirements(prd)
        
        return prd, requirements

    def _parse_requirements(self, prd_text: str) -> List[Dict[str, Any]]:
        """
        Parse PRD markdown to extract structured requirements.
        """
        requirements = []
        lines = prd_text.split('\n')
        current_req = {}
        capturing_ac = False

        for line in lines:
            line = line.strip()

            # Check for new Requirement Header (e.g., ### FR-001: Title)
            fr_match = re.match(r'^###\s+(FR-\d+):\s+(.+)$', line)
            if fr_match:
                if current_req:
                    requirements.append(current_req)

                current_req = {
                    "id": fr_match.group(1),
                    "title": fr_match.group(2),
                    "description": "",
                    "user_story": "",
                    "acceptance_criteria": [],
                    "priority": ""
                }
                capturing_ac = False
                continue

            if not current_req:
                continue

            # Parse fields within a requirement
            if line.startswith("**Description:**"):
                current_req["description"] = line.replace("**Description:**", "").strip()
                capturing_ac = False
            elif line.startswith("**User Story:**"):
                current_req["user_story"] = line.replace("**User Story:**", "").strip()
                capturing_ac = False
            elif line.startswith("**Priority:**"):
                current_req["priority"] = line.replace("**Priority:**", "").strip()
                capturing_ac = False
            elif line.startswith("**Acceptance Criteria:**"):
                capturing_ac = True
            elif capturing_ac and line.startswith("- [ ]"):
                criteria = line.replace("- [ ]", "").strip()
                current_req["acceptance_criteria"].append(criteria)
            elif line.startswith("## ") and current_req:
                # New section, save and reset
                requirements.append(current_req)
                current_req = {}
                capturing_ac = False

        if current_req:
            requirements.append(current_req)

        return requirements

    def generate_tech_spec(self, state: AgentState) -> str:
        """
        Generate Technical Specification (Spec Kit /speckit.plan style).
        """
        prd = state["prd"]
        add_status_message(state, "PRD Generator: drafting technical plan...")
        
        prompt = f"""
{self.helpers.get_role_definition("prd_generator")}

**Objective:**
Create a **Technical Plan** (Spec Kit style) based on the PRD.
Focus on "HOW" the requirements will be met.

**Input - PRD:**
{prd}

**Structure:**
# Technical Plan

## 1. System Overview
[High-level technical approach]

## 2. Technology Choices
- **Frontend:** [Choice] - [Justification]
- **Backend:** [Choice] - [Justification]
- **Database:** [Choice] - [Justification]

## 3. API Strategy
[REST vs GraphQL, Auth strategy]

## 4. Data Model (High Level)
[Key entities and relationships]

## 5. Security & Compliance
[Auth implementation, Data protection]

---
**Agent Guidance:**
The Architect agent will use this to design the detailed system architecture.
"""
        
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]