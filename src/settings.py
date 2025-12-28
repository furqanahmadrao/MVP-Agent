"""
Settings Management - MVP Agent v2.0
User-provided API keys, model selection, and configuration
"""

import os
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import gradio as gr
from google import generativeai as genai


class SettingsManager:
    """
    Manage user settings for MVP Agent.
    
    Settings include:
    - Gemini API key (user-provided)
    - Model selection (Pro/Flash/Flash-Lite)
    - TOON format toggle
    - Project level override
    """
    
    def __init__(self, settings_file: str = ".mvp_agent_settings.json"):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings file (relative to workspace)
        """
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Return defaults
        return {
            "api_key": os.getenv("GEMINI_API_KEY", ""),
            "model_name": "gemini-2.5-flash",
            "enable_toon": False,
            "project_level": "auto",  # auto, 0-4
            "show_advanced": False
        }
    
    def _save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                # Don't save API key to file (security)
                settings_to_save = {k: v for k, v in self.settings.items() if k != "api_key"}
                json.dump(settings_to_save, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set setting value"""
        self.settings[key] = value
    
    def get_api_key(self) -> str:
        """Get API key (from settings or env var)"""
        # Priority: settings > env var
        api_key = self.settings.get("api_key", "")
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY", "")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Gemini API key.
        
        Returns:
            (is_valid, message)
        """
        if not api_key or not api_key.strip():
            return False, "API key is empty"
        
        if not api_key.startswith("AIza"):
            return False, "Invalid API key format (should start with 'AIza')"
        
        # Try to use the API key
        try:
            genai.configure(api_key=api_key)
            # Try listing models (lightweight check)
            models = list(genai.list_models())
            if models:
                return True, f"✅ API key valid! Found {len(models)} available models."
            else:
                return False, "API key valid but no models available"
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg:
                return False, "❌ Invalid API key"
            elif "quota" in error_msg.lower():
                return False, "❌ API key valid but quota exceeded"
            else:
                return False, f"❌ Validation failed: {error_msg}"
    
    def get_available_models(self) -> list[str]:
        """Get list of available Gemini models"""
        return [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    
    def get_model_info(self, model_name: str) -> str:
        """Get information about a model"""
        model_info = {
            "gemini-2.5-pro": "🚀 Most capable, best for complex reasoning (2M token context)",
            "gemini-2.5-flash": "⚡ Balanced speed & quality (1M token context) - RECOMMENDED",
            "gemini-2.5-flash-8b": "💨 Fastest, best for simple tasks (1M token context)",
            "gemini-1.5-pro": "🔧 Previous generation Pro (2M token context)",
            "gemini-1.5-flash": "🔧 Previous generation Flash (1M token context)"
        }
        return model_info.get(model_name, "")
    
    def save(self) -> Tuple[bool, str]:
        """
        Save settings.
        
        Returns:
            (success, message)
        """
        if self._save_settings():
            return True, "✅ Settings saved successfully!"
        else:
            return False, "❌ Failed to save settings"


# ===== Gradio UI Components =====

def create_settings_ui(settings_manager: SettingsManager) -> gr.Blocks:
    """
    Create Gradio settings UI.
    
    Returns:
        Gradio Blocks component
    """
    
    with gr.Blocks() as settings_ui:
        gr.Markdown("""
        # ⚙️ Settings
        
        Configure your API keys and preferences for MVP Agent.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # API Key Section
                gr.Markdown("### 🔑 API Configuration")
                
                api_key_input = gr.Textbox(
                    label="Gemini API Key",
                    placeholder="AIza... (starts with AIza)",
                    type="password",
                    value=settings_manager.get_api_key(),
                    info="Get your free API key at https://aistudio.google.com/apikey"
                )
                
                with gr.Row():
                    validate_btn = gr.Button("🔍 Validate API Key", variant="secondary")
                    save_btn = gr.Button("💾 Save Settings", variant="primary")
                
                validation_output = gr.Textbox(
                    label="Validation Status",
                    interactive=False,
                    lines=2
                )
                
                # Model Selection
                gr.Markdown("### 🤖 Model Selection")
                
                model_dropdown = gr.Dropdown(
                    choices=settings_manager.get_available_models(),
                    value=settings_manager.get("model_name"),
                    label="Gemini Model",
                    info="Choose the model for PRD generation"
                )
                
                model_info = gr.Markdown(
                    settings_manager.get_model_info(settings_manager.get("model_name"))
                )
                
                # Advanced Options
                with gr.Accordion("🔧 Advanced Options", open=False):
                    enable_toon = gr.Checkbox(
                        label="Enable TOON Format (30-60% token reduction)",
                        value=settings_manager.get("enable_toon"),
                        info="Use TOON format for internal agent communication (experimental)"
                    )
                    
                    project_level = gr.Radio(
                        choices=["auto", "0", "1", "2", "3", "4"],
                        value=str(settings_manager.get("project_level")),
                        label="Project Complexity Level",
                        info="Auto-detect or manually set (0=Prototype, 2=Medium, 4=Enterprise)"
                    )
            
            with gr.Column(scale=1):
                # Info Panel
                gr.Markdown("""
                ### 📖 Quick Guide
                
                **API Key:**
                - Get free API key from [Google AI Studio](https://aistudio.google.com/apikey)
                - Free tier: 15 RPM, 1M tokens/day
                - Valid until Jan 5, 2026 (then paid)
                
                **Models:**
                - **Pro**: Best quality, slower
                - **Flash**: Recommended (balanced)
                - **Flash-8B**: Fastest, simpler
                
                **TOON Format:**
                - 30-60% token savings
                - Used for agent-to-agent data
                - User docs stay in Markdown
                
                **Project Levels:**
                - **0**: Prototype (1 story)
                - **1**: Small (1-10 stories)
                - **2**: Medium (5-15 stories) ⭐
                - **3**: Large (12-40 stories)
                - **4**: Enterprise (40+ stories)
                """)
                
                gr.Markdown("""
                ### 💡 Tips
                
                1. **First time?** Use default Flash model
                2. **Complex project?** Try Pro model
                3. **Save often** to preserve settings
                4. **Validate key** before generating
                """)
        
        # Event Handlers
        
        def validate_api_key(api_key: str) -> str:
            """Validate API key and return status"""
            is_valid, message = settings_manager.validate_api_key(api_key)
            return message
        
        def save_settings(api_key: str, model: str, toon: bool, level: str) -> str:
            """Save all settings"""
            settings_manager.set("api_key", api_key)
            settings_manager.set("model_name", model)
            settings_manager.set("enable_toon", toon)
            settings_manager.set("project_level", level)
            
            success, message = settings_manager.save()
            return message
        
        def update_model_info(model: str) -> str:
            """Update model info when selection changes"""
            return settings_manager.get_model_info(model)
        
        # Connect events
        validate_btn.click(
            fn=validate_api_key,
            inputs=[api_key_input],
            outputs=[validation_output]
        )
        
        save_btn.click(
            fn=save_settings,
            inputs=[api_key_input, model_dropdown, enable_toon, project_level],
            outputs=[validation_output]
        )
        
        model_dropdown.change(
            fn=update_model_info,
            inputs=[model_dropdown],
            outputs=[model_info]
        )
    
    return settings_ui


# ===== Standalone Test =====

if __name__ == "__main__":
    # Test settings UI
    settings_mgr = SettingsManager()
    ui = create_settings_ui(settings_mgr)
    ui.launch(share=False, server_name="0.0.0.0", server_port=7860)
