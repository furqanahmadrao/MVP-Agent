"""
AI Models Module - Gemini API Integration
Handles all interactions with Google Gemini AI models
Includes support for Gemini Search Grounding
"""

import os
import json
import re
import google.generativeai as genai
from google import genai as genai_new  # New SDK for grounding
from google.genai import types
from typing import Optional, Dict, Any, List
from enum import Enum


def _extract_json_block(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain extra commentary or formatting.
    
    Tries multiple strategies:
    1. Extract from triple-backtick code blocks
    2. Find first balanced { } or [ ] block
    3. Return cleaned text as-is
    
    Args:
        text: Raw text from LLM that should contain JSON
        
    Returns:
        Extracted JSON string or None if no JSON found
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Strategy 1: Extract from code blocks (```json or ```)
    # Find opening and closing markers, extract everything in between
    start_patterns = ['```json\n', '```json ', '```json', '```\n', '``` ', '```']
    for start_pattern in start_patterns:
        start_idx = text.find(start_pattern)
        if start_idx != -1:
            # Find the content start (after the opening marker)
            content_start = start_idx + len(start_pattern)
            # Find the closing marker
            end_idx = text.find('```', content_start)
            if end_idx != -1:
                extracted = text[content_start:end_idx].strip()
                # Verify it starts with { or [
                if extracted and extracted[0] in ('{', '['):
                    return extracted
            break
    
    # Strategy 2: Find first balanced JSON object or array
    # Find which comes first - object or array
    obj_idx = text.find('{')
    arr_idx = text.find('[')
    
    # Determine order to try based on which appears first
    if obj_idx == -1 and arr_idx == -1:
        # No JSON found, fall through to strategy 3
        pass
    else:
        # Try the one that appears first (or the only one that exists)
        pairs_to_try = []
        if obj_idx >= 0 and (arr_idx == -1 or obj_idx < arr_idx):
            pairs_to_try = [('{', '}'), ('[', ']')]
        else:
            pairs_to_try = [('[', ']'), ('{', '}')]
        
        for start_char, end_char in pairs_to_try:
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue
                
            # Count braces to find matching closing brace
            depth = 0
            in_string = False
            escape_next = False
            
            for i in range(start_idx, len(text)):
                char = text[i]
                
                # Handle string escaping
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                
                # Track if we're inside a string
                if char == '"' and not in_string:
                    in_string = True
                    continue
                elif char == '"' and in_string:
                    in_string = False
                    continue
                
                # Count braces only outside strings
                if not in_string:
                    if char == start_char:
                        depth += 1
                    elif char == end_char:
                        depth -= 1
                        
                        if depth == 0:
                            # Found matching closing brace
                            return text[start_idx:i+1]
    
    # Strategy 3: Return cleaned text as-is
    # Remove common non-JSON prefixes
    cleaned = text
    for prefix in ['json', 'JSON', 'Here is', 'Here\'s', 'Response:']:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            if cleaned.startswith(':'):
                cleaned = cleaned[1:].strip()
    
    return cleaned


class ModelType(Enum):
    """Enum for different Gemini model types based on task complexity"""
    PRO = "gemini-2.5-pro"  # Complex reasoning, synthesis
    FLASH = "gemini-2.5-flash"  # Medium tasks, general purpose
    FLASH_LITE = "gemini-2.5-flash-lite"  # Simple tasks, high speed


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key (if not provided, uses GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.models = {
            ModelType.PRO: genai.GenerativeModel(ModelType.PRO.value),
            ModelType.FLASH: genai.GenerativeModel(ModelType.FLASH.value),
            ModelType.FLASH_LITE: genai.GenerativeModel(ModelType.FLASH_LITE.value)
        }
        
        # Track token usage
        self.total_tokens = 0
    
    def generate(
        self,
        prompt: str,
        model_type: ModelType = ModelType.FLASH,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using specified Gemini model
        
        Args:
            prompt: The prompt to send to the model
            model_type: Which model to use (Pro, Flash, or Flash-8B)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            model = self.models[model_type]
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Track token usage (approximate)
            if hasattr(response, 'usage_metadata'):
                self.total_tokens += response.usage_metadata.total_token_count
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_with_grounding(
        self,
        prompt: str,
        model_type: ModelType = ModelType.FLASH,
        temperature: float = 0.3,
        dynamic_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate response with Gemini Search Grounding.
        
        Args:
            prompt: The prompt/query to send
            model_type: Which model to use
            temperature: Sampling temperature
            dynamic_threshold: Dynamic retrieval threshold (0.0-1.0)
        
        Returns:
            {
                "answer": str,           # Generated answer
                "chunks": List[Dict],    # Grounding chunks (sources)
                "supports": List[Dict],  # Citation supports
                "search_queries": List[str]  # Queries executed
            }
        """
        try:
            # Use new SDK for grounding
            client_new = genai_new.Client(api_key=self.api_key)
            
            # Configure grounding tool
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            
            config = types.GenerateContentConfig(
                tools=[grounding_tool],
                temperature=temperature,
                response_modalities=["TEXT"]
            )
            
            # Add dynamic threshold if specified
            if dynamic_threshold is not None:
                config.tool_config = types.ToolConfig(
                    google_search_retrieval=types.GoogleSearchRetrievalConfig(
                        dynamic_retrieval_config=types.DynamicRetrievalConfig(
                            mode=types.DynamicRetrievalConfig.Mode.MODE_DYNAMIC,
                            dynamic_threshold=dynamic_threshold
                        )
                    )
                )
            
            # Generate with grounding
            response = client_new.models.generate_content(
                model=model_type.value,
                contents=prompt,
                config=config
            )
            
            # Extract grounding metadata
            grounding_metadata = None
            if hasattr(response.candidates[0], 'grounding_metadata'):
                grounding_metadata = response.candidates[0].grounding_metadata
            
            # Parse grounding chunks (sources)
            chunks = []
            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
                for chunk in grounding_metadata.grounding_chunks:
                    chunks.append({
                        "title": getattr(chunk.web, 'title', 'Unknown'),
                        "uri": getattr(chunk.web, 'uri', ''),
                        "snippet": getattr(chunk.web, 'snippet', '')
                    })
            
            # Parse grounding supports
            supports = []
            if grounding_metadata and hasattr(grounding_metadata, 'grounding_supports'):
                for support in grounding_metadata.grounding_supports:
                    supports.append({
                        "segment": {
                            "start_index": support.segment.start_index if hasattr(support, 'segment') else 0,
                            "end_index": support.segment.end_index if hasattr(support, 'segment') else 0,
                            "text": support.segment.text if hasattr(support, 'segment') else ""
                        },
                        "grounding_chunk_indices": support.grounding_chunk_indices if hasattr(support, 'grounding_chunk_indices') else [],
                        "confidence_scores": support.confidence_scores if hasattr(support, 'confidence_scores') else []
                    })
            
            # Extract search queries
            search_queries = []
            if grounding_metadata and hasattr(grounding_metadata, 'search_entry_point'):
                search_queries = getattr(grounding_metadata.search_entry_point, 'rendered_content', '')
            
            # Track tokens
            if hasattr(response, 'usage_metadata'):
                self.total_tokens += response.usage_metadata.total_token_count
            
            return {
                "answer": response.text,
                "chunks": chunks,
                "supports": supports,
                "search_queries": [prompt] if not search_queries else search_queries,
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": "",
                "chunks": [],
                "supports": [],
                "search_queries": [prompt],
                "success": False,
                "error": str(e)
            }
    
    def generate_json(
        self,
        prompt: str,
        model_type: ModelType = ModelType.FLASH,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini
        
        Args:
            prompt: The prompt (should request JSON format)
            model_type: Which model to use
            temperature: Lower temperature for more structured output
            
        Returns:
            Parsed JSON as dictionary
        """
        
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON. No markdown, no explanations."
        
        response_text = self.generate(
            json_prompt,
            model_type=model_type,
            temperature=temperature
        )
        
        # Use tolerant JSON extraction
        extracted = _extract_json_block(response_text)
        
        if not extracted:
            raise ValueError(f"No JSON found in response. Response: {response_text[:200]}...")
        
        try:
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            # Provide detailed error with both extracted and original text
            raise ValueError(
                f"Failed to parse JSON: {e}\n"
                f"Extracted text: {extracted[:200]}...\n"
                f"Original response: {response_text[:200]}..."
            )
    
    def get_token_usage(self) -> int:
        """Get total tokens used in this session"""
        return self.total_tokens


class ModelRouter:
    """
    Smart router that selects the appropriate Gemini model based on task complexity
    """
    
    def __init__(self, client: GeminiClient):
        """
        Initialize model router
        
        Args:
            client: GeminiClient instance
        """
        self.client = client
    
    def route(self, task: str, prompt: str, **kwargs) -> str:
        """
        Route to appropriate model based on task type
        
        Args:
            task: Task type ('synthesis', 'search_query', 'simple', 'json')
            prompt: The prompt to send
            **kwargs: Additional arguments for generate()
            
        Returns:
            Generated response
        """
        # Task to model mapping
        task_mapping = {
            'synthesis': ModelType.PRO,        # Complex reasoning
            'analysis': ModelType.PRO,         # Deep analysis
            'planning': ModelType.FLASH,       # Medium complexity
            'search_query': ModelType.FLASH_LITE,  # Simple, fast
            'simple': ModelType.FLASH_LITE,      # Basic tasks
            'generation': ModelType.PRO,       # Content generation (MVP files) - Pro for large context
        }
        
        model_type = task_mapping.get(task, ModelType.FLASH)
        
        return self.client.generate(
            prompt=prompt,
            model_type=model_type,
            **kwargs
        )
    
    def route_json(self, task: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Route to appropriate model for JSON generation

        Args:
            task: Task type
            prompt: The prompt to send
            **kwargs: Additional arguments

        Returns:
            Parsed JSON response
        """
        task_mapping = {
            'synthesis': ModelType.PRO,        # Complex reasoning
            'analysis': ModelType.PRO,         # Deep analysis
            'planning': ModelType.FLASH,       # Medium complexity
            'search_query': ModelType.FLASH_LITE,  # Simple, fast
            'simple': ModelType.FLASH_LITE,      # Basic tasks
            'generation': ModelType.PRO,       # Content generation (MVP files) - Pro for large context
        }

        model_type = task_mapping.get(task, ModelType.FLASH)

        return self.client.generate_json(
            prompt=prompt,
            model_type=model_type,
            **kwargs
        )


# Convenience function
def create_client(api_key: Optional[str] = None) -> GeminiClient:
    """
    Create a new Gemini client
    
    Args:
        api_key: Optional API key
        
    Returns:
        Configured GeminiClient instance
    """
    return GeminiClient(api_key)
