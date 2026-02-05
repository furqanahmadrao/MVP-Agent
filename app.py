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

# Custom CSS for modern "Code Editor" look - Enhanced version with improved UX
CUSTOM_CSS = """
:root {
    --primary-orange: #FF6B35;
    --primary-orange-hover: #ff8555;
    --secondary-blue: #4A90E2;
    --dark-bg: #1a1a1a;
    --editor-bg: #1e1e1e;
    --sidebar-bg: #252526;
    --card-bg: #2a2d2e;
    --text-white: #ffffff;
    --text-gray: #cccccc;
    --text-muted: #808080;
    --border-color: #3e3e42;
    --success-green: #89d185;
    --warning-yellow: #e5c07b;
    --error-red: #f48771;
    --info-blue: #61afef;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.4);
}

* {
    transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.gradio-container {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Header styling with animated gradient */
.header-container {
    background: linear-gradient(135deg, var(--primary-orange), var(--secondary-blue), #9b59b6);
    background-size: 200% 200%;
    animation: gradientShift 10s ease infinite;
    padding: 25px 30px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.header-container h1 {
    color: white;
    font-weight: 700;
    margin: 0;
    font-size: 2em;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.header-container p {
    color: rgba(255, 255, 255, 0.95);
    margin-top: 8px;
    font-size: 1.05em;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

/* Sidebar styling with improved visual hierarchy */
.sidebar-container {
    background: linear-gradient(180deg, var(--sidebar-bg) 0%, rgba(37, 37, 38, 0.95) 100%);
    border-right: 1px solid var(--border-color);
    padding: 18px;
    height: 100%;
    border-radius: 10px;
    box-shadow: inset -2px 0 8px rgba(0, 0, 0, 0.2);
}

.file-btn {
    background: transparent !important;
    border: none !important;
    color: var(--text-gray) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
    width: 100% !important;
    border-radius: 6px !important;
    font-size: 0.95em !important;
    cursor: pointer !important;
    position: relative !important;
}

.file-btn:hover {
    background-color: rgba(42, 45, 46, 0.8) !important;
    color: var(--text-white) !important;
    transform: translateX(4px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.file-btn.selected {
    background: linear-gradient(90deg, rgba(255, 107, 53, 0.15) 0%, rgba(255, 107, 53, 0.05) 100%) !important;
    color: var(--text-white) !important;
    border-left: 4px solid var(--primary-orange) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(255, 107, 53, 0.2);
}

/* Status Terminal with enhanced readability */
#terminal-log {
    background: linear-gradient(180deg, #1a1a1a 0%, #1e1e1e 100%);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    padding: 16px;
    height: 250px;
    overflow-y: auto;
    color: #d4d4d4;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
    position: relative;
}

#terminal-log::-webkit-scrollbar {
    width: 10px;
}

#terminal-log::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 5px;
}

#terminal-log::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 5px;
}

#terminal-log::-webkit-scrollbar-thumb:hover {
    background: var(--primary-orange);
}

.log-info { color: var(--info-blue); font-weight: 500; }
.log-error { color: var(--error-red); font-weight: 600; }
.log-success { color: var(--success-green); font-weight: 500; }
.log-warning { color: var(--warning-yellow); font-weight: 500; }

.log-entry {
    margin-bottom: 6px;
    line-height: 1.6;
    padding: 4px 0;
    border-left: 2px solid transparent;
    padding-left: 8px;
    animation: fadeIn 0.3s ease-in;
}

.log-entry:hover {
    background-color: rgba(255, 255, 255, 0.03);
    border-left-color: var(--primary-orange);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Main Generate Button with enhanced effects */
#generate-btn {
    background: linear-gradient(135deg, var(--primary-orange), #ff8c42) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    padding: 16px 35px !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 6px 12px rgba(255, 107, 53, 0.4), 0 0 20px rgba(255, 107, 53, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

#generate-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

#generate-btn:hover::before {
    left: 100%;
}

#generate-btn:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 20px rgba(255, 107, 53, 0.5), 0 0 30px rgba(255, 107, 53, 0.3);
}

#generate-btn:active {
    transform: translateY(-1px) scale(0.98);
}

#generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
}

/* File badge indicators with improved styling */
.file-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 10px;
    font-weight: 700;
    margin-left: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}

.badge-analysis {
    background: linear-gradient(135deg, var(--secondary-blue), #5ba3ef);
    color: white;
}
.badge-planning {
    background: linear-gradient(135deg, var(--success-green), #9fdd9b);
    color: #1a1a1a;
}
.badge-solution {
    background: linear-gradient(135deg, var(--warning-yellow), #f0d393);
    color: #1a1a1a;
}
.badge-implementation {
    background: linear-gradient(135deg, var(--primary-orange), #ff8555);
    color: white;
}

/* Phase indicator with enhanced animations */
.phase-indicator {
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
    padding: 20px;
    background: linear-gradient(135deg, var(--sidebar-bg), rgba(37, 37, 38, 0.8));
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow);
}

.phase-step {
    text-align: center;
    padding: 15px;
    border-radius: 10px;
    min-width: 110px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 2px solid transparent;
    position: relative;
}

.phase-step::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 3px;
    background: var(--primary-orange);
    transition: width 0.4s ease;
}

.phase-step.active {
    background: linear-gradient(135deg, var(--primary-orange), #ff8555);
    color: white;
    transform: scale(1.1);
    box-shadow: 0 8px 16px rgba(255, 107, 53, 0.4);
    border-color: rgba(255, 255, 255, 0.3);
    animation: phaseGlow 2s infinite;
}

.phase-step.active::after {
    width: 100%;
}

@keyframes phaseGlow {
    0%, 100% { box-shadow: 0 8px 16px rgba(255, 107, 53, 0.4); }
    50% { box-shadow: 0 8px 24px rgba(255, 107, 53, 0.6); }
}

.phase-step.completed {
    background: linear-gradient(135deg, var(--success-green), #9fdd9b);
    color: #1a1a1a;
    transform: scale(1.02);
    border-color: var(--success-green);
}

.phase-step.completed::before {
    content: '✓';
    position: absolute;
    top: 5px;
    right: 5px;
    font-size: 14px;
    font-weight: bold;
}

.phase-step.pending {
    background: rgba(42, 45, 46, 0.5);
    color: var(--text-gray);
    opacity: 0.7;
}

.phase-step:hover:not(.pending) {
    transform: scale(1.05);
}

/* Card styling for better organization */
.info-card {
    background: linear-gradient(135deg, var(--card-bg), rgba(42, 45, 46, 0.8));
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: rgba(255, 107, 53, 0.3);
}

.info-card h3 {
    color: var(--primary-orange);
    margin-top: 0;
    font-size: 1.3em;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}

.info-card ul {
    list-style: none;
    padding-left: 0;
}

.info-card li {
    padding: 8px 0;
    padding-left: 28px;
    position: relative;
    line-height: 1.6;
}

.info-card li::before {
    content: '▸';
    position: absolute;
    left: 8px;
    color: var(--primary-orange);
    font-weight: bold;
}

/* Progress bar with enhanced visuals */
.progress-container {
    background: linear-gradient(90deg, rgba(30, 30, 30, 0.8), rgba(42, 45, 46, 0.6));
    border-radius: 12px;
    overflow: hidden;
    height: 32px;
    margin: 18px 0;
    border: 1px solid var(--border-color);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.progress-bar {
    background: linear-gradient(90deg, var(--primary-orange), var(--secondary-blue), #9b59b6);
    background-size: 200% 100%;
    height: 100%;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 13px;
    animation: progressShine 2s linear infinite;
    box-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
}

@keyframes progressShine {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

/* Responsive design for mobile/tablet */
@media (max-width: 768px) {
    .header-container h1 {
        font-size: 1.5em;
    }

    .phase-indicator {
        flex-wrap: wrap;
        gap: 10px;
    }

    .phase-step {
        min-width: 80px;
        padding: 10px;
    }

    #generate-btn {
        font-size: 15px !important;
        padding: 14px 28px !important;
    }

    .info-card {
        padding: 15px;
    }
}

@media (max-width: 480px) {
    .header-container {
        padding: 18px 20px;
    }

    .header-container h1 {
        font-size: 1.3em;
    }

    .sidebar-container {
        padding: 12px;
    }

    #terminal-log {
        height: 180px;
        font-size: 12px;
    }
}

/* Smooth scroll behavior */
html {
    scroll-behavior: smooth;
}

/* Enhanced tab styling */
.tabs button {
    transition: all 0.3s ease;
}

.tabs button:hover {
    transform: translateY(-2px);
}

.tabs button.selected {
    box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
}

/* Input field enhancements */
textarea, input[type="text"], input[type="number"] {
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
    background-color: var(--editor-bg) !important;
    color: var(--text-white) !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
}

textarea:focus, input:focus {
    border-color: var(--primary-orange) !important;
    box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    outline: none !important;
}

/* Code editor enhancements */
.code-container {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-color);
}

/* Accordion enhancements */
.accordion {
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--card-bg) !important;
}

.accordion summary {
    padding: 12px 16px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.accordion summary:hover {
    background: rgba(255, 107, 53, 0.1) !important;
}

/* Button enhancements for secondary buttons */
button[variant="secondary"] {
    background: linear-gradient(135deg, var(--sidebar-bg), var(--card-bg)) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-white) !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

button[variant="secondary"]:hover {
    background: linear-gradient(135deg, var(--card-bg), var(--sidebar-bg)) !important;
    border-color: var(--primary-orange) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(255, 107, 53, 0.2);
}

/* Loading spinner animation */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-spinner {
    animation: spin 1s linear infinite;
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
        "financial_model.md": "",
        "prd.md": "",
        "tech_spec.md": "",
        "feature_prioritization.md": "",
        "competitive_analysis.md": "",
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
    
    # Initialize workflow with session_id for real-time updates
    workflow = create_workflow(api_key=api_key, session_id=session_id)
    
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
            "financial_model.md": final_state.get("business_model", ""),
            "prd.md": final_state.get("prd", ""),
            "tech_spec.md": final_state.get("tech_spec", ""),
            "feature_prioritization.md": final_state.get("feature_prioritization", ""),
            "competitive_analysis.md": final_state.get("competitive_analysis", ""),
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
with gr.Blocks(css=CUSTOM_CSS, title="MVP Agent v2.0 - BMAD Edition", theme=gr.themes.Base()) as demo:
    
    # State for file content
    current_file = gr.State("overview.md")
    
    # Header
    with gr.Row():
        gr.HTML("""
        <div class="header-container">
            <h1>🤖 MVP Agent v2.0 - BMAD Edition</h1>
            <p>Transform your startup idea into a comprehensive, investor-ready PRD with financial modeling, feature prioritization, and competitive analysis.</p>
        </div>
        """)
    
    with gr.Tabs() as main_tabs:
        # === Generator Tab (moved to first position for better UX) ===
        with gr.Tab("⚡ Generator", id="generator-tab"):
            with gr.Row():
                with gr.Column(scale=2):
                    # Info card about capabilities
                    gr.HTML("""
                    <div class="info-card">
                        <h3>✨ What You'll Get</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li><strong>13 Professional Documents</strong> - Complete PRD package</li>
                            <li><strong>Financial Modeling</strong> - Revenue projections, CAC/LTV, burn rate</li>
                            <li><strong>Feature Prioritization</strong> - RICE scores, value vs. effort matrix</li>
                            <li><strong>Competitive Analysis</strong> - Side-by-side feature comparison</li>
                            <li><strong>Technical Architecture</strong> - System design, tech stack, APIs</li>
                            <li><strong>6-Week Roadmap</strong> - Sprint-by-sprint implementation plan</li>
                        </ul>
                    </div>
                    """)
                    
                    idea_input = gr.Textbox(
                        label="💡 What do you want to build?",
                        placeholder="Example: An AI-powered meal planning app for busy professionals that suggests personalized recipes based on dietary preferences, automates grocery shopping, and tracks nutrition goals.",
                        lines=6,
                        info="Be specific! Include target users, problem you're solving, and key features."
                    )
                    
                    with gr.Accordion("⚙️ Advanced Options", open=False):
                        project_level = gr.Slider(
                            minimum=0, 
                            maximum=4, 
                            step=1, 
                            value=2, 
                            label="Project Complexity Level",
                            info="0=Prototype, 1=Small, 2=Medium (recommended), 3=Large, 4=Enterprise"
                        )
                        gr.Markdown("""
                        **Complexity Levels:**
                        - **Level 0 (Prototype)**: Minimal documentation for quick validation
                        - **Level 1 (Small)**: 1-10 user stories, light PRD
                        - **Level 2 (Medium)**: 5-15 stories, full documentation ⭐ **Recommended**
                        - **Level 3 (Large)**: 12-40 stories, comprehensive planning
                        - **Level 4 (Enterprise)**: 40+ stories, full governance
                        """)
                    
                    generate_btn = gr.Button(
                        "🚀 Generate Complete Blueprint", 
                        variant="primary", 
                        elem_id="generate-btn",
                        size="lg"
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📟 Mission Control")
                    gr.HTML("""
                    <div class="phase-indicator">
                        <div class="phase-step pending">
                            <div style="font-size: 24px;">🔬</div>
                            <div>Analysis</div>
                        </div>
                        <div class="phase-step pending">
                            <div style="font-size: 24px;">📋</div>
                            <div>Planning</div>
                        </div>
                        <div class="phase-step pending">
                            <div style="font-size: 24px;">🏗️</div>
                            <div>Solution</div>
                        </div>
                        <div class="phase-step pending">
                            <div style="font-size: 24px;">🚀</div>
                            <div>Implementation</div>
                        </div>
                    </div>
                    """)
                    status_html = gr.HTML(elem_id="terminal-log")
                    editor_link = gr.HTML("")
        
        # === Code Editor Tab ===
        with gr.Tab("💻 Code Editor", id="editor-tab"):
            gr.Markdown("""
            ### 📂 Project Explorer
            Browse and edit your generated documents. All files are organized by phase following the BMAD methodology.
            """)
            
            with gr.Row():
                # Sidebar with organized file tree
                with gr.Column(scale=1, min_width=250, elem_classes="sidebar-container"):
                    gr.Markdown("""
                    <div style="background: linear-gradient(135deg, rgba(74, 144, 226, 0.2), rgba(74, 144, 226, 0.05));
                                padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;
                                border-left: 3px solid #4A90E2;">
                        <strong style="color: #4A90E2;">📁 Phase 1: Analysis</strong>
                    </div>
                    """)
                    gr.Markdown("""
                    <div style="padding-left: 10px; margin-bottom: 15px;">
                    📄 product_brief.md <span class="file-badge badge-analysis">Research</span><br>
                    💰 financial_model.md <span class="file-badge badge-analysis">Finance</span>
                    </div>
                    """)

                    gr.Markdown("""
                    <div style="background: linear-gradient(135deg, rgba(137, 209, 133, 0.2), rgba(137, 209, 133, 0.05));
                                padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;
                                border-left: 3px solid #89d185;">
                        <strong style="color: #89d185;">📁 Phase 2: Planning</strong>
                    </div>
                    """)
                    gr.Markdown("""
                    <div style="padding-left: 10px; margin-bottom: 15px;">
                    📋 prd.md <span class="file-badge badge-planning">Core</span><br>
                    🛠️ tech_spec.md <span class="file-badge badge-planning">Tech</span><br>
                    ⭐ feature_prioritization.md <span class="file-badge badge-planning">Priority</span><br>
                    🏆 competitive_analysis.md <span class="file-badge badge-planning">Market</span>
                    </div>
                    """)

                    gr.Markdown("""
                    <div style="background: linear-gradient(135deg, rgba(229, 192, 123, 0.2), rgba(229, 192, 123, 0.05));
                                padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;
                                border-left: 3px solid #e5c07b;">
                        <strong style="color: #e5c07b;">📁 Phase 3: Solution</strong>
                    </div>
                    """)
                    gr.Markdown("""
                    <div style="padding-left: 10px; margin-bottom: 15px;">
                    🏗️ architecture.md <span class="file-badge badge-solution">System</span><br>
                    👤 user_flow.md <span class="file-badge badge-solution">UX</span><br>
                    🎨 design_system.md <span class="file-badge badge-solution">Design</span>
                    </div>
                    """)

                    gr.Markdown("""
                    <div style="background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(255, 107, 53, 0.05));
                                padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;
                                border-left: 3px solid #FF6B35;">
                        <strong style="color: #FF6B35;">📁 Phase 4: Implementation</strong>
                    </div>
                    """)
                    gr.Markdown("""
                    <div style="padding-left: 10px; margin-bottom: 15px;">
                    📅 roadmap.md <span class="file-badge badge-implementation">Sprint</span><br>
                    ✅ testing_plan.md <span class="file-badge badge-implementation">QA</span><br>
                    🚀 deployment_guide.md <span class="file-badge badge-implementation">DevOps</span>
                    </div>
                    """)
                    
                    gr.Markdown("---")
                    
                    file_list = gr.Radio(
                        choices=list(generated_content_store.keys()),
                        value="overview.md",
                        label="Select File to View",
                        interactive=True,
                        container=False
                    )
                    
                    gr.Markdown("---")
                    dl_btn = gr.Button("⬇️ Download Complete Package (ZIP)", size="sm", variant="secondary")
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


        # === Settings Tab ===
        with gr.Tab("⚙️ Settings"):
            gr.Markdown("""
            ### 🔑 API Configuration
            Configure your Gemini API key and model preferences.
            """)
            create_settings_ui()
            
            gr.Markdown("""
            ---
            ### 📚 Resources
            - [Get Gemini API Key (Free)](https://aistudio.google.com/)
            - [BMAD Method Documentation](https://github.com/bmad-code-org/BMAD-METHOD)
            - [GitHub Spec Kit](https://github.com/github)
            - [Feature Prioritization Guide](https://www.productplan.com/glossary/rice-scoring-model/)
            """)
    
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
