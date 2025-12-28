"""
LangGraph Workflow - MVP Agent v2.0
BMAD-inspired multi-agent workflow for PRD generation
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime

from agent_state import (
    AgentState, WorkflowPhase, ProjectLevel,
    create_initial_state, detect_project_level,
    update_phase, add_status_message, add_error,
    validate_gate_check
)
from helpers import BMAdHelpers, get_standard_prompt_suffix
from toon_utils import should_use_toon_for_agent


class MVPAgentWorkflow:
    """
    LangGraph workflow orchestrator for MVP Agent.
    
    Implements BMAD-inspired 4-phase workflow:
    1. Analysis (Product Brief, Business Model)
    2. Planning (PRD, Tech Spec)
    3. Solutioning (Architecture, User Flow, Design System)
    4. Implementation (Roadmap, Testing Plan, Deployment Guide)
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize workflow with API key and model.
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow.
        
        Flow:
        START → detect_level → analysis → planning → solutioning → implementation → finalize → END
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("detect_level", self.detect_project_level_node)
        workflow.add_node("analysis", self.analysis_phase_node)
        workflow.add_node("planning", self.planning_phase_node)
        workflow.add_node("solutioning", self.solutioning_phase_node)
        workflow.add_node("implementation", self.implementation_phase_node)
        workflow.add_node("finalize", self.finalize_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("detect_level")
        workflow.add_edge("detect_level", "analysis")
        workflow.add_edge("analysis", "planning")
        workflow.add_edge("planning", "solutioning")
        workflow.add_edge("solutioning", "implementation")
        workflow.add_edge("implementation", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    # ===== Workflow Nodes =====
    
    def detect_project_level_node(self, state: AgentState) -> AgentState:
        """
        Node 0: Detect project complexity level.
        
        Auto-detects project level (0-4) based on idea.
        """
        try:
            add_status_message(state, "🔍 Detecting project complexity level...")
            
            # Auto-detect if not set
            if not state.get("project_level"):
                level = detect_project_level(state["idea"])
                state["project_level"] = level
                add_status_message(state, f"📊 Project level: {level.name} (Level {level.value})")
            
            state["progress_percentage"] = 5
            return state
            
        except Exception as e:
            add_error(state, "detect_level", str(e))
            state["phase"] = WorkflowPhase.ERROR
            return state
    
    def analysis_phase_node(self, state: AgentState) -> AgentState:
        """
        Phase 1: Analysis
        
        Generates:
        - Product Brief (market research, personas, competitors)
        - Business Model (revenue, costs, pricing)
        """
        try:
            update_phase(state, WorkflowPhase.ANALYSIS)
            add_status_message(state, "🔬 Starting Analysis Phase...")
            
            # Generate Product Brief
            add_status_message(state, "  → Generating product brief...")
            state["product_brief"] = self._generate_product_brief(state)
            state["progress_percentage"] = 20
            
            # Generate Business Model
            add_status_message(state, "  → Generating business model...")
            state["business_model"] = self._generate_business_model(state)
            state["progress_percentage"] = 30
            
            # Gate check
            if not validate_gate_check(state, "analysis", ["product_brief_not_empty"]):
                add_error(state, "analysis", "Gate check failed")
                state["fallback_used"] = True
            
            add_status_message(state, "✅ Analysis Phase complete")
            return state
            
        except Exception as e:
            add_error(state, "analysis", str(e))
            state["fallback_used"] = True
            return state
    
    def planning_phase_node(self, state: AgentState) -> AgentState:
        """
        Phase 2: Planning
        
        Generates:
        - PRD (requirements, user stories, acceptance criteria)
        - Tech Spec (detailed technical requirements)
        """
        try:
            update_phase(state, WorkflowPhase.PLANNING)
            add_status_message(state, "📋 Starting Planning Phase...")
            
            # Generate PRD
            add_status_message(state, "  → Generating PRD...")
            state["prd"] = self._generate_prd(state)
            state["progress_percentage"] = 50
            
            # Generate Tech Spec
            add_status_message(state, "  → Generating tech spec...")
            state["tech_spec"] = self._generate_tech_spec(state)
            state["progress_percentage"] = 60
            
            # Gate check
            if not validate_gate_check(state, "planning", ["requirements_count_gt_5"]):
                add_error(state, "planning", "Gate check failed - insufficient requirements")
            
            add_status_message(state, "✅ Planning Phase complete")
            return state
            
        except Exception as e:
            add_error(state, "planning", str(e))
            return state
    
    def solutioning_phase_node(self, state: AgentState) -> AgentState:
        """
        Phase 3: Solutioning
        
        Generates:
        - Architecture (system design, tech stack, database schema)
        - Design System (UI/UX, design tokens)
        - User Flow (user journeys, wireframes)
        """
        try:
            update_phase(state, WorkflowPhase.SOLUTIONING)
            add_status_message(state, "🏗️ Starting Solutioning Phase...")
            
            # Generate Architecture
            add_status_message(state, "  → Generating architecture...")
            state["architecture"] = self._generate_architecture(state)
            state["progress_percentage"] = 70
            
            # Generate Design System
            add_status_message(state, "  → Generating design system...")
            state["design_system"] = self._generate_design_system(state)
            state["progress_percentage"] = 75
            
            # Generate User Flow
            add_status_message(state, "  → Generating user flows...")
            state["user_flow"] = self._generate_user_flow(state)
            state["progress_percentage"] = 80
            
            # Gate check (NFR coverage)
            if not validate_gate_check(state, "solutioning", ["nfr_coverage_gt_90"]):
                add_error(state, "solutioning", "Gate check warning - low NFR coverage")
            
            add_status_message(state, "✅ Solutioning Phase complete")
            return state
            
        except Exception as e:
            add_error(state, "solutioning", str(e))
            return state
    
    def implementation_phase_node(self, state: AgentState) -> AgentState:
        """
        Phase 4: Implementation
        
        Generates:
        - Roadmap (sprints, timeline, milestones)
        - Testing Plan (test strategy, test cases)
        - Deployment Guide (infrastructure, CI/CD)
        """
        try:
            update_phase(state, WorkflowPhase.IMPLEMENTATION)
            add_status_message(state, "🚀 Starting Implementation Phase...")
            
            # Generate Roadmap
            add_status_message(state, "  → Generating roadmap...")
            state["roadmap"] = self._generate_roadmap(state)
            state["progress_percentage"] = 85
            
            # Generate Testing Plan
            add_status_message(state, "  → Generating testing plan...")
            state["testing_plan"] = self._generate_testing_plan(state)
            state["progress_percentage"] = 90
            
            # Generate Deployment Guide
            add_status_message(state, "  → Generating deployment guide...")
            state["deployment_guide"] = self._generate_deployment_guide(state)
            state["progress_percentage"] = 95
            
            add_status_message(state, "✅ Implementation Phase complete")
            return state
            
        except Exception as e:
            add_error(state, "implementation", str(e))
            return state
    
    def finalize_node(self, state: AgentState) -> AgentState:
        """
        Finalize: Generate overview and package outputs.
        """
        try:
            add_status_message(state, "📦 Finalizing outputs...")
            
            # Generate Overview (summary of all documents)
            add_status_message(state, "  → Generating overview...")
            state["overview"] = self._generate_overview(state)
            
            # Update final status
            update_phase(state, WorkflowPhase.COMPLETE)
            state["progress_percentage"] = 100
            add_status_message(state, "🎉 Blueprint generation complete!")
            
            return state
            
        except Exception as e:
            add_error(state, "finalize", str(e))
            return state
    
    # ===== Document Generators (Placeholder) =====
    # These will be implemented with actual agents in Phase 4
    
    def _generate_product_brief(self, state: AgentState) -> str:
        """Generate product brief (Market Analyst agent)"""
        # TODO: Implement in Phase 4
        return "# Product Brief\n\n[To be implemented with Market Analyst agent]"
    
    def _generate_business_model(self, state: AgentState) -> str:
        """Generate business model (Business Model agent)"""
        # TODO: Implement in Phase 4
        return "# Business Model\n\n[To be implemented with Business Model agent]"
    
    def _generate_prd(self, state: AgentState) -> str:
        """Generate PRD (PRD Generator agent)"""
        # TODO: Implement in Phase 4
        return "# Product Requirements Document\n\n[To be implemented with PRD Generator agent]"
    
    def _generate_tech_spec(self, state: AgentState) -> str:
        """Generate tech spec (PRD Generator agent)"""
        # TODO: Implement in Phase 4
        return "# Technical Specification\n\n[To be implemented with PRD Generator agent]"
    
    def _generate_architecture(self, state: AgentState) -> str:
        """Generate architecture (Architecture Designer agent)"""
        # TODO: Implement in Phase 4
        return "# Architecture\n\n[To be implemented with Architecture Designer agent]"
    
    def _generate_design_system(self, state: AgentState) -> str:
        """Generate design system (UX Designer agent)"""
        # TODO: Implement in Phase 4
        return "# Design System\n\n[To be implemented with UX Designer agent]"
    
    def _generate_user_flow(self, state: AgentState) -> str:
        """Generate user flow (UX Designer agent)"""
        # TODO: Implement in Phase 4
        return "# User Flow\n\n[To be implemented with UX Designer agent]"
    
    def _generate_roadmap(self, state: AgentState) -> str:
        """Generate roadmap (Sprint Planner agent)"""
        # TODO: Implement in Phase 4
        return "# Roadmap\n\n[To be implemented with Sprint Planner agent]"
    
    def _generate_testing_plan(self, state: AgentState) -> str:
        """Generate testing plan (Sprint Planner agent)"""
        # TODO: Implement in Phase 4
        return "# Testing Plan\n\n[To be implemented with Sprint Planner agent]"
    
    def _generate_deployment_guide(self, state: AgentState) -> str:
        """Generate deployment guide (Sprint Planner agent)"""
        # TODO: Implement in Phase 4
        return "# Deployment Guide\n\n[To be implemented with Sprint Planner agent]"
    
    def _generate_overview(self, state: AgentState) -> str:
        """Generate overview (summary of all documents)"""
        # TODO: Implement in Phase 4
        return "# Project Overview\n\n[To be implemented with Overview Generator]"
    
    # ===== Public Methods =====
    
    def run(self, idea: str, api_key: str, **kwargs) -> Dict[str, Any]:
        """
        Run workflow to generate MVP blueprint.
        
        Args:
            idea: User's startup idea
            api_key: Gemini API key
            **kwargs: Additional options (model_name, project_level, enable_toon)
        
        Returns:
            Final agent state with all generated documents
        """
        # Create initial state
        initial_state = create_initial_state(
            idea=idea,
            api_key=api_key,
            model_name=kwargs.get("model_name", self.model_name),
            project_level=kwargs.get("project_level"),
            enable_toon=kwargs.get("enable_toon", False)
        )
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state


# ===== Workflow Factory =====

def create_workflow(api_key: str, model_name: str = "gemini-2.5-flash") -> MVPAgentWorkflow:
    """
    Factory function to create workflow instance.
    
    Args:
        api_key: Gemini API key
        model_name: Gemini model to use
    
    Returns:
        MVPAgentWorkflow instance
    """
    return MVPAgentWorkflow(api_key=api_key, model_name=model_name)


# ===== Example Usage =====

if __name__ == "__main__":
    # Example workflow execution
    workflow = create_workflow(api_key="test_key")
    
    result = workflow.run(
        idea="A SaaS platform for small businesses to manage customer relationships",
        api_key="test_key",
        enable_toon=False
    )
    
    print(f"Workflow completed: {result['phase']}")
    print(f"Progress: {result['progress_percentage']}%")
    print(f"Generated documents: {len([k for k, v in result.items() if k.endswith('_brief') or k.endswith('_model') or k == 'prd'])}")
