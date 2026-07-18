"""
AirSense AI — Streamlit Frontend
=================================
This file ONLY handles UI/UX. No ML logic lives here.

IMPORTANT (per project constraints):
- The Random Forest model, notebook, and preprocessing pipeline are
  NOT touched by this file.
- The "Prediction Dashboard" below uses DUMMY placeholder values.
  Wire your real model's `.predict()` output into the
  `predicted_pm25`, `aqi_category`, etc. variables inside
  `render_prediction_section()` whenever you're ready — that is the
  only place prediction logic should ever be plugged in.

Structure of this file (all purely presentational):
  1. Page config + CSS loader
  2. Navbar
  3. Hero section
  4. Prediction section (inputs + dummy dashboard)
  5. Model information section
  6. Footer
"""

import base64
from pathlib import Path

import streamlit as st

# ==========================================================
# 1. PAGE CONFIG + CSS LOADER
# ==========================================================

# Resolve paths relative to THIS FILE, not the current working directory.
# Streamlit Cloud (and some local setups) can launch the app from the repo
# root even when app.py lives in a subfolder (e.g. "app/"), which breaks
# plain relative paths like "assets/logo.png". Anchoring to __file__ makes
# this work identically both locally and when deployed.
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"   # place the brand logo image here
CSS_PATH = BASE_DIR / "style.css"

