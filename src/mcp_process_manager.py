import subprocess
import sys
import time
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import requests


BASE_DIR = Path(__file__).resolve().parents[1]
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MCPConfig:
    name: str
    command: List[str]
    url: str
    health_path: str = "/health"
    start_timeout: float = 20.0  # seconds


class MCPManager:
    """
    Manages lifecycle of local MCP servers for MVP Agent.

    Responsibilities:
    - Start required MCP servers as subprocesses.
    - Wait for them to become healthy via HTTP checks.
    - Provide structured errors on failure.
    - Terminate all subprocesses on shutdown.

    Designed for:
    - Local dev: single `python app.py` starts everything.
    - Hugging Face Spaces: single-process entrypoint spawning child MCP servers.
    """

    def __init__(self) -> None:
        python_exe = sys.executable or "python"

        # NOTE: Google Search MCP removed in Phase 3 (replaced by Gemini Grounding)
        self.configs: List[MCPConfig] = [
            MCPConfig(
                name="file-manager-mcp",
                command=[python_exe, "-u", "tools/file_manager_mcp/run.py"],
                url="http://127.0.0.1:8081",
            ),
            MCPConfig(
                name="markdownify-mcp",
                command=[python_exe, "-u", "tools/markdownify_mcp/run.py"],
                url="http://127.0.0.1:8083",
            ),
        ]

        # name -> subprocess.Popen
        self.procs: Dict[str, subprocess.Popen] = {}
        # name -> file object (for logs)
        self._log_files: Dict[str, Any] = {}
        self.started: bool = False

    def start_all(self) -> None:
        """
        Start all MCP servers and wait for them to become healthy.

        Raises:
            RuntimeError if any server fails to start or become healthy.
        """
        if self.started:
            return

        errors: List[str] = []

        for cfg in self.configs:
            try:
                self._start_one(cfg)
            except Exception as e:
                errors.append(f"{cfg.name} failed to start: {e}")

        # If any failed at spawn time, bail out immediately
        if errors:
            self.stop_all()
            raise RuntimeError("; ".join(errors))

        # Wait for health for each
        for cfg in self.configs:
            ok, msg = self._wait_healthy(cfg)
            if not ok:
                errors.append(f"{cfg.name} unhealthy: {msg}")

        if errors:
            self.stop_all()
            raise RuntimeError("; ".join(errors))

        self.started = True

    def _start_one(self, cfg: MCPConfig) -> None:
        if cfg.name in self.procs and self.procs[cfg.name].poll() is None:
            # Already running
            return

        log_path = LOGS_DIR / f"{cfg.name}.log"
        # Removed buffering=0 to avoid performance issues and syscall overhead
        log_file = log_path.open("ab")
        
        # Environment: inherit, but ensure we are in project root
        env = os.environ.copy()
        # Start subprocess in BASE_DIR so relative paths in run.py work
        proc = subprocess.Popen(
            cfg.command,
            cwd=str(BASE_DIR),
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        self.procs[cfg.name] = proc
        self._log_files[cfg.name] = log_file

    def _wait_healthy(self, cfg: MCPConfig) -> Tuple[bool, str]:
        """
        Poll server until healthy or timeout.
        """
        deadline = time.time() + cfg.start_timeout
        health_url = cfg.url.rstrip("/") + cfg.health_path

        # If /health 404s, we fallback to root just to confirm it's listening.
        tried_root = False

        while time.time() < deadline:
            proc = self.procs.get(cfg.name)
            if proc is None or proc.poll() is not None:
                # Process exited - read last lines of log for debugging
                log_path = LOGS_DIR / f"{cfg.name}.log"
                error_details = self._read_log_tail(log_path, lines=10)
                return False, f"process exited during startup. Check {log_path}\nLast log lines:\n{error_details}"

            try:
                resp = requests.get(health_url, timeout=1)
                if resp.status_code == 200:
                    return True, "ok"
                # If /health not found, fall back once to /
                if resp.status_code == 404 and not tried_root:
                    tried_root = True
                    root_url = cfg.url
                    try:
                        root_resp = requests.get(root_url, timeout=1)
                        if root_resp.status_code in (200, 404):
                            # Listening; consider healthy for our purposes
                            return True, "ok (no /health, but port open)"
                    except Exception:
                        pass
            except Exception:
                # Not ready yet
                time.sleep(0.5)
                continue

        # Timeout - include log tail for debugging
        log_path = LOGS_DIR / f"{cfg.name}.log"
        error_details = self._read_log_tail(log_path, lines=10)
        return False, f"timeout after {cfg.start_timeout}s waiting for {health_url}. Check {log_path}\nLast log lines:\n{error_details}"
    
    def _read_log_tail(self, log_path: Path, lines: int = 10) -> str:
        """
        Read last N lines of log file for error reporting.
        """
        try:
            if not log_path.exists():
                return "(log file not found)"
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(tail_lines).strip() or "(empty log)"
        except Exception as e:
            return f"(could not read log: {e})"

    def stop_all(self) -> None:
        """
        Terminate all MCP subprocesses gracefully and clean up resources.
        """
        if not self.procs:
            return

        # Phase 1: Send TERM signal
        for name, proc in list(self.procs.items()):
            try:
                if proc.poll() is None:
                    # print(f"[MCP] Terminating {name}...")
                    proc.terminate()
            except Exception as e:
                print(f"[MCP] Error terminating {name}: {e}")

        # Phase 2: Wait for graceful shutdown
        # Allow 2 seconds per process max
        deadline = time.time() + (2 * len(self.procs))
        while time.time() < deadline:
            all_stopped = all(p.poll() is not None for p in self.procs.values())
            if all_stopped:
                break
            time.sleep(0.1)

        # Phase 3: Force kill stragglers
        for name, proc in list(self.procs.items()):
            try:
                if proc.poll() is None:
                    print(f"[MCP] Force killing {name}...")
                    proc.kill()
                    proc.wait(timeout=1)  # Reap zombie
            except Exception as e:
                print(f"[MCP] Error killing {name}: {e}")

        # Phase 4: Close log file handles
        for name, log_file in list(self._log_files.items()):
            try:
                log_file.close()
            except Exception:
                pass
        
        self._log_files.clear()
        self.procs.clear()
        self.started = False
