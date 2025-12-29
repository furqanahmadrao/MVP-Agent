"""
Agent State Module
Defines the shared state for the LangGraph workflow and project levels.
"""

from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum, IntEnum

class ProjectLevel(IntEnum):
    PROTOTYPE = 0  # Minimal: Brief + Tech Spec
    SMALL = 1      # Light: Brief + PRD + Arch
    MEDIUM = 2     # Standard: All 11 docs
    LARGE = 3      # Comprehensive: + Sprints
    ENTERPRISE = 4 # Full BMAD: + Governance

class WorkflowPhase(str, Enum):
    IDLE = "idle"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    SOLUTIONING = "solutioning"
    IMPLEMENTATION = "implementation"
    COMPLETE = "complete"
    ERROR = "error"

class AgentState(TypedDict):
    """
    Shared state object passed between LangGraph nodes.
    Follows BMAD pattern for state management.
    """
    # Inputs
    idea: str
    api_key: str
    model_name: str
    
    # Configuration
    project_level: int
    enable_toon: bool
    
    # Workflow Status
    phase: WorkflowPhase
    progress_percentage: int
    current_agent: str
    status_history: List[Dict[str, Any]]
    errors: List[str]
    fallback_used: bool
    
    # Generated Artifacts (The "Files")
    # Phase 1: Analysis
    product_brief: str  # Market Analyst output
    business_model: str # Business Model Designer output
    
    # Phase 2: Planning
    prd: str            # PRD Generator output (GitHub Spec Kit)
    tech_spec: str      # Technical Plan
    
    # Phase 3: Solutioning
    architecture: str   # Architecture Designer output
    design_system: str  # UX output
    user_flow: str      # UX output
    
    # Phase 4: Implementation
    roadmap: str        # Sprint Planner output
    testing_plan: str   # QA output
    deployment_guide: str
    
    # Final Output
    overview: str
    
    # Raw Data (Intermediate agent outputs, possibly in TOON)
    research_data: Dict[str, Any]
    requirements: List[Dict[str, Any]]
    
    # Metrics
    token_usage: int
    start_time: float
    end_time: float

def create_initial_state(idea: str, api_key: str, model_name: str = "gemini-2.5-flash", project_level: int = None, enable_toon: bool = True) -> AgentState:
    """Factory to create initial clean state."""
    import time
    return {
        "idea": idea,
        "api_key": api_key,
        "model_name": model_name,
        "project_level": project_level if project_level is not None else ProjectLevel.MEDIUM,
        "enable_toon": enable_toon,
        
        "phase": WorkflowPhase.IDLE,
        "progress_percentage": 0,
        "current_agent": "system",
        "status_history": [],
        "errors": [],
        "fallback_used": False,
        
        "product_brief": "",
        "business_model": "",
        "prd": "",
        "tech_spec": "",
        "architecture": "",
        "design_system": "",
        "user_flow": "",
        "roadmap": "",
        "testing_plan": "",
        "deployment_guide": "",
        "overview": "",
        
        "research_data": {},
        "requirements": [],
        
        "token_usage": 0,
        "start_time": time.time(),
        "end_time": 0.0
    }

def update_phase(state: AgentState, phase: WorkflowPhase) -> AgentState:
    """Helper to update phase and log it."""
    state["phase"] = phase
    return state

def add_status_message(state: AgentState, message: str, type: str = "INFO") -> AgentState:
    """Helper to add a status message."""
    import time
    state["status_history"].append({
        "timestamp": time.time(),
        "message": message,
        "type": type,
        "phase": state["phase"]
    })
    return state

def add_error(state: AgentState, source: str, error_msg: str) -> AgentState:
    """Helper to add an error."""
    state["errors"].append(f"[{source}] {error_msg}")
    add_status_message(state, f"Error in {source}: {error_msg}", "ERROR")
    return state

# Simple heuristics for auto-detection
def detect_project_level(idea: str) -> ProjectLevel:
    """Estimate project complexity based on idea description length and keywords."""
    text = idea.lower()
    
    # Keywords indicating complexity
    enterprise_keys = ["enterprise", "platform", "marketplace", "ecosystem", "compliance", "bank", "healthcare"]
    medium_keys = ["saas", "social", "app", "dashboard", "analytics"]
    
    score = 0
    if len(idea.split()) > 100: score += 1
    if any(k in text for k in enterprise_keys): score += 2
    if any(k in text for k in medium_keys): score += 1
    
    if score >= 3: return ProjectLevel.LARGE
    if score == 2: return ProjectLevel.MEDIUM
    if score == 1: return ProjectLevel.SMALL
    return ProjectLevel.PROTOTYPE

def validate_gate_check(state: AgentState, phase: str, checks: List[str]) -> bool:
    """
    Perform gate checks between phases.
    Returns True if passed, False if failed.
    """
    # Simple implementation - can be expanded with real validation logic
    passed = True
    for check in checks:
        if check == "product_brief_not_empty" and not state["product_brief"]:
            passed = False
        if check == "prd_not_empty" and not state["prd"]:
            passed = False
    
    if passed:
        add_status_message(state, f"✅ Gate check passed: {phase}")
    else:
        add_status_message(state, f"❌ Gate check failed: {phase}", "WARNING")
        
    return passed