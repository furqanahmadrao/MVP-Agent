"""
Settings Manager
Handles application configuration, API keys, and user preferences.
Persists settings to local storage (or .env for CLI).
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SETTINGS_FILE = Path("user_settings.json")

class SettingsManager:
    """
    Manages application settings, blending environment variables
    with user-defined local settings.
    """
    
    def __init__(self):
        self.settings: Dict[str, Any] = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults."""
        defaults = {
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "model_name": "gemini-2.5-flash",  # Default model
            "use_toon_format": True,
            "project_level_auto_detect": True,
            "language": "English",
            "theme": "Dark"
        }
        
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        return defaults

    def save_settings(self, new_settings: Dict[str, Any]):
        """Update and save settings to file."""
        self.settings.update(new_settings)
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_api_key(self) -> Optional[str]:
        """Get Gemini API key (user setting takes precedence over env)."""
        key = self.settings.get("gemini_api_key")
        if not key:
            key = os.getenv("GEMINI_API_KEY")
        return key

    def get_model(self) -> str:
        """Get selected Gemini model."""
        return self.settings.get("model_name", "gemini-2.5-flash")

    def use_toon(self) -> bool:
        """Check if TOON format is enabled."""
        return self.settings.get("use_toon_format", True)

# Global instance
_settings_manager = None

def get_settings_mgr() -> SettingsManager:
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def create_settings_ui():
    """Create Gradio UI components for settings (imported in app.py)."""
    import gradio as gr
    
    mgr = get_settings_mgr()
    
    with gr.Column():
        gr.Markdown("## ⚙️ Application Settings")
        
        api_key_input = gr.Textbox(
            label="Gemini API Key",
            value=mgr.get_api_key(),
            type="password",
            placeholder="AIzaSy...",
            info="Your key is stored locally. Leave empty to use env var."
        )
        
        model_dropdown = gr.Dropdown(
            choices=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash-lite"],
            label="AI Model",
            value=mgr.get_model(),
            info="Pro for quality, Flash for speed."
        )
        
        with gr.Row():
            toon_checkbox = gr.Checkbox(
                label="Use TOON Format",
                value=mgr.use_toon(),
                info="Reduces token usage by ~40% (Recommended)"
            )
            auto_level_checkbox = gr.Checkbox(
                label="Auto-Detect Project Level",
                value=mgr.settings.get("project_level_auto_detect", True),
                info="Automatically determine complexity (Level 0-4)"
            )
            
        save_btn = gr.Button("💾 Save Settings", variant="primary")
        status_msg = gr.Markdown("")
        
        def save(key, model, toon, auto_level):
            mgr.save_settings({
                "gemini_api_key": key,
                "model_name": model,
                "use_toon_format": toon,
                "project_level_auto_detect": auto_level
            })
            return "✅ Settings saved successfully!"
            
        save_btn.click(
            save,
            inputs=[api_key_input, model_dropdown, toon_checkbox, auto_level_checkbox],
            outputs=[status_msg]
        )