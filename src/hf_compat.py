"""
Compatibility shim for Gradio's legacy Hugging Face OAuth usage.

Some Gradio versions import:

    from huggingface_hub import HfFolder, whoami

But newer huggingface_hub versions removed or relocated HfFolder.
This module ensures HfFolder is available so that Gradio imports succeed,
without requiring fragile global version pinning.

Behavior:
- If huggingface_hub already provides HfFolder, this is a no-op.
- Otherwise, defines a minimal HfFolder with:
    - get_token(): read from env HF_TOKEN or ~/.huggingface/token
    - save_token(token): write to ~/.huggingface/token
"""

import os
from pathlib import Path

try:
    # If this works, we are on a compatible hub; nothing else to do.
    from huggingface_hub import HfFolder as _ExistingHfFolder  # type: ignore  # noqa:F401
except ImportError:
    # Define a minimal drop-in replacement.
    class HfFolder:  # type: ignore
        _TOKEN_PATH = Path.home() / ".huggingface" / "token"

        @classmethod
        def get_token(cls) -> str | None:
            # Priority: explicit env var if set
            token = os.environ.get("HF_TOKEN")
            if token:
                return token.strip() or None

            try:
                if cls._TOKEN_PATH.is_file():
                    return cls._TOKEN_PATH.read_text(encoding="utf-8").strip() or None
            except Exception:
                return None
            return None

        @classmethod
        def save_token(cls, token: str) -> None:
            try:
                cls._TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                cls._TOKEN_PATH.write_text(token.strip(), encoding="utf-8")
            except Exception:
                # Best-effort; silently ignore IO errors.
                pass

    # Expose HfFolder in huggingface_hub namespace if possible
    try:
        import huggingface_hub

        if not hasattr(huggingface_hub, "HfFolder"):
            setattr(huggingface_hub, "HfFolder", HfFolder)
    except Exception:
        # If we cannot modify the module, Gradio will still be able to import from this shim
        pass
