"""
╔══════════════════════════════════════════════════════════╗
║   PARALLEL SELF — AI Personality Clone Simulator        ║
║   Version_You.exe | Loading Fierce Mode…                ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import numpy as np
import time
import json

from personality_engine import (
    QUESTIONS, TRAIT_NAMES, TRAIT_LABELS,
    analyze_text_sample, compute_profile, apply_modifications,
    compute_divergence, get_personality_archetype,
)
from clone_engine import SCENARIOS, generate_comparison

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PARALLEL SELF",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cyberpunk CSS ─────────────────────────────────────────────────────────────

CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ── Root variables ── */
:root {
    --neon-cyan: #00f0ff;
    --neon-magenta: #ff00aa;
    --neon-green: #39ff14;
    --neon-yellow: #ffe600;
    --neon-orange: #ff6a00;
    --dark-bg: #0a0a0f;
    --dark-surface: #12121a;
    --dark-card: #1a1a2e;
    --dark-border: #2a2a3e;
    --text-primary: #e0e0ff;
    --text-muted: #8888aa;
}

/* ── Global background ── */
.stApp, [data-testid="stAppViewContainer"] {
    background: var(--dark-bg) !important;
    color: var(--text-primary) !important;
}
.stApp {
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(0, 240, 255, 0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(255, 0, 170, 0.03) 0%, transparent 50%) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #0d0d18 0%, #12121f 100%) !important;
    border-right: 1px solid var(--dark-border) !important;
}

/* ── Headers ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif !important;
    color: var(--neon-cyan) !important;
    letter-spacing: 2px !important;
}
h1 {
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.5), 0 0 40px rgba(0, 240, 255, 0.2) !important;
    border-bottom: 2px solid var(--neon-cyan) !important;
    padding-bottom: 10px !important;
}

/* ── Text ── */
p, li, span, div, label {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-primary) !important;
    font-size: 1.05rem !important;
}

/* ── Cards / containers ── */
.css-1r6slb0, .css-12oz5g7,
[data-testid="stMetric"],
[data-testid="stExpander"] {
    background: var(--dark-card) !important;
    border: 1px solid var(--dark-border) !important;
    border-radius: 8px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase !important;
    font-size: 0.85rem !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--neon-cyan) !important;
    font-family: 'Orbitron', sans-serif !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 170, 0.15)) !important;
    border: 1px solid var(--neon-cyan) !important;
    color: var(--neon-cyan) !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 1px !important;
    padding: 0.5rem 1.5rem !important;
    border-radius: 4px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.3), rgba(255, 0, 170, 0.3)) !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.4), 0 0 30px rgba(0, 240, 255, 0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Radio buttons & selectbox ── */
.stRadio > div, .stSelectbox > div {
    background: var(--dark-card) !important;
    border-radius: 8px !important;
    padding: 8px !important;
}
[data-testid="stRadio"] label span {
    color: var(--text-primary) !important;
}

/* ── Sliders ── */
.stSlider > div > div > div > div {
    background: var(--neon-cyan) !important;
}
.stSlider [data-testid="stThumbValue"] {
    color: var(--neon-cyan) !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Text areas & inputs ── */
.stTextArea textarea, .stTextInput input {
    background: var(--dark-surface) !important;
    border: 1px solid var(--dark-border) !important;
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
    border-radius: 4px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta)) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--dark-surface) !important;
    border-radius: 8px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 240, 255, 0.15) !important;
    color: var(--neon-cyan) !important;
    border-bottom: 2px solid var(--neon-cyan) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--dark-card) !important;
    border: 1px solid var(--dark-border) !important;
}

/* ── Neon glow box ── */
.neon-box {
    background: var(--dark-card);
    border: 1px solid var(--neon-cyan);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.1), inset 0 0 15px rgba(0, 240, 255, 0.05);
    margin: 10px 0;
}
.neon-box-magenta {
    background: var(--dark-card);
    border: 1px solid var(--neon-magenta);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(255, 0, 170, 0.1), inset 0 0 15px rgba(255, 0, 170, 0.05);
    margin: 10px 0;
}
.neon-box-green {
    background: var(--dark-card);
    border: 1px solid var(--neon-green);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.1), inset 0 0 15px rgba(57, 255, 20, 0.05);
    margin: 10px 0;
}

/* ── Terminal text ── */
.terminal {
    font-family: 'Share Tech Mono', monospace;
    color: var(--neon-green);
    font-size: 0.9rem;
    line-height: 1.8;
}
.terminal-cyan {
    font-family: 'Share Tech Mono', monospace;
    color: var(--neon-cyan);
    font-size: 0.95rem;
}
.terminal-magenta {
    font-family: 'Share Tech Mono', monospace;
    color: var(--neon-magenta);
    font-size: 0.95rem;
}

/* ── Trait bar ── */
.trait-bar-container {
    background: var(--dark-surface);
    border-radius: 4px;
    height: 24px;
    overflow: hidden;
    margin: 4px 0 12px 0;
    position: relative;
}
.trait-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}
.trait-bar-cyan {
    background: linear-gradient(90deg, rgba(0, 240, 255, 0.3), var(--neon-cyan));
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}
.trait-bar-magenta {
    background: linear-gradient(90deg, rgba(255, 0, 170, 0.3), var(--neon-magenta));
    box-shadow: 0 0 10px rgba(255, 0, 170, 0.3);
}

/* ── Divider ── */
.cyber-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
    margin: 20px 0;
}

/* ── Hide Streamlit defaults ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dark-bg); }
::-webkit-scrollbar-thumb { background: var(--dark-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--neon-cyan); }
</style>
"""

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)


