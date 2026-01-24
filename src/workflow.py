"""
LangGraph Workflow - MVP Agent v2.0
BMAD-inspired multi-agent workflow for PRD generation
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime

from .agent_state import (
    AgentState, WorkflowPhase, ProjectLevel,
    create_initial_state, detect_project_level,
    update_phase, add_status_message, add_error,
    validate_gate_check
)
from .helpers import BMAdHelpers, get_standard_prompt_suffix
from .toon_utils import should_use_toon_for_agent

# Import Agents
from .agents.market_analyst import MarketAnalystAgent
from .agents.prd_generator import PRDGeneratorAgent
from .agents.architect import ArchitectureDesignerAgent
from .agents.ux_designer import UXFlowDesignerAgent
from .agents.sprint_planner import SprintPlannerAgent
from .agents.financial_modeler import FinancialModelerAgent

class MVPAgentWorkflow:
    """
    LangGraph workflow orchestrator for MVP Agent.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow."""
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
        """Node 0: Detect project complexity level."""
        try:
            add_status_message(state, "🔍 Detecting project complexity level...")
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
        """Phase 1: Analysis"""
        try:
            update_phase(state, WorkflowPhase.ANALYSIS)
            add_status_message(state, "🔬 Starting Analysis Phase...")
            
            analyst = MarketAnalystAgent(state["api_key"], state["model_name"])
            
            add_status_message(state, "  → Generating product brief...")
            state["product_brief"], state["research_data"] = analyst.generate_product_brief(state)
            
            # Financial Modeling
            add_status_message(state, "  → Generating financial model...")
            financial_modeler = FinancialModelerAgent(state["api_key"], state["model_name"])
            state["business_model"] = financial_modeler.generate_financial_model(state, state["product_brief"])
            
            state["progress_percentage"] = 25
            add_status_message(state, "✅ Analysis Phase complete")
            return state
        except Exception as e:
            add_error(state, "analysis", str(e))
            state["fallback_used"] = True
            return state
    
    def planning_phase_node(self, state: AgentState) -> AgentState:
        """Phase 2: Planning"""
        try:
            update_phase(state, WorkflowPhase.PLANNING)
            add_status_message(state, "📋 Starting Planning Phase...")
            
            prd_gen = PRDGeneratorAgent(state["api_key"], state["model_name"])
            
            add_status_message(state, "  → Generating PRD...")
            state["prd"], state["requirements"] = prd_gen.generate_prd(state)
            
            add_status_message(state, "  → Generating Tech Spec...")
            state["tech_spec"] = prd_gen.generate_tech_spec(state)
            
            add_status_message(state, "  → Generating Feature Prioritization...")
            state["feature_prioritization"] = prd_gen.generate_feature_prioritization(state)
            
            add_status_message(state, "  → Generating Competitive Analysis...")
            state["competitive_analysis"] = prd_gen.generate_competitive_analysis(state)
            
            state["progress_percentage"] = 50
            add_status_message(state, "✅ Planning Phase complete")
            return state
        except Exception as e:
            add_error(state, "planning", str(e))
            return state
    
    def solutioning_phase_node(self, state: AgentState) -> AgentState:
        """Phase 3: Solutioning"""
        try:
            update_phase(state, WorkflowPhase.SOLUTIONING)
            add_status_message(state, "🏗️ Starting Solutioning Phase...")
            
            architect = ArchitectureDesignerAgent(state["api_key"], state["model_name"])
            ux_designer = UXFlowDesignerAgent(state["api_key"], state["model_name"])
            
            add_status_message(state, "  → Generating Architecture...")
            state["architecture"] = architect.generate_architecture(state)
            
            add_status_message(state, "  → Generating User Flows...")
            state["user_flow"] = ux_designer.generate_user_flows(state)
            
            add_status_message(state, "  → Generating Design System...")
            state["design_system"] = ux_designer.generate_design_system(state)
            
            state["progress_percentage"] = 75
            add_status_message(state, "✅ Solutioning Phase complete")
            return state
        except Exception as e:
            add_error(state, "solutioning", str(e))
            return state
    
    def implementation_phase_node(self, state: AgentState) -> AgentState:
        """Phase 4: Implementation"""
        try:
            update_phase(state, WorkflowPhase.IMPLEMENTATION)
            add_status_message(state, "🚀 Starting Implementation Phase...")
            
            sprint_planner = SprintPlannerAgent(state["api_key"], state["model_name"])
            
            add_status_message(state, "  → Generating Roadmap...")
            state["roadmap"] = sprint_planner.generate_roadmap(state)
            
            add_status_message(state, "  → Generating Testing Plan...")
            state["testing_plan"] = sprint_planner.generate_testing_plan(state)
            
            add_status_message(state, "  → Generating Deployment Guide...")
            state["deployment_guide"] = sprint_planner.generate_deployment_guide(state)
            
            state["progress_percentage"] = 95
            add_status_message(state, "✅ Implementation Phase complete")
            return state
        except Exception as e:
            add_error(state, "implementation", str(e))
            return state
    
    def finalize_node(self, state: AgentState) -> AgentState:
        """Finalize: Generate overview."""
        try:
            add_status_message(state, "📦 Finalizing outputs...")
            state["overview"] = self._generate_overview(state)
            
            update_phase(state, WorkflowPhase.COMPLETE)
            state["progress_percentage"] = 100
            add_status_message(state, "🎉 Blueprint generation complete!")
            return state
        except Exception as e:
            add_error(state, "finalize", str(e))
            return state
    
    def _generate_overview(self, state: AgentState) -> str:
        """Generate overview summary."""
        return f"""# Project Overview: {state['idea']}
        
## Generated Documents
1. **Product Brief:** Market analysis and vision
2. **PRD:** Product requirements and stories
3. **Architecture:** System design and stack
4. **User Flow:** User journeys and wireframes
5. **Design System:** UI standards
6. **Roadmap:** Implementation plan
7. **Testing Plan:** QA strategy
8. **Deployment Guide:** Operations manual

## Project Stats
- **Phase:** {state['phase']}
- **Project Level:** {state['project_level']}
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated by MVP Agent v2.0
"""
    
    def run(self, idea: str, api_key: str, **kwargs) -> Dict[str, Any]:
        """Run workflow."""
        initial_state = create_initial_state(
            idea=idea,
            api_key=api_key,
            model_name=kwargs.get("model_name", self.model_name),
            project_level=kwargs.get("project_level"),
            enable_toon=kwargs.get("enable_toon", False)
        )
        return self.workflow.invoke(initial_state)

def create_workflow(api_key: str, model_name: str = "gemini-2.5-flash") -> MVPAgentWorkflow:
    return MVPAgentWorkflow(api_key=api_key, model_name=model_name)
