
The MVP Agent can be configured via the UI or a `.env` file.

## UI Configuration

The following settings can be configured in the **Settings** tab of the UI:

-   **Google Gemini API Key:** Your Google GenAI key. This is required to use the application.
-   **Model:** The AI model to use for generating documents. You can choose between `gemini-1.5-flash` and `gemini-1.5-pro`.
-   **TOON Format:** Enable or disable the use of TOON (Token-Oriented Object Notation) format, which can reduce token usage by 30-60%.
-   **Auto-Detect Project Level:** Enable or disable automatic complexity estimation.

## .env File Configuration
` + "```" + `
GEMINI_API_KEY=your_api_key
USE_TOON_FORMAT=True
PROJECT_LEVEL_AUTO_DETECT=True
` + "```" + `

-   `GEMINI_API_KEY`: Your Google GenAI key.
-   `USE_TOON_FORMAT`: Set to `True` to enable token optimization.
-   `PROJECT_LEVEL_AUTO_DETECT`: Enable automatic complexity estimation.
