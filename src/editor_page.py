"""
Editor page component - Displays generated files in real-time.
This is shown on a separate page/interface during generation.
"""

import gradio as gr
import time
from typing import Dict, List, Any, Optional
from .generation_state import get_state_manager

# Custom CSS for the editor page (same styling as main app)
EDITOR_CSS = """
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
    height: 150px;
    overflow-y: auto;
    color: #d4d4d4;
}

.log-info { color: #569cd6; }
.log-error { color: #f48771; }
.log-success { color: #89d185; }
.log-warning { color: #cca700; }

/* Progress bar */
.progress-container {
    width: 100%;
    background-color: #2a2d2e;
    border-radius: 4px;
    margin: 10px 0;
}

.progress-bar {
    height: 8px;
    background: linear-gradient(90deg, var(--primary-orange), #ff8c5a);
    border-radius: 4px;
    transition: width 0.3s ease;
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

def poll_generation_updates(session_id: str, current_file: str):
    """
    Poll the state manager for updates to the current session.
    Returns updated status, files, and logs.
    """
    state_mgr = get_state_manager()
    session = state_mgr.get_session(session_id)
    
    if not session:
        return {
            "status": "⚠️ Session not found",
            "progress": 0,
            "phase": "",
            "logs": "<div class='log-error'>Session not found</div>",
            "editor_content": "# Error\n\nSession not found.",
            "file_choices": gr.Radio(choices=["overview.md"]),
            "download_btn": gr.Button(visible=False),
            "zip_file": gr.File(visible=False)
        }
    
    # Format status
    status_text = f"🔄 {session.status.upper()}"
    if session.status == "completed":
        status_text = "✅ COMPLETED"
    elif session.status == "error":
        status_text = "❌ ERROR"
    
    # Format logs
    logs_html = format_log_entries(session.logs)
    
    # Get current file content
    editor_content = session.files.get(current_file, "# Loading...\n\nContent not yet available.")
    
    # Get available files (only show files with actual content, not just "⏳ Generating...")
    available_files = [f for f, content in session.files.items() if content and "⏳" not in content[:50]]
    if not available_files:
        available_files = ["overview.md"]  # Always show at least overview
    
    # Check if we should show download button (only when completed)
    show_download = session.status == "completed"
    
    return {
        "status": f"{status_text} | Phase: {session.current_phase}",
        "progress": session.progress,
        "phase": session.current_phase,
        "logs": logs_html,
        "editor_content": editor_content,
        "file_choices": gr.Radio(choices=list(session.files.keys()), value=current_file),
        "download_btn": gr.Button(visible=show_download),
        "zip_file": gr.File(visible=False)
    }

def create_editor_interface() -> gr.Blocks:
    """Create the editor page interface."""
    
    with gr.Blocks(css=EDITOR_CSS, title="MVP Agent - Editor") as editor_demo:
        # Hidden state for session tracking
        session_id_state = gr.State("")
        current_file_state = gr.State("overview.md")
        
        with gr.Row():
            gr.Markdown("# 🤖 MVP Agent - Real-time Editor")
        
        with gr.Row():
            with gr.Column(scale=1):
                status_text = gr.Markdown("🔄 Status: Initializing...")
                progress_html = gr.HTML("""
                    <div class='progress-container'>
                        <div class='progress-bar' style='width: 0%'></div>
                    </div>
                """)
        
        with gr.Row():
            # Sidebar with file explorer
            with gr.Column(scale=1, min_width=200, elem_classes="sidebar-container"):
                gr.Markdown("### 📂 Generated Files")
                file_list = gr.Radio(
                    choices=["overview.md"],
                    value="overview.md",
                    label="Files",
                    interactive=True,
                    container=False
                )
                
                gr.Markdown("---")
                download_btn = gr.Button("⬇️ Download ZIP", size="sm", visible=False)
                zip_file = gr.File(label="Download", visible=False)
            
            # Main editor area
            with gr.Column(scale=4):
                code_editor = gr.Code(
                    value="# Project Overview\n\n⏳ Waiting for generation to start...",
                    language="markdown",
                    label="Editor",
                    interactive=True,
                    lines=25
                )
                
                # Status logs
                gr.Markdown("### 📟 Generation Log")
                status_logs = gr.HTML(elem_id="terminal-log")
        
        # Auto-refresh timer (polls every 2 seconds)
        refresh_timer = gr.Timer(value=2.0, active=True)
        
        # Event handlers
        def update_editor_from_poll(session_id, current_file):
            """Update editor based on current session state."""
            if not session_id:
                # Try to get current session
                state_mgr = get_state_manager()
                session_id = state_mgr.get_current_session_id()
                if not session_id:
                    return {
                        session_id_state: "",
                        status_text: "⚠️ No active generation session",
                        code_editor: "# No Active Session\n\nPlease start a generation from the main page.",
                        status_logs: "<div class='log-warning'>No active generation session</div>",
                    }
            
            updates = poll_generation_updates(session_id, current_file)
            
            # Format progress bar
            progress = updates["progress"]
            progress_bar_html = f"""
                <div class='progress-container'>
                    <div class='progress-bar' style='width: {progress}%'></div>
                </div>
                <div style='text-align: center; color: #cccccc; margin-top: 5px;'>{progress}%</div>
            """
            
            return {
                session_id_state: session_id,
                status_text: f"### {updates['status']}",
                progress_html: progress_bar_html,
                code_editor: updates["editor_content"],
                file_list: updates["file_choices"],
                status_logs: updates["logs"],
                download_btn: updates["download_btn"],
            }
        
        def handle_file_selection(session_id, selected_file):
            """Handle when user selects a different file."""
            state_mgr = get_state_manager()
            session = state_mgr.get_session(session_id)
            
            if session and selected_file in session.files:
                return {
                    current_file_state: selected_file,
                    code_editor: session.files[selected_file]
                }
            
            return {
                current_file_state: selected_file,
                code_editor: "# Error\n\nFile not found."
            }
        
        def handle_download():
            """Handle download button click."""
            # Get the latest generated ZIP file
            from .file_manager import get_file_manager
            file_mgr = get_file_manager()
            # This would need to be implemented to return the latest zip path
            # For now, return a placeholder
            return gr.File(visible=True)
        
        # Wire up events
        refresh_timer.tick(
            fn=update_editor_from_poll,
            inputs=[session_id_state, current_file_state],
            outputs=[session_id_state, status_text, progress_html, code_editor, file_list, status_logs, download_btn]
        )
        
        file_list.change(
            fn=handle_file_selection,
            inputs=[session_id_state, file_list],
            outputs=[current_file_state, code_editor]
        )
        
        download_btn.click(
            fn=handle_download,
            outputs=[zip_file]
        ).then(
            fn=lambda: gr.File(visible=True),
            outputs=[zip_file]
        )
    
    return editor_demo
