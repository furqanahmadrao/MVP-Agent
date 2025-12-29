"""
TOON Format Utilities
Handles encoding and decoding of Token-Oriented Object Notation (TOON)
for efficient LLM communication.
"""

import json
from typing import Any, Dict, List, Union
import toon_format

class ToonFormatter:
    """
    Utility class for handling TOON format conversions.
    TOON reduces token usage by 30-60% compared to JSON.
    """
    
    @staticmethod
    def encode(data: Union[Dict, List]) -> str:
        """
        Encode a Python object to TOON format string.
        
        Args:
            data: Python dictionary or list
            
        Returns:
            String in TOON format
        """
        try:
            return toon_format.encode(data)
        except Exception as e:
            # Fallback to JSON if TOON encoding fails
            print(f"TOON encoding failed: {e}. Falling back to JSON.")
            return json.dumps(data, indent=2)

    @staticmethod
    def decode(toon_str: str) -> Any:
        """
        Decode a TOON format string to Python object.
        
        Args:
            toon_str: String in TOON format
            
        Returns:
            Python dictionary or list
        """
        try:
            return toon_format.decode(toon_str)
        except Exception as e:
            # Try parsing as JSON as fallback
            try:
                return json.loads(toon_str)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode TOON or JSON: {e}")

    @staticmethod
    def estimate_tokens_saved(data: Union[Dict, List]) -> dict:
        """
        Estimate token savings of TOON vs JSON.
        
        Args:
            data: Python object
            
        Returns:
            Dict with 'json_len', 'toon_len', 'savings_pct'
        """
        json_str = json.dumps(data)
        toon_str = ToonFormatter.encode(data)
        
        # Rough character count approximation (1 token ~= 4 chars)
        json_len = len(json_str)
        toon_len = len(toon_str)
        
        savings = 0
        if json_len > 0:
            savings = ((json_len - toon_len) / json_len) * 100
            
        return {
            "json_chars": json_len,
            "toon_chars": toon_len,
            "savings_pct": round(savings, 2)
        }

def should_use_toon_for_agent(agent_name: str, settings: Dict) -> bool:
    """
    Determine if an agent should use TOON format based on settings.
    
    Args:
        agent_name: Name of the agent
        settings: Application settings dict
        
    Returns:
        Boolean indicating if TOON should be used
    """
    # TOON is generally enabled globally, but can be disabled in settings
    return settings.get("use_toon_format", True)