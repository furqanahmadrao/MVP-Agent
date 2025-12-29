# MVP Agent v2.0 - BMAD Edition
# Production-ready AI Agent for generating comprehensive PRDs

import gradio as gr
import os
import time
import threading
from dotenv import load_dotenv
from typing import Dict, List, Any
from pathlib import Path

# Import new architecture modules
from src.workflow import create_workflow, MVPAgentWorkflow
from src.settings import get_settings_mgr, create_settings_ui
from src.agent_state import AgentState
from src.file_manager import get_file_manager

# Load environment variables
load_dotenv()

# Custom CSS for modern "Code Editor" look
CUSTOM_CSS = """
:root {
    --primary-orange: #FF6B35;
    --dark-bg: #1e1e1e;
    --editor-bg: #1e1e1e;
    --sidebar-bg: #252526;
    --text-white: #ffffff;
    --text-gray: #cccccc;
    --border-color: #3e3e42;
}

.gradio-container {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
}

/* Sidebar styling */
.sidebar-container {
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
    padding: 10px;
    height: 100%;
}

.file-btn {
    background: transparent !important;
    border: none !important;
    color: var(--text-gray) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 5px 10px !important;
    margin-bottom: 2px !important;
    width: 100% !important;
}

.file-btn:hover {
    background-color: #2a2d2e !important;
    color: var(--text-white) !important;
}

.file-btn.selected {
    background-color: #37373d !important;
    color: var(--text-white) !important;
    border-left: 3px solid var(--primary-orange) !important;
}

/* Status Terminal */
#terminal-log {
    background-color: #1e1e1e;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    padding: 10px;
    height: 200px;
    overflow-y: auto;
    color: #d4d4d4;
}

.log-info { color: #569cd6; }
.log-error { color: #f48771; }
.log-success { color: #89d185; }
.log-warning { color: #cca700; }

/* Main Generate Button */
#generate-btn {
    background: var(--primary-orange) !important;
    color: white !important;
    font-weight: bold;
}
"""

def format_log_entries(log_events: List[Dict]) -> str:
    """Format status history as HTML for the terminal view."""
    html_log = ""
    for event in log_events:
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.get("timestamp", time.time())))
        msg_type = event.get("type", "INFO").lower()
        message = event.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
        
        color_class = f"log-{msg_type}"
        html_log += f"<div class='log-entry'><span style='color:#808080'>[{timestamp}]</span> <span class='{color_class}'>{message}</span></div>"
    
    # Auto-scroll script
    return f"""
    <div id='terminal-content'>
        {html_log}
    </div>
    <script>
        var terminal = document.getElementById('terminal-log');
        if(terminal) terminal.scrollTop = terminal.scrollHeight;
    </script>
    """

def get_empty_state_files() -> Dict[str, str]:
    return {
        "overview.md": "# Project Overview\n\nGenerated content will appear here.",
        "product_brief.md": "",
        "prd.md": "",
        "architecture.md": "",
        "user_flow.md": "",
        "design_system.md": "",
        "roadmap.md": "",
        "testing_plan.md": "",
        "deployment_guide.md": ""
    }

# Global state to hold generated content
generated_content_store = get_empty_state_files()

def run_generation(idea: str, project_level: int):
    """
    Main generator function called by the button.
    Yields updates to the UI.
    """
    settings = get_settings_mgr()
    api_key = settings.get_api_key()
    
    if not api_key:
        yield {
            "status_html": "<div class='log-error'>❌ Error: Gemini API Key not found. Please set it in the Settings tab.</div>",
            "generate_btn": gr.Button(interactive=True)
        }
        return

    # Initialize workflow
    workflow = create_workflow(api_key=api_key)
    
    # State container for the thread
    thread_state = {"done": False, "final_state": None, "error": None}
    
    # Update initial UI
    yield {
        "status_html": "<div class='log-info'>🚀 Starting MVP Agent v2.0...</div>",
        "generate_btn": gr.Button(interactive=False),
        "main_tabs": gr.Tabs(selected="editor-tab")
    }
    