st.set_page_config(
    page_title="AirSense AI",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css(path: Path = CSS_PATH) -> None:
    """Inject the external stylesheet into the Streamlit app."""
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def get_logo_base64(path: Path = LOGO_PATH) -> str:
    """
    Read the logo image from disk and return it as a base64 data-URI so it
    can be embedded directly inside custom HTML (navbar / footer).
    Falls back to an empty string if the file hasn't been added yet.
    """
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{encoded}"


load_css()
LOGO_URI = get_logo_base64()


# ==========================================================
# 2. NAVBAR
# ==========================================================

def render_navbar() -> None:
    """Sticky glass navbar with logo + nav links (anchor-based)."""
    logo_html = (
        f'<img src="{LOGO_URI}" alt="AirSense AI logo" />'
        if LOGO_URI
        else "<span>🌤️</span>"
    )
    st.markdown(
        f"""
        <div class="as-navbar">
            <div class="as-navbar-logo">
                {logo_html} AirSense AI
            </div>
            <div class="as-navbar-links">
                <a href="#home">Home</a>
                <a href="#about">About</a>
                <a href="#model">Model</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# 3. HERO SECTION
# ==========================================================

def render_hero() -> None:
    """Full-width hero with heading, subtitle and one primary CTA."""
    st.markdown('<div id="home"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="as-hero">
            <div class="as-hero-eyebrow">🌿 Cross-City AQI Intelligence</div>
            <h1>Predict air quality <span class="as-highlight">before it happens</span></h1>
            <p>
                AirSense AI uses a Random Forest model trained on Delhi's air quality
                data to forecast PM2.5 levels — validated across Bengaluru, Chennai
                and Kolkata for real-world reliability.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Primary CTA — centered, scrolls to the prediction section
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Try the Predictor →", use_container_width=True):
            st.markdown(
                "<script>document.getElementById('predict').scrollIntoView("
                "{behavior:'smooth'});</script>",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="as-spacer-sm"></div>', unsafe_allow_html=True)


# ==========================================================
# 4. PREDICTION SECTION
# ==========================================================

def render_prediction_section() -> None:
    """
    Two-column prediction UI.
    Left  -> pollutant / weather inputs (widgets only, no logic wired up)
    Right -> prediction dashboard (DUMMY values — do not treat as real output)
    """
    st.markdown('<div id="predict"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="as-section">
            <div class="as-section-head">
                <div class="as-section-tag">Live Predictor</div>
                <h2>Get your AQI forecast in seconds</h2>
                <p>Enter local pollutant and weather readings — the model
                predicts PM2.5, which is then translated into an AQI score
                and health advisory.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    # ---------------- LEFT: Pollutant Inputs ----------------
    # Using st.container(key=...) instead of a hand-split <div>...</div>
    # guarantees the widgets are REAL DOM children of the card, so the
    # glass box actually grows to fit them (this is what fixes the
    # previous "tiny card / unboxed sliders" misalignment).
    with left:
        with st.container(key="input_card"):
            st.markdown(
                """
                <div class="as-card-title">🧪 Pollutant &amp; Weather Inputs</div>
                <div class="as-card-sub">These fields feed the Random Forest model.</div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                st.slider("PM10 (µg/m³)", 0, 500, 120)
                st.slider("NO₂ (µg/m³)", 0, 200, 45)
                st.slider("SO₂ (µg/m³)", 0, 100, 12)
                st.number_input("Temperature (°C)", value=28.0, step=0.5)
            with c2:
                st.slider("CO (mg/m³)", 0, 10, 2)
                st.slider("O₃ (µg/m³)", 0, 200, 60)
                st.slider("Humidity (%)", 0, 100, 55)
                st.selectbox("City", ["Delhi", "Bengaluru", "Chennai", "Kolkata"])

            st.markdown("<div class='as-spacer-sm'></div>", unsafe_allow_html=True)
            st.button("Predict PM2.5", use_container_width=True, key="predict_btn")

    # ---------------- RIGHT: Prediction Dashboard (DUMMY) ----------------
    with right:
        with st.container(key="dashboard_stack"):
            # --- Placeholder / dummy values only — replace with real model output ---
            aqi_score = 148                # dummy AQI score (derived from PM2.5 downstream)
            predicted_pm25 = 58.7           # dummy PM2.5 value in µg/m³
            confidence = "87%"              # dummy confidence score

            # AQI category lookup: (emoji, css badge class, gauge ring color var)
            aqi_category = "Moderate"
            aqi_style = {
                "Good":         {"emoji": "🟢", "badge": "as-badge-good",         "ring": "#2F855A"},
                "Satisfactory": {"emoji": "🟡", "badge": "as-badge-satisfactory", "ring": "#C9A227"},
                "Moderate":     {"emoji": "🟠", "badge": "as-badge-moderate",     "ring": "#C05621"},
                "Poor":         {"emoji": "🔴", "badge": "as-badge-poor",         "ring": "#C53030"},
                "Very Poor":    {"emoji": "🟣", "badge": "as-badge-verypoor",     "ring": "#805AD5"},
                "Severe":       {"emoji": "🟤", "badge": "as-badge-severe",       "ring": "#7B3F00"},
            }[aqi_category]

            health_advisory = (
                "People with respiratory conditions should reduce prolonged "
                "outdoor activity."
            )
            # --------------------------------------------------------------------

            # ---- 1. AQI Result Card ----
            st.markdown(
                f"""
                <div class="as-card as-aqi-card">
                    <div class="as-card-title" style="justify-content:center;">🌍 AQI Result</div>
                    <div class="as-card-sub">Sample output · not a live prediction</div>
                    <div class="as-gauge" style="background:conic-gradient({aqi_style['ring']} 0deg, {aqi_style['ring']}55 122deg, rgba(15,23,42,0.06) 122deg 360deg);">
                        <div class="as-gauge-inner">
                            <div class="as-gauge-label">AQI</div>
                            <div class="as-gauge-value">{aqi_score}</div>
                        </div>
                    </div>
                    <span class="as-badge {aqi_style['badge']}">{aqi_style['emoji']} {aqi_category}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- 2. Predicted PM2.5 Card ----
            st.markdown(
                f"""
                <div class="as-card as-metric-card">
                    <div class="as-metric-icon">📈</div>
                    <div class="as-metric-text">
                        <div class="as-metric-label">Predicted PM2.5</div>
                        <div class="as-metric-value">{predicted_pm25} <span>µg/m³</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- 3. Health Advisory Card ----
            st.markdown(
                f"""
                <div class="as-card as-advisory-card">
                    <div class="as-advisory-icon">💡</div>
                    <div class="as-advisory-text">
                        <div class="as-metric-label">Health Advisory</div>
                        <p>{health_advisory}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ---- 4. Model Information Card ----
            st.markdown(
                """
                <div class="as-card as-modelinfo-card">
                    <div class="as-card-title">📊 Model Information</div>
                    <div class="as-modelinfo-row">
                        <span class="as-modelinfo-label">Model Used</span>
                        <span class="as-modelinfo-value">Random Forest Regressor</span>
                    </div>
                    <div class="as-modelinfo-row">
                        <span class="as-modelinfo-label">Training City</span>
                        <span class="as-modelinfo-value">Delhi</span>
                    </div>
                    <div class="as-modelinfo-row">
                        <span class="as-modelinfo-label">Test Cities</span>
                        <span class="as-modelinfo-value">Bengaluru, Chennai, Kolkata</span>
                    </div>
                    <div class="as-modelinfo-row">
                        <span class="as-modelinfo-label">R² Score</span>
                        <span class="as-modelinfo-value as-modelinfo-highlight">0.947</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)  # close as-section


# ==========================================================
# 5. MODEL INFORMATION SECTION
# ==========================================================

def render_model_section() -> None:
    """Static, informational section describing the model — no logic."""
    st.markdown('<div id="model"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="as-section" id="about">
            <div class="as-section-head">
                <div class="as-section-tag">Under the hood</div>
                <h2>Built on a Random Forest model</h2>
                <p>Trained on Delhi's historical air quality data and
                stress-tested across three other major Indian cities.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Stat cards row ---
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("Random Forest", "Model Architecture"),
        ("Delhi", "Training City"),
        ("R² 0.91", "Reported Accuracy"),
        ("MAE 14.2", "Mean Abs. Error (µg/m³)"),
    ]
    for col, (value, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(
                f"""
                <div class="as-stat-card">
                    <div class="as-stat-value">{value}</div>
                    <div class="as-stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='as-spacer-md'></div>", unsafe_allow_html=True)

    # --- Tested-on cities card ---
    st.markdown(
        """
        <div class="as-card" style="text-align:center;">
            <div class="as-card-title" style="justify-content:center;">🗺️ Cross-City Validation</div>
            <div class="as-card-sub">
                The model was trained exclusively on Delhi data, then evaluated
                on unseen cities to test real-world generalization.
            </div>
            <div>
                <span class="as-city-pill">📍 Bengaluru</span>
                <span class="as-city-pill">📍 Chennai</span>
                <span class="as-city-pill">📍 Kolkata</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)  # close as-section


# ==========================================================
# 6. FOOTER
# ==========================================================

def render_footer() -> None:
    """Clean footer with social / contact links (real brand SVG icons)."""
    st.markdown('<div id="contact"></div>', unsafe_allow_html=True)
    footer_logo_html = (
        f'<img src="{LOGO_URI}" alt="AirSense AI logo" />'
        if LOGO_URI
        else "🌤️ "
    )

    # Inline SVGs (currentColor) so hover states pick up theme color automatically
    github_icon = """<svg viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.744.083-.729.083-.729 1.205.084 1.84 1.237 1.84 1.237 1.07 1.834 2.807 1.304 3.492.997.108-.775.418-1.305.762-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.469-2.38 1.236-3.22-.124-.303-.535-1.523.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.873.118 3.176.77.84 1.235 1.91 1.235 3.22 0 4.61-2.807 5.625-5.479 5.921.43.372.823 1.102.823 2.222 0 1.606-.014 2.898-.014 3.293 0 .322.216.694.825.576C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>"""

    linkedin_icon = """<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>"""

    mail_icon = """<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/></svg>"""

    st.markdown(
        f"""
        <div class="as-footer">
            <div class="as-footer-top">
                <div class="as-footer-brand">{footer_logo_html}AirSense AI</div>
                <div class="as-footer-links">
                    <a href="https://github.com" target="_blank" title="GitHub">{github_icon}</a>
                    <a href="https://linkedin.com" target="_blank" title="LinkedIn">{linkedin_icon}</a>
                    <a href="mailto:hello@airsense.ai" title="Email">{mail_icon}</a>
                </div>
            </div>
            <div class="as-footer-bottom">
                © 2026 AirSense AI · Cross-city PM2.5 prediction powered by Random Forest
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# RENDER PAGE
# ==========================================================

render_navbar()
render_hero()
render_prediction_section()
render_model_section()
render_footer()
