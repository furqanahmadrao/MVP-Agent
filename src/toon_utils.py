"""
TOON Format Support (Optional)
Token-Oriented Object Notation for 30-60% token reduction

Note: TOON format is used for INTERNAL agent communication only.
Human-facing outputs remain in Markdown for readability.
"""

from typing import Any, Dict, List, Union, Optional
import json


class TOONEncoder:
    """
    Encode Python objects to TOON format.
    
    TOON Syntax:
    - Objects: key: value (YAML-like)
    - Arrays (uniform): [N,]{fields}: row1,row2,row3
    - Arrays (mixed): [N]: - item1 - item2
    - Primitives: direct values
    """
    
    @staticmethod
    def encode(data: Any, indent: int = 0) -> str:
        """
        Encode data to TOON format.
        
        Args:
            data: Python object (dict, list, primitive)
            indent: Indentation level (spaces)
        
        Returns:
            TOON formatted string
        """
        indent_str = "  " * indent
        
        if isinstance(data, dict):
            return TOONEncoder._encode_object(data, indent)
        elif isinstance(data, list):
            return TOONEncoder._encode_array(data, indent)
        elif isinstance(data, str):
            return TOONEncoder._encode_string(data)
        elif isinstance(data, (int, float, bool)):
            return str(data).lower() if isinstance(data, bool) else str(data)
        elif data is None:
            return "null"
        else:
            return str(data)
    
    @staticmethod
    def _encode_object(obj: Dict[str, Any], indent: int) -> str:
        """Encode dictionary to TOON object"""
        if not obj:
            return "{}"
        
        indent_str = "  " * indent
        lines = []
        
        for key, value in obj.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                lines.append(TOONEncoder._encode_object(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{indent_str}{key}{TOONEncoder._encode_array_header(value)}:")
                lines.append(TOONEncoder._encode_array(value, indent + 1))
            else:
                encoded_value = TOONEncoder.encode(value, 0)
                lines.append(f"{indent_str}{key}: {encoded_value}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _encode_array_header(arr: List[Any]) -> str:
        """Generate array header [N,]{fields} if uniform"""
        if not arr:
            return "[0]"
        
        # Check if all items are dicts with same keys (uniform)
        if all(isinstance(item, dict) for item in arr):
            first_keys = set(arr[0].keys())
            if all(set(item.keys()) == first_keys for item in arr):
                # Uniform array
                fields = ",".join(arr[0].keys())
                return f"[{len(arr)},]{{{fields}}}"
        
        # Non-uniform array
        return f"[{len(arr)}]"
    
    @staticmethod
    def _encode_array(arr: List[Any], indent: int) -> str:
        """Encode list to TOON array"""
        if not arr:
            return ""
        
        indent_str = "  " * indent
        
        # Check if uniform array of dicts
        if all(isinstance(item, dict) for item in arr):
            first_keys = list(arr[0].keys())
            if all(set(item.keys()) == set(first_keys) for item in arr):
                # Tabular format
                lines = []
                for item in arr:
                    row_values = [TOONEncoder._encode_string(str(item[k])) for k in first_keys]
                    lines.append(f"{indent_str}{','.join(row_values)}")
                return "\n".join(lines)
        
        # Mixed array (YAML-style)
        lines = []
        for item in arr:
            if isinstance(item, (dict, list)):
                lines.append(f"{indent_str}- ")
                lines.append(TOONEncoder.encode(item, indent + 1))
            else:
                encoded = TOONEncoder.encode(item, 0)
                lines.append(f"{indent_str}- {encoded}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _encode_string(s: str) -> str:
        """
        Encode string, quoting only when necessary.
        
        Quote if:
        - Empty string
        - Contains comma, colon, newline
        - Starts with special chars (-, [, {)
        - Numeric string that shouldn't be parsed as number
        """
        if not s:
            return '""'
        
        needs_quotes = (
            "," in s or
            ":" in s or
            "\n" in s or
            s[0] in ("-", "[", "{", "'", '"') or
            s in ("true", "false", "null") or
            s.strip() != s  # Leading/trailing whitespace
        )
        
        if needs_quotes:
            # Escape quotes
            escaped = s.replace('"', '\\"')
            return f'"{escaped}"'
        
        return s


class TOONDecoder:
    """
    Decode TOON format to Python objects.
    
    Note: This is a simplified decoder. For production use,
    consider the official toon-format Python package.
    """
    
    @staticmethod
    def decode(toon_str: str) -> Any:
        """
        Decode TOON string to Python object.
        
        Args:
            toon_str: TOON formatted string
        
        Returns:
            Python object (dict, list, or primitive)
        """
        # Simplified: for MVP, we primarily encode, not decode
        # In production, use the official toon-format package
        
        # For now, parse as YAML-like
        import yaml
        try:
            return yaml.safe_load(toon_str)
        except Exception as e:
            raise ValueError(f"TOON decode error: {e}")


class TOONUtils:
    """Utility functions for TOON format"""
    
    @staticmethod
    def compare_sizes(data: Any) -> Dict[str, int]:
        """
        Compare JSON vs TOON sizes.
        
        Returns:
            {
                "json_size": int,
                "toon_size": int,
                "savings": int,
                "savings_percentage": float
            }
        """
        json_str = json.dumps(data, indent=None)
        toon_str = TOONEncoder.encode(data)
        
        json_size = len(json_str)
        toon_size = len(toon_str)
        savings = json_size - toon_size
        savings_pct = (savings / json_size * 100) if json_size > 0 else 0
        
        return {
            "json_size": json_size,
            "toon_size": toon_size,
            "savings": savings,
            "savings_percentage": round(savings_pct, 2)
        }
    
    @staticmethod
    def should_use_toon(data: Any, threshold: float = 0.20) -> bool:
        """
        Decide if TOON format should be used.
        
        Use TOON if savings > threshold (default 20%)
        
        Args:
            data: Data to encode
            threshold: Minimum savings percentage to justify TOON
        
        Returns:
            True if TOON saves enough tokens
        """
        comparison = TOONUtils.compare_sizes(data)
        return comparison["savings_percentage"] > (threshold * 100)


# ===== Example Usage =====

def example_toon_encoding():
    """Example of TOON encoding for agent data"""
    
    # Example: Requirements data
    requirements = [
        {
            "id": "FR-001",
            "title": "User Authentication",
            "priority": "Must-Have",
            "points": 5
        },
        {
            "id": "FR-002",
            "title": "User Profile",
            "priority": "Should-Have",
            "points": 3
        },
        {
            "id": "NFR-001",
            "title": "Performance",
            "priority": "Must-Have",
            "points": 8
        }
    ]
    
    # Encode to TOON
    toon_output = TOONEncoder.encode({"requirements": requirements})
    
    print("TOON Output:")
    print(toon_output)
    print()
    
    # Compare sizes
    comparison = TOONUtils.compare_sizes({"requirements": requirements})
    print(f"JSON size: {comparison['json_size']} bytes")
    print(f"TOON size: {comparison['toon_size']} bytes")
    print(f"Savings: {comparison['savings']} bytes ({comparison['savings_percentage']}%)")
    
    """
    Expected TOON Output:
    
    requirements[3,]{id,title,priority,points}:
      FR-001,User Authentication,Must-Have,5
      FR-002,User Profile,Should-Have,3
      NFR-001,Performance,Must-Have,8
    
    This is 30-60% smaller than equivalent JSON.
    """


# ===== Integration with Agent State =====

def encode_agent_state_to_toon(state: Dict[str, Any], fields: List[str]) -> str:
    """
    Encode specific agent state fields to TOON for inter-agent communication.
    
    Args:
        state: Agent state dict
        fields: Fields to encode (e.g., ["requirements", "personas"])
    
    Returns:
        TOON encoded string
    """
    # Extract specified fields
    data = {field: state.get(field, []) for field in fields}
    
    # Encode to TOON
    return TOONEncoder.encode(data)


def should_use_toon_for_agent(state: Dict[str, Any]) -> bool:
    """
    Decide if TOON should be used based on state settings.
    
    Args:
        state: Agent state
    
    Returns:
        True if enable_toon is True and data is suitable
    """
    # Check if TOON is enabled in settings
    if not state.get("enable_toon", False):
        return False
    
    # Check if we have structured data (requirements, personas)
    has_structured_data = (
        len(state.get("requirements", [])) > 0 or
        len(state.get("personas", [])) > 0 or
        len(state.get("epics", [])) > 0
    )
    
    return has_structured_data


# ===== Agent Prompt Helpers =====

def get_toon_format_instructions() -> str:
    """
    Instructions for agents to output TOON format.
    
    Use this in prompts when TOON is enabled.
    """
    return """
**Output Format: TOON (Token-Oriented Object Notation)**

Use TOON format for structured data to reduce token usage by 30-60%.

**TOON Syntax:**
- Objects: `key: value` (YAML-like indentation)
- Uniform arrays: `[N,]{fields}: row1,row2,row3` (CSV-like)
- Mixed arrays: `[N]: - item1 - item2`
- Quote strings only when necessary (contains comma, colon, newline, or special chars)

**Example:**
```toon
requirements[3,]{id,title,priority,points}:
  FR-001,User Authentication,Must-Have,5
  FR-002,User Profile,Should-Have,3
  NFR-001,Performance,Must-Have,8
```

**When to use TOON:**
- For lists of requirements, personas, epics
- For tabular data (tech stack, features)
- For inter-agent communication (not user-facing docs)

**When NOT to use TOON:**
- User-facing markdown documents (use Markdown)
- Narrative text (descriptions, rationale)
- Complex nested structures (fallback to JSON)
"""


if __name__ == "__main__":
    # Run example
    example_toon_encoding()
