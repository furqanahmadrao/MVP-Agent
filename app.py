"""
MVP Agent - AI-powered MVP Blueprint Generator
For MCP Hackathon 2025 - Track 2: MCP In Action (Agents)

This is the main Gradio application file.
"""

from src import hf_compat  # noqa: F401  # Ensure HfFolder compatibility for gradio.oauth
import gradio as gr
import os
import time
from dotenv import load_dotenv
import threading
from threading import Event, Lock

# Load environment variables
load_dotenv()

# Import our modules
from src.agent_brain import create_agent
from src.file_manager import get_file_manager
from src.error_handler import get_error_handler, MVPAgentError, ErrorCategory
from src.validators import validate_idea, sanitize_idea
from src.mcp_process_manager import MCPManager

# Custom CSS for orange/black theme
CUSTOM_CSS = """
:root {
    --primary-orange: #FF6B35;
    --dark-bg: #1a1a1a;
    --darker-bg: #0d0d0d;
    --text-white: #ffffff;
    --text-gray: #cccccc;
    --border-gray: #333333;
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

/* Status box */
#status-box textarea {
    background-color: var(--darker-bg) !important;
    color: var(--primary-orange) !important;
    border: 1px solid var(--border-gray) !important;
    border-radius: 8px !important;
    font-family: 'Courier New', monospace !important;
    font-size: 14px !important;
}

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
"""

# Initialize agent (will be created on first use)
_agent = None
_file_manager = None
_mcp_manager: MCPManager | None = None

def get_mcp_manager() -> MCPManager:
    """
    Get or create the global MCPManager.

    This ensures MCP servers are started exactly once per process.
    """
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager


def get_agent():
    """Get or create the agent instance"""
    global _agent
    if _agent is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
        _agent = create_agent(api_key)
    return _agent

def get_file_mgr():
    """Get or create the file manager instance"""
    global _file_manager
    if _file_manager is None:
        _file_manager = get_file_manager()
    return _file_manager

