import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import textwrap

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="CueBand | AI Assistive Interface",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SYSTEM-WIDE HELPER FUNCTIONS (PREVENT INDENT CODE BLOCK BUG)
# ============================================================
def safe_html(html_code):
    """Renders HTML safely to prevent Streamlit from interpreting leading space as a code block."""
    try:
        st.html(textwrap.dedent(html_code).strip())
    except AttributeError:
        st.markdown(textwrap.dedent(html_code).strip(), unsafe_allow_html=True)

# ============================================================
# HAPTIC WAVEFORM GENERATORS (NUMPY BASED PHYSICAL PATTERNS)
# ============================================================
def generate_nod_pattern():
    """Double short pulse representing agree/nod (180Hz frequency, 400ms duration)"""
    t = np.linspace(0, 400, 400)
    s = np.zeros_like(t)
    # First pulse (50ms - 150ms)
    s[(t >= 50) & (t <= 150)] = 0.85 * np.sin((t[(t >= 50) & (t <= 150)] - 50) * np.pi / 100)
    # Second pulse (250ms - 350ms)
    s[(t >= 250) & (t <= 350)] = 0.85 * np.sin((t[(t >= 250) & (t <= 350)] - 250) * np.pi / 100)
    return t, s

def generate_smile_pattern():
    """Smooth sine surge representing smile (150Hz frequency, 600ms duration)"""
    t = np.linspace(0, 600, 600)
    s = np.zeros_like(t)
    # Warm sine rise and fall (100ms - 500ms)
    s[(t >= 100) & (t <= 500)] = 0.60 * np.sin((t[(t >= 100) & (t <= 500)] - 100) * np.pi / 400)
    return t, s

def generate_gaze_left():
    """Left channel activation shifting to right (150Hz frequency, 800ms duration)"""
    t = np.linspace(0, 800, 800)
    s = np.zeros_like(t)
    # Peaks early (100ms - 500ms)
    s[(t >= 100) & (t <= 500)] = 0.70 * np.sin((t[(t >= 100) & (t <= 500)] - 100) * np.pi / 400)
    return t, s

def generate_gaze_right():
    """Right channel activation shifting from left (150Hz frequency, 800ms duration)"""
    t = np.linspace(0, 800, 800)
    s = np.zeros_like(t)
    # Peaks late (300ms - 700ms)
    s[(t >= 300) & (t <= 700)] = 0.70 * np.sin((t[(t >= 300) & (t <= 700)] - 300) * np.pi / 400)
    return t, s

def generate_reduced_pattern():
    """Muted faint pulse representing decreased response (120Hz frequency, 300ms duration)"""
    t = np.linspace(0, 300, 300)
    s = np.zeros_like(t)
    # Very gentle, low amplitude bump (100ms - 200ms)
    s[(t >= 100) & (t <= 200)] = 0.30 * np.sin((t[(t >= 100) & (t <= 200)] - 100) * np.pi / 100)
    return t, s

def generate_confusion_pattern():
    """Erratic high-frequency jagged bursts representing confusion (220Hz frequency, 700ms duration)"""
    t = np.linspace(0, 700, 700)
    s = np.zeros_like(t)
    # Jagged erratic waveform (150ms - 550ms)
    s_core = 0.50 * np.sin((t[(t >= 150) & (t <= 550)] - 150) * 2 * np.pi * 12 / 400) * np.sin((t[(t >= 150) & (t <= 550)] - 150) * np.pi / 400)
    # Add random micro-peaks to simulate confusion
    np.random.seed(42)
    s_noise = 0.15 * np.random.uniform(-1, 1, size=len(s_core))
    s[(t >= 150) & (t <= 550)] = np.clip(s_core + s_noise, 0, 0.75)
    return t, s

# ============================================================
# GLOBAL CSS THEME SYSTEM (ICY TECH WHITE THEME)
# ============================================================
safe_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

/* Global Light Theme Reset */
.stApp {
    font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    background-color: #f8fafc !important;
    background-image: 
        linear-gradient(rgba(79, 70, 229, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79, 70, 229, 0.02) 1px, transparent 1px) !important;
    background-size: 32px 32px !important;
    color: #0f172a !important;
}

h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #0f172a !important;
}

/* Brand Header formatting */
.brand-header {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 0.2rem;
    border-bottom: none !important;
}
.brand-logo {
    margin-right: 15px;
}
.brand-title {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}
.brand-subtitle {
    font-size: 0.95rem;
    color: #64748b !important;
    font-weight: 500;
    margin-left: 12px;
    padding-left: 12px;
    border-left: 2px solid rgba(79, 70, 229, 0.2);
}

/* Sidebar Brand styles */
.sidebar-brand {
    text-align: center;
    padding: 1.8rem 0 1.2rem 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}
.sidebar-title {
    font-size: 1.45rem;
    font-weight: 900;
    color: #2563eb !important;
    letter-spacing: -0.5px;
}
.sidebar-subtitle {
    font-size: 0.8rem;
    color: #64748b !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Glassmorphism Cards */
.glass-card, .metric-card, .component-card, .lra-card, .info-box {
    background: rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 20px !important;
    padding: 1.8rem !important;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.02),
                0 0 15px 0 rgba(37, 99, 235, 0.02) !important;
    color: #0f172a !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.glass-card:hover, .metric-card:hover, .component-card:hover, .lra-card:hover {
    transform: translateY(-4px) !important;
    background: rgba(255, 255, 255, 0.8) !important;
    border-color: rgba(37, 99, 235, 0.3) !important;
    box-shadow: 0 15px 35px 0 rgba(37, 99, 235, 0.08),
                0 0 20px 0 rgba(37, 99, 235, 0.04) !important;
}

/* Research Callout Box */
.research-title-box {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.7) 0%, rgba(248, 250, 252, 0.6) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    border-left: 6px solid #2563eb !important;
    border-radius: 20px !important;
    padding: 2rem 2.2rem !important;
    margin-bottom: 2.5rem !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02) !important;
}
.research-title-label {
    font-size: 0.8rem;
    font-weight: 800;
    color: #2563eb !important;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 0.6rem;
    display: block;
}
.research-title-content {
    font-size: 1.7rem;
    font-weight: 900;
    color: #0f172a !important;
    line-height: 1.4;
    letter-spacing: -0.5px;
}

.section-header {
    border-left: 4px solid #2563eb;
    padding-left: 1.2rem;
    margin: 3rem 0 1.8rem 0;
}
.section-header h2 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 900;
    color: #0f172a !important;
    letter-spacing: -0.5px;
}

/* Tech Spec List items */
.spec-item {
    background: rgba(248, 250, 252, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: all 0.25s ease;
}
.spec-item:hover {
    background: white;
    transform: translateX(4px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
}
.spec-circle {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #2563eb;
    box-shadow: 0 0 8px #2563eb;
}
.spec-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.spec-value {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1e293b;
    margin-top: 2px;
}

/* Tabs and Tables */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(241, 245, 249, 0.6);
    padding: 6px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.8);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 800;
    color: #475569 !important;
    background-color: transparent;
    border: none;
    transition: all 0.25s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(255, 255, 255, 0.8);
    color: #2563eb !important;
}
.stTabs [aria-selected="true"] {
    background-color: white !important;
    color: #2563eb !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02) !important;
}

.stDataFrame {
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

/* Sidebar Custom Tech Slider Styling */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    border-right: 1px solid rgba(79, 70, 229, 0.08) !important;
    width: 65px !important;
    min-width: 65px !important;
    max-width: 65px !important;
    transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    overflow-x: hidden !important;
    z-index: 100;
}
section[data-testid="stSidebar"]:hover {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
}

section[data-testid="stSidebar"] > div {
    opacity: 0;
    transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    pointer-events: none;
}
section[data-testid="stSidebar"]:hover > div {
    opacity: 1;
    pointer-events: auto;
}

section[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    top: 25px;
    left: 20px;
    width: 25px;
    height: 25px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%232563eb' stroke-width='2.5'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M4 6h16M4 12h16m-7 6h7'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    transition: opacity 0.2s ease;
    pointer-events: none;
    opacity: 1;
}
section[data-testid="stSidebar"]:hover::after {
    opacity: 0;
}

.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(79, 70, 229, 0.1), transparent);
    margin: 2rem 0;
}

