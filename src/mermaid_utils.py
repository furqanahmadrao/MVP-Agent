"""
Mermaid Diagram Validation and Correction Module
Ensures generated Mermaid diagrams are syntactically valid for Gradio rendering
"""

import re
from typing import Tuple, Optional
from datetime import datetime
import os


def extract_mermaid_blocks(markdown: str) -> list[str]:
    """
    Extract all Mermaid code blocks from markdown content
    
    Args:
        markdown: Full markdown content
        
    Returns:
        List of Mermaid code blocks (with fences removed)
    """
    # Pattern to match ```mermaid ... ```
    pattern = r'```mermaid\s*\n(.*?)```'
    matches = re.findall(pattern, markdown, re.DOTALL)
    return matches


def validate_mermaid_block(mermaid_code: str) -> Tuple[bool, str]:
    """
    Validate a single Mermaid diagram for common syntax errors
    
    Args:
        mermaid_code: Mermaid diagram content (without fences)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mermaid_code or not mermaid_code.strip():
        return False, "empty diagram content"
    
    lines = [line.strip() for line in mermaid_code.splitlines() if line.strip()]
    
    if not lines:
        return False, "no non-empty lines found"
    
    # Check first line for recognized diagram type
    first_line = lines[0].lower()
    recognized_types = [
        'graph', 'flowchart', 'sequencediagram', 'gantt', 
        'classDiagram', 'stateDiagram', 'erDiagram', 'journey'
    ]
    
    if not any(first_line.startswith(t.lower()) for t in recognized_types):
        return False, f"first line '{lines[0]}' is not a recognized Mermaid diagram type (graph, flowchart, sequenceDiagram, etc.)"
    
    # Check for balanced brackets/parentheses
    bracket_pairs = [('(', ')'), ('[', ']'), ('{', '}')]
    for open_char, close_char in bracket_pairs:
        open_count = mermaid_code.count(open_char)
        close_count = mermaid_code.count(close_char)
        if open_count != close_count:
            return False, f"unbalanced {open_char}{close_char} brackets: {open_count} opening vs {close_count} closing"
    
    # Check for incomplete arrows (lines ending with arrow but no target)
    arrow_patterns = [
        r'-->\s*$',      # -->
        r'->\s*$',       # ->
        r'==>\s*$',      # ==>
        r'-\.->\s*$',    # .->
        r'---\s*$',      # ---
    ]
    
    for line in lines:
        for pattern in arrow_patterns:
            if re.search(pattern, line):
                return False, f"line ends with incomplete arrow: '{line[:50]}...'"
    
    # Check for node IDs with spaces (common error) - but exclude sequence diagrams
    # Sequence diagrams use "participant A as User" syntax which is valid
    first_line_lower = lines[0].lower()
    if not first_line_lower.startswith('sequencediagram'):
        if re.search(r'\b\w+\s+\w+\s*-->', mermaid_code):
            return False, "node IDs contain spaces (use underscores or camelCase)"
    
    return True, ""


def validate_markdown_mermaid(markdown: str) -> Tuple[bool, str]:
    """
    Validate all Mermaid blocks in a markdown document
    
    Args:
        markdown: Full markdown content
        
    Returns:
        Tuple of (all_valid, error_message)
    """
    blocks = extract_mermaid_blocks(markdown)
    
    if not blocks:
        # No Mermaid blocks found - this is OK for some files
        return True, ""
    
    for i, block in enumerate(blocks):
        is_valid, error = validate_mermaid_block(block)
        if not is_valid:
            return False, f"Mermaid block {i+1}/{len(blocks)}: {error}"
    
    return True, ""


def create_fix_prompt(original_block: str, error_reason: str) -> str:
    """
    Create a focused prompt to fix a broken Mermaid diagram
    
    Args:
        original_block: The invalid Mermaid code
        error_reason: Description of what's wrong
        
    Returns:
        Prompt string for the AI to fix the diagram
    """
    return f"""# Task: Fix Mermaid Diagram Syntax Error

You are a Mermaid diagram syntax expert. Fix ONLY the syntax error in the diagram below. Output EXACTLY one valid Mermaid code block and nothing else.

## Error Found:
{error_reason}

