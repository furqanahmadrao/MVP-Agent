# MVP Agent v2.0 - BMAD Edition
# Production-ready AI Agent for generating comprehensive PRDs

import gradio as gr
import os
import time
import threading
import re
from html import escape
from dotenv import load_dotenv
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Import new architecture modules
from src.workflow import create_workflow, MVPAgentWorkflow
from src.settings import get_settings_mgr, create_settings_ui
from src.agent_state import AgentState
from src.file_manager import get_file_manager
from src.generation_state import get_state_manager
from src.editor_page import create_editor_interface
from src.styles import GLOBAL_CSS

# Load environment variables
load_dotenv()

# Custom CSS is now imported from src.styles


def validate_and_sanitize_idea(idea: str) -> Tuple[bool, str, str]:
    """
    Validate user idea input.
    
    Returns:
        (is_valid, sanitized_idea, error_message)
    """
    if not idea:
        return False, "", "Please enter an idea."
        
    # Check length
    if len(idea.strip()) < 10:
        return False, "", "Idea must be at least 10 characters."
    
    if len(idea) > 5000:
        return False, "", "Idea is too long (max 5000 characters)."
    
    # Remove control characters except newlines/tabs
    sanitized = ''.join(char for char in idea if ord(char) >= 32 or char in '\n\r\t')
    
    # HTML escape for safety in display
    # Note: We keep the original for the LLM (it handles raw text), but for UI display/filenames we use sanitized
    sanitized_display = escape(sanitized)
    
    # Check for prompt injection patterns (basic check)
    dangerous_patterns = [
        r'ignore\s+(all\s+)?previous\s+instructions',
        r'output\s+(all\s+)?(environment|env)\s+variables',
        r'print\s+(api|secret|password)',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized.lower()):
            return False, "", "Input contains prohibited patterns."
    
    return True, sanitized, ""


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

# Global state removed - replaced with per-session gr.State
# generated_content_store = get_empty_state_files()

