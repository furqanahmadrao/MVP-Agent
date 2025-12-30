# Enhanced Real-time Editor Feature

## Overview

The MVP Agent now includes an enhanced editor with real-time file updates displayed on a separate tab as files are generated.

## Key Features

### 🔄 Real-time Updates
- Files appear in the editor as soon as they're generated
- No need to wait for the entire generation to complete
- Progress bar shows current phase and percentage
- Live log stream displays agent activities

### 📝 Enhanced Editor Interface
- Separate "Editor" tab in the main interface
- File explorer sidebar showing all generated files
- Syntax-highlighted markdown editor
- Same dark "Code Editor" theme styling
- Download ZIP button appears when generation completes

### 🔐 Session Management
- Each generation creates a unique session with session ID
- Sessions are thread-safe and isolated
- State persists across tab switches
- Automatic cleanup of old sessions (after 1 hour)

## How to Use

1. **Start Generation**
   - Enter your startup idea in the "Generator" tab
   - Click "Generate Blueprint"
   - A link "Open Editor" will appear

2. **Watch Progress**
   - Switch to the "Editor" tab
   - Files will appear as they're generated:
     - Product Brief (Analysis phase)
     - PRD & Tech Spec (Planning phase)
     - Architecture, User Flow, Design System (Solutioning phase)
     - Roadmap, Testing Plan, Deployment Guide (Implementation phase)
     - Overview (Finalization)

3. **View Files**
   - Click any file in the sidebar to view it
   - Files are editable in the editor
   - Progress bar shows current phase

4. **Download**
   - When complete, click "Download ZIP"
   - All files are packaged and ready to download

## Architecture

### Components

- **src/generation_state.py**: Thread-safe session manager
- **src/editor_page.py**: Real-time editor interface with auto-refresh
- **src/workflow.py**: Enhanced with real-time file updates
- **app.py**: Multi-tab interface combining Generator and Editor

### Real-time Updates Flow

```
User starts generation
    ↓
Session created with unique ID
    ↓
Workflow begins
    ↓
Each phase generates files
    ↓
State manager updated immediately
    ↓
Editor polls every 2 seconds
    ↓
New files appear in sidebar
    ↓
User can view/edit files
    ↓
Generation completes
    ↓
Download button appears
```

## Technical Details

### Polling Mechanism
- Editor uses Gradio Timer to poll every 2 seconds
- Polls the state manager for session updates
- Updates UI with new files, progress, and logs

### Thread Safety
- All state manager operations use locks
- Supports concurrent sessions
- No race conditions or data corruption

### Performance
- Lightweight polling (only changed data transmitted)
- In-memory state (no database overhead)
- Session cleanup prevents memory leaks

## Configuration

No additional configuration required. The feature is enabled by default.

To adjust polling interval, modify `editor_page.py`:

```python
refresh_timer = gr.Timer(value=2.0, active=True)  # Change 2.0 to desired seconds
```

## Testing

Run the test suite:

```bash
python -c "
from src.generation_state import get_state_manager
mgr = get_state_manager()
session_id = mgr.create_session('Test idea')
mgr.update_file(session_id, 'test.md', '# Test')
print('✓ Tests passed')
"
```

## Troubleshooting

**Editor not updating?**
- Check that JavaScript is enabled in browser
- Verify session ID is valid
- Ensure generation is still running

**Files not appearing?**
- Check workflow is calling `_update_state_manager()`
- Verify no exceptions in logs
- Check state manager is initialized

## Future Enhancements

- WebSocket streaming (replace polling)
- Collaborative editing (multiple users)
- Version history
- Custom refresh intervals
- Push notifications

## Credits

- Implemented by: GitHub Copilot
- Framework: Gradio 5.49.1
- Architecture: BMAD (Breakthrough Method for Agile AI-Driven Development)

---

For technical documentation, see the inline comments in:
- `src/generation_state.py`
- `src/editor_page.py`
- `src/workflow.py`
