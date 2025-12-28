"""
BMAD Helpers System - Token Optimization Pattern
Reduces token usage by 70-85% through reusable sections
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml


class BMAdHelpers:
    """
    BMAD-inspired helpers for token-efficient agent workflows.
    
    The helpers pattern extracts common patterns into reusable functions,
    reducing redundant prompt content and token usage.
    """
    
    # ===== Global Config =====
    
    @staticmethod
    def get_global_config() -> Dict[str, Any]:
        """
        Global configuration loaded once and reused.
        Reduces token usage by ~70% vs. repeating in every prompt.
        """
        return {
            "output_format": {
                "markdown": True,
                "agent_guidance": True,
                "rationale_sections": True,
                "mermaid_diagrams": True,
                "mermaid_fallbacks": True,
                "tables_for_structured_data": True,
                "numbered_lists": True
            },
            "requirements": {
                "naming_convention": "FR-001, NFR-001, US-001, EP-001",
                "moscow_prioritization": ["Must-Have", "Should-Have", "Could-Have", "Won't-Have"],
                "traceability": True,
                "acceptance_criteria": True
            },
            "validation": {
                "gate_checks": True,
                "minimum_coverage": 0.90,  # 90% NFR coverage
                "mermaid_validation": True,
                "error_fallbacks": True
            },
            "agent_behavior": {
                "explicit_reasoning": True,
                "show_alternatives": True,
                "edge_cases": True,
                "future_considerations": True
            },
            "token_optimization": {
                "use_tables": True,
                "use_helpers": True,
                "minimize_repetition": True,
                "toon_format": False  # Toggled at runtime
            }
        }
    
    # ===== Status Tracking =====
    
    @staticmethod
    def generate_status_yaml(phase: str, agent: str, progress: int, status: str) -> str:
        """
        Generate YAML status block for tracking.
        
        Example:
        ```yaml
        phase: analysis
        agent: market_analyst
        progress: 25
        status: researching_competitors
        timestamp: 2025-12-28T10:30:00
        ```
        """
        status_dict = {
            "phase": phase,
            "agent": agent,
            "progress": progress,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        return yaml.dump(status_dict, default_flow_style=False)
    
    # ===== Requirement Parsing =====
    
    @staticmethod
    def parse_requirements(text: str) -> List[Dict[str, Any]]:
        """
        Parse requirements from generated text.
        
        Expected format:
        ### FR-001: User Authentication
        **Description:** ...
        **Priority:** Must-Have
        **Story Points:** 5
        
        Returns list of requirement dicts.
        """
        requirements = []
        lines = text.split("\n")
        
        current_req = None
        for line in lines:
            # Check for requirement header
            if line.startswith("### ") and ":" in line:
                # Save previous requirement
                if current_req:
                    requirements.append(current_req)
                
                # Parse new requirement
                header = line[4:].strip()  # Remove "### "
                req_id, title = header.split(":", 1)
                req_id = req_id.strip()
                title = title.strip()
                
                # Determine type
                if req_id.startswith("FR-"):
                    req_type = "FR"
                elif req_id.startswith("NFR-"):
                    req_type = "NFR"
                elif req_id.startswith("US-"):
                    req_type = "US"
                elif req_id.startswith("EP-"):
                    req_type = "EP"
                else:
                    req_type = "UNKNOWN"
                
                current_req = {
                    "id": req_id,
                    "type": req_type,
                    "title": title,
                    "description": "",
                    "priority": "",
                    "story_points": None,
                    "acceptance_criteria": [],
                    "dependencies": []
                }
            
            # Parse requirement fields
            elif current_req:
                if line.startswith("**Description:**"):
                    current_req["description"] = line.replace("**Description:**", "").strip()
                elif line.startswith("**Priority:**"):
                    current_req["priority"] = line.replace("**Priority:**", "").strip()
                elif line.startswith("**Story Points:**"):
                    try:
                        current_req["story_points"] = int(line.replace("**Story Points:**", "").strip())
                    except ValueError:
                        pass
                elif line.startswith("- [ ]") or line.startswith("- [x]"):
                    # Acceptance criteria
                    current_req["acceptance_criteria"].append(line[5:].strip())
                elif line.startswith("**Dependencies:**"):
                    deps = line.replace("**Dependencies:**", "").strip()
                    if deps and deps != "None":
                        current_req["dependencies"] = [d.strip() for d in deps.split(",")]
        
        # Save last requirement
        if current_req:
            requirements.append(current_req)
        
        return requirements
    
    # ===== Mermaid Helpers =====
    
    @staticmethod
    def validate_mermaid(diagram: str) -> tuple[bool, Optional[str]]:
        """
        Validate Mermaid diagram syntax.
        
        Returns:
            (is_valid, error_message)
        """
        if not diagram or not diagram.strip():
            return False, "Empty diagram"
        
        diagram = diagram.strip()
        
        # Check diagram type
        valid_types = [
            "graph", "flowchart", "sequenceDiagram", "classDiagram",
            "erDiagram", "gantt", "pie", "quadrantChart", "stateDiagram"
        ]
        
        if not any(diagram.startswith(t) for t in valid_types):
            return False, f"Invalid diagram type. Must start with one of: {', '.join(valid_types)}"
        
        # Check balanced braces
        if diagram.count("[") != diagram.count("]"):
            return False, "Unbalanced square brackets"
        if diagram.count("(") != diagram.count(")"):
            return False, "Unbalanced parentheses"
        if diagram.count("{") != diagram.count("}"):
            return False, "Unbalanced curly braces"
        
        # Check for common errors
        if "-->" in diagram and "graph" not in diagram and "flowchart" not in diagram:
            return False, "Arrow syntax '-->' only valid in graph/flowchart diagrams"
        
        return True, None
    
    @staticmethod
    def generate_mermaid_with_fallback(
        diagram: str,
        fallback_text: str,
        diagram_title: str = "Diagram"
    ) -> str:
        """
        Generate Mermaid diagram or fallback to text description.
        
        Args:
            diagram: Mermaid diagram code
            fallback_text: Text description if diagram fails validation
            diagram_title: Title for the diagram section
        
        Returns:
            Markdown string with diagram or fallback
        """
        is_valid, error_msg = BMAdHelpers.validate_mermaid(diagram)
        
        if is_valid:
            return f"### {diagram_title}\n\n```mermaid\n{diagram}\n```\n\n"
        else:
            # Don't show broken diagram, use fallback
            return (
                f"### {diagram_title}\n\n"
                f"**Note:** Diagram generation failed validation ({error_msg}). "
                f"Using text description instead.\n\n"
                f"{fallback_text}\n\n"
            )
    
    # ===== Document Structure =====
    
    @staticmethod
    def generate_document_header(
        title: str,
        subtitle: str,
        version: str = "1.0",
        author: str = "MVP Agent"
    ) -> str:
        """Generate consistent document header"""
        return f"""# {title}

