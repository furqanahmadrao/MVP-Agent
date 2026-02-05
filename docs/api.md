# API Reference

MVP Agent v2.0 is primarily a UI-driven application and does not expose a public HTTP API. This reference documents the internal Python interfaces most relevant for extension and integration.

## Workflow entry point

### `create_workflow`

```python
from src.workflow import create_workflow

workflow = create_workflow(api_key="YOUR_KEY")
result = workflow.run(idea="Your startup idea", api_key="YOUR_KEY")
```

**Parameters**

- `api_key` (str): Gemini API key
- `model_name` (str, optional): defaults to `gemini-2.5-flash`

**Returns**

A dictionary containing generated artifacts:

- `overview`
- `product_brief`
- `prd`
- `architecture`
- `user_flow`
- `design_system`
- `roadmap`
- `testing_plan`
- `deployment_guide`

## Settings manager

### `get_settings_mgr`

```python
from src.settings import get_settings_mgr

mgr = get_settings_mgr()
api_key = mgr.get_api_key()
model = mgr.get_model()
```

Provides access to application configuration and persistent settings stored in `user_settings.json`.

## File manager

### `get_file_manager`

```python
from src.file_manager import get_file_manager

manager = get_file_manager()
zip_info = manager.save_mvp_files(files, idea)
```

Creates ZIP archives from in-memory markdown files for download.
