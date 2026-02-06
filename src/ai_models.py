"""
AI Models Module
Handles interactions with Google Gemini API, including native Search Grounding.
"""

import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain_google_genai import ChatGoogleGenerativeAI
from .settings import get_settings_mgr

class ModelType:
    FLASH_LITE = "gemini-2.0-flash-lite"
    FLASH = "gemini-2.5-flash"
    PRO = "gemini-2.5-pro"

class GeminiClient:
    """
    Wrapper for Google Gemini API with support for:
    - Native Search Grounding
    - LangChain integration
    - Token usage tracking
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.settings = get_settings_mgr()
        self.api_key = api_key or self.settings.get_api_key()
        
        if not self.api_key:
            raise ValueError("Gemini API Key not found. Please set it in Settings or environment variables.")
            
        genai.configure(api_key=self.api_key)
        
        # Track token usage session-wide
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    def get_model(self, model_name: str = None, tools: list = None):
        """Get a configured generative model instance."""
        model_name = model_name or self.settings.get_model()
        
        return genai.GenerativeModel(
            model_name=model_name,
            tools=tools
        )

    def generate_with_grounding(self, prompt: str, model_name: str = None, timeout: int = 120) -> Dict[str, Any]:
        """
        Generate content with Google Search grounding.
        
        Args:
            prompt: The prompt to send to the model
            model_name: Optional model name override
            timeout: Maximum time to wait for response in seconds (default: 120)
            
        Returns:
            Dictionary containing text, grounding_metadata, and citations
        """
        model_name = model_name or self.settings.get_model()
        
        # Configure tool for Google Search
        tools = [{"google_search": {}}]
        model = self.get_model(model_name, tools=tools)
        
        try:
            import concurrent.futures
            
            # Run generation in a thread pool with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                try:
                    response = future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    raise Exception(f"Gemini API request timed out after {timeout}s")
            
            # Extract usage metadata if available
            if response.usage_metadata:
                self._update_usage(response.usage_metadata)

            result = {
                "text": response.text,
                "grounding_metadata": None,
                "citations": []
            }
            
            # Extract grounding metadata
            if response.candidates and response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                result["grounding_metadata"] = metadata
                
                # Format citations for easy display
                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            result["citations"].append({
                                "title": chunk.web.title,
                                "uri": chunk.web.uri
                            })
                            
            return result
            
        except Exception as e:
            print(f"Error in generate_with_grounding: {e}")
            raise

    def get_langchain_model(self, model_name: str = None, temperature: float = 0.7):
        """
        Get a LangChain-compatible ChatGoogleGenerativeAI instance.
        """
        model_name = model_name or self.settings.get_model()
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            convert_system_message_to_human=True
        )

    def _update_usage(self, usage_metadata):
        """Update internal token usage counter."""
        self.token_usage["prompt_tokens"] += usage_metadata.prompt_token_count
        self.token_usage["completion_tokens"] += usage_metadata.candidates_token_count
        self.token_usage["total_tokens"] += usage_metadata.total_token_count

    def get_token_usage(self) -> int:
        return self.token_usage["total_tokens"]

class ModelRouter:
    """
    Routes tasks to the appropriate model (Pro vs Flash vs Flash-Lite).
    """
    def __init__(self, client: GeminiClient):
        self.client = client

    def route(self, task: str, prompt: str, tools: list = None) -> Any:
        # Simple routing logic - can be expanded
        if task == "generation":
            model = ModelType.PRO
        elif task == "research":
            model = ModelType.FLASH
        else:
            model = ModelType.FLASH_LITE
            
        # Implementation details handled by client
        return self.client.generate_with_grounding(prompt, model_name=model)