import subprocess
import sys
import time
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

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

        self.configs: List[MCPConfig] = [
            MCPConfig(
                name="file-manager-mcp",
                command=[python_exe, "-u", "tools/file_manager_mcp/run.py"],
                url="http://127.0.0.1:8081",
            ),
            MCPConfig(
                name="google-search-mcp",
                command=[python_exe, "-u", "tools/google_search_mcp/run.py"],
                url="http://127.0.0.1:8082",
            ),
            MCPConfig(
                name="markdownify-mcp",
                command=[python_exe, "-u", "tools/markdownify_mcp/run.py"],
                url="http://127.0.0.1:8083",
            ),
        ]

        # name -> subprocess.Popen
        self.procs: Dict[str, subprocess.Popen] = {}
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

        log_file = (LOGS_DIR / f"{cfg.name}.log").open("ab", buffering=0)
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

    def _wait_healthy(self, cfg: MCPConfig) -> (bool, str):
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
        Terminate all MCP subprocesses gracefully.
        """
        for name, proc in list(self.procs.items()):
            try:
                if proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass

        # Give them a moment to exit, then kill if needed
        deadline = time.time() + 5
        for name, proc in list(self.procs.items()):
            if proc.poll() is None and time.time() < deadline:
                time.sleep(0.2)

        for name, proc in list(self.procs.items()):
            try:
                if proc.poll() is None:
                    proc.kill()
            except Exception:
                pass

        self.procs.clear()
        self.started = False