def run_generation(idea: str, project_level: int, session_files: Dict[str, str]):
    """
    Main generator function called by the button.
    Yields updates to the UI and creates a new generation session.
    """
    # Validate input
    is_valid, sanitized_idea, error_msg = validate_and_sanitize_idea(idea)
    if not is_valid:
        yield (
            f"<div class='log-error'>❌ {error_msg}</div>", # status_html
            gr.Button(interactive=True),                    # generate_btn
            gr.update(),                                    # code_editor
            gr.update(),                                    # file_list
            gr.update(),                                    # editor_link
            gr.update(),                                    # session_files
            gr.update()                                     # session_id_state
        )
        return

    settings = get_settings_mgr()
    api_key = settings.get_api_key()
    
    if not api_key:
        yield (
            "<div class='log-error'>❌ Error: Gemini API Key not found. Please set it in the Settings tab.</div>",
            gr.Button(interactive=True),
            gr.update(),
            gr.update(),
            gr.HTML(""),
            gr.update(),
            gr.update()
        )
        return

    # Create a new generation session
    state_mgr = get_state_manager()
    session_id = state_mgr.create_session(sanitized_idea)
    
    # Initialize workflow with session_id for real-time updates
    workflow = create_workflow(api_key=api_key, session_id=session_id)
    
    # State container for the thread
    thread_state = {"done": False, "final_state": None, "error": None, "session_id": session_id}
    
    # Update initial UI and show link to editor page
    yield (
        "<div class='log-info'>🚀 Starting MVP Agent v2.0...</div>", # status_html
        gr.Button(interactive=False), # generate_btn
        gr.update(), # code_editor
        gr.update(), # file_list
        gr.HTML(f"""
            <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #FF6B35;'>
                <p style='color: #89d185; margin: 0 0 10px 0; font-weight: bold;'>✅ Generation started!</p>
                <p style='color: #cccccc; margin: 0 0 10px 0;'>Open the editor page to watch real-time progress:</p>
                <a href='/editor' target='_blank' style='display: inline-block; background: #FF6B35; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;'>
                    🚀 Open Editor (New Window)
                </a>
                <p style='color: #808080; margin: 10px 0 0 0; font-size: 12px;'>Session ID: {session_id}</p>
            </div>
        """), # editor_link
        gr.update(), # session_files
        session_id   # session_id_state
    )
    
    state_mgr.update_status(session_id, "running", progress=5)
    state_mgr.add_log(session_id, "🚀 Starting MVP Agent v2.0...", "INFO")
    
    def worker():
        try:
            # Update state as we progress
            state_mgr.add_log(session_id, "🔍 Analyzing idea and detecting project level...", "INFO")
            state_mgr.update_status(session_id, "running", progress=10, phase="Analysis")
            
            # Run the synchronous workflow
            # Use sanitized idea
            result = workflow.run(idea=sanitized_idea, api_key=api_key)
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
        
        yield (
            format_log_entries(logs), # status_html
            gr.update(), # generate_btn
            gr.update(), # code_editor
            gr.update(), # file_list
            gr.update(), # editor_link
            gr.update(), # session_files
            gr.update()  # session_id_state
        )
        time.sleep(2)
        
    # Handle completion
    if thread_state["error"]:
        yield (
            format_log_entries(logs), # status_html
            gr.Button(interactive=True), # generate_btn
            gr.update(), # code_editor
            gr.update(), # file_list
            gr.HTML(f"""
                <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #f48771;'>
                    <p style='color: #f48771; margin: 0; font-weight: bold;'>❌ Generation failed</p>
                    <p style='color: #cccccc; margin: 10px 0 0 0;'>Check the logs above for details.</p>
                </div>
            """), # editor_link
            gr.update(), # session_files
            gr.update()  # session_id_state
        )
    else:
        final_state = thread_state["final_state"]
        
        # Populate session state (replaces global store)
        new_session_files = {
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
        
        # Save files using file manager (for internal zip creation later)
        file_mgr = get_file_manager()
        # We don't necessarily need to call this here if we do it on download,
        # but it warms up the cache/temp file.
        # file_mgr.save_mvp_files(new_session_files, sanitized_idea)
        
        # Get logs from state
        history = final_state.get("status_history", [])
        
        yield (
            format_log_entries(history), # status_html
            gr.Button(interactive=True), # generate_btn
            new_session_files["overview.md"], # code_editor
            gr.Radio(choices=list(new_session_files.keys()), value="overview.md"), # file_list
            gr.HTML(f"""
                <div style='background: #2a2d2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #89d185;'>
                    <p style='color: #89d185; margin: 0 0 10px 0; font-weight: bold;'>✅ Generation complete!</p>
                    <p style='color: #cccccc; margin: 0 0 10px 0;'>View your generated files in the editor:</p>
                    <a href='/editor' target='_blank' style='display: inline-block; background: #FF6B35; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: bold;'>
                        📝 Open Editor
                    </a>
                </div>
            """), # editor_link
            new_session_files, # session_files
            session_id # session_id_state
        )
        return

def load_file_content(filename: str, session_files: Dict[str, str]):
    """Load content into the editor when a file is selected."""
    if session_files and filename in session_files:
        return session_files[filename]
    return ""

def download_zip(session_files: Dict[str, str], session_id: str):
    """Create ZIP and return path for current session."""
    file_mgr = get_file_manager()
    
    idea = "mvp"
    if session_id:
        state_mgr = get_state_manager()
        session = state_mgr.get_session(session_id)
        if session:
            idea = session.idea
            
    # Create ZIP from session files
    result = file_mgr.save_mvp_files(session_files, idea)
    zip_path = result.get("zip")
    
    if zip_path and os.path.exists(zip_path):
        return zip_path
    else:
        return None  # Gradio will show error

# Build UI
with gr.Blocks(css=GLOBAL_CSS, title="MVP Agent v2.0 - BMAD Edition") as demo:
    
    # State for file content
    session_files = gr.State(get_empty_state_files())
    session_id_state = gr.State("")
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
                        choices=list(get_empty_state_files().keys()),
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
                        value=get_empty_state_files()["overview.md"],
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
        inputs=[file_list, session_files],
        outputs=[code_editor]
    )
    
    # 2. Generation
    generate_btn.click(
        fn=run_generation,
        inputs=[idea_input, project_level, session_files],
        outputs=[status_html, generate_btn, code_editor, file_list, editor_link, session_files, session_id_state]
    )
    
    # 3. Download
    dl_btn.click(
        fn=download_zip,
        inputs=[session_files, session_id_state],
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
