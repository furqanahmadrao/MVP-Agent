# MVP Agent - AI-powered MVP Blueprint Generator
# For MCP Hackathon 2025 - Track 2: MCP In Action (Agents)
# This is the main Gradio application file.


from src import hf_compat  # noqa: F401  # Ensure HfFolder compatibility for gradio.oauth
import gradio as gr
import os
import time
from dotenv import load_dotenv
import threading
from typing import Dict, List, Any
from src.agent_brain import create_agent
from src.file_manager import get_file_manager
from src.error_handler import get_error_handler, MVPAgentError, ErrorCategory
from src.validators import validate_idea, sanitize_idea
from src.mcp_process_manager import MCPManager
from src.settings import SettingsManager, create_settings_ui

# Explicitly load environment variables
load_dotenv()

# Custom CSS for orange/black theme
CUSTOM_CSS = """
:root {
    --primary-orange: #FF6B35;
    --dark-bg: #1a1a1a;
    --darker-bg: #0d0d0d;
    --text-white: #ffffff;
    --text-gray: #cccccc;
    --border-gray: #333333;
    --info-color: #3498db;     /* Blue */
    --warning-color: #f39c12;  /* Orange */
    --error-color: #e74c3c;    /* Red */
    --success-color: #2ecc71;  /* Green */
    --debug-color: #95a5a6;    /* Gray */
}

/* Main container */
.gradio-container {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
}

/* Input textbox */
#idea-input textarea {
    background-color: var(--darker-bg) !important;
    color: var(--text-white) !important;
    border: 2px solid var(--primary-orange) !important;
    border-radius: 8px !important;
    font-size: 16px !important;
}

/* Generate button */
#generate-btn {
    background: linear-gradient(135deg, var(--primary-orange) 0%, #ff8c42 100%) !important;
    color: var(--text-white) !important;
    border: none !important;
    padding: 12px 32px !important;
    font-size: 18px !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: transform 0.2s !important;
}

#generate-btn:hover {
    transform: scale(1.05) !important;
}

/* New Status display components */
.status-metric {
    font-size: 1.1em;
    font-weight: bold;
    color: var(--primary-orange);
    text-align: center;
}

#activity-log-display {
    background-color: var(--darker-bg);
    border: 1px solid var(--border-gray);
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    height: 300px; /* Fixed height for scrolling */
    overflow-y: auto; /* Enable scrolling */
    padding: 10px;
    color: var(--text-white);
}

.log-entry {
    padding: 2px 0;
    border-bottom: 1px dotted rgba(255, 255, 255, 0.1);
}
.log-entry:last-child {
    border-bottom: none;
}
.log-info { color: var(--info-color); }
.log-warning { color: var(--warning-color); }
.log-error { color: var(--error-color); }
.log-success { color: var(--success-color); }
.log-debug { color: var(--debug-color); }


/* Tabs */
.tab-nav button {
    background-color: var(--darker-bg) !important;
    color: var(--text-gray) !important;
    border: 1px solid var(--border-gray) !important;
}

.tab-nav button.selected {
    background-color: var(--primary-orange) !important;
    color: var(--text-white) !important;
    border-color: var(--primary-orange) !important;
}

/* Markdown content */
.markdown-body {
    background-color: var(--darker-bg) !important;
    color: var(--text-white) !important;
    padding: 20px !important;
    border-radius: 8px !important;
}

/* File download buttons */
.file-download {
    background-color: var(--primary-orange) !important;
    color: var(--text-white) !important;
    border-radius: 6px !important;
}

/* ZIP download section - clean CTA style */
#zip-download-section {
    background-color: var(--dark-bg);
    border: 1px solid var(--border-gray);
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0 0 0;
}

#zip-download-section .zip-title {
    color: var(--text-white);
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 4px 0;
}

#zip-download-section .zip-subtitle {
    color: var(--text-gray);
    font-size: 13px;
    margin: 0 0 12px 0;
}

/* Make the File component look like a proper orange download button
   Note: Gradio's markup varies across versions. We target several
   possible class names to ensure the entire area is styled and clickable. */
#zip-file,
#zip-file .file,
#zip-file .gr-file,
#zip-file .file-preview,
#zip-file .download-link,
#zip-file .file-wrap,
#zip-file .wrap {
    background: var(--dark-bg) !important;
    color: var(--text-white) !important;
}

/* Anchor / download link styling - make full width and orange */
#zip-file a,
#zip-file .download-link,
#zip-file .file a,
#zip-file .gr-file a,
#zip-file .file-preview a {
    display: block !important;
    width: 100% !important; /* full area clickable */
    background: linear-gradient(135deg, var(--primary-orange) 0%, #ff8c42 100%) !important;
    color: #ffffff !important;
    padding: 14px 24px !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    text-align: center !important;
    transition: transform 0.12s ease-in-out !important;
    box-sizing: border-box !important;
    pointer-events: auto !important;
}

#zip-file a:hover,
#zip-file .download-link:hover,
#zip-file .file-preview a:hover {
    transform: scale(1.03) !important;
    background: linear-gradient(135deg, #ff8c42 0%, var(--primary-orange) 100%) !important;
}

/* Hide upload controls if present */
#zip-file input[type="file"],
#zip-file .file-upload,
#zip-file .upload {
    display: none !important;
}

/* Header Styling */
.header-title h1 {
    color: var(--primary-orange) !important;
    font-family: 'Arial', sans-serif !important;
    text-align: center;
    font-size: 3.5em !important; /* Larger font size */
    font-weight: bold !important; /* Explicitly bold */
    margin-bottom: 5px !important; /* Reduced margin */
}

.header-title h3 {
    color: var(--text-white) !important;
    font-family: 'Arial', sans-serif !important;
    text-align: center;
    font-size: 1.6em !important; /* Slightly larger for tagline */
    margin-top: 5px !important; /* Reduced margin */
    font-weight: normal !important;
}

.header-title p {
    color: var(--text-gray) !important;
    text-align: center;
    font-size: 1.1em !important;
    max-width: 800px;
    margin: 10px auto !important;
}
"""