# ── Utility Functions ─────────────────────────────────────────────────────────

def cyber_header(text, subtitle=None):
    """Render a cyberpunk-styled header."""
    html = f'<h1 style="text-align:center; margin-bottom: 5px;">{text}</h1>'
    if subtitle:
        html += f'<p style="text-align:center; color: #8888aa; font-family: Share Tech Mono, monospace; font-size: 0.9rem; letter-spacing: 3px;">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def neon_metric(label, value, color="cyan"):
    """Render a glowing metric."""
    color_map = {"cyan": "#00f0ff", "magenta": "#ff00aa", "green": "#39ff14", "yellow": "#ffe600", "orange": "#ff6a00"}
    c = color_map.get(color, "#00f0ff")
    st.markdown(f"""
    <div style="text-align:center; padding:15px; background: #1a1a2e; border:1px solid {c}; border-radius:8px;
                box-shadow: 0 0 12px {c}33; margin: 5px 0;">
        <div style="font-family:'Share Tech Mono',monospace; color:#8888aa; font-size:0.75rem; text-transform:uppercase; letter-spacing:2px;">{label}</div>
        <div style="font-family:'Orbitron',sans-serif; color:{c}; font-size:1.8rem; text-shadow: 0 0 10px {c}88; margin-top:4px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def trait_bar(label_low, label_high, value, color="cyan"):
    """Render a custom trait progress bar."""
    color_map = {"cyan": "#00f0ff", "magenta": "#ff00aa", "green": "#39ff14"}
    c = color_map.get(color, "#00f0ff")
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#8888aa;">
        <span>{label_low}</span>
        <span style="color:{c}; font-size:0.9rem;">{value:.0f}%</span>
        <span>{label_high}</span>
    </div>
    <div style="background:#12121a; border-radius:4px; height:22px; overflow:hidden; margin:4px 0 16px 0; border:1px solid #2a2a3e;">
        <div style="width:{value}%; height:100%; background:linear-gradient(90deg, {c}44, {c}); border-radius:4px;
                    box-shadow: 0 0 8px {c}55; transition: width 0.8s ease;"></div>
    </div>
    """, unsafe_allow_html=True)


def typing_effect(text):
    """Simulate terminal typing in Streamlit."""
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(f'<span class="terminal">{displayed}▊</span>', unsafe_allow_html=True)
        time.sleep(0.015)
    placeholder.markdown(f'<span class="terminal">{displayed}</span>', unsafe_allow_html=True)