## Invalid Diagram:
```mermaid
{original_block}
```

## Requirements:
1. Output ONLY a fenced code block starting with ```mermaid and ending with ```
2. Fix the specific error mentioned above
3. Preserve the diagram's structure and meaning
4. Use only valid Mermaid syntax:
   - Diagram types: graph TD/LR, flowchart TD/LR, sequenceDiagram, etc.
   - Node shapes: [] for boxes, () for rounded, {{}} for decisions, [()] for circles
   - Arrows: -->, ---, .-.>, ==>, -->|label|
   - No spaces in node IDs (use underscores or camelCase)
5. Ensure all brackets and parentheses are balanced
6. No incomplete arrows (every arrow must have a target)

## Output Format (EXACT):
```mermaid
[corrected diagram here]
```

Do NOT add explanations, comments, or text outside the code block."""


def log_mermaid_attempt(
    file_type: str,
    attempt: int,
    content: str,
    is_valid: bool,
    error: str = ""
) -> None:
    """
    Log Mermaid generation/correction attempts for debugging
    
    Args:
        file_type: Type of file (architecture, user_flow, etc.)
        attempt: Attempt number (0 = original, 1+ = fixes)
        content: The Mermaid code
        is_valid: Whether it passed validation
        error: Validation error message if any
    """
    # Create logs/mermaid directory if it doesn't exist
    log_dir = "logs/mermaid"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_dir}/{file_type}_{timestamp}_attempt{attempt}.log"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== Mermaid Diagram Log ===\n")
        f.write(f"File Type: {file_type}\n")
        f.write(f"Attempt: {attempt}\n")
        f.write(f"Valid: {is_valid}\n")
        if error:
            f.write(f"Error: {error}\n")
        f.write(f"\n=== Content ===\n")
        f.write(content)
        f.write(f"\n\n=== End Log ===\n")


def fix_common_mermaid_errors(mermaid_code: str) -> str:
    """
    Apply automatic fixes for common Mermaid syntax errors
    
    Args:
        mermaid_code: Raw Mermaid code (with or without fences)
        
    Returns:
        Fixed Mermaid code
    """
    # Remove fences if present
    code = mermaid_code.strip()
    if code.startswith("```mermaid") or code.startswith("```"):
        lines = code.split("\n")
        # Find where mermaid block starts and ends
        start_idx = 1 if lines[0].startswith("```") else 0
        end_idx = len(lines) - 1 if lines and lines[-1].strip() == "```" else len(lines)
        code = "\n".join(lines[start_idx:end_idx])
    
    # Fix 1: Replace spaces in node IDs with underscores (but not in sequence diagrams)
    lines = code.split("\n")
    first_line = lines[0].lower() if lines else ""
    
    if not first_line.startswith('sequencediagram'):
        # Pattern: NodeWith Spaces --> becomes NodeWith_Spaces -->
        code = re.sub(r'(\w+)\s+(\w+)(\s*(?:-->|---|\.->|==>))', r'\1_\2\3', code)
    
    # Fix 2: Ensure first line has proper diagram type
    lines = code.split("\n")
    if lines and not any(lines[0].lower().startswith(t) for t in ['graph', 'flowchart', 'sequence']):
        # Prepend a default diagram type
        lines.insert(0, "graph TD")
    
    # Fix 3: Remove incomplete arrows at end of lines
    fixed_lines = []
    for line in lines:
        # If line ends with arrow but no target, remove the arrow
        if re.search(r'-->\s*$', line):
            line = re.sub(r'-->\s*$', '', line)
        fixed_lines.append(line)
    
    return "\n".join(fixed_lines)


def extract_and_validate_all(markdown: str) -> Tuple[bool, list[Tuple[str, bool, str]]]:
    """
    Extract all Mermaid blocks and validate each one
    
    Args:
        markdown: Full markdown content
        
    Returns:
        Tuple of (all_valid, list of (block, is_valid, error))
    """
    blocks = extract_mermaid_blocks(markdown)
    results = []
    all_valid = True
    
    for block in blocks:
        is_valid, error = validate_mermaid_block(block)
        results.append((block, is_valid, error))
        if not is_valid:
            all_valid = False
    
    return all_valid, results