# Main MVP generation function
def generate_mvp(idea: str):
    """
    Main function to generate MVP specifications using the real agent.
    """
    # CRITICAL: First yield MUST happen immediately to prevent Gradio's processing window
    # This ensures the user sees our custom agent status box from the very first moment
    yield {
        status_box: "🤖 Initializing MVP Agent...",
        output_tabs: gr.Tabs(visible=False),
        zip_file: gr.File(visible=False),
        features_display: "",
        architecture_display: "",
        design_display: "",
        user_flow_display: "",
        roadmap_display: ""
    }

    error_handler = get_error_handler()

    # Validate input
    is_valid, error_msg = validate_idea(idea)
    if not is_valid:
        yield {
            status_box: f"❌ {error_msg}",
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        return

    # Sanitize input
    idea = sanitize_idea(idea)
    
    try:
        # Get agent instance
        agent = get_agent()
        file_mgr = get_file_mgr()
        
        # Track status updates with real-time display
        status_log = []
        
        def status_callback(message: str):
            """Callback to update status in real-time"""
            status_log.append(message)
            # Return updated status (will be used by yields below)
            return "\n".join(status_log)
        
        # Set up callback but we'll manually yield updates
        status_display = ["🤖 Initializing MVP Agent..."]
        time.sleep(1)
        
        # Phase 1: Understanding intent
        status_display.append("🧠 Understanding your startup idea...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        # Generate search queries (AI call happens here)
        queries = agent._generate_search_queries(idea)
        
        status_display.append("✅ Intent understood - planning research strategy")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        # Phase 2: Research
        status_display.append("🔍 Searching for competitor features...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("🔍 Analyzing user feedback from web sources...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        research_results = agent._conduct_research(queries)
        
        status_display.append("✅ Research complete - found valuable insights")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        # Phase 3: Analysis
        status_display.append("🧠 Analyzing market gaps and opportunities...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("📊 Identifying core problems and target audience...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        research_summary = agent._summarize_research(idea, research_results)
        
        status_display.append("✅ Analysis complete - key insights identified")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        # Phase 4: Planning & Generation
        status_display.append("✨ Planning feature prioritization (P0, P1, P2)...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("🏗️ Designing technical architecture...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("🎨 Creating UX design philosophy...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("🗺️ Mapping user flows and journeys...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        status_display.append("📅 Building 6-week launch roadmap...")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        mvp_files = agent._generate_files(idea, research_summary)
        
        status_display.append("✅ All MVP files generated successfully!")
        yield {
            status_box: "\n".join(status_display),
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        time.sleep(10)
        
        # Extract content for display BEFORE saving to disk (like working app)
        features_content = mvp_files.get("features_md", "# Error\nFailed to generate features.")
        architecture_content = mvp_files.get("architecture_md", "# Error\nFailed to generate architecture.")
        design_content = mvp_files.get("design_md", "# Error\nFailed to generate design.")
        user_flow_content = mvp_files.get("user_flow_md", "# Error\nFailed to generate user flow.")
        roadmap_content = mvp_files.get("roadmap_md", "# Error\nFailed to generate roadmap.")
        
        # Save files to disk
        file_paths = file_mgr.save_mvp_files(mvp_files, idea)
        
        # Final status
        status_display.append("✅ Complete! Your MVP blueprint is ready.")
        status_display.append("� Download your complete blueprint below")
        final_status = "\n".join(status_display)

        # Get ZIP file path
        zip_file_path = file_paths.get('zip', None)

        # Final yield with all outputs - use simple direct assignment like working app
        yield {
            status_box: final_status,
            zip_file: gr.File(value=zip_file_path, visible=True),
            output_tabs: gr.Tabs(visible=True),
            features_display: features_content,
            architecture_display: architecture_content,
            design_display: design_content,
            user_flow_display: user_flow_content,
            roadmap_display: roadmap_content
        }
        
    except MVPAgentError as e:
        # Our custom errors with user-friendly messages
        error_handler.logger.log_error(e, {"idea": idea[:50]})
        error_msg = f"❌ {e.user_message}\n\nTechnical Details: {e.message}"
        yield {
            status_box: error_msg,
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        return
        
    except ValueError as e:
        # API key / configuration errors
        error_handler.logger.log_error(e, {"context": "configuration"})
        error_msg = f"❌ Configuration Error: {str(e)}\n\nPlease check:\n1. GEMINI_API_KEY is set in .env file\n2. API key is valid and has quota remaining"
        yield {
            status_box: error_msg,
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        return
        
    except Exception as e:
        # Unexpected errors - log and provide helpful message
        error_handler.logger.log_error(e, {"idea": idea[:50], "context": "generate_mvp"})
        error_msg = (
            f"⚠️ Unexpected Error: {str(e)}\n\n"
            f"Don't worry! Your request has been logged.\n"
            f"Please try:\n"
            f"1. Simplifying your idea description\n"
            f"2. Waiting a moment and trying again\n"
            f"3. Checking your internet connection\n\n"
            f"If the problem persists, check the logs/ folder for details."
        )
        yield {
            status_box: error_msg,
            output_tabs: gr.Tabs(visible=False),
            zip_file: gr.File(visible=False),
            features_display: "",
            architecture_display: "",
            design_display: "",
            user_flow_display: "",
            roadmap_display: ""
        }
        return

# Create Gradio interface
with gr.Blocks(css=CUSTOM_CSS, title="MVP Agent", theme=gr.themes.Base()) as demo:
    
    # Header
    # Try to start MCP servers before exposing full UI
    mcp_error_box = gr.Markdown(visible=False)

    gr.Markdown("""
    # 🚀 MVP Agent
    ### AI-powered MVP Blueprint Generator
    Transform your startup idea into a complete, actionable MVP specification in seconds.
    """)
    
    # Input section
    with gr.Row():
        with gr.Column():
            idea_input = gr.Textbox(
                label="Your Startup Idea  (estimated time: 8-10 min)",
                placeholder="e.g., An AI-powered meal planning app that helps busy professionals eat healthier...",
                lines=4,
                elem_id="idea-input"
            )
            generate_btn = gr.Button(
                "🎯 Generate MVP Blueprint",
                variant="primary",
                elem_id="generate-btn"
            )
    
    # Status section
    gr.Markdown("### 🤖 Agent Status")
    status_box = gr.Textbox(
        label="",
        value="Ready to generate your MVP blueprint. Enter your idea above and click the button!",
        lines=10,
        max_lines=20,
        interactive=False,
        elem_id="status-box",
        autoscroll=True
    )
    
    # Download button (initially hidden)
    zip_file = gr.File(
        label="� Download All Files as ZIP",
        visible=False,
        elem_id="download-zip"
    )

    # Output tabs (initially hidden)
    with gr.Tabs(visible=False) as output_tabs:
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
    
    # Footer
    gr.Markdown("""
    ---
    **MCP 1st Birthday** | Track 2: MCP In Action (Agents)  
    Powered by Gemini API and custom internal MCP servers:
    file-manager-mcp, google-search-mcp, markdownify-mcp
    """)

    # Event handler - Production Mode
    generate_btn.click(
        fn=generate_mvp,
        inputs=[idea_input],
        outputs=[
            status_box,
            zip_file,
            output_tabs,
            features_display,
            architecture_display,
            design_display,
            user_flow_display,
            roadmap_display,
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
