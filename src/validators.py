"""
Validators Module - Input validation and sanitization
Ensures all user inputs are safe and valid
"""

import re
from typing import Dict, List, Tuple, Optional

class InputValidator:
    """Validates user inputs for MVP Agent"""
    
    # Constants
    MIN_IDEA_LENGTH = 10
    MAX_IDEA_LENGTH = 1000
    DANGEROUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'eval\(',
        r'exec\(',
    ]
    
    @staticmethod
    def validate_startup_idea(idea: str) -> Tuple[bool, Optional[str]]:
        """
        Validate startup idea input
        
        Args:
            idea: The startup idea string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if not idea:
            return False, "Please enter a startup idea"
        
        # Check type
        if not isinstance(idea, str):
            return False, "Idea must be text"
        
        # Strip whitespace
        idea = idea.strip()
        
        # Check length
        if len(idea) < InputValidator.MIN_IDEA_LENGTH:
            return False, f"Idea too short. Please enter at least {InputValidator.MIN_IDEA_LENGTH} characters"
        
        if len(idea) > InputValidator.MAX_IDEA_LENGTH:
            return False, f"Idea too long. Please keep it under {InputValidator.MAX_IDEA_LENGTH} characters"
        
        # Check for dangerous patterns (basic XSS prevention)
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, idea, re.IGNORECASE):
                return False, "Invalid characters detected in idea"
        
        # Check if meaningful (not just spaces or special chars)
        if not re.search(r'[a-zA-Z]', idea):
            return False, "Please enter a meaningful idea with text"
        
        return True, None
    
    @staticmethod
    def sanitize_idea(idea: str) -> str:
        """
        Sanitize startup idea for safe processing
        
        Args:
            idea: The raw idea
            
        Returns:
            Sanitized idea string
        """
        # Strip whitespace
        idea = idea.strip()
        
        # Remove control characters
        idea = ''.join(char for char in idea if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit consecutive spaces
        idea = re.sub(r'\s+', ' ', idea)
        
        # Remove HTML-like tags
        idea = re.sub(r'<[^>]+>', '', idea)
        
        return idea
    
    @staticmethod
    def validate_api_key(api_key: str, key_name: str = "API key") -> Tuple[bool, Optional[str]]:
        """
        Validate API key format
        
        Args:
            api_key: The API key to validate
            key_name: Name of the key (for error messages)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, f"{key_name} is required"
        
        if not isinstance(api_key, str):
            return False, f"{key_name} must be a string"
        
        api_key = api_key.strip()
        
        if len(api_key) < 10:
            return False, f"{key_name} appears to be invalid (too short)"
        
        # Check for obvious placeholder values
        placeholder_values = [
            'your_api_key',
            'insert_key_here',
            'api_key_here',
            'placeholder',
            'xxxxxx'
        ]
        
        if api_key.lower() in placeholder_values:
            return False, f"Please replace the placeholder {key_name}"
        
        return True, None
    
    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file path for safety
        
        Args:
            path: File path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "File path cannot be empty"
        
        # Check for path traversal attempts
        if '..' in path:
            return False, "Invalid file path (path traversal detected)"
        
        # Check for absolute paths (we want relative only)
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return False, "Only relative paths are allowed"
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '|', '\0', '\n', '\r']
        if any(char in path for char in dangerous_chars):
            return False, "Invalid characters in file path"
        
        return True, None

class OutputValidator:
    """Validates agent outputs"""
    
    @staticmethod
    def validate_mvp_files(files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate generated MVP files
        
        Args:
            files: Dictionary of file contents
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_files = [
            'features_md',
            'architecture_md',
            'design_md',
            'user_flow_md',
            'roadmap_md'
        ]
        
        # Check all required files present
        for file_key in required_files:
            if file_key not in files:
                errors.append(f"Missing required file: {file_key}")
            elif not files[file_key]:
                errors.append(f"Empty file: {file_key}")
            elif len(files[file_key]) < 100:
                errors.append(f"File too short (< 100 chars): {file_key}")
        
        # Check for markdown headers
        for file_key, content in files.items():
            if file_key in required_files:
                if not content.strip().startswith('#'):
                    errors.append(f"File missing markdown header: {file_key}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_structure(data: dict, required_keys: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate JSON structure has required keys
        
        Args:
            data: JSON data as dictionary
            required_keys: List of required keys
            
        Returns:
            Tuple of (is_valid, list_of_missing_keys)
        """
        missing_keys = []
        
        for key in required_keys:
            if key not in data:
                missing_keys.append(key)
            elif data[key] is None:
                missing_keys.append(f"{key} (null value)")
        
        return len(missing_keys) == 0, missing_keys

# Convenience functions
def validate_idea(idea: str) -> Tuple[bool, Optional[str]]:
    """Quick validation of startup idea"""
    return InputValidator.validate_startup_idea(idea)

def sanitize_idea(idea: str) -> str:
    """Quick sanitization of startup idea"""
    return InputValidator.sanitize_idea(idea)

def validate_files(files: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Quick validation of MVP files"""
    return OutputValidator.validate_mvp_files(files)
