"""
Agent State Management for MVP Agent v2.0
BMAD-inspired state structure for LangGraph workflow
"""

from typing import TypedDict, Annotated, Optional, Dict, List, Any
from enum import Enum
from datetime import datetime
import operator


class ProjectLevel(Enum):
    """BMAD-inspired project complexity levels"""
    PROTOTYPE = 0  # 1 story, minimal docs
    SMALL = 1      # 1-10 stories, light docs
    MEDIUM = 2     # 5-15 stories, standard docs (default)
    LARGE = 3      # 12-40 stories, comprehensive docs
    ENTERPRISE = 4 # 40+ stories, enterprise docs


class WorkflowPhase(Enum):
    """BMAD workflow phases"""
    IDLE = "idle"
    ANALYSIS = "analysis"           # Product Brief
    PLANNING = "planning"           # PRD, Tech Spec
    SOLUTIONING = "solutioning"     # Architecture
    IMPLEMENTATION = "implementation" # Roadmap, Sprints
    COMPLETE = "complete"
    ERROR = "error"


class RequirementType(Enum):
    """Requirement types for traceability"""
    FUNCTIONAL = "FR"      # Functional Requirement
    NON_FUNCTIONAL = "NFR" # Non-Functional Requirement
    USER_STORY = "US"      # User Story
    EPIC = "EP"            # Epic


class Requirement(TypedDict):
    """Structured requirement for traceability"""
    id: str                    # e.g., "FR-001", "NFR-001"
    type: RequirementType
    title: str
    description: str
    priority: str              # Must/Should/Could/Won't (MoSCoW)
    story_points: Optional[int]
    acceptance_criteria: List[str]
    dependencies: List[str]    # List of requirement IDs
    status: str                # draft/approved/implemented


class AgentState(TypedDict):
    """
    Shared state across all LangGraph agents.
    
    This state is passed between agents and updated incrementally.
    Uses Annotated with operator.add for lists to enable appending.
    """
    
    # ===== Input =====
    idea: str                              # User's startup idea
    api_key: str                           # User's Gemini API key
    model_name: str                        # gemini-2.5-pro/flash/flash-8b
    project_level: ProjectLevel            # Auto-detected complexity level
    enable_toon: bool                      # Use TOON format for agent outputs
    
    # ===== Workflow Control =====
    phase: WorkflowPhase                   # Current phase
    current_agent: str                     # Currently executing agent
    started_at: datetime
    updated_at: datetime
    
    # ===== Generated Documents (11 files) =====
    product_brief: str                     # Analysis phase output
    prd: str                               # Planning phase output (PRD)
    tech_spec: str                         # Planning phase output (tech details)
    architecture: str                      # Solutioning phase output
    design_system: str                     # Solutioning phase output (UI/UX)
    user_flow: str                         # Solutioning phase output
    roadmap: str                           # Implementation phase output
    business_model: str                    # Analysis phase output
    testing_plan: str                      # Solutioning phase output
    deployment_guide: str                  # Implementation phase output
    overview: str                          # Summary (generated last)
    
    # ===== Structured Data (BMAD pattern) =====
    requirements: Annotated[List[Requirement], operator.add]  # All requirements
    epics: Annotated[List[Dict[str, Any]], operator.add]      # User story epics
    personas: Annotated[List[Dict[str, Any]], operator.add]   # User personas
    tech_stack: Dict[str, List[str]]                          # Technology choices
    
    # ===== Research Data (Gemini Grounding) =====
    research_queries: Annotated[List[str], operator.add]      # Queries executed
    research_results: Annotated[List[Dict[str, Any]], operator.add]  # Search results
    citations: Annotated[List[Dict[str, Any]], operator.add]  # Grounding citations
    competitor_data: Annotated[List[Dict[str, Any]], operator.add]   # Competitors
    
    # ===== Validation & Gate Checks =====
    gate_checks: Dict[str, bool]           # Phase gate check results
    validation_errors: Annotated[List[str], operator.add]     # Validation errors
    warnings: Annotated[List[str], operator.add]              # Non-blocking warnings
    
    # ===== Error Handling =====
    errors: Annotated[List[Dict[str, Any]], operator.add]     # Error log
    retry_count: int                       # Retry attempts
    fallback_used: bool                    # Whether fallback template was used
    
    # ===== Metrics & Logging =====
    token_usage: Dict[str, int]            # Total tokens used per agent
    execution_time: Dict[str, float]       # Execution time per agent
    api_calls: int                         # Total API calls made
    
    # ===== Status Messages (for UI) =====
    status_messages: Annotated[List[str], operator.add]       # Real-time status
    progress_percentage: int               # 0-100


