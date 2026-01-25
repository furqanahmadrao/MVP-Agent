
This guide will help you get the MVP Agent up and running in just a few minutes.

## Prerequisites

- Docker
- Git

## Installation

1. **Clone the Repository:**
   `bash
   git clone https://github.com/furqanahmadrao/MVP-Agent.git
   cd MVP-Agent
   `

2. **Build the Docker Image:**
   `bash
   docker build -t mvp-agent .
   `

3. **Run the Docker Container:**
   `bash
   docker run -p 7860:7860 mvp-agent
   `

## Usage

1. **Open in Browser:** `http://localhost:7860`
2. **Settings:** Go to the **Settings** tab and enter your **Google Gemini API Key**.
3. **Generator:** Switch to the **Generator** tab.
4. **Input:** Describe your startup idea.
5. **Generate:** Click "Generate Blueprint".
6. **Download:** Once complete, use the **Code Editor** tab to review, edit, and download your files.
