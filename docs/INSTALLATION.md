
There are two ways to install and run the MVP Agent: using Docker (recommended) or setting up a local development environment.

## Option A: Docker (Recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

### Instructions

1.  **Clone the Repository:**
    `bash
    git clone https://github.com/furqanahmadrao/MVP-Agent.git
    cd MVP-Agent
    `

2.  **Build the Docker Image:**
    `bash
    docker build -t mvp-agent .
    `

3.  **Run the Docker Container:**
    `bash
    docker run -p 7860:7860 mvp-agent
    `

4.  **Open in Browser:** `http://localhost:7860`

## Option B: Local Installation

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Instructions

1.  **Clone the Repository:**
    `bash
    git clone https://github.com/furqanahmadrao/MVP-Agent.git
    cd MVP-Agent
    `

2.  **Install Dependencies:**
    `bash
    pip install -r requirements.txt
    `

3.  **Run the Application:**
    `bash
    python app.py
    `