def create_initial_state(
    idea: str,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
    project_level: Optional[ProjectLevel] = None,
    enable_toon: bool = False
) -> AgentState:
    """
    Create initial agent state.
    
    Args:
        idea: User's startup idea
        api_key: Gemini API key
        model_name: Gemini model to use
        project_level: Project complexity level (auto-detected if None)
        enable_toon: Enable TOON format for agent outputs
    
    Returns:
        AgentState: Initial state for LangGraph workflow
    """
    now = datetime.now()
    
    return AgentState(
        # Input
        idea=idea,
        api_key=api_key,
        model_name=model_name,
        project_level=project_level or ProjectLevel.MEDIUM,
        enable_toon=enable_toon,
        
        # Workflow control
        phase=WorkflowPhase.IDLE,
        current_agent="",
        started_at=now,
        updated_at=now,
        
        # Generated documents (empty)
        product_brief="",
        prd="",
        tech_spec="",
        architecture="",
        design_system="",
        user_flow="",
        roadmap="",
        business_model="",
        testing_plan="",
        deployment_guide="",
        overview="",
        
        # Structured data (empty lists/dicts)
        requirements=[],
        epics=[],
        personas=[],
        tech_stack={},
        
        # Research data (empty)
        research_queries=[],
        research_results=[],
        citations=[],
        competitor_data=[],
        
        # Validation (empty)
        gate_checks={},
        validation_errors=[],
        warnings=[],
        
        # Error handling
        errors=[],
        retry_count=0,
        fallback_used=False,
        
        # Metrics
        token_usage={},
        execution_time={},
        api_calls=0,
        
        # Status
        status_messages=[],
        progress_percentage=0
    )


def detect_project_level(idea: str) -> ProjectLevel:
    """
    Auto-detect project complexity level from idea.
    
    Rules:
    - Keywords like "marketplace", "platform", "SaaS" → MEDIUM+
    - "Simple", "basic", "prototype" → SMALL
    - "Enterprise", "scalable", "multi-tenant" → LARGE+
    - Character count: <100 → SMALL, 100-300 → MEDIUM, >300 → LARGE
    
    Args:
        idea: User's startup idea
    
    Returns:
        ProjectLevel: Detected complexity level
    """
    idea_lower = idea.lower()
    
    # Check keywords
    enterprise_keywords = ["enterprise", "scalable", "multi-tenant", "microservices", 
                          "distributed", "high-availability", "mission-critical"]
    large_keywords = ["marketplace", "platform", "ecosystem", "integrations", 
                     "multi-language", "real-time", "analytics"]
    medium_keywords = ["saas", "app", "web", "mobile", "api", "dashboard"]
    small_keywords = ["simple", "basic", "prototype", "mvp", "minimal", "quick"]
    
    if any(kw in idea_lower for kw in enterprise_keywords):
        return ProjectLevel.ENTERPRISE
    elif any(kw in idea_lower for kw in large_keywords):
        return ProjectLevel.LARGE
    elif any(kw in idea_lower for kw in medium_keywords):
        return ProjectLevel.MEDIUM
    elif any(kw in idea_lower for kw in small_keywords):
        return ProjectLevel.SMALL
    
    # Check length
    if len(idea) < 100:
        return ProjectLevel.SMALL
    elif len(idea) > 300:
        return ProjectLevel.LARGE
    
    # Default to MEDIUM
    return ProjectLevel.MEDIUM


def update_phase(state: AgentState, new_phase: WorkflowPhase) -> AgentState:
    """Update workflow phase and timestamp"""
    state["phase"] = new_phase
    state["updated_at"] = datetime.now()
    return state


def add_status_message(state: AgentState, message: str) -> AgentState:
    """Add status message for UI"""
    state["status_messages"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    state["updated_at"] = datetime.now()
    return state


def add_error(state: AgentState, agent: str, error: str, details: Optional[Dict] = None) -> AgentState:
    """Add error to state"""
    state["errors"].append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "error": error,
        "details": details or {}
    })
    state["updated_at"] = datetime.now()
    return state


def validate_gate_check(state: AgentState, phase: str, criteria: List[str]) -> bool:
    """
    Validate gate check criteria before proceeding.
    
    Example criteria:
    - "product_brief_not_empty"
    - "requirements_count_gt_5"
    - "nfr_coverage_gt_90"
    
    Args:
        state: Current agent state
        phase: Phase name for gate check
        criteria: List of validation criteria
    
    Returns:
        bool: True if all criteria pass
    """
    all_passed = True
    
    for criterion in criteria:
        if criterion == "product_brief_not_empty":
            if not state.get("product_brief", "").strip():
                state["validation_errors"].append(f"Gate check failed: {criterion}")
                all_passed = False
        
        elif criterion == "requirements_count_gt_5":
            if len(state.get("requirements", [])) < 5:
                state["validation_errors"].append(f"Gate check failed: {criterion}")
                all_passed = False
        
        elif criterion == "nfr_coverage_gt_90":
            # Check if 90% of NFRs are addressed in architecture
            nfrs = [r for r in state.get("requirements", []) if r["type"] == RequirementType.NON_FUNCTIONAL]
            if nfrs:
                architecture = state.get("architecture", "")
                covered = sum(1 for nfr in nfrs if nfr["id"] in architecture)
                coverage = (covered / len(nfrs)) * 100
                if coverage < 90:
                    state["validation_errors"].append(
                        f"Gate check failed: {criterion} (coverage: {coverage:.1f}%)"
                    )
                    all_passed = False
    
    state["gate_checks"][phase] = all_passed
    return all_passed