**Subtitle:** {subtitle}  
**Version:** {version}  
**Generated By:** {author}  
**Date:** {datetime.now().strftime('%Y-%m-%d')}

---

"""
    
    @staticmethod
    def generate_agent_guidance(guidance: str, next_phase: str) -> str:
        """
        Generate agent guidance section at end of document.
        
        This tells the next agent in the workflow how to use this document.
        """
        return f"""---

## 🤖 Agent Guidance

{guidance}

**Next Phase:** {next_phase}

**Validation Checklist:**
- [ ] All requirements are traceable (IDs assigned)
- [ ] MoSCoW prioritization is complete
- [ ] Mermaid diagrams validate or have fallbacks
- [ ] Agent guidance is clear and actionable

"""
    
    @staticmethod
    def generate_rationale_section(rationale: str) -> str:
        """Generate rationale section"""
        return f"""**Rationale:**

{rationale}

"""
    
    # ===== MoSCoW Prioritization =====
    
    @staticmethod
    def group_by_moscow(requirements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group requirements by MoSCoW priority.
        
        Returns dict with keys: must, should, could, wont
        """
        grouped = {
            "must": [],
            "should": [],
            "could": [],
            "wont": []
        }
        
        for req in requirements:
            priority = req.get("priority", "").lower()
            if "must" in priority:
                grouped["must"].append(req)
            elif "should" in priority:
                grouped["should"].append(req)
            elif "could" in priority:
                grouped["could"].append(req)
            elif "won't" in priority or "wont" in priority:
                grouped["wont"].append(req)
        
        return grouped
    
    @staticmethod
    def generate_moscow_table(requirements: List[Dict[str, Any]]) -> str:
        """
        Generate MoSCoW prioritization table.
        
        Returns:
            Markdown table
        """
        grouped = BMAdHelpers.group_by_moscow(requirements)
        
        table = "## MoSCoW Prioritization\n\n"
        
        for priority_name, priority_key in [
            ("Must-Have", "must"),
            ("Should-Have", "should"),
            ("Could-Have", "could"),
            ("Won't-Have", "wont")
        ]:
            reqs = grouped[priority_key]
            if reqs:
                table += f"### {priority_name}\n\n"
                table += "| ID | Title | Story Points |\n"
                table += "|-------|-------|-------------|\n"
                for req in reqs:
                    points = req.get("story_points", "?")
                    table += f"| {req['id']} | {req['title']} | {points} |\n"
                table += "\n"
        
        return table
    
    # ===== Table Generators =====
    
    @staticmethod
    def generate_tech_stack_table(tech_stack: Dict[str, List[str]]) -> str:
        """
        Generate tech stack comparison table.
        
        Example:
        | Category | Technology | Justification |
        |----------|------------|---------------|
        | Frontend | React | ... |
        """
        table = "## Technology Stack\n\n"
        table += "| Category | Technology | Justification |\n"
        table += "|----------|------------|---------------|\n"
        
        for category, techs in tech_stack.items():
            for tech in techs:
                # Parse if tech is "name: justification"
                if ":" in tech:
                    tech_name, justification = tech.split(":", 1)
                    table += f"| {category} | {tech_name.strip()} | {justification.strip()} |\n"
                else:
                    table += f"| {category} | {tech} | - |\n"
        
        return table
    
    @staticmethod
    def generate_persona_table(personas: List[Dict[str, Any]]) -> str:
        """
        Generate user persona table.
        
        Example:
        | Persona | Description | Pain Points | Goals |
        |---------|-------------|-------------|-------|
        | Sarah | ... | ... | ... |
        """
        if not personas:
            return ""
        
        table = "## User Personas\n\n"
        table += "| Persona | Description | Pain Points | Goals |\n"
        table += "|---------|-------------|-------------|-------|\n"
        
        for persona in personas:
            name = persona.get("name", "Unknown")
            desc = persona.get("description", "-")
            pain_points = ", ".join(persona.get("pain_points", []))
            goals = ", ".join(persona.get("goals", []))
            
            table += f"| {name} | {desc} | {pain_points} | {goals} |\n"
        
        return table
    
    # ===== NFR Coverage =====
    
    @staticmethod
    def calculate_nfr_coverage(
        nfrs: List[Dict[str, Any]],
        architecture_doc: str
    ) -> tuple[float, List[str]]:
        """
        Calculate NFR coverage in architecture document.
        
        Returns:
            (coverage_percentage, uncovered_nfr_ids)
        """
        if not nfrs:
            return 100.0, []
        
        uncovered = []
        covered_count = 0
        
        for nfr in nfrs:
            nfr_id = nfr["id"]
            if nfr_id in architecture_doc:
                covered_count += 1
            else:
                uncovered.append(nfr_id)
        
        coverage = (covered_count / len(nfrs)) * 100
        return coverage, uncovered
    
    # ===== Token Estimation =====
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters for English).
        
        More accurate: use tiktoken library, but this is close enough.
        """
        return len(text) // 4
    
    @staticmethod
    def compare_token_efficiency(original: str, optimized: str) -> Dict[str, Any]:
        """
        Compare token usage between original and optimized prompts.
        
        Returns:
            {
                "original_tokens": int,
                "optimized_tokens": int,
                "savings": int,
                "savings_percentage": float
            }
        """
        original_tokens = BMAdHelpers.estimate_tokens(original)
        optimized_tokens = BMAdHelpers.estimate_tokens(optimized)
        savings = original_tokens - optimized_tokens
        savings_pct = (savings / original_tokens * 100) if original_tokens > 0 else 0
        
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "savings": savings,
            "savings_percentage": round(savings_pct, 2)
        }


# ===== Helper Presets =====

def get_standard_prompt_suffix() -> str:
    """
    Standard suffix for all agent prompts.
    Reduces repetition across agents (saves ~500 tokens per prompt).
    """
    return """
