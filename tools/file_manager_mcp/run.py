import os
import io
import zipfile
import time
import re
from pathlib import Path
from typing import List, Optional, Dict
import tempfile

from fastapi import FastAPI
from pydantic import BaseModel, validator
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
    
    @validator('content')
    def validate_content(cls, v):
        MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10MB per file
        if len(v.encode('utf-8')) > MAX_CONTENT_SIZE:
            raise ValueError(f'Content too large (max {MAX_CONTENT_SIZE} bytes)')
        if '\x00' in v:
            raise ValueError('Content contains null bytes')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        # Prevent directory traversal in filename itself
        if '..' in v or '\\' in v.replace('\\', '/'):
            raise ValueError('Invalid filename: contains directory traversal')
        if len(v) > 255:
            raise ValueError('Filename too long (max 255 characters)')
        # Allow alphanumeric, dash, underscore, dot, and forward slash for paths
        if not re.match(r'^[a-zA-Z0-9_\-./]+$', v):
            raise ValueError('Filename contains invalid characters')
        return v


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
        # Security: Resolve absolute path and verify it's within BASE_DIR
        if os.path.isabs(payload.filename):
            target = Path(payload.filename).resolve()
        else:
            target = (BASE_DIR / payload.filename).resolve()
        
        # Security: Verify resolved path is within BASE_DIR
        try:
            target.relative_to(BASE_DIR)
        except ValueError:
            return {
                "success": False,
                "path": payload.filename,
                "message": "Security: Path must be within project directory"
            }
        
        ensure_parent(target)
        target.write_text(payload.content, encoding="utf-8")
        return {
            "success": True,
            "path": str(target),
            "message": "File created successfully."
        }
    except OSError as e:
        return {
            "success": False,
            "path": payload.filename,
            "message": f"Failed to create file: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "path": payload.filename,
            "message": "Internal server error"
        }

@app.post("/create_zip_from_memory")
def create_zip_from_memory(payload: ZipInMemoryRequest):
    try:
        # Security: Limit total size and file count
        MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB
        MAX_FILES = 1000
        
        if len(payload.files) > MAX_FILES:
            return {
                "success": False,
                "path": None,
                "message": f"Too many files (max {MAX_FILES})"
            }
        
        # Calculate total size
        total_size = 0
        for filename, content in payload.files.items():
            content_size = len(content.encode('utf-8'))
            total_size += content_size
            
            if total_size > MAX_TOTAL_SIZE:
                return {
                    "success": False,
                    "path": None,
                    "message": f"Total size exceeds limit ({MAX_TOTAL_SIZE} bytes)"
                }
        
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
    except OSError as e:
        return {
            "success": False,
            "path": None,
            "message": f"File operation failed: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": "Internal server error"
        }


@app.post("/validate_markdown")
def validate_markdown(payload: ValidateMarkdownRequest):
    try:
        # Security: Resolve absolute path and verify it's within BASE_DIR
        if os.path.isabs(payload.filename):
            path = Path(payload.filename).resolve()
        else:
            path = (BASE_DIR / payload.filename).resolve()
        
        # Security: Verify resolved path is within BASE_DIR
        try:
            path.relative_to(BASE_DIR)
        except ValueError:
            return {
                "success": False,
                "path": payload.filename,
                "errors": ["Security: Path must be within project directory"],
                "message": "Invalid markdown file."
            }
        
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
            except OSError as e:
                errors.append(f"Error reading file: {e}")

        return {
            "success": len(errors) == 0,
            "path": str(path),
            "errors": errors,
            "message": "OK" if not errors else "Invalid markdown file."
        }
    except Exception as e:
        return {
            "success": False,
            "path": payload.filename,
            "errors": ["Internal server error"],
            "message": "Invalid markdown file."
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
        
        # Security: Verify zip target is within outputs_dir
        try:
            zip_target.relative_to(outputs_dir)
        except ValueError:
            return {
                "success": False,
                "path": None,
                "message": "Security: Invalid zip target path"
            }
        
        ensure_parent(zip_target)

        with zipfile.ZipFile(zip_target, "w", zipfile.ZIP_DEFLATED) as zipf:
            if target.is_dir():
                # Zip all files under the most recent subdirectory
                # Security: followlinks=False prevents symlink attacks
                for root, _, files in os.walk(target, followlinks=False):
                    for name in files:
                        if name.startswith("."):
                            continue
                        full_path = Path(root) / name
                        
                        # Security: Verify file is still within outputs_dir
                        try:
                            full_path.resolve().relative_to(outputs_dir)
                        except ValueError:
                            continue  # Skip files outside outputs_dir
                        
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
                    # Security: Verify file is within outputs_dir
                    try:
                        target.resolve().relative_to(outputs_dir)
                    except ValueError:
                        return {
                            "success": False,
                            "message": "Security: File outside allowed directory"
                        }
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

    except OSError as e:
        return {
            "success": False,
            "path": None,
            "message": f"File operation failed: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": "Internal server error"
        }


if __name__ == "__main__":
    # Security: Bind to localhost only to prevent network exposure
    # Default port 8081 for file-manager-mcp
    uvicorn.run(app, host="127.0.0.1", port=8081)
