"""
Editor page component - Displays generated files in real-time.
This is shown on a separate page/interface during generation.
"""

import gradio as gr
import time
from typing import Dict, List, Any, Optional
from .generation_state import get_state_manager

# Custom CSS for the editor page (enhanced with animations and better styling)
EDITOR_CSS = """
:root {
    --primary-orange: #FF6B35;
    --primary-orange-hover: #ff8555;
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
}

* {
    transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.gradio-container {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Sidebar styling */
.sidebar-container {
    background: linear-gradient(180deg, var(--sidebar-bg) 0%, rgba(37, 37, 38, 0.95) 100%);
    border-right: 1px solid var(--border-color);
    padding: 15px;
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
    padding: 8px 12px !important;
    margin-bottom: 3px !important;
    width: 100% !important;
    border-radius: 6px !important;
    cursor: pointer !important;
}

.file-btn:hover {
    background-color: rgba(42, 45, 46, 0.8) !important;
    color: var(--text-white) !important;
    transform: translateX(3px);
}

.file-btn.selected {
    background: linear-gradient(90deg, rgba(255, 107, 53, 0.15) 0%, rgba(255, 107, 53, 0.05) 100%) !important;
    color: var(--text-white) !important;
    border-left: 3px solid var(--primary-orange) !important;
    font-weight: 600 !important;
}

/* Status Terminal */
#terminal-log {
    background: linear-gradient(180deg, #1a1a1a 0%, #1e1e1e 100%);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    padding: 12px;
    height: 150px;
    overflow-y: auto;
    color: #d4d4d4;
    box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
}

#terminal-log::-webkit-scrollbar {
    width: 8px;
}

#terminal-log::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

#terminal-log::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

#terminal-log::-webkit-scrollbar-thumb:hover {
    background: var(--primary-orange);
}

.log-info { color: var(--info-blue); font-weight: 500; }
.log-error { color: var(--error-red); font-weight: 600; }
.log-success { color: var(--success-green); font-weight: 500; }
.log-warning { color: var(--warning-yellow); font-weight: 500; }

.log-entry {
    animation: fadeInEntry 0.3s ease-in;
}

@keyframes fadeInEntry {
    from { opacity: 0; transform: translateY(-3px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Progress bar */
.progress-container {
    width: 100%;
    background: linear-gradient(90deg, rgba(30, 30, 30, 0.8), rgba(42, 45, 46, 0.6));
    border-radius: 6px;
    margin: 12px 0;
    overflow: hidden;
    border: 1px solid var(--border-color);
}

.progress-bar {
    height: 10px;
    background: linear-gradient(90deg, var(--primary-orange), #ff8c5a, var(--primary-orange));
    background-size: 200% 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
    animation: progressFlow 2s linear infinite;
}

@keyframes progressFlow {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

/* Button enhancements */
button {
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
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
