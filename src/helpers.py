"""
BMAD Helpers Module
Implements the "Helpers Pattern" from BMAD method for efficient prompt management.
These helpers reduce token usage by centralizing common instructions.
"""

from typing import List, Dict, Any

class BMAdHelpers:
    """
    Collection of reusable prompt sections (helpers).
    """
    
    @staticmethod
    def get_role_definition(role: str) -> str:
        """Get standardized role definition."""
        roles = {
            "market_analyst": "You are a Senior Market Analyst specializing in data-driven product research.",
            "prd_generator": "You are a Technical Product Manager following the GitHub Spec Kit methodology.",
            "architect": "You are a Principal System Architect with expertise in cloud-native solutions.",
            "ux_designer": "You are a Lead UX Designer focused on accessibility and user-centric flows.",
            "sprint_planner": "You are an Agile Scrum Master expert in sprint estimation and planning."
        }
        return roles.get(role, "You are an expert AI assistant.")

    @staticmethod
    def get_output_format_instruction(use_toon: bool = True) -> str:
        """Get instruction for output format (TOON or JSON)."""
        if use_toon:
            return """
**Output Format:**
Respond ONLY in TOON format (Token-Oriented Object Notation).
Example:
section: Executive Summary
content: This product...
tags[3]: saas,mvp,ai
"""
        else:
            return """
**Output Format:**
Respond ONLY in valid JSON format.
"""

    @staticmethod
    def get_gate_check_instruction() -> str:
        """Instruction for self-validation (Gate Check)."""
        return """
**Gate Check:**
Before outputting, verify:
1. All required sections are present.
2. No placeholder text remains.
3. All claims are supported by research (if applicable).
"""

    @staticmethod
    def get_mermaid_guidelines() -> str:
        """Guidelines for generating valid Mermaid diagrams."""
        return """
**Mermaid Diagram Rules:**
1. Use standard syntax only (graph TB, sequenceDiagram, etc.).
2. Avoid special characters in node names unless escaped.
3. Keep diagrams simple and readable.
4. If a diagram is complex, break it into smaller sub-graphs.
"""

    @staticmethod
    def generate_agent_guidance(guidance: str, next_phase: str) -> str:
        """
        Generate standard "Agent Guidance" footer for documents.
        This helps the next agent in the chain understand context.
        """
        return f"""
---
**Agent Guidance:**
{guidance}

**Next Phase:** {next_phase}
"""

    @staticmethod
    def calculate_nfr_coverage(nfrs: List[Dict], implementation: str) -> tuple[float, List[str]]:
        """
        Helper to calculate NFR coverage percentage.
        (Simple keyword matching simulation for now)
        """
        covered_count = 0
        uncovered = []
        
        impl_lower = implementation.lower()
        
        for nfr in nfrs:
            # Check if NFR ID or title is mentioned
            if nfr.get('id', '').lower() in impl_lower or nfr.get('title', '').lower() in impl_lower:
                covered_count += 1
            else:
                uncovered.append(nfr.get('id', 'Unknown'))
                
        if not nfrs:
            return 100.0, []
            
        return (covered_count / len(nfrs)) * 100, uncovered

# Standard prompt suffix to be appended to all agent prompts
def get_standard_prompt_suffix() -> str:
    return """
Ensure your response is comprehensive, specific, and actionable.
Avoid generic advice. Use concrete examples and metrics where possible.
"""