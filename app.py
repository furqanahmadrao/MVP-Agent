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

# Custom CSS for modern "Code Editor" look - Enhanced version
CUSTOM_CSS = """
:root {
    --primary-orange: #FF6B35;
    --secondary-blue: #4A90E2;
    --dark-bg: #1e1e1e;
    --editor-bg: #1e1e1e;
    --sidebar-bg: #252526;
    --text-white: #ffffff;
    --text-gray: #cccccc;
    --border-color: #3e3e42;
    --success-green: #89d185;
    --warning-yellow: #cca700;
    --error-red: #f48771;
}

.gradio-container {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
}

/* Header styling */
.header-container {
    background: linear-gradient(135deg, var(--primary-orange), var(--secondary-blue));
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.header-container h1 {
    color: white;
    font-weight: bold;
    margin: 0;
}

.header-container p {
    color: rgba(255, 255, 255, 0.9);
    margin-top: 5px;
}

/* Sidebar styling */
.sidebar-container {
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
    padding: 15px;
    height: 100%;
    border-radius: 8px;
}

.file-btn {
    background: transparent !important;
    border: none !important;
    color: var(--text-gray) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    margin-bottom: 3px !important;
    width: 100% !important;
    border-radius: 4px !important;
    transition: all 0.2s;
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
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    padding: 15px;
    height: 250px;
    overflow-y: auto;
    color: #d4d4d4;
}

.log-info { color: var(--secondary-blue); }
.log-error { color: var(--error-red); }
.log-success { color: var(--success-green); }
.log-warning { color: var(--warning-yellow); }

.log-entry {
    margin-bottom: 4px;
    line-height: 1.5;
}

/* Main Generate Button */
#generate-btn {
    background: linear-gradient(135deg, var(--primary-orange), #ff8c42) !important;
    color: white !important;
    font-weight: bold;
    font-size: 16px !important;
    padding: 15px 30px !important;
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(255, 107, 53, 0.3);
    transition: all 0.3s;
}

#generate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(255, 107, 53, 0.4);
}

#generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* File badge indicators */
.file-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: bold;
    margin-left: 8px;
}

.badge-analysis { background-color: var(--secondary-blue); color: white; }
.badge-planning { background-color: var(--success-green); color: black; }
.badge-solution { background-color: var(--warning-yellow); color: black; }
.badge-implementation { background-color: var(--primary-orange); color: white; }

/* Phase indicator */
.phase-indicator {
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
    padding: 15px;
    background: var(--sidebar-bg);
    border-radius: 8px;
}

.phase-step {
    text-align: center;
    padding: 10px;
    border-radius: 6px;
    min-width: 100px;
    transition: all 0.3s;
}

.phase-step.active {
    background: var(--primary-orange);
    color: white;
    transform: scale(1.05);
}

.phase-step.completed {
    background: var(--success-green);
    color: black;
}

.phase-step.pending {
    background: var(--dark-bg);
    color: var(--text-gray);
    opacity: 0.6;
}

/* Card styling for better organization */
.info-card {
    background: var(--sidebar-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.info-card h3 {
    color: var(--primary-orange);
    margin-top: 0;
}

/* Progress bar */
.progress-container {
    background: var(--dark-bg);
    border-radius: 10px;
    overflow: hidden;
    height: 30px;
    margin: 15px 0;
}

.progress-bar {
    background: linear-gradient(90deg, var(--primary-orange), var(--secondary-blue));
    height: 100%;
    transition: width 0.5s;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
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
                    gr.Markdown("#### 📁 Phase 1: Analysis")
                    gr.Markdown("""
                    <div style="padding-left: 10px;">
                    📄 product_brief.md <span class="file-badge badge-analysis">Research</span><br>
                    💰 financial_model.md <span class="file-badge badge-analysis">Finance</span>
                    </div>
                    """)
                    
                    gr.Markdown("#### 📁 Phase 2: Planning")
                    gr.Markdown("""
                    <div style="padding-left: 10px;">
                    📋 prd.md <span class="file-badge badge-planning">Core</span><br>
                    🛠️ tech_spec.md <span class="file-badge badge-planning">Tech</span><br>
                    ⭐ feature_prioritization.md <span class="file-badge badge-planning">Priority</span><br>
                    🏆 competitive_analysis.md <span class="file-badge badge-planning">Market</span>
                    </div>
                    """)
                    
                    gr.Markdown("#### 📁 Phase 3: Solution")
                    gr.Markdown("""
                    <div style="padding-left: 10px;">
                    🏗️ architecture.md <span class="file-badge badge-solution">System</span><br>
                    👤 user_flow.md <span class="file-badge badge-solution">UX</span><br>
                    🎨 design_system.md <span class="file-badge badge-solution">Design</span>
                    </div>
                    """)
                    
                    gr.Markdown("#### 📁 Phase 4: Implementation")
                    gr.Markdown("""
                    <div style="padding-left: 10px;">
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

<<<<<<< HEAD
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

=======
>>>>>>> copilot/improve-agent-ui-features
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
