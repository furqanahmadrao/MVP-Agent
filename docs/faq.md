# FAQ

## Do I need a Gemini API key?
Yes. MVP Agent uses Gemini models for generation. Provide a key in the Settings tab or via `GEMINI_API_KEY`.

## Is there a public REST API?
No. The application is UI-first and does not expose a public HTTP API at this time.

## Where are settings stored?
Settings entered in the UI are saved to `user_settings.json` in the repository root.

## Can I customize the output format?
Yes. You can edit generated markdown in the UI and extend the workflow to emit additional artifacts.

## Does MVP Agent store my data?
Outputs are generated in-memory and packaged into a ZIP for download. Long-term persistence is not enabled by default.

## Can I run this offline?
The UI can run offline, but generation requires network access to Gemini.

## How do I change models?
Use the model dropdown in the Settings tab to select between available Gemini models.
