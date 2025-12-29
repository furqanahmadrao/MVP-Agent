"""
Sprint Planner Agent - BMAD Implementation Phase
Generates Roadmap, Testing Plan, and Deployment Guide.
"""

from typing import Dict, Any, Tuple
from ..ai_models import GeminiClient, ModelType
from ..helpers import BMAdHelpers, get_standard_prompt_suffix, get_mermaid_guidelines
from ..agent_state import AgentState, add_status_message

class SprintPlannerAgent:
    """
    Sprint Planner - Implementation Phase
    
    Responsibilities:
    - Create Roadmap/Gantt Chart
    - Define Testing Strategy
    - Create Deployment Guide
    
    Output: roadmap.md, testing_plan.md, deployment_guide.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
        
    def generate_roadmap(self, state: AgentState) -> str:
        """Generate Roadmap."""
        prd = state["prd"]
        add_status_message(state, "Sprint Planner: Planning roadmap...")
        
        prompt = f"""
{self.helpers.get_role_definition("sprint_planner")}

**Objective:**
Create a **Project Roadmap** broken down into Sprints.

**Input - PRD:**
{prd[:2000]}...

**Structure:**
# Implementation Roadmap

## 1. Timeline (Gantt)
{self.helpers.get_mermaid_guidelines()}
```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Setup :a1, 2024-01-01, 5d
    Dev   :a2, after a1, 10d
```

## 2. Sprint Breakdown
### Sprint 1: Foundation (Weeks 1-2)
- [ ] Setup Repo
- [ ] Database Schema
- [ ] Auth API

### Sprint 2: Core Features (Weeks 3-4)
- [ ] Feature A
- [ ] Feature B

## 3. Milestones
- MVP Launch: [Date/Conditions]
- V1.0 Release: [Date/Conditions]

---
**Agent Guidance:**
Focus on MVP critical path first.
"""
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]

    def generate_testing_plan(self, state: AgentState) -> str:
        """Generate Testing Plan."""
        add_status_message(state, "Sprint Planner: Creating test strategy...")
        
        prompt = f"""
{self.helpers.get_role_definition("sprint_planner")}

**Objective:**
Create a **Testing & QA Plan**.

**Structure:**
# Testing Plan

## 1. Test Strategy
- Unit Tests (Jest/Pytest)
- Integration Tests
- E2E Tests (Playwright/Cypress)

## 2. Test Cases (Sample)
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| TC-01 | Login | Enter valid creds | Redirect to dash |

## 3. CI/CD Integration
- Run tests on PR
- Block merge on failure

---
**Agent Guidance:**
Ensure critical user flows from UX design are covered.
"""
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]

    def generate_deployment_guide(self, state: AgentState) -> str:
        """Generate Deployment Guide."""
        arch = state["architecture"]
        add_status_message(state, "Sprint Planner: Writing deployment guide...")
        
        prompt = f"""
{self.helpers.get_role_definition("sprint_planner")}

**Objective:**
Create a **Deployment Guide** based on the Architecture.

**Input - Architecture:**
{arch[:2000]}...

**Structure:**
# Deployment Guide

## 1. Prerequisites
- Docker
- Cloud Account (AWS/GCP)

## 2. Environment Variables
- `DB_HOST`
- `API_KEY`

## 3. Docker Instructions
```bash
docker build -t app .
docker run -p 8000:8000 app
```

## 4. CI/CD Pipeline
- GitHub Actions workflow
- Automated deployment steps

---
**Agent Guidance:**
Keep instructions simple and actionable for a DevOps engineer.
"""
        result = self.llm.generate_with_grounding(prompt, model_name=self.model_name)
        return result["text"]