.stRadio div[role="radiogroup"] {
    gap: 6px;
}
.stRadio div[role="radiogroup"] label {
    background: rgba(248, 250, 252, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    padding: 12px 18px !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.stRadio div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(37, 99, 235, 0.2) !important;
    transform: translateY(-1px);
}
.stRadio div[role="radiogroup"] [data-checked="true"] {
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
    border-color: #2563eb !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.15) !important;
}
.stRadio div[role="radiogroup"] [data-checked="true"] span {
    color: white !important;
}

.footer {
    text-align: center;
    padding: 3rem;
    color: #64748b !important;
    font-size: 0.85rem;
    border-top: 1px solid rgba(79, 70, 229, 0.08);
    margin-top: 5rem;
}
</style>
""")

# ============================================================
# HIGH FIDELITY SVG LOGO GENERATOR
# ============================================================
def get_logo_svg(size=44):
    """Returns circular high-tech vector logo markup without any newlines or indentation inside blocks."""
    svg = f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" class="brand-logo" style="vertical-align: middle;">'
    svg += '<defs>'
    svg += '<linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
    svg += '<stop offset="0%" stop-color="#2563eb" />'
    svg += '<stop offset="100%" stop-color="#06b6d4" />'
    svg += '</linearGradient>'
    svg += '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
    svg += '<feGaussianBlur stdDeviation="3" result="blur" />'
    svg += '<feComposite in="SourceGraphic" in2="blur" operator="over" filter="url(#glow)" />'
    svg += '</filter>'
    svg += '</defs>'
    svg += '<circle cx="50" cy="50" r="44" stroke="rgba(37, 99, 235, 0.1)" stroke-width="2" fill="none" />'
    svg += '<circle cx="50" cy="50" r="38" stroke="url(#logoGrad)" stroke-width="1.5" stroke-dasharray="8 6 15 4" fill="none" opacity="0.8" />'
    svg += '<path d="M 28,50 A 22,22 0 0,1 72,50" stroke="#2563eb" stroke-width="4.5" fill="none" stroke-linecap="round" />'
    svg += '<path d="M 18,50 A 32,32 0 0,0 82,50" stroke="#06b6d4" stroke-width="3" stroke-dasharray="8 6" fill="none" stroke-linecap="round" />'
    svg += '<circle cx="50" cy="50" r="10" fill="url(#logoGrad)" />'
    svg += '<circle cx="50" cy="50" r="4" fill="#ffffff" />'
    svg += '</svg>'
    return svg

def render_brand_header(title, subtitle="", is_home=False):
    if is_home:
        logo = get_logo_svg(69)
        title_style = 'font-size: 3.3rem; font-weight: 900; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -1px; display: inline-block; vertical-align: middle;'
        subtitle_style = 'font-size: 1.425rem; color: #64748b !important; font-weight: 500; margin-left: 18px; padding-left: 18px; border-left: 3px solid rgba(79, 70, 229, 0.2); display: inline-block; vertical-align: middle; line-height: 1.2;'
        html = f'<div class="brand-header" style="margin-bottom: 2.5rem; border-bottom: none !important; padding-bottom: 0.2rem; display: flex; align-items: center; flex-wrap: wrap; gap: 10px;">{logo}<span style="{title_style}">{title}</span>'
        if subtitle:
            html += f'<span style="{subtitle_style}">{subtitle}</span>'
        html += '</div>'
    else:
        logo = get_logo_svg(46)
        html = f'<div class="brand-header" style="border-bottom: none !important; padding-bottom: 0.2rem;">{logo}<span class="brand-title">{title}</span>'
        if subtitle:
            html += f'<span class="brand-subtitle">{subtitle}</span>'
        html += '</div>'
    safe_html(html)

def render_divider():
    safe_html('<div class="custom-divider"></div>')

def render_section_header(title):
    safe_html(f'<div class="section-header"><h2>{title}</h2></div>')

# ============================================================
# PAGE 1: HOME - IMMERSIVE 3D SIMULATION CANVAS AT TOP
# ============================================================
def page_home():
    # IMMERSIVE IMMEDIATE ANIMATION CANVAS AT TOP - OCCUPIES 100% WIDTH
    # 3D radial skin gradients and neat hair cap models styled after the user's photo
    html_widget_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Noto+Sans+KR:wght@400;700&display=swap');
    
    body {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        margin: 0;
        padding: 0;
        background: transparent;
        display: flex;
        flex-direction: column;
        height: 700px;
        color: #0f172a;
        overflow: hidden;
    }
    
    /* Massive Immersive Canvas */
    .canvas-container {
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 28px;
        position: relative;
        box-shadow: 0 10px 40px rgba(31, 38, 135, 0.03);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        overflow: hidden;
        padding: 20px;
        box-sizing: border-box;
    }
    
    .scene {
        width: 100%;
        height: 480px;
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 40px;
        box-sizing: border-box;
    }

    .svg-scene-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
    }

    /* Hotspot Tag Labels */
    .device-tag {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        background: #2563eb;
        color: white;
        font-size: 11px;
        font-weight: 800;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        border: 1.5px solid white;
        cursor: pointer;
        transition: all 0.25s ease;
        letter-spacing: 0.5px;
        pointer-events: auto;
        box-sizing: border-box;
    }
    .device-tag:hover {
        transform: scale(1.05) translateY(-2px);
        background: #06b6d4;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }

    /* Timeline Indicator HUD */
    .timeline-hud {
        width: 100%;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(0,0,0,0.03);
        border-radius: 18px;
        padding: 14px 28px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
    }
    .hud-step {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 800;
        color: #94a3b8;
        transition: all 0.3s ease;
    }
    .hud-step.active {
        color: #2563eb;
    }
    .hud-step-num {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #475569;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }
    .hud-step.active .hud-step-num {
        background: #2563eb;
        color: white;
        box-shadow: 0 0 10px rgba(37,99,235,0.4);
    }
    
    /* Latency Counter Overlay */
    .latency-hud {
        position: absolute;
        top: 25px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 8px 18px;
        font-size: 0.85rem;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: 0.5px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        z-index: 5;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .latency-val {
        color: #ffffff;
        font-family: monospace;
        font-size: 1.15rem;
        text-shadow: 0 0 8px rgba(56, 189, 248, 0.8);
    }

    /* Narrative Banner */
    .status-banner {
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(79, 70, 229, 0.08);
        padding: 16px;
        border-radius: 18px;
        font-size: 0.92rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        box-sizing: border-box;
        margin-top: 15px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px #10b981;
        animation: pulse-dot 1s infinite alternate;
    }
    @keyframes pulse-dot {
        0% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* Fully Responsive Media Queries */
    @media (max-width: 768px) {
        body {
            height: auto !important;
            min-height: 800px;
            overflow-y: auto;
        }
        .canvas-container {
            height: auto !important;
            min-height: 850px;
            padding: 12px;
            border-radius: 20px;
        }
        .scene {
            height: 380px !important;
            padding: 0 10px;
        }
        .timeline-hud {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
            padding: 12px 20px;
            border-radius: 14px;
        }
        .hud-step {
            font-size: 0.76rem;
        }
        .latency-hud {
            font-size: 0.74rem;
            padding: 6px 12px;
            width: 90%;
            text-align: center;
            justify-content: center;
            top: 15px;
        }
        .status-banner {
            font-size: 0.82rem;
            padding: 12px;
            margin-top: 10px;
        }
    }
</style>
</head>
<body>

    <!-- Massive Immersive Simulation Canvas -->
    <div class="canvas-container">
        
        <!-- Latency Counter HUD -->
        <div class="latency-hud">
            <span>⚙️ E2E TRANSMISSION LATENCY:</span>
            <span class="latency-val" id="hud-timer">000</span><span>ms</span>
            <span style="font-size: 0.72rem; color: #94a3b8; margin-left: 10px; border-left: 1px solid #475569; padding-left: 10px;">⏱️ 10x SLOW-MOTION VIEW</span>
        </div>
        
        <div class="scene">
            <!-- Full size SVG vector scene -->
            <svg class="svg-scene-container" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <!-- Gradients and Filter Definitions inside `<defs>` for a stunning, smooth 3D face render -->
                <defs>
                    <!-- 3D Skin Radial Gradient for a soft, glowing, rounded face -->
                    <radialGradient id="skinGrad" cx="50%" cy="40%" r="60%" fx="40%" fy="30%">
                        <stop offset="0%" stop-color="#fff0ea" />
                        <stop offset="60%" stop-color="#ffd5c6" />
                        <stop offset="100%" stop-color="#fcaea0" />
                    </radialGradient>
                    
                    <!-- 3D Hair Soft Gradient -->
                    <linearGradient id="hairGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#b6714c" />
                        <stop offset="60%" stop-color="#935332" />
                        <stop offset="100%" stop-color="#693417" />
                    </linearGradient>

                    <!-- 3D Hair Bangs Gradient (slightly darker for contrast) -->
                    <linearGradient id="hairBangsGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#9a5a38" />
                        <stop offset="100%" stop-color="#55270f" />
                    </linearGradient>

                    <!-- 3D Jacket Gradient -->
                    <linearGradient id="jacketGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#ffffff" />
                        <stop offset="85%" stop-color="#f8fafc" />
                        <stop offset="100%" stop-color="#cbd5e1" />
                    </linearGradient>

                    <!-- Soft Shadow Gradient -->
                    <linearGradient id="shadowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="rgba(105, 52, 23, 0.25)" />
                        <stop offset="100%" stop-color="rgba(105, 52, 23, 0)" />
                    </linearGradient>

                    <!-- Circular mesh grad for high tech logo -->
                    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#2563eb" />
                        <stop offset="100%" stop-color="#06b6d4" />
                    </linearGradient>
                    
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="6" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    
                    <linearGradient id="laserGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="rgba(0, 255, 255, 0.35)" />
                        <stop offset="100%" stop-color="rgba(0, 255, 255, 0.0)" />
                    </linearGradient>
                </defs>

                <!-- Grid background lines -->
                <line x1="50" y1="420" x2="750" y2="420" stroke="rgba(79, 70, 229, 0.08)" stroke-width="1.5" stroke-dasharray="10 5" />
                
                <!-- Nice soft cyan/blue visual circles behind characters -->
                <circle cx="150" cy="240" r="130" fill="url(#skinGrad)" opacity="0.04" />
                <circle cx="650" cy="240" r="130" fill="url(#skinGrad)" opacity="0.04" />
                <circle cx="150" cy="240" r="110" stroke="rgba(37,99,235,0.06)" stroke-width="1" fill="none" stroke-dasharray="5 5" />
                <circle cx="650" cy="240" r="110" stroke="rgba(37,99,235,0.06)" stroke-width="1" fill="none" stroke-dasharray="5 5" />

                <!-- ==================== LEFT CUTE 3D CHARACTER (SENDER) ==================== -->
                <g id="partner-head" style="transition: transform 0.8s ease-in-out;">
                    <!-- Shirt / White Jacket -->
                    <path d="M 120,380 L 150,420 L 180,380 Z" fill="#0ea5e9" />
                    <path d="M 80,380 L 50,450 L 250,450 L 220,380 Z" fill="url(#jacketGrad)" stroke="#cbd5e1" stroke-width="1.5" />
                    <path d="M 105,380 L 132,410 L 150,380" fill="none" stroke="#cbd5e1" stroke-width="2.5" />
                    <path d="M 195,380 L 168,410 L 150,380" fill="none" stroke="#cbd5e1" stroke-width="2.5" />

                    <!-- Neck with soft shading -->
                    <rect x="136" y="300" width="28" height="85" rx="5" fill="url(#skinGrad)" />
                    <path d="M 136,305 L 164,305 L 164,318 L 136,310 Z" fill="rgba(0,0,0,0.08)" />

                    <!-- Ears -->
                    <circle cx="82" cy="240" r="13" fill="url(#skinGrad)" />
                    <circle cx="218" cy="240" r="13" fill="url(#skinGrad)" />

                    <!-- Round Face Head Base (3D Radial Gradient) -->
                    <circle cx="150" cy="240" r="65" fill="url(#skinGrad)" />

                    <!-- Smooth Rounded Brown Hair Cap -->
                    <path d="M 82,230 C 82,140 218,140 218,230 C 224,210 212,165 180,160 C 160,155 140,155 120,160 C 88,165 76,210 82,230 Z" fill="url(#hairGrad)" />
                    <!-- Sideburns -->
                    <path d="M 82,220 L 82,248 C 88,248 90,238 90,220 Z" fill="url(#hairGrad)" />
                    <path d="M 218,220 L 218,248 C 212,248 210,238 210,220 Z" fill="url(#hairGrad)" />
                    <!-- Bangs -->
                    <path d="M 90,198 Q 150,178 210,198 Q 150,192 90,198 Z" fill="url(#hairBangsGrad)" />

                    <!-- Eyebrows -->
                    <g id="partner-brows">
                        <rect id="partner-brow-l" x="113" y="202" width="18" height="6.5" rx="3.2" fill="#55270f" style="transition: transform 0.8s ease;" />
                        <rect id="partner-brow-r" x="169" y="202" width="18" height="6.5" rx="3.2" fill="#55270f" style="transition: transform 0.8s ease;" />
                    </g>

                    <!-- Eyes -->
                    <circle id="partner-eye-l" cx="122" cy="224" r="5" fill="#1a1a1a" style="transition: cx 0.8s ease, cy 0.8s ease, r 0.8s ease;" />
                    <circle id="partner-eye-r" cx="178" cy="224" r="5" fill="#1a1a1a" style="transition: cx 0.8s ease, cy 0.8s ease, r 0.8s ease;" />

                    <!-- Nose -->
                    <circle cx="150" cy="238" r="4.5" fill="#fcaea0" opacity="0.9" />
                    <path d="M 147,241 Q 150,245 153,241" fill="none" stroke="#e09780" stroke-width="2.5" stroke-linecap="round" />

                    <!-- Smiling Lips path -->
                    <path id="partner-lips" d="M 132,268 Q 150,275 168,268" stroke="#55270f" stroke-width="4.5" fill="none" stroke-linecap="round" style="transition: d 0.8s ease;" />
                </g>

                <!-- Step 2: Holographic scan laser grid -->
                <polygon id="scanner-laser" points="620,160 205,130 225,250 620,160" fill="url(#laserGrad)" opacity="0" style="transition: opacity 0.4s ease;" />

                <!-- ==================== RIGHT CUTE 3D CHARACTER (RECEIVER) ==================== -->
                <g id="user-head">
                    <!-- Shirt / White Jacket -->
                    <path d="M 620,380 L 650,420 L 680,380 Z" fill="#2563eb" />
                    <path d="M 580,380 L 550,450 L 750,450 L 720,380 Z" fill="url(#jacketGrad)" stroke="#cbd5e1" stroke-width="1.5" />
                    <path d="M 605,380 L 632,410 L 650,380" fill="none" stroke="#cbd5e1" stroke-width="2.5" />
                    <path d="M 695,380 L 668,410 L 650,380" fill="none" stroke="#cbd5e1" stroke-width="2.5" />

                    <!-- Neck with soft shading -->
                    <rect x="636" y="300" width="28" height="85" rx="5" fill="url(#skinGrad)" />
                    <path d="M 636,305 L 664,305 L 664,318 L 636,310 Z" fill="rgba(0,0,0,0.08)" />

                    <!-- Ears -->
                    <circle cx="582" cy="240" r="13" fill="url(#skinGrad)" />
                    <circle cx="718" cy="240" r="13" fill="url(#skinGrad)" />

                    <!-- Round Face Head Base (3D Radial Gradient) -->
                    <circle cx="650" cy="240" r="65" fill="url(#skinGrad)" />

                    <!-- Smooth Rounded Brown Hair Cap -->
                    <path d="M 582,230 C 582,140 718,140 718,230 C 724,210 712,165 680,160 C 660,155 640,155 620,160 C 588,165 576,210 582,230 Z" fill="url(#hairGrad)" />
                    <path d="M 582,220 L 582,248 C 588,248 590,248 590,220 Z" fill="url(#hairGrad)" />
                    <path d="M 718,220 L 718,248 C 712,248 710,238 710,220 Z" fill="url(#hairGrad)" />
                    <path d="M 592,198 Q 650,178 708,198 Q 650,192 592,198 Z" fill="url(#hairBangsGrad)" />

                    <!-- Nose -->
                    <circle cx="650" cy="238" r="4.5" fill="#fcaea0" opacity="0.9" />
                    <path d="M 647,241 Q 650,245 653,241" fill="none" stroke="#e09780" stroke-width="2.5" stroke-linecap="round" />

                    <!-- Smiling Lips -->
                    <path d="M 632,268 Q 650,275 668,268" stroke="#55270f" stroke-width="4.5" fill="none" stroke-linecap="round" />

                    <!-- Sleek Realistic Smart Glasses Redesign (TR-90 Dual smoke lenses) -->
                    <!-- Left Ear Temple -->
                    <path d="M 590,225 Q 582,228 580,240" stroke="#1e293b" stroke-width="3.5" fill="none" stroke-linecap="round" />
                    <!-- Right Ear Temple -->
                    <path d="M 710,225 Q 718,228 720,240" stroke="#1e293b" stroke-width="3.5" fill="none" stroke-linecap="round" />

                    <!-- Left Lens & Frame Rim -->
                    <rect x="596" y="210" width="40" height="30" rx="10" fill="#1e293b" opacity="0.88" stroke="#00ffff" stroke-width="1.5" />
                    <!-- Right Lens & Frame Rim -->
                    <rect x="664" y="210" width="40" height="30" rx="10" fill="#1e293b" opacity="0.88" stroke="#00ffff" stroke-width="1.5" />

                    <!-- HUD visual glow indicators inside lenses -->
                    <rect x="600" y="214" width="32" height="22" rx="8" fill="none" stroke="rgba(0, 255, 255, 0.4)" stroke-width="1" />
                    <rect x="668" y="214" width="32" height="22" rx="8" fill="none" stroke="rgba(0, 255, 255, 0.4)" stroke-width="1" />

                    <!-- Bridge -->
                    <path d="M 636,220 Q 650,216 664,220" stroke="#1e293b" stroke-width="4" fill="none" stroke-linecap="round" />

                    <!-- Metal rivets & glowing power micro-LED -->
                    <circle cx="593" cy="222" r="1.5" fill="#e2e8f0" />
                    <circle cx="707" cy="222" r="1.5" fill="#e2e8f0" />
                    <circle cx="598" cy="216" r="2" fill="#00ffcc" filter="url(#glow)" />
                </g>

                <!-- User's Arm and Wristband (CueBand Hub) -->
                <g id="user-arm" transform="translate(60, 30)">
                    <!-- Arm sleeve -->
                    <path d="M 525,370 C 520,310 500,290 480,285 C 472,282 465,275 470,265 C 475,258 485,260 490,265 C 505,278 520,300 533,370 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" />
                    <path d="M 480,285 C 472,282 465,275 470,265 C 475,258 485,260 490,265 L 493,275 Z" fill="url(#skinGrad)" />
                    <!-- Wristband (CueBand Haptic Unit) -->
                    <rect x="474" y="270" width="12" height="20" rx="4" fill="#1e293b" stroke="#2563eb" stroke-width="2" transform="rotate(-15, 480, 280)" />
                    <circle cx="480" cy="280" r="3.5" fill="#00ffff" />
                </g>

                <!-- ==================== SIGNAL NETWORKS ==================== -->
                <!-- BLE Signal packets from Glasses Visor to Smartphone Gateway -->
                <path d="M 605,215 Q 500,270 400,270" fill="none" stroke="rgba(37,99,235,0.06)" stroke-width="3" />
                <path id="sig-path-1" d="M 605,215 Q 500,270 400,270" fill="none" stroke="#00ffff" stroke-width="4.5" stroke-dasharray="12, 12" stroke-dashoffset="0" opacity="0" style="transition: opacity 0.2s;" />
                
                <!-- Phone Hub to Wristband -->
                <path d="M 400,270 Q 470,270 540,310" fill="none" stroke="rgba(37,99,235,0.06)" stroke-width="3" />
                <path id="sig-path-2" d="M 400,270 Q 470,270 540,310" fill="none" stroke="#2563eb" stroke-width="4.5" stroke-dasharray="12, 12" stroke-dashoffset="0" opacity="0" style="transition: opacity 0.2s;" />

                <!-- Central Smartphone gateway hub -->
                <g id="hub-phone" transform="translate(400, 270)">
                    <rect x="-24" y="-36" width="48" height="72" rx="10" fill="white" stroke="#2563eb" stroke-width="2.5" filter="url(#glow)" />
                    <rect x="-20" y="-30" width="40" height="60" rx="6" fill="#f8fafc" />
                    <circle cx="0" cy="0" r="8" fill="url(#logoGrad)" />
                    <line x1="-15" y1="0" x2="-8" y2="0" stroke="#06b6d4" stroke-width="1.5"/>
                    <line x1="8" y1="0" x2="15" y2="0" stroke="#06b6d4" stroke-width="1.5"/>
                    <line x1="0" y1="-15" x2="0" y2="-8" stroke="#06b6d4" stroke-width="1.5"/>
                    <line x1="0" y1="8" x2="0" y2="15" stroke="#06b6d4" stroke-width="1.5"/>
                </g>

                <!-- ==================== HAPTIC WAVESHAPES ==================== -->
                <g id="wave-nod" opacity="0">
                    <circle cx="540" cy="310" r="16" stroke="#4f46e5" stroke-width="2.5" fill="none" class="pulse-wave-1" />
                    <circle cx="540" cy="310" r="28" stroke="#4f46e5" stroke-width="1.5" fill="none" class="pulse-wave-2" />
                </g>
                <g id="wave-smile" opacity="0">
                    <path d="M 520,305 Q 500,285 480,305" stroke="#10b981" stroke-width="3.5" fill="none" stroke-linecap="round" />
                    <path d="M 515,320 Q 495,300 475,320" stroke="#10b981" stroke-width="2" fill="none" stroke-linecap="round" />
                </g>
                <g id="wave-look_away" opacity="0">
                    <path d="M 515,300 L 490,285 L 500,280 M 490,285 L 502,298" stroke="#ef4444" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M 555,325 L 580,340 M 580,340 L 569,342 M 580,340 L 578,328" stroke="#ef4444" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
                </g>
                <g id="wave-reduced" opacity="0">
                    <circle cx="540" cy="310" r="18" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4" fill="none" />
                </g>
                <g id="wave-confusion" opacity="0">
                    <path d="M 530,295 L 510,280 L 520,265 L 495,255" stroke="#f59e0b" stroke-width="2.5" fill="none" stroke-linecap="round" />
                    <path d="M 535,325 L 525,345 L 510,340 L 500,360" stroke="#f59e0b" stroke-width="2.5" fill="none" stroke-linecap="round" />
                </g>

                <!-- SVG-embedded Responsive 100% stable Tag Labels using foreignObject -->
                <foreignObject x="580" y="130" width="180" height="42">
                    <div xmlns="http://www.w3.org/1999/xhtml" style="width:100%; height:100%;">
                        <button class="device-tag" id="tag-glasses" onclick="switchTab('glasses')">🕶️ AI 스마트 안경 사양</button>
                    </div>
                </foreignObject>

                <foreignObject x="415" y="325" width="165" height="42">
                    <div xmlns="http://www.w3.org/1999/xhtml" style="width:100%; height:100%;">
                        <button class="device-tag" id="tag-band" onclick="switchTab('band')">⌚ 햅틱 밴드 사양</button>
                    </div>
                </foreignObject>
            </svg>
        </div>
        
        <!-- Live Narrative HUD Step Bar -->
        <div class="timeline-hud">
            <div class="hud-step" id="step-1">
                <div class="hud-step-num">1</div>
                <span>상대방 3D 안면 표정 변화</span>
            </div>
            <div class="hud-step" id="step-2">
                <div class="hud-step-num">2</div>
                <span>스마트 글라스 캡처 스캔</span>
            </div>
            <div class="hud-step" id="step-3">
                <div class="hud-step-num">3</div>
                <span>POSTER V2 AI 판별 & BLE 전송</span>
            </div>
            <div class="hud-step" id="step-4">
                <div class="hud-step-num">4</div>
                <span>LRA 다채널 햅틱 진동 피드백</span>
            </div>
        </div>

        <!-- Live Status Narrative banner -->
        <div class="status-banner">
            <div class="status-dot"></div>
            <span id="narrative-text" style="line-height: 1.6;">대화 상대방의 미세한 안면 변화가 0.5초 이내에 햅틱 자극으로 번역되는 과정을 시뮬레이션합니다.</span>
        </div>
    </div>

    <script>
    // 3D Avatar specific expression paths and rotations
    const faces = {
        smile: {
            eyeL: { cx: 122, cy: 224, r: 5 },
            eyeR: { cx: 178, cy: 224, r: 5 },
            browL: "translate(0, -3) rotate(-3, 113, 202)",
            browR: "translate(0, -3) rotate(3, 169, 202)",
            lips: "M 130,262 Q 150,278 170,262",
            nod: false
        },
        nod: {
            eyeL: { cx: 122, cy: 224, r: 5 },
            eyeR: { cx: 178, cy: 224, r: 5 },
            browL: "",
            browR: "",
            lips: "M 132,268 Q 150,275 168,268",
            nod: true
        },
        look_away: {
            eyeL: { cx: 118, cy: 224, r: 5 }, // shifted left
            eyeR: { cx: 174, cy: 224, r: 5 }, // shifted left
            browL: "translate(-2, 1)",
            browR: "translate(-2, 1)",
            lips: "M 132,268 Q 150,273 168,268",
            nod: false
        },
        reduced: {
            eyeL: { cx: 122, cy: 224, r: 3.5 },
            eyeR: { cx: 178, cy: 224, r: 3.5 },
            browL: "translate(0, 2)",
            browR: "translate(0, 2)",
            lips: "M 135,268 L 165,268", // flat straight line
            nod: false
        },
        confusion: {
            eyeL: { cx: 122, cy: 226, r: 5 },
            eyeR: { cx: 178, cy: 222, r: 5 },
            browL: "translate(0, 2) rotate(12, 113, 202)", // left brow tilted up
            browR: "translate(0, -2) rotate(-12, 169, 202)", // right brow tilted down
            lips: "M 134,270 Q 150,262 166,270", // wavy lip path
            nod: false
        }
    };

    // Specs detail tab panel contents
    const contents = {
        glasses: `
            <div class="spec-title" style="font-weight: 800; font-size: 1.1rem; color: #2563eb;">🕶️ CueBand AI 스마트 안경 사양</div>
            <div class="spec-subtitle" style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">대화 상대방의 안면 표정 및 비언어 신호를 프라이버시 침해 없이 즉각적으로 감지하는 고성능 비침습 안경 유닛입니다.</div>
            <div class="spec-card-list">
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">광학 감지 모듈</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">720p @ 30fps 초소형 광각 렌즈 (3mm 직경)</div>
                    </div>
                </div>
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">경량성 및 편의 소재</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">TR-90 바이오 플라스틱 테 / 무게 40g 미만 설계</div>
                    </div>
                </div>
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">프라이버시 보증</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">영상 저장장치 원천 배제 / 촬영 유도 표시등(LED) 강제 탑재</div>
                    </div>
                </div>
            </div>
        `,
        band: `
            <div class="spec-title" style="font-weight: 800; font-size: 1.1rem; color: #2563eb;">⌚ CueBand 햅틱 손목 밴드 사양</div>
            <div class="spec-subtitle" style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">상대의 안면 표정 분석결과에 대입된 독자적 햅틱 주파수를 사용자의 피부 접촉으로 변환 전달하는 핵심 피드백 채널입니다.</div>
            <div class="spec-card-list">
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">햅틱 드라이브</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">다채널 LRA (Linear Resonant Actuator) 4～6구 등간격 배치</div>
                    </div>
                </div>
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">임베디드 무선 프로세서</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">ESP32-S3 Dual-core / BLE 5.0 (저지연 프로토콜 연동)</div>
                    </div>
                </div>
                <div class="spec-item" style="padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div class="spec-circle" style="width: 8px; height: 8px; background: #2563eb; border-radius: 50%;"></div>
                    <div>
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700;">배터리 라이프</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">250mAh LiPo 탑재 / 절전 알고리즘 기반 8시간 이상 구동</div>
                    </div>
                </div>
            </div>
        `,
        flow: `
            <div class="spec-title" style="font-weight: 800; font-size: 1.1rem; color: #2563eb;">🔄 실시간 통신 E2E 프로세스</div>
            <div class="spec-subtitle" style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">스마트 글라스에서 포착한 안면 신호가 사용자 피부에 감각으로 변환되기까지 0.5초 이내에 완료되는 4단계 초저지연 연동 기술입니다.</div>
            <div class="spec-card-list">
                <div class="spec-item" style="padding: 6px 12px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div style="font-weight: 800; font-size: 0.8rem; color: #2563eb;">Step 1</div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #1e293b;">상대 얼굴 프레임 영상 버퍼 전송 (지연: 33ms 미만)</div>
                </div>
                <div class="spec-item" style="padding: 6px 12px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div style="font-weight: 800; font-size: 0.8rem; color: #2563eb;">Step 2</div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #1e293b;">POSTER V2 AI 표정 랜드마크 융합 연산 (지연: 150ms 미만)</div>
                </div>
                <div class="spec-item" style="padding: 6px 12px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div style="font-weight: 800; font-size: 0.8rem; color: #2563eb;">Step 3</div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #1e293b;">감정 상태 고유 진동 파형 매핑 연산 (지연: 10ms 미만)</div>
                </div>
                <div class="spec-item" style="padding: 6px 12px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; background: rgba(248, 250, 252, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px;">
                    <div style="font-weight: 800; font-size: 0.8rem; color: #2563eb;">Step 4</div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #1e293b;">BLE 무선 가동 및 손목 피부 햅틱 자극 인지 (지연: 30ms 미만)</div>
                </div>
            </div>
        `
    };

    function switchTab(tabId) {
        // Find inside iframe (this is inside visual context)
        const activeBtn = document.getElementById('tab-btn-' + tabId);
        if (activeBtn) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            activeBtn.classList.add('active');
        }
        
        const contentDiv = document.getElementById('panel-content');
        if (contentDiv) {
            contentDiv.innerHTML = contents[tabId];
        }
        
        if (tabId === 'glasses') {
            triggerGlassesHighlight();
        } else if (tabId === 'band') {
            triggerBandHighlight();
        } else if (tabId === 'flow') {
            resetAndRunSimulation();
        }
    }

    // Spec Tab support for parent callback routing
    window.switchTab = switchTab;

    // Immersively triggered sequential loop (Slowed slightly to 7.0 seconds per full cycle to allow comfortable reading of all 4 steps!)
    const simulationStates = [
        { key: 'smile', text: '대화 상대방의 안면에 자연스럽고 따뜻한 미소가 퍼져 나갑니다.', time: 223 },
        { key: 'nod', text: '대화 상대방이 고개를 상하로 흔들며 이야기의 요지에 동의를 표합니다.', time: 215 },
        { key: 'look_away', text: '대화 상대방이 주의력을 잃고 머리 방향과 시선을 좌우로 분산시켰습니다.', time: 232 },
        { key: 'reduced', text: '대화 상대방의 감정 교환 활동이 식으며 무표정한 반응 상태에 머뭅니다.', time: 205 },
        { key: 'confusion', text: '순간적인 질문에 대화 상대방의 미간이 좁혀지며 다소 당황한 표정이 감지됩니다.', time: 240 }
    ];
    
    let currentIdx = 0;
    let globalTimer = null;
    let digitalCounterInterval = null;

    function triggerGlassesHighlight() {
        const scanLaser = document.getElementById('scanner-laser');
        if (scanLaser) {
            scanLaser.style.opacity = '0.7';
            setTimeout(() => { scanLaser.style.opacity = '0'; }, 600);
        }
    }

    function triggerBandHighlight() {
        const nodWave = document.getElementById('wave-nod');
        if (nodWave) {
            nodWave.style.opacity = '1';
            setTimeout(() => { nodWave.style.opacity = '0'; }, 800);
        }
    }

    function runMilisecondsCounter(targetMs) {
        clearInterval(digitalCounterInterval);
        const timerElem = document.getElementById('hud-timer');
        if (!timerElem) return;
        
        let currentCount = 0;
        const duration = 1200; // premium slow digital countup
        const increment = targetMs / (duration / 16);
        
        digitalCounterInterval = setInterval(() => {
            currentCount += increment;
            if (currentCount >= targetMs) {
                currentCount = targetMs;
                clearInterval(digitalCounterInterval);
            }
            timerElem.innerText = String(Math.floor(currentCount)).padStart(3, '0');
        }, 16);
    }

    function executeSimulationStep() {
        const state = simulationStates[currentIdx];
        
        // Reset haptics
        const waves = ['wave-nod', 'wave-smile', 'wave-look_away', 'wave-reduced', 'wave-confusion'];
        waves.forEach(w => {
            const elem = document.getElementById(w);
            if (elem) elem.style.opacity = '0';
        });
        
        // Reset HUD steps
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        steps.forEach(s => {
            const elem = document.getElementById(s);
            if (elem) elem.classList.remove('active');
        });
        
        // ==================== Step 1: 3D Avatar Facial Expressions Morph ====================
        const step1 = document.getElementById('step-1');
        if (step1) step1.classList.add('active');
        
        const faceData = faces[state.key];
        
        const eyeL = document.getElementById('partner-eye-l');
        const eyeR = document.getElementById('partner-eye-r');
        const browL = document.getElementById('partner-brow-l');
        const browR = document.getElementById('partner-brow-r');
        const lipsPath = document.getElementById('partner-lips');
        
        if (eyeL) {
            eyeL.setAttribute('cx', faceData.eyeL.cx);
            eyeL.setAttribute('cy', faceData.eyeL.cy);
            eyeL.setAttribute('r', faceData.eyeL.r);
        }
        if (eyeR) {
            eyeR.setAttribute('cx', faceData.eyeR.cx);
            eyeR.setAttribute('cy', faceData.eyeR.cy);
            eyeR.setAttribute('r', faceData.eyeR.r);
        }
        if (browL) browL.setAttribute('transform', faceData.browL);
        if (browR) browR.setAttribute('transform', faceData.browR);
        if (lipsPath) lipsPath.setAttribute('d', faceData.lips);
        
        // Nod transition
        const headGroup = document.getElementById('partner-head');
        if (headGroup) {
            if (faceData.nod) {
                headGroup.style.transform = "translateY(15px)";
                setTimeout(() => {
                    headGroup.style.transform = "translateY(0px)";
                    setTimeout(() => {
                        headGroup.style.transform = "translateY(12px)";
                        setTimeout(() => {
                            headGroup.style.transform = "translateY(0px)";
                        }, 250);
                    }, 200);
                }, 250);
            } else {
                headGroup.style.transform = "translateY(0px)";
            }
        }
        
        const narrElem = document.getElementById('narrative-text');
        if (narrElem) {
            let labelText = '';
            if (state.key === 'smile') labelText = '미소/웃음';
            if (state.key === 'nod') labelText = '고개 끄덕임';
            if (state.key === 'look_away') labelText = '시선 이탈';
            if (state.key === 'reduced') labelText = '반응 감소';
            if (state.key === 'confusion') labelText = '당황/멈칫';
            narrElem.innerHTML = `<strong>[Step 1. 상대 표정 변화]</strong> 대화 상대방의 안면에 미세한 <strong>${labelText}</strong> 표정 변화가 선명하게 감지되기 시작합니다.`;
        }
        
        // ==================== Step 2: Glasses Scan Face (Laser beam activation) ====================
        setTimeout(() => {
            const step2 = document.getElementById('step-2');
            if (step2) step2.classList.add('active');
            const scanLaser = document.getElementById('scanner-laser');
            if (scanLaser) {
                scanLaser.style.opacity = '0.6';
                setTimeout(() => { scanLaser.style.opacity = '0'; }, 750);
            }
            if (narrElem) {
                narrElem.innerHTML = `<strong>[Step 2. 스마트 글라스 스캔]</strong> 스마트 글라스의 내장 3mm 카메라가 프라이버시 침해 없이 안면 프레임을 스캔하여 온디바이스 메모리에 고속 로딩합니다.`;
            }
        }, 1500);
        
        // ==================== Step 3: Signal routing (BLE Packets) ====================
        setTimeout(() => {
            const step3 = document.getElementById('step-3');
            if (step3) step3.classList.add('active');
            
            const sig1 = document.getElementById('sig-path-1');
            const sig2 = document.getElementById('sig-path-2');
            
            if (sig1) sig1.style.opacity = '1';
            runMilisecondsCounter(state.time);
            
            if (narrElem) {
                narrElem.innerHTML = `<strong>[Step 3. AI 판별 & BLE 전송]</strong> 모바일 에이전트 내의 POSTER V2 AI 모델이 감정을 판별(분석 지연: <strong>${state.time}ms</strong>)하고 BLE 5.0 가속 무선 링크로 햅틱 변역 코드를 손목으로 전송합니다.`;
            }
            
            setTimeout(() => {
                if (sig1) sig1.style.opacity = '0';
                if (sig2) sig2.style.opacity = '1';
                setTimeout(() => { if (sig2) sig2.style.opacity = '0'; }, 600);
            }, 600);
        }, 3200);
        
        // ==================== Step 4: Wristband CueBand pulses ====================
        setTimeout(() => {
            const step4 = document.getElementById('step-4');
            if (step4) step4.classList.add('active');
            
            const targetWave = document.getElementById('wave-' + state.key);
            if (targetWave) {
                targetWave.style.opacity = '1';
            }
            
            let hapticTerm = '';
            if (state.key === 'smile') hapticTerm = '부드러운 물결 정현파 1회 진동 (150Hz / 600ms)';
            if (state.key === 'nod') hapticTerm = '짧고 단단한 더블 임펄스 톡톡 (180Hz / 400ms)';
            if (state.key === 'look_away') hapticTerm = '좌측에서 우측 모터로 비끼는 방향 이동 진동 (150Hz / 800ms)';
            if (state.key === 'reduced') hapticTerm = '가볍고 연하게 스치는 미온 진동 1회 (120Hz / 300ms)';
            if (state.key === 'confusion') hapticTerm = '불규칙하게 날카롭게 갈라지는 단속 펄스 진동 (220Hz / 700ms)';
            
            if (narrElem) {
                narrElem.innerHTML = `<strong>[Step 4. 촉각 피드백 완료]</strong> ${state.text} <span style="color:#2563eb; font-weight:800;">➡️ [LRA 햅틱 번역] ${hapticTerm}</span>`;
            }
        }, 5000);

        currentIdx = (currentIdx + 1) % simulationStates.length;
    }

    function resetAndRunSimulation() {
        if (globalTimer) clearInterval(globalTimer);
        executeSimulationStep();
        globalTimer = setInterval(executeSimulationStep, 7200); // 7.2s to match the richer, slowed down step pacing perfectly!
    }
    
    // Initialize default tab on start
    setTimeout(() => {
        switchTab('glasses');
        resetAndRunSimulation();
    }, 100);
</script>
</body>
</html>
    """
    
    # 1. Canvas at the absolute top of the page (Occupying a huge 700px vertical space for maximum immersion!)
    st.components.v1.html(html_widget_code, height=700)
    
    render_divider()

    # 2. Detailed introductory cards and specifications placed BELOW the canvas
    cols = st.columns([1.2, 0.8])
    
    with cols[0]:
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <h3 style="color: #2563eb !important; font-weight: 900; margin-top: 0; margin-bottom: 1.2rem; letter-spacing: -0.5px;">🎯 CueBand의 혁신성과 기획 이념</h3>
            <p style="font-size: 1.02rem; line-height: 1.8; color: #475569 !important; margin: 0; text-align: justify;">
                본 프로젝트는 보조공학 기기가 가질 수밖에 없던 외관상의 이질감과 이로 인한 사회적 수치심(Stigma)을 설계 단계부터 완벽히 제거하기 위해 기획되었습니다. 
                사용자가 '장애인용 특수 보조구'를 장착했다는 부자연스러운 인상을 주지 않도록, 현대 스마트 기술 환경에서 대중화된 <b>경량 안경</b>과 <b>컴팩트 피트니스 밴드</b>의 형태를 철저하게 계승했습니다.<br/><br/>
                눈에 띄지 않는 기기의 내면에 SOTA급 안면 표정 분석 알고리즘인 <b>POSTER V2 AI</b> 신경망과 <b>고속 LRA(선형 공진 액추에이터) 매핑 엔진</b>을 융합했습니다. 
                이를 통해 시각장애인이 주변 환경의 어떠한 청각적 방해도 받지 않고 대화 상대방의 미세한 표정 및 반응 변화를 0.5초 이내에 자신의 손목 피부로만 전달받는 <b>"비침습적 은밀성(Non-invasive Stealthiness)"</b>을 제공합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        # Specifications tab panel explorer below the canvas
        # Rich spec cards that swap dynamically on click
        st.markdown("""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <h4 style="color:#2563eb !important; font-weight:900; margin-top:0; margin-bottom: 1rem;">💡 CueBand 기술 규격 신속 안내</h4>
            <div style="font-size: 0.9rem; line-height: 1.6; color: #475569 !important; margin-bottom: 1.5rem;">
                상단의 <b>안경 사양</b> 및 <b>밴드 사양</b> 핫스팟 태그 버튼을 클릭하시면 실시간 연동 원리와 상세 물리 명세가 캔버스 내부에서 즉각 전환 렌더링됩니다.<br/><br/>
                스마트 안경 내부의 3mm 카메라 모듈, 모바일 에이전트 내의 POSTER V2 AI 분류 모듈, 그리고 손목 다채널 LRA 햅틱 모듈은 223ms 미만의 타임 버젯 분할을 거쳐 동작합니다.
            </div>
            <div style="background: rgba(241, 245, 249, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(0,0,0,0.03);">
                <span style="font-weight: 800; font-size: 0.8rem; color: #2563eb; display: block; margin-bottom: 4px; text-transform: uppercase;">상태 정보 동기화</span>
                <span style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">BLE 5.0 가속 프로토콜 탑재 (접속 주기: 7.5ms 고정)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PAGE 2: RESEARCH PROJECT & OBJECTIVES (연구과제 및 목표)
# ============================================================
def page_objectives():
    render_section_header("🎯 연구과제 및 최종 목표 (최종 연구 계획서)")
    
    st.markdown("""
    대면 의사소통 상황에서 시각장애인이 시각적 경로로 접할 수 없는 대화 상대방의 비언어적 정서 신호(표정, 고개 끄덕임, 시선 분산, 멈칫함 등)를 
    스마트 글래스 내장형 초소형 카메라로 포착하고, 모바일 에이전트 내의 **SOTA급 안면 감정 신경망(POSTER V2)**을 통해 실시간으로 해석합니다. 
    이후 시각장애인 사용자가 주변의 음성 및 배경 소리를 듣는 청각 채널의 부하 없이, 
    손목에 등간격 밀착 배치된 **LRA 다채널 햅틱 밴드**를 통해 5가지 유형별 물리적으로 구별되는 진동 주파수로 전달받을 수 있도록 구성하는 **웨어러블 비언어 정서 통역 인터페이스** 설계가 본 과제의 연구과제이자 최종 목표입니다.
    """)

    render_divider()

    st.markdown("### 1. 5대 세부 정량적 연구 과제 명세")
    
    st.markdown("""
    #### 과제 1. 고정밀 멀티모달 비언어 신호 파싱 AI 신경망 수립
    - **핵심 기술**: 최첨단 얼굴 특징 추출 인공신경망인 **POSTER V2 (FER)** 모델 기반 안면 랜드마크 분석 스트림과 이미지 특징 융합.
    - **통합 설계**: MediaPipe Face Mesh 알고리즘을 융합하여 머리의 회전 각도(Yaw, Pitch, Roll)에 기반한 **고개 끄덕임(Nodding)** 검출 및 안구 중심 위치 조정을 통한 **시선 방향(Gaze direction)**을 실시간 연산하도록 아키텍처를 설계합니다.
    - **기술 성능 지표**: 표정 7개 클래스 감지 정확도 85% 이상 확보, 저지연 temporal 필터 적용을 통한 비언어 오판률 5% 미만 억제.

    #### 과제 2. 정서 신호 - 촉각 물리 자극 햅틱 매핑 엔진 개발
    - **참여형 설계 방법론**: 시각장애인 공동설계(Co-design) 워크숍 그룹(10～15명)을 발족하고, 각 감정에 적응하기 쉽고 직관적인 햅틱 주파수 영역(50Hz～300Hz) 및 펄스 형태를 직접 설계합니다.
    - **JND 정량 측정**: 최소 인지 차이(Just Noticeable Difference) 실험과 다차원 햅틱 맵 변별도 평가를 반복 수행하여 감정별 변별도 지표를 확보합니다.
    - **식별 정확도**: 일련의 임의 햅틱 자극 투입 시 최소 75% 이상의 자극별 식별 정확도를 확보함을 연구 개발의 핵심 목표로 설정합니다.

    #### 과제 3. 초경량 고탄성 LRA 햅틱 밴드 프로토타입 설계
    - **하드웨어 아키텍처**: ESP32-S3 임베디드 코어 MCU 및 TI DRV2605L 가속 햅틱 드라이버 칩셋 활용.
    - **피드백 설계**: 손목 둘레 방향으로 등간격 4～6구의 LRA 선형 공진 액추에이터 밀착 배치. 각 모터를 독립적 채널로 제어하여 순차 방향 회전 자극(시선 이탈 시 유용) 등 역동적 촉각 도파 구현.
    - **편의성 규격**: 종일 착용에 따른 무리가 없도록 총 중량 35g 이하로 가공하며, 장시간 땀 배출과 피부 자극 방지를 위해 의료용 통기성 실리콘 밴드 소재 및 IP54 이상의 방진 방수 능력을 설계합니다.

    #### 과제 4. 저지연 온디바이스 스마트 글래스 연동 시스템
    - **초경량 하우징**: 3mm 크기의 720p 30fps 초경량 광각 카메라 센서를 TR-90 프레임 안경 힌지에 내장하여 총 무게 40g 이하로 수렴시킵니다.
    - **프로토콜 연동**: 초저지연 Bluetooth Low Energy 5.0 가속 통신 프로토콜을 수립하여 글라스 캡처부터 밴드 가동까지의 End-to-End 지연 시간을 총 **223ms 이하**로 고정 최적화합니다.
    - **보안 장치**: 로컬 엣지 디바이스 처리 원칙을 수립하여 메모리상에서 프레임 해석 후 완전 삭제(Zero-trace)함으로써 피촬영자의 프라이버시를 전적으로 보호합니다.

    #### 과제 5. 시각장애인 대상 임상 사용성 평가 및 공익성 검증
    - **사용자 평가 설계**: 구조화된 대화 시나리오(배우 활용) 환경 하에서 CueBand 사용에 따른 대화 만족도 지수 및 사회적 연결지수를 정량 평가합니다.
    - **정성적 정량적 평가 연계**: 만족도 평가(SUS Score) 목표치 75점 이상 획득, 작업 부하량(NASA-TLX) 30% 이하 저감, 대화 상대방과의 상호 공감 지표 점수 유의미한 상승 검증을 통계 분석 기반으로 확보합니다.
    """)

    render_divider()

    st.markdown("### 2. 연구 참여자 구성 설계 명세")
    
    participants_df = pd.DataFrame({
        "참여자 그룹": ["공동설계 워크숍 그룹 (Co-design)", "임상 실험군 (Experimental Group)", "임상 대조군 (Control Group)", "대면 대화 상대방 (Non-disabled Partners)", "전문가 자문단 (Scientific Advisors)"],
        "대상 및 구성 요건": ["시각장애인 당사자 (다양한 실명 시기 및 정도 고려)", "시각장애인 당사자 (CueBand 장치 실장용)", "시각장애인 당사자 (기존 오디오 음성 피드백 사용용)", "실험군 및 대조군과 대화할 비장애인 파트너", "보조공학, HCI, 신경과학 분야 교수 및 전문의"],
        "정량적 인원수": ["10 ～ 15 명", "20 명", "20 명", "20 명", "5 명"],
        "연구 내 주요 역할": ["촉각 매핑 펄스 및 주파수 공동설계, JND 테스트 피드백", "스마트 안경 + 햅틱 밴드 실장 기반 실대화 수행", "전통 오디오 낭독 TTS 인터페이스 적용 대화 수행", "통제 대화 시나리오 수행 및 시선/표정 변화 제공", "연구 설계 타당성 평가, IRB 승인 가이드라인 지도"]
    })
    st.dataframe(participants_df, use_container_width=True, hide_index=True)

    st.markdown("""
    #### 📊 평가지표별 정량적 타겟 목표
    - **시스템 수용성 (System Usability Scale)**: SUS 75점 이상 (매우 우수 등급) 달성 보증.
    - **감각 및 인지 부하량 (NASA-TLX)**: 기존 음성 피드백 대비 30% 이하의 피로도 수준 도달 검증.
    - **대인 정서 연결지수 (Inclusion of Other in the Self Scale)**: 통계적 유의성 p < 0.05 수준에서 대조군 대비 유의미한 친밀성 증가 검증.
    """)

# ============================================================
# PAGE 3: BACKGROUND & SIGNIFICANCE (연구 배경 및 필요성)
# ============================================================
def page_background():
    # Large Topic Box at Top
    st.markdown("""
    <div class="research-title-box">
        <span class="research-title-label">연구 과제 주제 명세</span>
        <span class="research-title-content">시각장애인의 사회적 상호작용 향상을 위한 촉각 기반 비언어적 정서 신호 전달 AI인터페이스 설계</span>
    </div>
    """, unsafe_allow_html=True)

    render_section_header("🔬 연구 배경 및 기술 개발의 필요성")

    st.markdown("""
    ### 1. 비언어적 정서 소통의 단절과 시각장애인의 소외
    심리학 및 커뮤니케이션 연구에 따르면 대면 의사소통 과정에서 상대방의 미소, 고개 끄덕임, 눈맞춤, 눈길 피함, 곤혹스러운 멈춤 등 **비언어적 신호(Nonverbal Cues)는 의사 정보 전달 비중의 55%에서 최대 93%까지 차지**합니다 (Mehrabian, 1971). 
    이러한 미세 비언어 반응들은 대화의 템포 조율, 호감 표현, 대화 거부 등 맥락 이해에 핵심적인 피드백 경로입니다.
    
    하지만 시각장애인 당사자는 이러한 시각 피드백 채널에 대한 정보 접근권이 원천 단절되어 있어 대면 상호작용에서 깊은 불안감과 의사 장벽을 경험하고 있습니다.
    """)

    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🛑 대화 흐름 파악 장애 및 맥락 오판</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                상대방이 이야기 중간에 무표정해지거나(반응 감소) 눈길을 다른 곳으로 돌리며 흥미를 잃어가는 순간(시선 이탈)을 인지하지 못하여, 주제 전환 타이밍을 놓치고 일방적인 의사소통에 머물게 되는 리스크가 큽니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="component-card" style="margin-top: 1rem; height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🛑 사회적 상호작용의 심각한 비대칭성</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                비장애인 대화 상대방은 시각장애인의 감정 표출과 몸짓을 읽으며 관계를 조율할 수 있는 반면, 시각장애인은 상대의 즉각적인 피드백 정서를 제공받지 못해 만성적인 '대인 신호 비대칭'에 노출됩니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🛑 기존 솔루션의 청각 정보 과부하 문제</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                기존의 AI 정서 묘사 어플리케이션은 파트너의 표정을 스피커나 이어폰을 통해 텍스트 음성(TTS)으로 길게 낭독해 줍니다. 이는 파트너의 육성을 듣고 주변 환경 음을 통해 안전을 인지해야 하는 시각장애인의 귀를 완전히 틀어막아 치명적인 커뮤니케이션 방해를 자초했습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="component-card" style="margin-top: 1rem; height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🛑 시각 보조기기의 사회적 스티그마(Stigma)</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                부피가 크고 기이한 고성능 카메라 고정 장비나 헤드 마운트 센서 등은 일상적인 대화 장소에서 타인의 눈길과 동정을 불필요하게 모으게 되어, 사용자의 실질적인 사회 생활 속 상시 착용을 꺼리게 만드는 주원인이었습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    render_divider()

    st.markdown("### 2. 기존 보조 공학 솔루션의 구체적 한계점 대비 CueBand 해결 전략")
    
    background_comparison = pd.DataFrame({
        "평가 영역 차원": ["실시간성 및 지연속도", "감각 피드백 채널", "비언어 해독 스펙트럼", "착용 시 외관 및 사회적 시선", "최종 체감 피로 수준"],
        "기존 보조 공학 한계 사항": [
            "서버 연동 묘사 방식으로 수 초(2～5s)의 전송 지연이 발생해 실시간 대화 피드백 불가능",
            "청각 매체(음성 이어폰) 위주 알림 전달로 음성 청취를 직접 간섭하여 사용 피로 유발",
            "단순 안면 기본 감정 7대 카테고리에만 치우쳐 고개 움직임 등 동적 피드백 수용 불가능",
            "부피가 큰 카메라 고정 장치나 이색적인 외관으로 주변인의 호기심과 불필요한 동정 유발",
            "청각 과부하와 늦은 반응 지체로 인해 30분 사용 시에도 심각한 두통 및 인지 정체 유발"
        ],
        "CueBand만의 독창적 극복 전략": [
            "POSTER V2 임베디드 INT8 경량 추론 연산으로 0.2초대 E2E 초저지연(223ms) 피드백 실현",
            "청각을 완전히 자유롭게 방존하는 비침습 햅틱 손목 피부 자극을 통해 본질적 피로도 해소",
            "MediaPipe 머리 각도 및 시선 벡터를 결합해 대화 상황 맥락 비언어 행동의 다채널 해독 구현",
            "일반 패션 안경테 규격의 초소형 글라스(40g) 및 웰니스 스타일 스마트 손목 밴드(35g) 은폐 설계",
            "피부 접촉형 분산 자극 매핑을 통해 하루 종일 상시 착용해도 거부감이 없는 쾌적성 보장"
        ]
    })
    st.dataframe(background_comparison, use_container_width=True, hide_index=True)

# ============================================================
# PAGE 4: SYSTEM DESIGN (연구 시스템 설계)
# ============================================================
def page_system_design():
    render_section_header("🏗️ CueBand 전체 시스템 아키텍처 설계")

    st.markdown("""
    ### 3-노드 분산 임베디드 저지연 아키텍처
    스마트 글라스 유닛의 초소형 카메라에서 캡처된 안면 이미지 프레임은 nRF5340 칩셋에 의해 압축 전송된 뒤, 
    스마트폰 모바일 에이전트에 탑재된 SOTA 표정 분류망(POSTER V2)을 활용해 즉각 감정이 판별됩니다. 
    이후 매핑 함수에 따라 물리 주파수로 변환된 햅틱 제어 코드가 BLE 5.0 무선 링크를 거쳐 ESP32-S3 햅틱 밴드로 주입되어 피부로 즉각 체감됩니다.
    """)

    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🕶️ 초경량 스마트 안경 상세 규격</h4>
            <div class="spec-card-list" style="margin-top:1.2rem;">
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">광학 수집 칩셋</span>
                        <span class="spec-value">3mm 초광각 720p 30fps 초소형 카메라 센서 힌지부 통합</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">임베디드 무선 SoC</span>
                        <span class="spec-value">nRF5340 (ARM Cortex-M33) 코어 기반 7.5ms BLE 가속 커넥터</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">배터리 및 전원공급</span>
                        <span class="spec-value">200mAh 리튬폴리머(LiPo) 안경다리 내부 매립 / 연속 4시간 가동</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">디자인 및 중량</span>
                        <span class="spec-value">TR-90 고탄성 무독성 생체 수지 프레임 / 총 무게 40g 미만 수렴</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">⌚ LRA 햅틱 손목 밴드 상세 규격</h4>
            <div class="spec-card-list" style="margin-top:1.2rem;">
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">햅틱 액추에이터</span>
                        <span class="spec-value">독립 구동형 초소형 LRA(선형 공진 모터) 4～6구 등간격 탑재</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">구동 컨트롤 및 드라이버</span>
                        <span class="spec-value">ESP32-S3 (듀얼 240MHz) / TI DRV2605L 햅틱 모터 드라이버 통합</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">소재 및 편의 규격</span>
                        <span class="spec-value">통기 메시 직물 결합형 의료용 실리콘 / IP54 등급 생활방수</span>
                    </div>
                </div>
                <div class="spec-item">
                    <div class="spec-circle"></div>
                    <div class="spec-text">
                        <span class="spec-label">총중량 및 구동 전원</span>
                        <span class="spec-value">총 중량 35g 이하 고정 / 250mAh LiPo 탑재로 상시 8시간 보증</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_divider()

    st.markdown("### ⏱️ 초저지연 기술을 위한 타임 버젯 분할 (E2E Latency: 223 ms)")
    
    stages = ["카메라 촬영 및 버퍼링", "POSTER V2 AI 판별", "햅틱 신호 매핑", "BLE 5.0 무선 송신", "LRA 모터 구동 지연"]
    durations = [33, 150, 10, 20, 10]
    colors = ["#94a3b8", "#2563eb", "#14b8a6", "#06b6d4", "#3b82f6"]
    
    fig = go.Figure()
    for stage, dur, color in zip(stages, durations, colors):
        fig.add_trace(go.Bar(
            y=["E2E Latency Budget"], x=[dur], name=stage,
            orientation='h', marker=dict(color=color),
            text=[f"{dur}ms"], textposition='inside',
            textfont=dict(color='white', family='Outfit', size=11)
        ))
        
    fig.update_layout(
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        height=180, margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(title="단위 지연 (ms)", gridcolor="rgba(0,0,0,0.04)", tickfont=dict(color="#475569")),
        yaxis=dict(showticklabels=False),
        legend=dict(orientation='h', y=-0.6, x=0.5, xanchor='center', font=dict(size=10, family='Outfit'))
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5: IMPLEMENTATION & VISUALIZATION (구현 과정 - AI & LRA)
# ============================================================
def page_implementation():
    render_section_header("⚙️ 구현 과정 (AI 안면 감정 해석 및 LRA 햅틱 파형 연계)")

    st.markdown("""
    ### 1. 안면 표정 분석 SOTA 신경망 모델 — POSTER V2
    CueBand의 핵심 정서 분류 시스템은 안면 인식 기술 분야 최선두 모델인 **POSTER V2 (Mao et al., 2023)** 아키텍처를 기반으로 설계되었습니다.
    기존 표정 분류 모델들이 얼굴의 부분적 각도 기울어짐이나 찡그릴 때의 불규칙 가려짐(안경 등) 상황에서 정확도가 급감하던 문제를 
    **Dual-Stream** 특징점 융합 구조를 통해 극복했습니다.
    """)

    # AI Accuracy chart comparison
    models = ["DeepFace (2014)", "EfficientFace (2021)", "DAN (2022)", "POSTER V2 (2023)"]
    raf_scores = [71.0, 88.4, 89.7, 92.21]
    
    fig_comp = go.Figure(go.Bar(
        x=models, y=raf_scores,
        marker=dict(
            color=['#cbd5e1', '#94a3b8', '#38bdf8', '#2563eb'],
            line=dict(color='white', width=1.5)
        ),
        text=[f"{v}%" for v in raf_scores],
        textposition='outside',
        textfont=dict(color='#0f172a', size=11, family="Outfit")
    ))
    
    fig_comp.update_layout(
        title=dict(text="RAF-DB 안면 감정 인식 정확도 벤치마크 점수 비교 (%)", font=dict(size=13, color="#0f172a", family="Outfit")),
        yaxis=dict(range=[60, 98], gridcolor="rgba(0,0,0,0.03)", tickfont=dict(color="#475569")),
        xaxis=dict(tickfont=dict(color="#475569")),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("""
    #### 🔧 POSTER V2 아키텍처 구체 사양 및 직관적 작동 원리
    - **Dual-Stream 구조**: 입력 이미지 전반의 ViT 뉘앙스 시각 특징을 다루는 **Image Stream**과, 얼굴 눈코입 미세 경계점을 추적하는 **Landmark Stream**을 독립 병렬 처리합니다.
    - **Cross-Attention**: 두 갈래의 스트림에서 산출된 가중치 맵을 어텐션 필터로 교차 연산하여, 얼굴 일부가 손이나 마이크 등으로 가려진 척박한 실대화 현장에서도 정확도를 획득합니다.
    - **INT8 모바일 양자화 가속**: 무거운 딥러닝 신경망을 지식 증류(Knowledge Distillation) 기법 및 정밀도 무손실 **INT8 정수 양자화(Quantization)** 가공을 거쳐 스마트폰 CPU 내부에서 150ms 이내에 즉각 추론되도록 최적화했습니다.
    """)

    render_divider()

    st.markdown("### 2. 5대 핵심 비언어적 햅틱 파형 시각화")
    st.markdown("상대방 비언어 정보 형태에 따라 다채널 LRA 액추에이터에 입력되는 구체적인 시간(ms) 대비 구동 전압/진폭(Amplitude) 파형을 실시간 탭 차트로 제공합니다.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🙂 고개 끄덕임 (Nod)", "😊 미소 / 웃음 (Smile)", "👀 시선 이탈 (Gaze Away)", "😐 반응 감소 (Reduced)", "😳 당황 / 멈칫함 (Confusion)"
    ])

    plot_layout = dict(
        yaxis=dict(title="진동 진폭 (Amplitude)", range=[-0.1, 1.05], gridcolor="rgba(0,0,0,0.03)", tickfont=dict(color="#475569")),
        xaxis=dict(title="지속 시간 (ms)", gridcolor="rgba(0,0,0,0.03)", tickfont=dict(color="#475569")),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a", family="Outfit"),
        height=280, margin=dict(l=10, r=10, t=30, b=10)
    )

    with tab1:
        t, s = generate_nod_pattern()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=s, mode='lines', fill='tozeroy',
                                 line=dict(color='#2563eb', width=2),
                                 fillcolor='rgba(37, 99, 235, 0.12)', name='LRA 구동 진폭'))
        fig.update_layout(title="고개 끄덕임: 짧게 두 번 톡톡 (▌ · ▌)", **plot_layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="lra-card">
            <h4 style="margin:0; color:#2563eb !important; font-weight:800;">💡 패턴 기획 의도</h4>
            <p style="margin: 0.5rem 0 0 0; font-size:0.9rem; line-height:1.7; color:#475569 !important;">
                상대방이 긍정 또는 동의의 끄덕임 신호를 보낼 때 작동합니다. 손가락으로 손목을 "톡 톡" 두드리듯 
                <b>짧은 연속 펄스 형태의 선명한 진동</b>을 2회 주어, 사용자가 상대의 적극적 끄덕임과 지지를 직관적으로 파악하게 합니다. (주파수: 180Hz)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        t, s = generate_smile_pattern()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=s, mode='lines', fill='tozeroy',
                                 line=dict(color='#10b981', width=2),
                                 fillcolor='rgba(16, 185, 129, 0.12)', name='LRA 구동 진폭'))
        fig.update_layout(title="미소/웃음: 부드럽게 한 번 (∿∿∿)", **plot_layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="lra-card">
            <h4 style="margin:0; color:#10b981 !important; font-weight:800;">💡 패턴 기획 의도</h4>
            <p style="margin: 0.5rem 0 0 0; font-size:0.9rem; line-height:1.7; color:#475569 !important;">
                상대방의 긍정적인 안면 미소나 유쾌한 웃음이 검출될 때 발생합니다. 
                시간 경과에 따라 서서히 차오르다 감쇄하는 <b>부드럽고 완만한 정현파(Sine wave) 펄스</b>로 따뜻하고 편안한 느낌을 선사합니다. (주파수: 150Hz)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        t, s_l = generate_gaze_left()
        _, s_r = generate_gaze_right()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=s_l, mode='lines', fill='tozeroy',
                                 line=dict(color='#ef4444', width=2),
                                 fillcolor='rgba(239, 68, 68, 0.1)', name='왼쪽 LRA'))
        fig.add_trace(go.Scatter(x=t, y=s_r, mode='lines', fill='tozeroy',
                                 line=dict(color='#3b82f6', width=2),
                                 fillcolor='rgba(59, 130, 246, 0.1)', name='오른쪽 LRA'))
        fig.update_layout(title="시선 이탈: 좌/우 LRA 순차 구동 (◁ · · ▷)", **plot_layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="lra-card">
            <h4 style="margin:0; color:#ef4444 !important; font-weight:800;">💡 패턴 기획 의도</h4>
            <p style="margin: 0.5rem 0 0 0; font-size:0.9rem; line-height:1.7; color:#475569 !important;">
                대화 상대방의 눈길이 좌측이나 우측 허공으로 빗나가며 집중이 흐트러질 때 트리거됩니다. 
                <b>왼쪽 LRA에서 시작해 오른쪽 LRA로 물 흐르듯 이어지는 순차 진동</b>을 활용하여 시선의 이동 방향과 흐름을 손목 감각으로 명확히 읽어내도록 돕습니다. (주파수: 150Hz)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        t, s = generate_reduced_pattern()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=s, mode='lines', fill='tozeroy',
                                 line=dict(color='#64748b', width=2),
                                 fillcolor='rgba(100, 116, 139, 0.12)', name='LRA 구동 진폭'))
        fig.update_layout(title="반응 감소: 약하게 한 번 (·)", **plot_layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="lra-card">
            <h4 style="margin:0; color:#64748b !important; font-weight:800;">💡 패턴 기획 의도</h4>
            <p style="margin: 0.5rem 0 0 0; font-size:0.9rem; line-height:1.7; color:#475569 !important;">
                상대방의 표정 변화량이 급감하거나 피드백 호응이 정체될 때(무표정의 지속) 트리거됩니다. 
                피로를 주지 않도록 **아주 스치듯이 짧고 약한 미세 햅틱 신호**를 1회만 내보내어 사용자가 화제를 전환하거나 대화 흐름을 환기하도록 돕습니다. (주파수: 120Hz)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        t, s = generate_confusion_pattern()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=s, mode='lines', fill='tozeroy',
                                 line=dict(color='#f59e0b', width=2),
                                 fillcolor='rgba(245, 158, 11, 0.12)', name='LRA 구동 진폭'))
        fig.update_layout(title="당황/멈칫함: 짧고 끊긴 패턴 (▌▌·▌▌▌)", **plot_layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="lra-card">
            <h4 style="margin:0; color:#f59e0b !important; font-weight:800;">💡 패턴 기획 의도</h4>
            <p style="margin: 0.5rem 0 0 0; font-size:0.9rem; line-height:1.7; color:#475569 !important;">
                상대방이 질문을 받고 당혹스러운 미세 표정을 보이거나 갑자기 동작을 멈추는 정서 불일치 순간을 탐지합니다. 
                <b>잘게 쪼개어지고 불규칙하게 떨리는 단속적 피드백</b>을 전달하여 상대의 일시적 멈칫함을 느낄 수 있도록 돕습니다. (주파수: 220Hz)
            </p>
        </div>
        """, unsafe_allow_html=True)

    render_divider()

    st.markdown("### 비언어 감지 정서 매핑 파형 설계 수치 비교표")
    
    mapping_data = pd.DataFrame({
        "상대방 비언어 상태": ["고개 끄덕임 (Nod)", "미소 / 웃음 (Smile)", "시선 이탈 (Gaze Away)", "반응 감소 (Reduced)", "당황 / 멈칫함 (Confusion)"],
        "CueBand 햅틱 번역 규격": ["선명한 2회 임펄스 진동", "정현파 온화한 1회 진동", "좌→우 햅틱 모터 순차 가동", "엷게 스치는 미소 진동 1회", "파쇄형 불규칙 펄스 진동"],
        "진폭 세기 조절": ["0.85 (강)", "0.60 (중)", "0.70 (중)", "0.30 (약)", "0.40 ～ 0.75 (불규칙)"],
        "구동 주파수": ["180 Hz", "150 Hz", "150 Hz", "120 Hz", "220 Hz"],
        "물리 자극 지속시간": ["400 ms 내외", "600 ms 내외", "800 ms 내외", "300 ms 내외", "700 ms 내외"]
    })
    
    st.dataframe(mapping_data, use_container_width=True, hide_index=True)

# ============================================================
# PAGE 6: EXPECTED EFFECTS & CONCLUSION (기대효과 및 결론)
# ============================================================
def page_outcomes():
    render_section_header("📈 연구 과제 기대 효과 및 최종 결론")

    st.markdown("""
    ### 시각장애인 정서 주권 실현과 보조공학 생태계 확장
    본 연구 계획은 첨단 딥러닝 비전 신경망인 **POSTER V2**와 비침습 햅틱 감각 제어 기술을 융합하여, 
    그간 사회적 교류 상황에서 철저히 소외되었던 시각장애인의 비언어적 정보 접근성을 비장애인 수준으로 상향 평준화하는 포용적 포석입니다.
    """)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🎓 학술적 및 기술적 파급</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                - 랜드마크 스케일 보정 어텐션망의 온디바이스 TFLite 최적화 기틀 제시<br/>
                - 시각장애인 참여형 HCI Co-design 및 촉각 변별도 학술 데이터 확립<br/>
                - 다채널 LRA 구동 햅틱 가이던스 라이브러리 소스코드 공개
            </p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🤝 공익적 및 사회 복지 기여</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                - 대면 커뮤니케이션 감정 배제의 극복 및 자신감 고양<br/>
                - 특수 교육 직무 교육, 장애인 취업 면접 상황 시 정서 장벽 해소<br/>
                - 심리적 고립감의 만성적 고착을 끊어 사회 참여 비용 축소
            </p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="component-card" style="height:100%;">
            <h4 style="color:#2563eb !important; font-weight:800; margin-top:0;">🚀 미래 확장성</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.92rem; line-height:1.7;">
                - 타인 표정 해석에 장벽이 있는 자폐 스펙트럼(ASD) 훈련 도구 활용<br/>
                - 화상 비즈니스 통화 시 햅틱 피드백 스마트워치 확장 연동<br/>
                - 범용 스마트워치(Galaxy Watch / Apple Watch) 모터 지원 연동 솔루션 구축
            </p>
        </div>
        """, unsafe_allow_html=True)

    render_divider()

    st.markdown("### 📅 연구 과제 핵심 마일스톤 및 일정 (24개월 전체 계획)")
    
    milestones_df = pd.DataFrame({
        "구분 단계": ["1단계: 사용자 요구 탐색 및 공동 설계", "2단계: 온디바이스 AI 신경망 모델 완성", "3단계: 햅틱 스마트 밴드 하드웨어 완성", "4단계: 무선 연동 최적화 및 동반자 앱 완성", "5단계: 대인 인터상호작용 임상 평가 및 최종 보고"],
        "주요 추진 일정": ["M1 ～ M6 (6개월)", "M3 ～ M12 (9개월)", "M6 ～ M14 (8개월)", "M12 ～ M18 (6개월)", "M16 ～ M24 (8개월)"],
        "핵심 산출 성과물": ["시각장애인 당사자 FGI 보고서, 햅틱 주파수 매핑 펄스 v1", "POSTER V2 미세조정 완료 TFLite 모델, 머리각도 추적 알고리즘", "ESP32-S3 기반 LRA 4-6채널 회로 및 하우징 시제품 2종", "End-to-End 초저지연 연동 프로토콜, 안드로이드 전용 매핑 관리 앱", "연구 효과 보고서, SCI(E)급 학술 논문 게재 2편 및 특허 출원 1건"]
    })
    st.dataframe(milestones_df, use_container_width=True, hide_index=True)

    st.markdown("### 💰 연구 과제 필요 소요 예산 총괄 명세")
    
    budget_df = pd.DataFrame({
        "예산 비목 항목": ["직접 인건비 (연구원 및 연구보조원)", "연구 장비 구입비 (GPU 서버 및 회로 가공기)", "연구 재료 소모비 (LRA 모터, ESP32 모듈, TR-90 실장부품)", "연구 활동비 (시각장애인 공동설계 사례비, 자문료)", "여비 및 학회 참가비", "논문 게재료 및 특허 등록 비용"],
        "정량적 배정 금액": ["180,000,000 원", "41,000,000 원", "3,000,000 원", "10,500,000 원", "8,000,000 원", "2,000,000 원"],
        "비고 및 세부 용도": ["책임연구원 1명, 공동연구원 1명, 보조원 2명 24개월 고용 비용", "Deep Learning 추론용 GPU 워크스테이션 및 3D 회로 실장 장치", "실제 프로토타입 50세트 양산용 원부자재 일체 소요비", "워크숍 5회 운영비 및 공동설계 피험자 소정의 참가 수수료", "국내외 보조공학/HCI 대표 학회 성과 발표 여비 일체", "글로벌 상위 Q1 저널 게재료 및 특허 출원/대리인 수수료"]
    })
    st.dataframe(budget_df, use_container_width=True, hide_index=True)
    st.markdown("<p style='font-size: 0.95rem; font-weight: 800; text-align: right; color: #2563eb;'>총 배정 과제 연구비 합계: 약 244,500,000 원</p>", unsafe_allow_html=True)

    render_divider()

    st.markdown("### 🔒 연구의 안전성 및 윤리적 보호 장치")
    
    st.markdown("""
    #### 1. 생명윤리위원회(IRB) 가이드라인 엄격 준수
    연구 개시 전, 시각장애인 참여자 권익 보호와 감각 피로도 시험의 안전성 검증을 위해 주관 기관 생명윤리심의위원회(IRB) 승인을 전수 취득합니다. 
    동의서 및 임상 절차 설명문은 시각장애인이 손쉽게 해독할 수 있도록 **점자 인쇄본 및 AI 음성 낭독 매체**로 이중 교차 배포합니다.

    #### 2. 촬영 대상자의 초상권 및 프라이버시 보호 장치
    스마트 글래스 내부에는 사진/동영상을 누적 보존하기 위한 플래시 메모리 등 비휘발성 저장 매체를 원천 배제합니다. 
    카메라 센서에서 취득된 이미지 프레임은 CPU 내의 휘발성 프레임 버퍼상에서 POSTER V2 추론 분류가 완료된 즉시 **완전 소거(Zero-trace)** 됩니다. 
    또한 안경 안쪽과 바깥에 고정형 LED 인디케이터가 탑재되어, 카메라 가동 시 안경테가 부드럽게 점멸함으로써 타인에게 장비 가동 상태를 시각적으로 은은하게 공지하여 프라이버시 불안을 소멸시킵니다.

    #### 3. AI 모델 편향 보정
    특정 인종, 연령층, 혹은 성별 차이에 의해 AI 모델이 표정을 찡그림이나 다른 정서로 오역할 가능성을 전면 차단하기 위해, AffectNet 및 RAF-DB 등 글로벌 대형 정서 말뭉치를 결합 검증하여 감정 파싱의 완전한 기하학적 중립성을 수립합니다.
    """)

    render_divider()

    st.markdown("### 📚 참고문헌 (Scientific References)")
    st.markdown("""
    1. Mehrabian, A. (1971). *Silent Messages*. Wadsworth Publishing.
    2. Ekman, P. (1992). An argument for basic emotions. *Cognition & Emotion*, 6(3-4), 169-200.
    3. Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161-1178.
    4. Hertenstein, M. J. et al. (2006). Touch communicates distinct emotions. *Emotion*, 6(3), 528-533.
    5. Mollahosseini, A. et al. (2019). AffectNet: A database for facial expression in the wild. *IEEE Transactions on Affective Computing*, 10(1), 18-31.
    6. **Mao, J. et al. (2023). POSTER V2: A simpler and stronger facial expression recognition network. *arXiv:2301.12149*.**
    7. Tsai, Y. H. H. et al. (2019). Multimodal Transformer for Joint Systematic Prediction. *ACL 2019*.
    8. Noroozi, F. et al. (2018). Survey on emotional body gesture recognition. *IEEE Transactions on Affective Computing*, 12(2), 505-523.
    9. Yoo, Y. et al. (2015). Emotional responses of tactile icons on hand wristwear. *IEEE World Haptics*.
    10. Lahtinen, R. (2008). *Haptices and haptemes for the deafblind community*. University of Helsinki.
    """)

# ============================================================
# SIDEBAR NAVIGATION CONFIGURATION (6 PAGES MENU - NO SPACER BUG)
# ============================================================
with st.sidebar:
    # Sidebar Brand Header - safe from markdown code block parser
    logo_svg_sidebar = get_logo_svg(42)
    html_sidebar = f"""
    <div class="sidebar-brand">
        {logo_svg_sidebar}
        <div class="sidebar-title">CueBand</div>
        <div class="sidebar-subtitle">AI Assistive Interface</div>
    </div>
    """
    safe_html(html_sidebar)

    st.markdown('<div class="custom-divider" style="margin: 0.8rem 0;"></div>', unsafe_allow_html=True)

    # 6-page navigation layout
    page = st.radio(
        "📑 NAVIGATION",
        [
            "🏠 홈 (CueBand 소개 및 인터랙티브 체험)",
            "🔬 연구 배경 및 필요성",
            "🎯 연구과제 및 목표",
            "🏗️ 연구 시스템 설계",
            "⚙️ 구현 과정 (AI 모델 & 햅틱 시각화)",
            "📈 기대효과 및 결론"
        ],
        label_visibility="collapsed"
    )

    st.markdown('<div class="custom-divider" style="margin: 0.8rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; font-size: 0.72rem; color: #64748b; padding: 0.5rem; line-height: 1.7;">
        <b>CueBand Core Config</b><br/><br/>
        🕶️ TR-90 Glasses (40g↓)<br/>
        🧠 POSTER V2 TFLite INT8<br/>
        ⌚ LRA Multichannel (35g↓)<br/>
        ⚡ E2E Latency: 223ms<br/>
        <br/>
        <span style="color: #2563eb; font-weight: 800; letter-spacing:0.5px;">CYBER TECH WHITE THEME</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN ROUTING
# ============================================================
page_map = {
    "🏠 홈 (CueBand 소개 및 인터랙티브 체험)": page_home,
    "🔬 연구 배경 및 필요성": page_background,
    "🎯 연구과제 및 목표": page_objectives,
    "🏗️ 연구 시스템 설계": page_system_design,
    "⚙️ 구현 과정 (AI 모델 & 햅틱 시각화)": page_implementation,
    "📈 기대효과 및 결론": page_outcomes
}

# Main Application Title Rendering with Circular Tech Logo next to it
is_home = (page == "🏠 홈 (CueBand 소개 및 인터랙티브 체험)")
render_brand_header("CueBand", "시각장애인을 위한 비언어 정서 신호 AI 촉각 번역 인터페이스", is_home=is_home)

# Route to selected page function
page_map[page]()

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <p style="font-weight: 800; color: #475569 !important; letter-spacing: -0.5px;">CueBand — AI 스마트 글라스와 햅틱 손목밴드를 통한 시각장애인 비언어 정서 신호 번역 인터페이스 기획</p>
    <p>© 2026 | Designed with Cybernetic Light Grid Tech Layout</p>
</div>
""", unsafe_allow_html=True)



st.markdown("---")

st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
    © 2026 Seohyeon Woo. This project is for educational and portfolio purposes.<br>
    Unauthorized copying, redistribution, or commercial use is not permitted.
    </div>
    """,
    unsafe_allow_html=True
)