# Initialize agent (will be created on first use)
_agent = None
_file_manager = None
_mcp_manager: MCPManager | None = None
_settings_manager: SettingsManager | None = None

def get_mcp_manager() -> MCPManager:
    """
    Get or create the global MCPManager.

    This ensures MCP servers are started exactly once per process.
    """
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager

settings_mgr() -> SettingsManager:
    """Get or create the settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_agent():
    """Get or create the agent instance"""
    global _agent
    if _agent is None:
        # Try to get API key from settings first, fallback to env var
        settings_mgr = get_settings_mgr()
        api_key = settings_mgr.get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please add it in Settings tab o
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
        _agent = create_agent(api_key)
    return _agent

def get_file_mgr():
    """Get or create the file manager instance"""
    global _file_manager
    if _file_manager is None:
        _file_manager = get_file_manager()
    return _file_manager

# Helper function to format structured log entries into HTML
def format_log_entries(log_events: List[Dict]) -> str:
    html_log = ""
    for event in log_events:
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.get("timestamp", time.time())))
        message_type = event.get("type", "INFO").lower()
        message = event.get("message", "No Message").replace("<", "&lt;").replace(">", "&gt;") # Sanitize message
        phase = event.get("phase", "N/A")
        
        color_class = f"log-{message_type}"
        
        html_log += f"<div class='log-entry'><span class='{color_class}'>[{timestamp}] [{phase.upper()}] {message}</span></div>"
    return f"<div id='log-container'>{html_log}</div>"


# Main MVP generation function
def generate_mvp(idea: str, tech_preference: str = "", platform: str = "", constraint: str = ""):
    """
    Main function to generate MVP specifications using the real agent.
    """
    # CRITICAL: First yield MUST happen immediately to prevent Gradio's processing window
    # Initial state for display components
    initial_yield = {
        current_phase_display: "⚡ Current Phase: Initializing",
        elapsed_time_display: "⏱️ Elapsed Time: 0.0s",
        tokens_used_display: "🧠 Tokens Used: 0",
        activity_log_display: format_log_entries([{"message": "Ready to generate your MVP blueprint.", "type": "INFO", "phase": "idle"}]),
        output_tabs: gr.Tabs(visible=False),
        zip_file: gr.File(visible=False),
        overview_display: "", features_display: "", architecture_display: "",
        design_display: "", user_flow_display: "", roadmap_display: "",
        business_model_display: "", testing_plan_display: ""
    }
    yield initial_yield

    error_handler = get_error_handler()

    # Validate input
    is_valid, error_msg = validate_idea(idea)
    if not is_valid:
        error_event = {"message": error_msg, "type": "ERROR", "phase": "validation", "timestamp": time.time()}
        yield {
            current_phase_display: "❌ Error",
            elapsed_time_display: "-",
            tokens_used_display: "-",
            activity_log_display: format_log_entries([error_event]),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            # ... keep other empty fields ...
            overview_display: "", features_display: "", architecture_display: "",
            design_display: "", user_flow_display: "", roadmap_display: "",
            business_model_display: "", testing_plan_display: ""
        }
        return

    # Sanitize input
    idea = sanitize_idea(idea)
    
    # Shared state for thread communication
    state = {
        "status_events": [], # Store structured events
        "files": None,
        "error": None,
        "done": False,
        "current_phase": "idle",
        "elapsed_time": 0.0,
        "tokens_used": 0
    }

    def agent_worker():
        try:
            # Create a fresh agent instance for thread safety
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found. Check .env file.")
                
            agent = create_agent(api_key)
            file_mgr = get_file_mgr()
            
            def status_callback(status_event: Dict):
                state["status_events"].append(status_event)
                state["current_phase"] = status_event.get("phase", "N/A")
                state["elapsed_time"] = status_event.get("elapsed_time", 0.0)
                state["tokens_used"] = status_event.get("tokens_used", 0)
                
            agent.set_status_callback(status_callback)
            
            # The agent_brain.py methods will now emit all necessary status updates
            queries = agent._generate_search_queries(idea)
            research_results = agent._conduct_research(queries)
            research_summary = agent._summarize_research(idea, research_results)
            
            mvp_files = agent._generate_files(
                idea, 
                research_summary, 
                tech_preference=tech_preference,
                platform=platform,
                constraint=constraint
            )
            
            # Final success message will be from agent_brain, but we need to ensure files are saved
            paths = file_mgr.save_mvp_files(mvp_files, idea)
            
            state["files"] = (mvp_files, paths)
            state["done"] = True
            
        except Exception as e:
            state["error"] = e
            state["done"] = True

    # Start worker thread
    t = threading.Thread(target=agent_worker)
    t.start()
    
    start_time = time.time()

    # Loop and yield while worker is running
    last_event_count = 0
    final_elapsed_time = 0.0 # To store the final time
    while not state["done"]:
        elapsed = time.time() - start_time
        final_elapsed_time = elapsed # Update here in every iteration
        
        # Only update log if new events arrived, but always update timer
        yield {
            current_phase_display: f"⚡ Current Phase: {state['current_phase'].upper()}",
            elapsed_time_display: f"⏱️ Elapsed Time: {elapsed:.1f}s",
            tokens_used_display: f"🧠 Tokens Used: {state['tokens_used']}",
            activity_log_display: format_log_entries(state["status_events"]),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            overview_display: "", features_display: "", architecture_display: "",
            design_display: "", user_flow_display: "", roadmap_display: "",
            business_model_display: "", testing_plan_display: ""
        }
        
        if len(state["status_events"]) > last_event_count:
            last_event_count = len(state["status_events"])
            
        time.sleep(0.1) # Check for updates more frequently

    # Handle completion
    if state["error"]:
        e = state["error"]
        # Log the error event
        error_event = {}
        if isinstance(e, MVPAgentError):
            error_msg = f"❌ {e.user_message}\n\nTechnical Details: {e.message}"
            error_event = {"message": error_msg, "type": "ERROR", "phase": state["current_phase"], "timestamp": time.time(), "elapsed_time": state["elapsed_time"], "tokens_used": state["tokens_used"], "details": {"exception": str(e)}}
        else:
            error_msg = (
                f"⚠️ Unexpected Error: {str(e)}\n\n"
                f"Don't worry! Your request has been logged.\n"
                f"Please try:\n"
                f"1. Simplifying your idea description\n"
                f"2. Waiting a moment and trying again\n"
                f"3. Checking your internet connection\n\n"
                f"If the problem persists, check the logs/ folder for details."
            )
            error_event = {"message": error_msg, "type": "ERROR", "phase": state["current_phase"], "timestamp": time.time(), "elapsed_time": state["elapsed_time"], "tokens_used": state["tokens_used"], "details": {"exception": str(e)}}
            error_handler.logger.log_error(e, {"idea": idea[:50]})

        # Append final error to status_events for display
        state["status_events"].append(error_event)
        
        yield {
            current_phase_display: f"❌ Error in Phase: {state['current_phase'].upper()}",
            elapsed_time_display: f"⏱️ Elapsed Time: {final_elapsed_time:.1f}s", # Use the stored final time
            tokens_used_display: f"🧠 Tokens Used: {state['tokens_used']}",
            activity_log_display: format_log_entries(state["status_events"]),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            overview_display: "", features_display: "", architecture_display: "",
            design_display: "", user_flow_display: "", roadmap_display: "",
            business_model_display: "", testing_plan_display: ""
        }
    else:
        # Success
        mvp_files, paths = state["files"]
        zip_path = paths.get('zip')
        
        # Final success messages from app.py
        state["status_events"].append({"message": "✅ Complete! Your MVP blueprint is ready.", "type": "SUCCESS", "phase": "complete", "timestamp": time.time(), "elapsed_time": state["elapsed_time"], "tokens_used": state["tokens_used"]})
        state["status_events"].append({"message": "⬇️ Download your complete blueprint below", "type": "INFO", "phase": "complete", "timestamp": time.time(), "elapsed_time": state["elapsed_time"], "tokens_used": state["tokens_used"]})
        
        yield {
            current_phase_display: f"✅ Generation Complete!",
            elapsed_time_display: f"⏱️ Total Time: {final_elapsed_time:.1f}s", # Use the stored final time
            tokens_used_display: f"🧠 Total Tokens: {state['tokens_used']}", # Use the final tokens from agent_brain
            activity_log_display: format_log_entries(state["status_events"]),
            zip_file: gr.File(value=zip_path, visible=True),
            output_tabs: gr.Tabs(visible=True),
            overview_display: mvp_files.get("overview_md", ""),
            features_display: mvp_files.get("features_md", ""),
            architecture_display: mvp_files.get("architecture_md", ""),
            design_display: mvp_files.get("design_md", ""),
            user_flow_display: mvp_files.get("user_flow_md", ""),
            roadmap_display: mvp_files.get("roadmap_md", ""),
            business_model_display: mvp_files.get("business_model_md", ""),
            testing_plan_display: mvp_files.get("testing_plan_md", "")
        }

# Create Gradio interface
    
    # Main tabs for app sections
    with gr.Tabs() as main_tabs:
        # ===== Generate Tab =====
        with gr.Tab("🎯 Generate Blueprint", id="generate-tab"):
with gr.Blocks(css=CUSTOM_CSS, title="MVP Agent", theme=gr.themes.Base()) as demo:
    
    # Header
    # Try to start MCP servers before exposing full UI
    mcp_error_box = gr.Markdown(visible=False)
        
            # Input section
            with gr.Row():
                with gr.Column():
                    idea_input = gr.Textbox(
                        label="Your Startup Idea  (estimated time: 8-10 min)",
                        placeholder="e.g., An AI-powered meal planning app that helps busy professionals eat healthier...",
                        lines=4,
                        elem_id="idea-input"
                    idea_input = gr.Textbox(
                label="Your Startup Idea  (estimated time: 8-10 min)",
                placeholder="e.g., An AI-powered meal planning app that helps busy professionals eat healthier...",
                lines=4,
                elem_id="idea-input"
            )
                    
                    # Advanced Configuration
                    with gr.Accordion("🛠️ Advanced Configuration (Optional)", open=False):
                        with gr.Row():
                            platform_input = gr.Dropdown(
                                choices=["Web App", "Mobile App (iOS/Android)", "Cross-Platform", "Desktop", "CLI Tool", "API Service"],
                                label="Target Platform",
                                value="Web App",
                                info="Where will your users interact with the product?"
                            )
                            tech_input = gr.Textbox(
                                label="Preferred Tech Stack",
                                placeholder="e.g. Next.js, Python/FastAPI, Flutter, No-Code...",
                                info="Leave empty to let the AI decide"
                            )
                        constraint_input = gr.Textbox(
                            label="Key Constraints",
                            placeholder="e.g. Must be Open Source, Max $50/mo hosting, HIPAA compliant...",
                            info="Any specific limitations or requirements?"
                        )

                    generate_btn = gr.Button(
                        "🎯 Generate MVP Blueprint",
                        variant="primary",
                        elem_id="generate-btn"
                    )
            
            # Status section
            gr.Markdown("### 🤖 Agent Status - Mission Control")
            with gr.Column():
                with gr.Row():
                    current_phase_display = gr.Markdown("⚡ Current Phase: Idle", elem_classes="status-metric")
                    elapsed_time_display = gr.Markdown("⏱️ Elapsed Time: 0.0s", elem_classes="status-metric")
                    tokens_used_display = gr.Markdown("🧠 Tokens Used: 0", elem_classes="status-metric")
                activity_log_display = gr.HTML("<div id='log-container'>Ready to generate your MVP blueprint. Enter your idea above and click the button!</div>", elem_id="activity-log-display")
            
            # Download button (initially hidden)
            zip_file = gr.File(
                label=" Download All Files as ZIP",
                visible=False,
                elem_id="download-zip"
            )

            # Output tabs (initially hidden)
            with gr.Tabs(visible=False) as output_tabs:
                with gr.Tab("📝 Overview"):
                    overview_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("📋 Features"):
                    features_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("🏗️ Architecture"):
                    architecture_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("🎨 Design"):
                    design_display = gr.Markdown("", elem_classes=["markdown-body"])

                with gr.Tab("🗺️ User Flow"):
                    user_flow_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("📅 Roadmap"):
                    roadmap_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("💼 Business Model"):
                    business_model_display = gr.Markdown("", elem_classes="markdown-body")

                with gr.Tab("🧪 Testing Plan"):
                    testing_plan_display = gr.Markdown("", elem_classes="markdown-body")
        
        # == (outside tabs, applies to all)
    gr.Markdown("""
    ---
    **MVP Agent v2.0** | Production-Ready with BMAD Method  
    Powered by Gemini API, LangChain/LangGraph, and MCP servers
    gr.Markdown("""
    ---
    **MCP 1st Birthday** | Track 2: MCP In Action (Agents)  
    Powered by Gemini API and custom internal MCP servers:
    file-manager-mcp, google-search-mcp, markdownify-mcp
    """)

    # Event handler - Production Mode
    generate_btn.click(
        fn=generate_mvp,
        inputs=[idea_input, tech_input, platform_input, constraint_input],
        outputs=[
            current_phase_display,
            elapsed_time_display,
            tokens_used_display,
            activity_log_display,
            zip_file,
            output_tabs,
            overview_display,
            features_display,
            architecture_display,
            design_display,
            user_flow_display,
            roadmap_display,
            business_model_display,
            testing_plan_display,
        ],
        show_progress="hidden"  # Hide Gradio's default processing window
    )

# Launch the app
if __name__ == "__main__":
    import atexit
    import socket
    
    # Find available port starting from 7860
    def find_free_port(start_port=7860, max_port=7870):
        for port in range(start_port, max_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        return start_port
    
    # Ensure MCP servers are started before launch; fail fast with clear logs if needed.
    try:
        manager = get_mcp_manager()
        manager.start_all()
        print("✅ MCP servers started successfully.")
    except Exception as e:
        print("❌ Failed to start MCP servers:", e)
        print("Check logs/mcp_*.log for details.")
        raise SystemExit(1)

    # Ensure graceful shutdown of MCP servers when app exits
    def _cleanup_mcp():
        mgr = globals().get("_mcp_manager")
        if mgr is not None:
            try:
                mgr.stop_all()
                print("🧹 MCP servers stopped.")
            except Exception:
                pass

    atexit.register(_cleanup_mcp)

    port = find_free_port()
    print(f"\n🚀 Starting MVP Agent on port {port}...\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )