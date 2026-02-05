"""
Shared state manager for real-time generation updates across pages.
This allows the editor page to poll for updates while generation is running.
"""

import threading
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class GenerationSession:
    """Represents a single generation session."""
    session_id: str
    idea: str
    start_time: float = field(default_factory=time.time)
    status: str = "initializing"  # initializing, running, completed, error
    progress: int = 0  # 0-100
    current_phase: str = ""
    files: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    
class GenerationStateManager:
    """Thread-safe manager for generation sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, GenerationSession] = {}
        self._lock = threading.Lock()
        self._current_session_id: Optional[str] = None
    
    def create_session(self, idea: str) -> str:
        """Create a new generation session and return its ID."""
        session_id = f"gen_{int(time.time() * 1000)}"
        
        with self._lock:
            session = GenerationSession(
                session_id=session_id,
                idea=idea,
                files={
                    "overview.md": "# Project Overview\n\n⏳ Generating...",
                    "product_brief.md": "⏳ Generating...",
                    "prd.md": "⏳ Generating...",
                    "architecture.md": "⏳ Generating...",
                    "user_flow.md": "⏳ Generating...",
                    "design_system.md": "⏳ Generating...",
                    "roadmap.md": "⏳ Generating...",
                    "testing_plan.md": "⏳ Generating...",
                    "deployment_guide.md": "⏳ Generating...",
                }
            )
            self._sessions[session_id] = session
            self._current_session_id = session_id
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[GenerationSession]:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current active session ID."""
        with self._lock:
            return self._current_session_id
    
    def update_status(self, session_id: str, status: str, progress: int = None, phase: str = None):
        """Update session status."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = status
                if progress is not None:
                    session.progress = progress
                if phase is not None:
                    session.current_phase = phase
    
    def update_file(self, session_id: str, filename: str, content: str):
        """Update a file in the session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.files[filename] = content
    
    def add_log(self, session_id: str, message: str, log_type: str = "INFO"):
        """Add a log entry to the session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.logs.append({
                    "timestamp": time.time(),
                    "message": message,
                    "type": log_type
                })
    
    def set_error(self, session_id: str, error: str):
        """Set an error on the session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = "error"
                session.error = error
                self.add_log(session_id, f"Error: {error}", "ERROR")
    
    def complete_session(self, session_id: str, final_files: Dict[str, str]):
        """Mark session as complete and update all files."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = "completed"
                session.progress = 100
                session.files.update(final_files)
                self.add_log(session_id, "🎉 Generation complete!", "SUCCESS")
    
    def cleanup_old_sessions(self, max_age_seconds: int = 3600):
        """Clean up sessions older than max_age_seconds."""
        current_time = time.time()
        with self._lock:
            to_remove = [
                sid for sid, session in self._sessions.items()
                if current_time - session.start_time > max_age_seconds
            ]
            for sid in to_remove:
                del self._sessions[sid]

# Singleton instance
_state_manager = None

def get_state_manager() -> GenerationStateManager:
    """Get the singleton state manager."""
    global _state_manager
    if _state_manager is None:
        _state_manager = GenerationStateManager()
    return _state_manager
