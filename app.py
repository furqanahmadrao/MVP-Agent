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
from src.generation_state import get_state_manager
from src.editor_page import create_editor_interface

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
    Yields updates to the UI and creates a new generation session.
    """
    settings = get_settings_mgr()
    api_key = settings.get_api_key()
    
    if not api_key:
        yield {
            "status_html": "<div class='log-error'>❌ Error: Gemini API Key not found. Please set it in the Settings tab.</div>",
            "generate_btn": gr.Button(interactive=True),
            "editor_link": gr.HTML("")
        }
        return

    # Create a new generation session
    state_mgr = get_state_manager()
    session_id = state_mgr.create_session(idea)
    
    # Initialize workflow
    workflow = create_workflow(api_key=api_key)
    
    # State container for the thread
    thread_state = {"done": False, "final_state": None, "error": None, "session_id": session_id}
    
    # Update initial UI and show link to editor page
    editor_url = f"http://localhost:7860/editor"  # This will be the editor page URL
    yield {
        "status_html": "<div class='log-info'>🚀 Starting MVP Agent v2.0...</div>",
        "generate_btn": gr.Button(interactive=False),
        "editor_link": gr.HTML(f"""
            <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #FF6B35;'>
                <p style='color: #89d185; margin: 0 0 10px 0; font-weight: bold;'>✅ Generation started!</p>
                <p style='color: #cccccc; margin: 0 0 10px 0;'>Open the editor page to watch real-time progress:</p>
                <a href='/editor' target='_blank' style='display: inline-block; background: #FF6B35; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;'>
                    🚀 Open Editor (New Window)
                </a>
                <p style='color: #808080; margin: 10px 0 0 0; font-size: 12px;'>Session ID: {session_id}</p>
            </div>
        """)
    }
    
    state_mgr.update_status(session_id, "running", progress=5)
    state_mgr.add_log(session_id, "🚀 Starting MVP Agent v2.0...", "INFO")
    
    def worker():
        try:
            # Update state as we progress
            state_mgr.add_log(session_id, "🔍 Analyzing idea and detecting project level...", "INFO")
            state_mgr.update_status(session_id, "running", progress=10, phase="Analysis")
            
            # Run the synchronous workflow
            result = workflow.run(idea=idea, api_key=api_key)
            thread_state["final_state"] = result
            
            # Extract and update files as they're generated
            if result:
                state_mgr.update_status(session_id, "running", progress=90, phase="Finalizing")
                
                # Update all files
                files = {
                    "overview.md": result.get("overview", ""),
                    "product_brief.md": result.get("product_brief", ""),
                    "prd.md": result.get("prd", ""),
                    "architecture.md": result.get("architecture", ""),
                    "user_flow.md": result.get("user_flow", ""),
                    "design_system.md": result.get("design_system", ""),
                    "roadmap.md": result.get("roadmap", ""),
                    "testing_plan.md": result.get("testing_plan", ""),
                    "deployment_guide.md": result.get("deployment_guide", "")
                }
                
                # Update state manager with all files
                for filename, content in files.items():
                    if content:
                        state_mgr.update_file(session_id, filename, content)
                
                # Copy logs from workflow to state manager
                for log_entry in result.get("status_history", []):
                    state_mgr.add_log(session_id, log_entry.get("message", ""), log_entry.get("type", "INFO"))
                
                state_mgr.complete_session(session_id, files)
        except Exception as e:
            thread_state["error"] = str(e)
            state_mgr.set_error(session_id, str(e))
        finally:
            thread_state["done"] = True

    t = threading.Thread(target=worker)
    t.start()
    
    # Polling loop - update the main page status
    logs = []
    while not thread_state["done"]:
        # Get logs from state manager
        session = state_mgr.get_session(session_id)
        if session:
            logs = session.logs
        else:
            logs.append({"timestamp": time.time(), "message": "Agents are working... (Analysis -> Planning -> Solutioning)", "type": "INFO"})
        
        yield {
            "status_html": format_log_entries(logs)
        }
        time.sleep(2)
        
    # Handle completion
    if thread_state["error"]:
        yield {
            "status_html": format_log_entries(logs),
            "generate_btn": gr.Button(interactive=True),
            "editor_link": gr.HTML(f"""
                <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #f48771;'>
                    <p style='color: #f48771; margin: 0; font-weight: bold;'>❌ Generation failed</p>
                    <p style='color: #cccccc; margin: 10px 0 0 0;'>Check the logs above for details.</p>
                </div>
            """)
        }
    else:
        final_state = thread_state["final_state"]
        
        # Populate global store (for backward compatibility with old editor tab)
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
            "file_list": gr.Radio(choices=list(generated_content_store.keys()), value="overview.md"),
            "editor_link": gr.HTML(f"""
                <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #89d185;'>
                    <p style='color: #89d185; margin: 0 0 10px 0; font-weight: bold;'>✅ Generation complete!</p>
                    <p style='color: #cccccc; margin: 0 0 10px 0;'>View your generated files in the editor:</p>
                    <a href='/editor' target='_blank' style='display: inline-block; background: #FF6B35; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;'>
                        📝 Open Editor
                    </a>
                </div>
            """)
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
                    
                    # Editor page link (shows after generation starts)
                    editor_link = gr.HTML("")
                
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
        outputs=[status_html, generate_btn, code_editor, file_list, editor_link]
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
    # Create the editor interface
    editor_demo = create_editor_interface()
    
    # Mount both apps using TabbedInterface or manual route mounting
    # Note: Gradio 5.x doesn't have native multi-page routing in Blocks
    # We'll use a workaround with gr.mount_gradio_app if running under FastAPI
    # For standalone mode, we'll just launch the main demo and provide instructions
    
    # Check if we should launch editor only (can be passed as command line arg)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--editor":
        print("Launching Editor interface only...")
        editor_demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
    else:
        # Launch main demo with both interfaces combined
        # Create a combined interface using TabbedInterface for simplicity
        from gradio import TabbedInterface
        
        combined = TabbedInterface(
            [demo, editor_demo],
            ["🏠 Main", "📝 Editor"],
            title="MVP Agent v2.0"
        )
        
        print("=" * 60)
        print("MVP Agent v2.0 - BMAD Edition")
        print("=" * 60)
        print("Main Interface: http://localhost:7860/?__theme=dark")
        print("Editor Interface: Switch to 'Editor' tab after generation")
        print("=" * 60)
        
        combined.launch(server_name="0.0.0.0", server_port=7860)
