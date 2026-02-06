"""
File Manager Module - Handles saving and managing generated MVP files
"""

import os
import io
import shutil
import zipfile
import tempfile
import re
import threading
from typing import Dict, Optional, Tuple
from datetime import datetime

from .mcp_http_clients import FileManagerMCPClient


def sanitize_markdown(content: str) -> str:
    """
    Sanitize markdown content by removing invisible/control characters.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Sanitized markdown content
    """
    if not content:
        return content
    
    # Remove common invisible characters (zero-width spaces, BOM, etc.)
    # Keep newlines, tabs, and standard spaces
    sanitized = content.replace('\ufeff', '')  # BOM
    sanitized = sanitized.replace('\u200b', '')  # Zero-width space
    sanitized = sanitized.replace('\u200c', '')  # Zero-width non-joiner
    sanitized = sanitized.replace('\u200d', '')  # Zero-width joiner
    sanitized = sanitized.replace('\ufffe', '')  # Reverse BOM
    
    # Remove any other control characters except newline, carriage return, and tab
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
    
    # Normalize line endings to \n
    sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n')
    
    return sanitized


class FileManager:
    """Manages saving MVP files - uses in-memory ZIP for HF Spaces compatibility"""
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize file manager
        
        Args:
            output_dir: Directory to save files (default: outputs/) - NOT USED in production
        """
        self.output_dir = output_dir
        self.mcp_client = FileManagerMCPClient()
        # No longer creating output directory - we use temp files instead
    
    def create_zip_in_memory(self, files: Dict[str, str], idea: str) -> str:
        """
        Create a temporary ZIP file from generated content.
        The ZIP file is stored in system temp directory and will be auto-cleaned.
        
        Args:
            files: Dictionary with file contents (keys: features_md, architecture_md, etc.)
            idea: The startup idea (used for naming)
            
        Returns:
            Path to temporary ZIP file (will be auto-deleted by OS)
        """
        # Prepare file content
        zip_content = {}
        
        # File mapping - updated with new documents
        file_names = {
            "overview_md": "overview.md",
            "product_brief": "product_brief.md",
            "prd": "prd.md",
            "tech_spec": "tech_spec.md",
            "feature_prioritization": "feature_prioritization.md",
            "competitive_analysis": "competitive_analysis.md",
            "architecture": "architecture.md",
            "user_flow": "user_flow.md",
            "design_system": "design_system.md",
            "roadmap": "roadmap.md",
            "testing_plan": "testing_plan.md",
            "deployment_guide": "deployment_guide.md",
            "business_model": "financial_model.md"
        }
        
        # Add all markdown files (sanitized)
        for key, filename in file_names.items():
            if key in files:
                # Sanitize content before writing
                zip_content[filename] = sanitize_markdown(files[key])
        
        # Add README
        readme_content = f"""# MVP Blueprint - Professional PRD

**Idea:** {idea}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📚 Documents Included

### Phase 1: Analysis & Research
- **product_brief.md** - Market analysis, competitors, user personas, and value proposition
- **financial_model.md** - Revenue projections, unit economics, burn rate, and funding requirements

### Phase 2: Planning & Strategy
- **prd.md** - Product Requirements Document with functional/non-functional requirements
- **tech_spec.md** - Technical specification and implementation approach
- **feature_prioritization.md** - RICE scoring, MoSCoW prioritization, and value vs. effort matrix
- **competitive_analysis.md** - Feature-by-feature comparison with competitors

### Phase 3: Solution Design
- **architecture.md** - System architecture, tech stack, database schema, and API design
- **user_flow.md** - User journeys, wireframes, and interaction patterns
- **design_system.md** - UI/UX guidelines, colors, typography, and component library

### Phase 4: Implementation & Launch
- **roadmap.md** - Sprint breakdown, timeline, and milestones
- **testing_plan.md** - QA strategy, test cases, and quality metrics
- **deployment_guide.md** - Infrastructure, CI/CD, and deployment instructions

## 🚀 Quick Start

1. Read **product_brief.md** first to understand the market opportunity
2. Review **feature_prioritization.md** to see which features to build first
3. Follow **prd.md** and **tech_spec.md** for detailed requirements
4. Use **architecture.md** and **user_flow.md** for implementation
5. Execute **roadmap.md** sprint-by-sprint

## 💡 How to Use

This blueprint is designed for:
- **Developers**: Use tech_spec.md and architecture.md to start coding
- **Designers**: Use user_flow.md and design_system.md for UI/UX
- **Product Managers**: Use prd.md and feature_prioritization.md for planning
- **Investors**: Use product_brief.md and financial_model.md for pitch

## 🤖 AI Agent Ready

All documents include "Agent Guidance" sections to help AI coding agents understand context and implement correctly.

---
*Generated by MVP Agent v2.0 - BMAD Edition*
*Following GitHub Spec Kit methodology and BMAD best practices*
"""
        zip_content["README.md"] = readme_content

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_idea = "".join(c for c in idea[:30] if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_idea = safe_idea.replace(" ", "_") or "mvp"
        zip_filename = f'mvp_{safe_idea}_{timestamp}.zip'

        # Try MCP first
        try:
            resp = self.mcp_client.create_zip_from_memory(zip_content, zip_filename)
            if resp.get("success") and resp.get("path"):
                print(f"✅ Successfully created ZIP via MCP: {resp.get('path')}")
                return resp.get("path")
            else:
                print(f"⚠️ MCP ZIP creation failed: {resp.get('message')}. Falling back to local.")
        except Exception as e:
             print(f"⚠️ MCP ZIP creation error: {e}. Falling back to local.")

        # Fallback: Create temp file locally
        temp_zip = tempfile.NamedTemporaryFile(
            mode='w+b',
            suffix='.zip',
            prefix=f'mvp_{safe_idea}_{timestamp}_',
            delete=False  # We'll let Gradio handle deletion after download
        )
        temp_zip.close()  # Close it so we can write to it with zipfile
        
        # Create ZIP in the temp file with atomic write
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in zip_content.items():
                zipf.writestr(filename, content)
        
        print(f"✅ Successfully created ZIP locally: {temp_zip.name}")
        return temp_zip.name
    
    def save_mvp_files(self, files: Dict[str, str], idea: str) -> Dict[str, str]:
        """
        Create in-memory ZIP file for download.
        NO persistent storage - perfect for Hugging Face Spaces.
        
        Args:
            files: Dictionary with file contents (keys: features_md, architecture_md, etc.)
            idea: The startup idea (used for naming)
            
        Returns:
            Dictionary with 'zip' key pointing to temporary file path
        """
        # Create temporary ZIP file
        zip_path = self.create_zip_in_memory(files, idea)
        
        return {
            "zip": zip_path,
            "directory": "temp",  # No actual directory
        }
    
    def get_latest_mvp_dir(self) -> str:
        """
        Deprecated - not used with in-memory ZIP approach.
        Returns empty string.
        """
        return ""

# Singleton instance
_file_manager = None
_file_manager_lock = threading.Lock()

def get_file_manager() -> FileManager:
    """Get or create the file manager singleton"""
    global _file_manager
    if _file_manager is None:
        with _file_manager_lock:
            if _file_manager is None:
                _file_manager = FileManager()
    return _file_manager