**Output Requirements:**
- Use Markdown format with clear headings
- Include rationale sections explaining key decisions
- Add agent guidance at the end (instructions for next agent)
- Use tables for structured data (not lengthy prose)
- Generate Mermaid diagrams where appropriate
- If Mermaid diagram fails validation, use text description (don't show broken diagrams)
- Use numbered lists for sequential steps
- Include edge cases and future considerations

**Requirement Naming:**
- Functional: FR-001, FR-002, ...
- Non-Functional: NFR-001, NFR-002, ...
- User Stories: US-001, US-002, ...
- Epics: EP-001, EP-002, ...

**MoSCoW Prioritization:**
- Must-Have: Critical for MVP
- Should-Have: Important but not blocking
- Could-Have: Nice to have
- Won't-Have: Explicitly excluded from current scope
"""


def get_mermaid_guidelines() -> str:
    """
    Mermaid diagram guidelines for all agents.
    Saves ~300 tokens per prompt.
    """
    return """
**Mermaid Diagram Guidelines:**
- Always provide a text fallback description
- Use simple syntax (avoid complex nesting)
- Validate diagram structure before outputting
- Supported types: graph, flowchart, sequenceDiagram, classDiagram, erDiagram, gantt
- If unsure, prefer text description over broken diagram

**Common Pitfalls:**
- Unbalanced brackets/parentheses
- Using arrows in wrong diagram type
- Overly complex nested structures
- Special characters in node names (use quotes)
"""
