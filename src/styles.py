"""
Global CSS styles and theme definitions for MVP Agent.
Implements a "Premium High-Tech" aesthetic with deep space greys, vibrant orange accents, 
and professional typography.
"""

THEME_COLORS = """
    /* Primary Palette - Mars Mission Orange */
    --primary-500: #FF6B35;
    --primary-600: #E85A2D;
    --primary-900: #662200;
    --primary-glow: rgba(255, 107, 53, 0.4);

    /* Secondary Palette - Deep Space Blue */
    --secondary-500: #4A90E2;
    --secondary-900: #1A2B45;

    /* Neutrals - Void Greys */
    --bg-dark: #0F1115;      /* Main background - slightly blue-tinted black */
    --bg-panel: #16191D;     /* Sidebar/Panels */
    --bg-card: #1C2026;      /* Cards */
    --bg-input: #121418;     /* Inputs */
    
    --border-subtle: #2A303C;
    --border-light: #3E4552;
    
    --text-main: #ECEFF4;
    --text-muted: #949BA6;
    --text-dim: #5C6370;

    /* Semantic */
    --success: #05D588;
    --warning: #F2C94C;
    --error: #FF4D4D;
    --info: #2F80ED;
"""

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    """ + THEME_COLORS + """
    --font-main: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
    
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.3);
    --shadow-glow: 0 0 20px var(--primary-glow);
}

body, .gradio-container {
    background-color: var(--bg-dark) !important;
    color: var(--text-main) !important;
    font-family: var(--font-main) !important;
}

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-main);
}

code, kbd, pre, .font-mono {
    font-family: var(--font-mono) !important;
}

/* --- Layout Components --- */

/* Header */
.header-container {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(74, 144, 226, 0.05));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 30px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.header-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: var(--primary-500);
}

.header-container h1 {
    font-size: 2.2em;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #fff, #ccc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-container p {
    color: var(--text-muted);
    font-size: 1.1em;
    max-width: 600px;
    line-height: 1.6;
}

/* Cards */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 24px;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--border-light);
}

.info-card h3 {
    color: var(--primary-500);
    font-size: 1.25rem;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.info-card ul li {
    position: relative;
    padding-left: 24px;
    margin-bottom: 12px;
    color: var(--text-muted);
}

.info-card ul li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--secondary-500);
}

/* --- Interactive Elements --- */

/* Primary Button */
#generate-btn {
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    padding: 16px 32px !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-glow) !important;
    transition: all 0.2s ease !important;
}

#generate-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(255, 107, 53, 0.6) !important;
}

#generate-btn:active {
    transform: translateY(0) !important;
}

/* Inputs */
textarea, input[type="text"], .gr-input {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-main) !important;
    font-family: var(--font-main) !important;
    transition: all 0.2s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: var(--primary-500) !important;
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2) !important;
}

/* Tabs */
.tabs {
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 20px;
}

.tab-nav button {
    font-weight: 500;
    color: var(--text-muted);
    border: none;
    background: transparent;
}

.tab-nav button.selected {
    color: var(--primary-500);
    border-bottom: 2px solid var(--primary-500);
}

/* --- Phase Indicator --- */
.phase-indicator {
    display: flex;
    gap: 12px;
    background: var(--bg-panel);
    padding: 16px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
}

.phase-step {
    flex: 1;
    text-align: center;
    padding: 12px;
    border-radius: var(--radius-sm);
    background: var(--bg-card);
    border: 1px solid transparent;
    transition: all 0.3s ease;
    opacity: 0.5;
}

.phase-step.active {
    opacity: 1;
    border-color: var(--primary-500);
    background: rgba(255, 107, 53, 0.1);
    box-shadow: 0 0 15px rgba(255, 107, 53, 0.15);
}

.phase-step.completed {
    opacity: 1;
    border-color: var(--success);
    color: var(--success);
}

/* --- Terminal/Logs --- */
#terminal-log {
    background-color: #0d0e10 !important;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    padding: 16px;
    height: 300px;
    overflow-y: auto;
}

.log-entry {
    margin-bottom: 6px;
    border-left: 2px solid transparent;
    padding-left: 10px;
}

.log-entry:hover {
    background: rgba(255,255,255,0.03);
}

.log-info { color: var(--secondary-500); }
.log-success { color: var(--success); }
.log-warning { color: var(--warning); }
.log-error { color: var(--error); }

/* --- Sidebar (Editor) --- */
.sidebar-container {
    background-color: var(--bg-panel);
    border-right: 1px solid var(--border-subtle);
    padding: 16px;
    height: 100%;
}

.file-btn {
    width: 100%;
    text-align: left;
    padding: 10px 14px;
    margin-bottom: 4px;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-muted);
    border: 1px solid transparent;
    transition: all 0.2s;
    font-size: 0.9rem;
}

.file-btn:hover {
    background: var(--bg-card);
    color: var(--text-main);
}

.file-btn.selected {
    background: rgba(255, 107, 53, 0.1);
    color: var(--primary-500);
    border-color: rgba(255, 107, 53, 0.2);
    font-weight: 600;
}

.file-badge {
    font-size: 0.7em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    margin-left: 8px;
    letter-spacing: 0.5px;
}

.badge-analysis { color: var(--secondary-500); background: rgba(74, 144, 226, 0.1); }
.badge-planning { color: var(--success); background: rgba(5, 213, 136, 0.1); }
.badge-solution { color: var(--warning); background: rgba(242, 201, 76, 0.1); }
.badge-implementation { color: var(--primary-500); background: rgba(255, 107, 53, 0.1); }

/* --- Scrollbars --- */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-500);
}

/* --- Gradio Overrides --- */
.block.padded {
    padding: 0 !important;
}

.accordion {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
}

/* Animations */
@keyframes pulse-glow {
    0% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 107, 53, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0); }
}

.pulse {
    animation: pulse-glow 2s infinite;
}
"""
