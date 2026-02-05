# Configuration

MVP Agent can be configured through environment variables or the in-app Settings UI.

## Settings UI

The **Settings** tab persists configuration in `user_settings.json` at the repository root. This file is loaded on startup and overrides environment variables where applicable.

## Environment variables

| Variable | Description | Required |
| --- | --- | --- |
| `GEMINI_API_KEY` | API key for Google Gemini | Yes (unless saved in settings) |

## Application settings

| Setting | Description | Default |
| --- | --- | --- |
| `gemini_api_key` | API key stored in `user_settings.json` | Empty |
| `model_name` | Gemini model selection | `gemini-2.5-flash` |
| `use_toon_format` | Token optimization via TOON | `true` |
| `project_level_auto_detect` | Auto-detect complexity | `true` |
| `language` | Output language preference | `English` |
| `theme` | UI theme preference | `Dark` |

## Model selection

The model dropdown provides several Gemini options. Use **Pro** for quality and **Flash** for speed and cost optimization.

## Project complexity

The project complexity slider (0-4) influences the depth and detail of generated artifacts. If auto-detect is enabled, the system infers a level based on the prompt.