def render_response_box(title, response, color_class="neon-box"):
    """Render a response in a neon-bordered box."""
    st.markdown(f"""
    <div class="{color_class}">
        <div style="font-family:'Orbitron',sans-serif; font-size:0.85rem; letter-spacing:2px; margin-bottom:10px;
                    color:{'#00f0ff' if 'cyan' in color_class or color_class == 'neon-box' else '#ff00aa'};">
            {title}
        </div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.05rem; line-height:1.7; color:#e0e0ff;">
            {response}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Initialize Session State ──────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "home"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "base_profile" not in st.session_state:
    st.session_state.base_profile = None
if "clone_profile" not in st.session_state:
    st.session_state.clone_profile = None
if "text_sample" not in st.session_state:
    st.session_state.text_sample = ""
if "text_analysis" not in st.session_state:
    st.session_state.text_analysis = None
if "modifications" not in st.session_state:
    st.session_state.modifications = {t: 0 for t in TRAIT_NAMES}


# ── Sidebar Navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0;">
        <div style="font-family:'Orbitron',sans-serif; font-size:1.4rem; color:#00f0ff;
                    text-shadow: 0 0 15px rgba(0,240,255,0.5); letter-spacing:3px;">
            PARALLEL<br>SELF
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#8888aa;
                    letter-spacing:2px; margin-top:5px;">
            v2.0 // NEURAL REPLICA ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border:none; height:1px; background: linear-gradient(90deg, transparent, #00f0ff, transparent);">', unsafe_allow_html=True)

    nav_options = {
        "home": "🏠  HOME",
        "profiling": "🧬  PROFILING",
        "clone_lab": "🔧  CLONE LAB",
        "simulation": "⚡  SIMULATION",
        "dashboard": "📊  DASHBOARD",
    }

    for key, label in nav_options.items():
        is_active = st.session_state.page == key
        if st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = key
            st.rerun()

    st.markdown('<hr style="border:none; height:1px; background: linear-gradient(90deg, transparent, #2a2a3e, transparent);">', unsafe_allow_html=True)

    # Status panel
    profile_status = "✅ LOADED" if st.session_state.base_profile else "⬜ PENDING"
    clone_status = "✅ ACTIVE" if st.session_state.clone_profile else "⬜ PENDING"

    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#8888aa; padding:10px;">
        <div>SYSTEM STATUS</div>
        <div style="margin-top:8px;">
            <span style="color:{'#39ff14' if st.session_state.base_profile else '#555'};">●</span> Base Profile: {profile_status}
        </div>
        <div style="margin-top:4px;">
            <span style="color:{'#ff00aa' if st.session_state.clone_profile else '#555'};">●</span> Clone Status: {clone_status}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE: HOME ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "home":
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px 0;">
        <div style="font-family:'Orbitron',sans-serif; font-size:3rem; color:#00f0ff;
                    text-shadow: 0 0 30px rgba(0,240,255,0.6), 0 0 60px rgba(0,240,255,0.2);
                    letter-spacing: 6px;">
            PARALLEL SELF
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:1rem; color:#ff00aa;
                    letter-spacing:4px; margin-top:10px;
                    text-shadow: 0 0 10px rgba(255,0,170,0.5);">
            AI PERSONALITY CLONE SIMULATOR
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#8888aa;
                    margin-top:20px; letter-spacing:2px;">
            VERSION_YOU.EXE // LOADING FIERCE MODE...
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="neon-box" style="text-align:center; min-height:180px;">
            <div style="font-size:2rem;">🧬</div>
            <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:0.9rem; margin:10px 0;">PROFILE</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem;">
                Answer 20 behavioral questions.<br>AI extracts your personality DNA.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="neon-box-magenta" style="text-align:center; min-height:180px;">
            <div style="font-size:2rem;">🔧</div>
            <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:0.9rem; margin:10px 0;">MODIFY</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem;">
                Adjust trait sliders.<br>Confidence +20%, Fear −40%.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="neon-box-green" style="text-align:center; min-height:180px;">
            <div style="font-size:2rem;">⚡</div>
            <div style="font-family:'Orbitron',sans-serif; color:#39ff14; font-size:0.9rem; margin:10px 0;">SIMULATE</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem;">
                Compare Real You vs Parallel You<br>across real-life scenarios.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("⚡  INITIALIZE NEURAL REPLICA", use_container_width=True):
            st.session_state.page = "profiling"
            st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:30px; font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#555;">
        NLP Feature Extraction • Personality Trait Clustering • Sentiment Polarity Scoring<br>
        Behavioral Simulation Modeling • Parameter-Controlled Response Generation
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE: PROFILING ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "profiling":
    cyber_header("🧬 PERSONALITY PROFILING", "NEURAL PATTERN EXTRACTION")

    # Progress
    answered = len(st.session_state.answers)
    total = len(QUESTIONS)
    progress = answered / total if total > 0 else 0
    st.progress(progress)
    st.markdown(f'<div class="terminal-cyan" style="text-align:center;">{answered}/{total} RESPONSES CAPTURED</div>', unsafe_allow_html=True)

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # Questions
    current_trait = None
    for i, q in enumerate(QUESTIONS):
        if q["trait"] != current_trait:
            current_trait = q["trait"]
            low_label, high_label = TRAIT_LABELS[current_trait]
            st.markdown(f"""
            <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:0.85rem;
                        letter-spacing:2px; margin:25px 0 10px 0; padding:8px;
                        border-left:3px solid #ff00aa;">
                DIMENSION: {current_trait.replace('_', ' ').upper()} ({low_label} → {high_label})
            </div>
            """, unsafe_allow_html=True)

        options = [opt[0] for opt in q["options"]]
        selected = st.radio(
            f"Q{i+1}: {q['text']}",
            options=options,
            key=f"q_{i}",
            index=None if i not in st.session_state.answers else options.index(
                next(opt[0] for opt in q["options"] if opt[1] == st.session_state.answers[i])
            ),
        )

        if selected is not None:
            score = next(opt[1] for opt in q["options"] if opt[0] == selected)
            st.session_state.answers[i] = score

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # Text sample (optional)
    st.markdown("""
    <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:0.85rem; letter-spacing:2px; margin-bottom:10px;">
        📝 OPTIONAL: TEXT SAMPLE ANALYSIS
    </div>
    <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem; margin-bottom:10px;">
        Paste a paragraph about yourself, your goals, or how you handle challenges.
        The AI will extract additional personality signals from your writing style.
    </div>
    """, unsafe_allow_html=True)

    text_sample = st.text_area(
        "Write about yourself (optional)",
        value=st.session_state.text_sample,
        height=120,
        placeholder="Example: I believe in pushing boundaries. When I face a challenge, I...",
        label_visibility="collapsed",
    )
    st.session_state.text_sample = text_sample

    # Generate profile
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧠  GENERATE PERSONALITY PROFILE", use_container_width=True):
            if len(st.session_state.answers) < 10:
                st.warning("⚠️ Please answer at least 10 questions for an accurate profile.")
            else:
                with st.spinner(""):
                    # Show boot sequence
                    boot = st.empty()
                    boot_msgs = [
                        "▸ Initializing Neural Pattern Scanner...",
                        "▸ Extracting behavioral signatures...",
                        "▸ Running sentiment polarity analysis...",
                        "▸ Clustering personality dimensions...",
                        "▸ Compiling identity matrix...",
                        "▸ Profile generation complete ✓",
                    ]
                    for msg in boot_msgs:
                        boot.markdown(f'<span class="terminal">{msg}</span>', unsafe_allow_html=True)
                        time.sleep(0.4)

                    # Compute profile
                    question_scores = {}
                    for idx, score in st.session_state.answers.items():
                        trait = QUESTIONS[idx]["trait"]
                        if trait not in question_scores:
                            question_scores[trait] = []
                        question_scores[trait].append(score)

                    text_analysis = None
                    if text_sample.strip():
                        text_analysis = analyze_text_sample(text_sample)
                        st.session_state.text_analysis = text_analysis

                    profile = compute_profile(question_scores, text_analysis)
                    st.session_state.base_profile = profile

                    boot.empty()

                st.success("✅ Profile generated! Navigate to CLONE LAB to create your parallel self.")
                time.sleep(1)
                st.session_state.page = "clone_lab"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE: CLONE LAB ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "clone_lab":
    cyber_header("🔧 CLONE LAB", "TRAIT MODIFICATION ENGINE")

    if st.session_state.base_profile is None:
        st.markdown("""
        <div class="neon-box" style="text-align:center;">
            <div class="terminal" style="color:#ff6a00;">⚠ NO BASE PROFILE DETECTED</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; margin-top:10px;">
                Complete the Personality Profiling first to initialize your neural replica.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Go to Profiling"):
            st.session_state.page = "profiling"
            st.rerun()
    else:
        base = st.session_state.base_profile
        archetype, arch_desc = get_personality_archetype(base)

        # Show base profile
        st.markdown(f"""
        <div class="neon-box">
            <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:0.85rem; letter-spacing:2px;">
                BASE IDENTITY: {archetype}
            </div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:1rem; margin-top:5px;">
                {arch_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Side-by-side: base traits + modification sliders
        col_base, col_mod = st.columns(2)

        with col_base:
            st.markdown("""
            <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:0.85rem; letter-spacing:2px; margin-bottom:15px;">
                🟢 BASE PROFILE
            </div>
            """, unsafe_allow_html=True)
            for trait in TRAIT_NAMES:
                low_label, high_label = TRAIT_LABELS[trait]
                trait_bar(low_label, high_label, base[trait], "cyan")

        with col_mod:
            st.markdown("""
            <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:0.85rem; letter-spacing:2px; margin-bottom:15px;">
                🔴 MODIFICATION SLIDERS
            </div>
            """, unsafe_allow_html=True)
            modifications = {}
            for trait in TRAIT_NAMES:
                low_label, high_label = TRAIT_LABELS[trait]
                mod = st.slider(
                    f"{trait.replace('_', ' ').title()}",
                    min_value=-50,
                    max_value=50,
                    value=st.session_state.modifications.get(trait, 0),
                    step=5,
                    key=f"mod_{trait}",
                    help=f"Adjust {low_label} ↔ {high_label}",
                )
                modifications[trait] = mod

        st.session_state.modifications = modifications

        # Preset buttons
        st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',sans-serif; color:#ffe600; font-size:0.8rem; letter-spacing:2px; margin-bottom:10px;">
            ⚡ QUICK PRESETS
        </div>
        """, unsafe_allow_html=True)

        preset_cols = st.columns(5)
        presets = {
            "🔥 FIERCE": {"confidence": 30, "aggression": 25, "optimism": 15, "risk_taking": 20, "discipline": 10},
            "🧊 STOIC": {"confidence": 15, "aggression": -10, "optimism": 5, "risk_taking": -15, "discipline": 35},
            "🚀 BOLD": {"confidence": 20, "aggression": 10, "optimism": 25, "risk_taking": 35, "discipline": 5},
            "🎯 FOCUSED": {"confidence": 10, "aggression": 5, "optimism": 10, "risk_taking": -10, "discipline": 40},
            "⚡ MAX": {"confidence": 50, "aggression": 50, "optimism": 50, "risk_taking": 50, "discipline": 50},
        }
        for col, (preset_name, preset_vals) in zip(preset_cols, presets.items()):
            with col:
                if st.button(preset_name, use_container_width=True, key=f"preset_{preset_name}"):
                    st.session_state.modifications = preset_vals
                    st.rerun()

        # Generate clone
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡  ACTIVATE PARALLEL CLONE", use_container_width=True):
                with st.spinner(""):
                    boot = st.empty()
                    for msg in [
                        "▸ Applying trait modifications...",
                        "▸ Recalibrating neural pathways...",
                        "▸ Stabilizing clone identity matrix...",
                        "▸ Clone activation complete ✓",
                    ]:
                        boot.markdown(f'<span class="terminal">{msg}</span>', unsafe_allow_html=True)
                        time.sleep(0.35)

                    clone = apply_modifications(base, modifications)
                    st.session_state.clone_profile = clone
                    boot.empty()

                # Show clone profile
                clone_arch, clone_desc = get_personality_archetype(clone)
                divergence = compute_divergence(base, clone)

                st.markdown(f"""
                <div class="neon-box-magenta">
                    <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:0.85rem; letter-spacing:2px;">
                        CLONE IDENTITY: {clone_arch}
                    </div>
                    <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:1rem; margin-top:5px;">
                        {clone_desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Divergence metrics
                m1, m2, m3 = st.columns(3)
                with m1:
                    neon_metric("IDENTITY DIVERGENCE", f"{divergence['identity_divergence']}%", "magenta")
                with m2:
                    neon_metric("CLONE STABILITY", f"{divergence['clone_stability']}%", "cyan")
                with m3:
                    neon_metric("DOMINANT SHIFT", divergence['dominant_shift'].replace('_', ' ').upper(), "green")

                # Clone trait bars
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:0.85rem; letter-spacing:2px; margin-bottom:15px;">
                    🔴 CLONE PROFILE
                </div>
                """, unsafe_allow_html=True)
                for trait in TRAIT_NAMES:
                    low_label, high_label = TRAIT_LABELS[trait]
                    trait_bar(low_label, high_label, clone[trait], "magenta")

                st.success("✅ Clone active! Navigate to SIMULATION to test scenarios.")


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE: SIMULATION ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "simulation":
    cyber_header("⚡ SCENARIO SIMULATION", "REAL YOU vs PARALLEL YOU")

    if st.session_state.base_profile is None or st.session_state.clone_profile is None:
        st.markdown("""
        <div class="neon-box" style="text-align:center;">
            <div class="terminal" style="color:#ff6a00;">⚠ PROFILES NOT READY</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; margin-top:10px;">
                Complete Profiling and Clone Lab first to run simulations.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Scenario selector
        scenario_options = {k: f"{v['icon']} {v['title']}" for k, v in SCENARIOS.items()}
        selected_scenario = st.selectbox(
            "SELECT SCENARIO",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
        )

        scenario = SCENARIOS[selected_scenario]
        st.markdown(f"""
        <div class="neon-box" style="text-align:center;">
            <div style="font-size:2.5rem;">{scenario['icon']}</div>
            <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:1.1rem; margin:10px 0;">
                {scenario['title'].upper()}
            </div>
            <div style="font-family:'Rajdhani',sans-serif; color:#e0e0ff; font-size:1.1rem; line-height:1.7;">
                "{scenario['description']}"
            </div>
            <div style="font-family:'Share Tech Mono',monospace; color:#8888aa; font-size:0.8rem; margin-top:10px;">
                Context: {scenario['context']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡  RUN SIMULATION", use_container_width=True):
                with st.spinner(""):
                    boot = st.empty()
                    for msg in [
                        "▸ Loading scenario parameters...",
                        "▸ Generating base personality response...",
                        "▸ Generating clone personality response...",
                        "▸ Running comparative analysis...",
                        "▸ Simulation complete ✓",
                    ]:
                        boot.markdown(f'<span class="terminal">{msg}</span>', unsafe_allow_html=True)
                        time.sleep(0.35)
                    boot.empty()

                result = generate_comparison(
                    st.session_state.base_profile,
                    st.session_state.clone_profile,
                    selected_scenario,
                )

                # Display responses
                col_real, col_clone = st.columns(2)
                with col_real:
                    render_response_box("🟢 REAL YOU", result["real_response"], "neon-box")
                with col_clone:
                    render_response_box("🔴 PARALLEL YOU", result["clone_response"], "neon-box-magenta")

                # Analysis
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="neon-box-green">
                    <div style="font-family:'Orbitron',sans-serif; color:#39ff14; font-size:0.85rem; letter-spacing:2px; margin-bottom:10px;">
                        📊 COMPARATIVE ANALYSIS
                    </div>
                    <div style="font-family:'Rajdhani',sans-serif; color:#e0e0ff; font-size:1rem; line-height:1.8;">
                        {result['analysis']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Quick-run all scenarios
        st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
        with st.expander("🔄 RUN ALL SCENARIOS"):
            if st.button("Generate All Comparisons"):
                for sc_key, sc_data in SCENARIOS.items():
                    result = generate_comparison(
                        st.session_state.base_profile,
                        st.session_state.clone_profile,
                        sc_key,
                    )
                    st.markdown(f"### {sc_data['icon']} {sc_data['title']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        render_response_box("REAL YOU", result["real_response"], "neon-box")
                    with c2:
                        render_response_box("PARALLEL YOU", result["clone_response"], "neon-box-magenta")
                    st.markdown(f"""<div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem; margin:10px 0 25px 0;">{result['analysis']}</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE: DASHBOARD ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "dashboard":
    cyber_header("📊 IDENTITY DASHBOARD", "FULL NEURAL ANALYSIS")

    if st.session_state.base_profile is None:
        st.markdown("""
        <div class="neon-box" style="text-align:center;">
            <div class="terminal" style="color:#ff6a00;">⚠ NO DATA AVAILABLE</div>
            <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; margin-top:10px;">
                Complete Profiling to view your dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        base = st.session_state.base_profile
        clone = st.session_state.clone_profile

        # Archetypes
        base_arch, base_desc = get_personality_archetype(base)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="neon-box" style="text-align:center;">
                <div style="font-family:'Share Tech Mono',monospace; color:#8888aa; font-size:0.7rem; letter-spacing:2px;">BASE IDENTITY</div>
                <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:1.2rem; margin:8px 0;">{base_arch}</div>
                <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem;">{base_desc}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if clone:
                clone_arch, clone_desc = get_personality_archetype(clone)
                st.markdown(f"""
                <div class="neon-box-magenta" style="text-align:center;">
                    <div style="font-family:'Share Tech Mono',monospace; color:#8888aa; font-size:0.7rem; letter-spacing:2px;">CLONE IDENTITY</div>
                    <div style="font-family:'Orbitron',sans-serif; color:#ff00aa; font-size:1.2rem; margin:8px 0;">{clone_arch}</div>
                    <div style="font-family:'Rajdhani',sans-serif; color:#8888aa; font-size:0.95rem;">{clone_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="neon-box-magenta" style="text-align:center; opacity:0.5;">
                    <div style="font-family:'Share Tech Mono',monospace; color:#8888aa; font-size:0.7rem;">CLONE NOT ACTIVATED</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Trait comparison
        st.markdown("""
        <div style="font-family:'Orbitron',sans-serif; color:#00f0ff; font-size:0.85rem; letter-spacing:2px; margin-bottom:15px;">
            TRAIT COMPARISON MATRIX
        </div>
        """, unsafe_allow_html=True)

        for trait in TRAIT_NAMES:
            low_label, high_label = TRAIT_LABELS[trait]
            base_val = base[trait]
            clone_val = clone[trait] if clone else None

            st.markdown(f"""
            <div style="font-family:'Orbitron',sans-serif; color:#e0e0ff; font-size:0.8rem; letter-spacing:1px; margin-top:12px;">
                {trait.replace('_', ' ').upper()}
            </div>
            """, unsafe_allow_html=True)

            # Base bar
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin:4px 0;">
                <span style="font-family:'Share Tech Mono',monospace; color:#00f0ff; font-size:0.75rem; width:60px;">BASE</span>
                <div style="flex:1; background:#12121a; border-radius:4px; height:18px; border:1px solid #2a2a3e;">
                    <div style="width:{base_val}%; height:100%; background:linear-gradient(90deg, #00f0ff44, #00f0ff); border-radius:4px;
                                box-shadow: 0 0 6px #00f0ff55;"></div>
                </div>
                <span style="font-family:'Share Tech Mono',monospace; color:#00f0ff; font-size:0.8rem; width:45px; text-align:right;">{base_val:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)

            # Clone bar
            if clone_val is not None:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; margin:4px 0;">
                    <span style="font-family:'Share Tech Mono',monospace; color:#ff00aa; font-size:0.75rem; width:60px;">CLONE</span>
                    <div style="flex:1; background:#12121a; border-radius:4px; height:18px; border:1px solid #2a2a3e;">
                        <div style="width:{clone_val}%; height:100%; background:linear-gradient(90deg, #ff00aa44, #ff00aa); border-radius:4px;
                                    box-shadow: 0 0 6px #ff00aa55;"></div>
                    </div>
                    <span style="font-family:'Share Tech Mono',monospace; color:#ff00aa; font-size:0.8rem; width:45px; text-align:right;">{clone_val:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)

        # Divergence metrics
        if clone:
            st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
            divergence = compute_divergence(base, clone)

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                neon_metric("DIVERGENCE INDEX", f"{divergence['identity_divergence']}%", "magenta")
            with m2:
                neon_metric("CLONE STABILITY", f"{divergence['clone_stability']}%", "cyan")
            with m3:
                neon_metric("DOMINANT SHIFT", divergence['dominant_shift'].replace('_', ' ').upper(), "green")
            with m4:
                max_diff = max(divergence['trait_diffs'].values())
                neon_metric("MAX TRAIT DELTA", f"{max_diff:.0f}%", "orange")

        # Text analysis (if available)
        if st.session_state.text_analysis:
            st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'Orbitron',sans-serif; color:#ffe600; font-size:0.85rem; letter-spacing:2px; margin-bottom:10px;">
                📝 TEXT SAMPLE ANALYSIS
            </div>
            """, unsafe_allow_html=True)

            ta = st.session_state.text_analysis
            t1, t2, t3, t4 = st.columns(4)
            with t1:
                neon_metric("SENTIMENT", f"{ta['sentiment']['compound']:.2f}", "cyan")
            with t2:
                neon_metric("POSITIVE", f"{ta['sentiment']['pos']:.0%}", "green")
            with t3:
                neon_metric("NEGATIVE", f"{ta['sentiment']['neg']:.0%}", "magenta")
            with t4:
                neon_metric("WORD COUNT", str(ta['word_count']), "yellow")

        # Export data
        st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
        with st.expander("💾 EXPORT PROFILE DATA"):
            export_data = {
                "base_profile": base,
                "base_archetype": base_arch,
                "clone_profile": clone if clone else None,
                "clone_archetype": clone_arch if clone else None,
                "modifications": st.session_state.modifications,
                "divergence": divergence if clone else None,
            }
            st.json(export_data)
            st.download_button(
                "📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name="parallel_self_profile.json",
                mime="application/json",
            )

        # AI Techniques section
        st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',sans-serif; color:#8888aa; font-size:0.75rem; letter-spacing:2px; text-align:center; margin:20px 0;">
            TECHNIQUES EMPLOYED
        </div>
        <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:10px; padding:10px;">
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#00f0ff; background:#00f0ff15;
                         padding:4px 12px; border-radius:20px; border:1px solid #00f0ff44;">NLP Feature Extraction</span>
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#ff00aa; background:#ff00aa15;
                         padding:4px 12px; border-radius:20px; border:1px solid #ff00aa44;">Personality Clustering</span>
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#39ff14; background:#39ff1415;
                         padding:4px 12px; border-radius:20px; border:1px solid #39ff1444;">Sentiment Polarity Scoring</span>
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#ffe600; background:#ffe60015;
                         padding:4px 12px; border-radius:20px; border:1px solid #ffe60044;">Behavioral Simulation</span>
            <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#ff6a00; background:#ff6a0015;
                         padding:4px 12px; border-radius:20px; border:1px solid #ff6a0044;">Parameter-Controlled Generation</span>
        </div>
        """, unsafe_allow_html=True)
