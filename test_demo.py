"""Quick demo to show the editor interface"""
import gradio as gr
from src.editor_page import create_editor_interface
from src.generation_state import get_state_manager

# Create a test session
state_mgr = get_state_manager()
session_id = state_mgr.create_session("AI-powered productivity app")

# Simulate some generation progress
state_mgr.update_status(session_id, "running", 50, "Planning")
state_mgr.update_file(session_id, "product_brief.md", """# Product Brief

## Executive Summary
AI-powered productivity app that helps users manage tasks efficiently.

## Market Analysis
- Target: Remote workers and freelancers
- Market size: $10B
- Key competitors: Todoist, Notion, Asana
""")

state_mgr.update_file(session_id, "prd.md", """# Product Requirements Document

## User Stories
1. As a user, I want to create tasks quickly
2. As a user, I want to track my progress
3. As a user, I want AI suggestions for task prioritization
""")

state_mgr.add_log(session_id, "✅ Product brief generated", "SUCCESS")
state_mgr.add_log(session_id, "📋 Generating PRD...", "INFO")

print(f"Demo session created: {session_id}")
print("Starting editor interface...")

# Create and launch editor
editor = create_editor_interface()
editor.launch(server_name="0.0.0.0", server_port=7861)