def worker():
        try:
            # Run the synchronous workflow
            result = workflow.run(idea=idea, api_key=api_key)
            thread_state["final_state"] = result
        except Exception as e:
            thread_state["error"] = str(e)
        finally:
            thread_state["done"] = True

    t = threading.Thread(target=worker)
    t.start()
    
    # Polling loop
    logs = []
    while not thread_state["done"]:
        # In a real LangGraph implementation with streaming, we'd pull logs here.
        # Since our current implementation is synchronous inside run(), 
        # we simulated status updates in the agent_state but can't easily poll them 
        # without a shared reference or async streaming.
        # For this version, we'll show a "Working..." animation or simulated logs.
        
        # NOTE: A fully async LangGraph implementation would allow real-time event streaming.
        # For now, we wait.
        logs.append({"timestamp": time.time(), "message": "Agents are working... (Analysis -> Planning -> Solutioning)", "type": "INFO"})
        yield {
            "status_html": format_log_entries(logs)
        }
        time.sleep(2)
        
    # Handle completion
    if thread_state["error"]:
        logs.append({"timestamp": time.time(), "message": f"Error: {thread_state['error']}", "type": "ERROR"})
        yield {
            "status_html": format_log_entries(logs),
            "generate_btn": gr.Button(interactive=True)
        }
    else:
        final_state = thread_state["final_state"]
        
        # Populate global store
        global generated_content_store
        generated_content_store = {
            "overview.md": final_state.get("overview", ""),
            "product_brief.md": final_state.get("product_brief", ""),
            "prd.md": final_state.get("prd", ""),
            "architecture.md": final_state.get("architecture", ""),
            "user_flow.md": final_state.get("user_flow", ""),
            "design_system.md": final_state.get("design_system", ""),
            "roadmap.md": final_state.get("roadmap", ""),
            "testing_plan.md": final_state.get("testing_plan", ""),
            "deployment_guide.md": final_state.get("deployment_guide", "")
        }
        
        # Save files using file manager
        file_mgr = get_file_manager()
        file_mgr.save_mvp_files(generated_content_store, idea)
        
        # Get logs from state
        history = final_state.get("status_history", [])
        
        yield {
            "status_html": format_log_entries(history),
            "generate_btn": gr.Button(interactive=True),
            # Update editor with overview
            "code_editor": generated_content_store["overview.md"],
            "file_list": gr.Radio(choices=list(generated_content_store.keys()), value="overview.md")
        }

def load_file_content(filename: str):
    """Load content into the editor when a file is selected."""
    return generated_content_store.get(filename, "")

def download_zip():
    """Create ZIP and return path."""
    file_mgr = get_file_manager()
    # Assuming files were already saved during generation
    # We can trigger a re-zip or just point to the latest
    # For simplicity, we'll implement a basic zip creation here if needed
    # but the File Manager already handles it.
    # We'll just return the path to the expected zip file.
    # In a robust app, we'd track the specific run ID.
    return "outputs/mvp_package.zip"

# Build UI
with gr.Blocks(css=CUSTOM_CSS, title="MVP Agent v2.0", theme=gr.themes.Base()) as demo:
    
    # State for file content
    current_file = gr.State("overview.md")
    
    with gr.Row():
        gr.Markdown("# 🤖 MVP Agent v2.0 - BMAD Edition")
    
    with gr.Tabs() as main_tabs:
        # === Editor Tab ===
        with gr.Tab("💻 Code Editor", id="editor-tab"):
            with gr.Row():
                # Sidebar
                with gr.Column(scale=1, min_width=200, elem_classes="sidebar-container"):
                    gr.Markdown("### 📂 Explorer")
                    file_list = gr.Radio(
                        choices=list(generated_content_store.keys()),
                        value="overview.md",
                        label="Project Files",
                        interactive=True,
                        container=False
                    )
                    
                    gr.Markdown("---")
                    dl_btn = gr.Button("⬇️ Download ZIP", size="sm")
                    zip_out = gr.File(label="Download", visible=False)

                # Main Editor Area
                with gr.Column(scale=4):
                    code_editor = gr.Code(
                        value=generated_content_store["overview.md"],
                        language="markdown",
                        label="overview.md",
                        interactive=True, # Allow user to edit text
                        lines=25
                    )

        # === Generator Tab ===
        with gr.Tab("⚡ Generator", id="generator-tab"):
            with gr.Row():
                with gr.Column(scale=2):
                    idea_input = gr.Textbox(
                        label="What do you want to build?",
                        placeholder="Describe your startup idea...",
                        lines=5
                    )
                    with gr.Accordion("Advanced Options", open=False):
                        project_level = gr.Slider(minimum=0, maximum=4, step=1, value=2, label="Project Complexity (Level)")
                    
                    generate_btn = gr.Button("🚀 Generate Blueprint", variant="primary", elem_id="generate-btn")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📟 Mission Control")
                    status_html = gr.HTML(elem_id="terminal-log")

        # === Settings Tab ===
        with gr.Tab("⚙️ Settings"):
            create_settings_ui()

    # Event Wiring
    
    # 1. File Selection
    file_list.change(
        fn=load_file_content,
        inputs=[file_list],
        outputs=[code_editor]
    )
    
    # 2. Generation
    generate_btn.click(
        fn=run_generation,
        inputs=[idea_input, project_level],
        outputs=[status_html, generate_btn, main_tabs, code_editor, file_list]
    )
    
    # 3. Download
    dl_btn.click(
        fn=download_zip,
        inputs=[],
        outputs=[zip_out]
    ).then(
        fn=lambda: gr.File(visible=True),
        outputs=[zip_out]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
