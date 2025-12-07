import os
import io
import zipfile
import time
from pathlib import Path
from typing import List, Optional, Dict
import tempfile

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "outputs"

app = FastAPI(title="file-manager-mcp", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "file-manager-mcp"}


class CreateFileRequest(BaseModel):
    filename: str
    content: str


class ValidateMarkdownRequest(BaseModel):
    filename: str


class ZipFilesRequest(BaseModel):
    source_dir: Optional[str] = None
    zip_path: Optional[str] = None

class ZipInMemoryRequest(BaseModel):
    files: Dict[str, str]
    output_filename: str

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@app.post("/create_file")
def create_file(payload: CreateFileRequest):
    try:
        # Respect existing paths (usually under outputs/)
        target = (BASE_DIR / payload.filename) if not payload.filename.startswith(str(BASE_DIR)) else Path(payload.filename)
        ensure_parent(target)
        target.write_text(payload.content, encoding="utf-8")
        return {
            "success": True,
            "path": str(target),
            "message": "File created successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "path": payload.filename,
            "message": f"Failed to create file: {e}"
        }

@app.post("/create_zip_from_memory")
def create_zip_from_memory(payload: ZipInMemoryRequest):
    try:
        # Use system temp directory
        tmp_dir = tempfile.gettempdir()
        zip_path = os.path.join(tmp_dir, payload.output_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in payload.files.items():
                zipf.writestr(filename, content)
        
        return {
            "success": True,
            "path": zip_path,
            "message": "Zip created successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": f"Failed to create ZIP archive: {e}"
        }


@app.post("/validate_markdown")
def validate_markdown(payload: ValidateMarkdownRequest):
    path = (BASE_DIR / payload.filename) if not payload.filename.startswith(str(BASE_DIR)) else Path(payload.filename)
    errors: List[str] = []

    if not path.exists():
        errors.append("File does not exist.")
    else:
        try:
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                errors.append("File is empty.")
            # Minimal validation only; preserve behavior and avoid heavy deps.
            # Hook point for future markdown linting if needed.
        except UnicodeDecodeError:
            errors.append("File is not valid UTF-8 text.")
        except Exception as e:
            errors.append(f"Error reading file: {e}")

    return {
        "success": len(errors) == 0,
        "path": str(path),
        "errors": errors,
        "message": "OK" if not errors else "Invalid markdown file."
    }


@app.post("/zip_files")
def zip_files(payload: ZipFilesRequest):
    """
    Zip only the most recent run's files under outputs/.

    Behavior:
    - Looks at BASE_DIR / "outputs".
    - Selects the most recently modified entry (subdirectory or file).
    - Zips only that target into outputs/mvp_outputs.zip.
    - Enforces a ~5 second time limit.
    - Always returns a bounded JSON response.
    """
    try:
        start = time.time()
        outputs_dir = (BASE_DIR / "outputs").resolve()

        if not outputs_dir.exists():
            return {
                "success": False,
                "path": None,
                "message": f"Directory '{outputs_dir}' not found."
            }

        # Find most recent candidate (subdir or file) inside outputs/
        candidates = sorted(
            outputs_dir.glob("*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not candidates:
            return {
                "success": False,
                "path": None,
                "message": f"No recent files found in '{outputs_dir}'."
            }

        target = candidates[0]
        zip_target = (outputs_dir / "mvp_outputs.zip").resolve()
        ensure_parent(zip_target)

        with zipfile.ZipFile(zip_target, "w", zipfile.ZIP_DEFLATED) as zipf:
            if target.is_dir():
                # Zip all files under the most recent subdirectory
                for root, _, files in os.walk(target):
                    for name in files:
                        if name.startswith("."):
                            continue
                        full_path = Path(root) / name
                        rel_path = full_path.relative_to(outputs_dir)
                        zipf.write(full_path, arcname=rel_path)

                        if time.time() - start > 5:
                            return {
                                "success": False,
                                "message": "Zipping aborted: took too long."
                            }
            else:
                # Single file case
                if not target.name.startswith("."):
                    zipf.write(target, arcname=target.name)

            if time.time() - start > 5:
                return {
                    "success": False,
                    "message": "Zipping aborted: took too long."
                }

        return {
            "success": True,
            "path": str(zip_target),
            "message": "Zip created successfully."
        }

    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": f"Failed to create ZIP archive: {e}"
        }


if __name__ == "__main__":
    # Default port 8081 for file-manager-mcp
    uvicorn.run(app, host="0.0.0.0", port=8081)
