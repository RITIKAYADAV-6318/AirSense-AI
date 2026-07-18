"""
AirSense AI — Streamlit Frontend
=================================
This file handles UI/UX. All ML logic lives in `backend.py`.
 
IMPORTANT (per project constraints):
- The Random Forest model, notebook, and preprocessing pipeline are
  NOT touched by this file (or by backend.py). backend.py only loads
  and calls the artifacts already saved in app/models/.
- The "Prediction Dashboard" now shows REAL model output, computed by
  `backend.run_full_prediction()` inside `render_prediction_section()`.
- The model expects a few features the original inputs didn't collect
  (NO, NOx, and date/lag/rolling PM2.5 features) — these were added as
  extra widgets in the same visual style, since the model can't run
  without them. No existing widget, layout, or CSS class was changed.
 
Structure of this file (presentational, calling into backend.py for logic):
  1. Page config + CSS loader
  2. Navbar
  3. Hero section
  4. Prediction section (inputs + real dashboard)
  5. Model information section
  6. Footer
"""
 
import base64
from datetime import date
from pathlib import Path
 
import streamlit as st

import backend
 
# ==========================================================
# 1. PAGE CONFIG + CSS LOADER
# ==========================================================
 
LOGO_PATH = "assets/logo.png"  # place the brand logo image here
 
st.set_page_config(
    page_title="AirSense AI",
    page_icon=LOGO_PATH if Path(LOGO_PATH).exists() else "🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
 
from pathlib import Path

def load_css() -> None:
    css_path = Path(__file__).parent / "style.css"

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    else:
        st.error(f"CSS file not found: {css_path}") 
 
@st.cache_data
def get_logo_base64(path: str = LOGO_PATH) -> str:
    """
    Read the logo image from disk and return it as a base64 data-URI so it
    can be embedded directly inside custom HTML (navbar / footer).
    Falls back to an empty string if the file hasn't been added yet.
    """
    file = Path(path)
    if not file.exists():
        return ""
    encoded = base64.b64encode(file.read_bytes()).decode()
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
                pm10 = st.slider("PM10 (µg/m³)", 0, 500, 120)
                no = st.slider("NO (µg/m³)", 0, 200, 20)
                no2 = st.slider("NO₂ (µg/m³)", 0, 200, 45)
                nox = st.slider("NOx (µg/m³)", 0, 200, 40)
                st.number_input("Temperature (°C)", value=28.0, step=0.5)
            with c2:
                so2 = st.slider("SO₂ (µg/m³)", 0, 100, 12)
                co = st.slider("CO (mg/m³)", 0, 10, 2)
                o3 = st.slider("O₃ (µg/m³)", 0, 200, 60)
                st.slider("Humidity (%)", 0, 100, 55)
                selected_city = st.selectbox("City", ["Delhi", "Bengaluru", "Chennai", "Kolkata"])
 
            # The model was trained on time + recent-history features
            # (Year/Month/Day/DayOfWeek/WeekOfYear + PM2.5 Lag1/Lag7/
            # Rolling7). These weren't in the original input set, so
            # they're added here — same widget style, no layout change —
            # since the saved model can't run without them.
            st.markdown("<div class='as-spacer-sm'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="as-card-title">📅 Date &amp; Recent PM2.5 Trend</div>
                <div class="as-card-sub">Used to build the model's time and lag features.</div>
                """,
                unsafe_allow_html=True,
            )
            c3, c4 = st.columns(2)
            with c3:
                prediction_date = st.date_input("Prediction Date", value=date.today())
                pm25_lag1 = st.number_input("PM2.5 Yesterday (µg/m³)", value=60.0, step=1.0, min_value=0.0)
            with c4:
                pm25_lag7 = st.number_input("PM2.5 — 7 Days Ago (µg/m³)", value=60.0, step=1.0, min_value=0.0)
                pm25_rolling7 = st.number_input("PM2.5 — 7-Day Avg (µg/m³)", value=60.0, step=1.0, min_value=0.0)
 
            st.markdown("<div class='as-spacer-sm'></div>", unsafe_allow_html=True)
            predict_clicked = st.button("Predict PM2.5", use_container_width=True, key="predict_btn")
 
            if predict_clicked:
                raw_inputs = {
                    "PM10": pm10,
                    "NO": no,
                    "NO2": no2,
                    "NOx": nox,
                    "CO": co,
                    "SO2": so2,
                    "O3": o3,
                    "Year": prediction_date.year,
                    "Month": prediction_date.month,
                    "Day": prediction_date.day,
                    "DayOfWeek": prediction_date.weekday(),
                    "WeekOfYear": prediction_date.isocalendar()[1],
                    "PM2.5_Lag1": pm25_lag1,
                    "PM2.5_Lag7": pm25_lag7,
                    "PM2.5_Rolling7": pm25_rolling7,
                }
                try:
                    result = backend.run_full_prediction(raw_inputs)
                    result["city"] = selected_city
                    st.session_state["prediction_result"] = result
                except Exception as exc:  # surfaced to the user, app keeps running
                    st.session_state["prediction_error"] = str(exc)
                    st.session_state.pop("prediction_result", None)
                else:
                    st.session_state.pop("prediction_error", None)
 
    # ---------------- RIGHT: Prediction Dashboard (REAL) ----------------
    with right:
        with st.container(key="dashboard_stack"):
            error_message = st.session_state.get("prediction_error")
            result = st.session_state.get("prediction_result")

            if error_message:
                st.error(f"Prediction failed: {error_message}")

            # Until the user runs a prediction, show neutral placeholder
            # values so the dashboard cards have something to render.
            if result is None:
                predicted_pm25 = 0.0
                aqi_score = 0
                aqi_category = "Good"
                aqi_style = backend.get_aqi_style(aqi_category)
                health_advisory = "Fill in the inputs and click \"Predict PM2.5\" to see your forecast."
                subtitle = "Awaiting input · no prediction yet"
            else:
                predicted_pm25 = result["predicted_pm25"]
                aqi_score = result["aqi_score"]
                aqi_category = result["aqi_category"]
                aqi_style = result["style"]
                health_advisory = result["health_advisory"]
                city_label = result.get("city", "")
                subtitle = (
                    f"Live prediction for {city_label}"
                    if city_label
                    else "Live prediction from the Random Forest model"
                )
 
            # ---- 1. AQI Result Card ----
            gauge_deg = min(360, (aqi_score / 500) * 360) if aqi_score else 0
            st.markdown(
                f"""
                <div class="as-card as-aqi-card">
                    <div class="as-card-title" style="justify-content:center;">🌍 AQI Result</div>
                    <div class="as-card-sub">{subtitle}</div>
                    <div class="as-gauge" style="background:conic-gradient({aqi_style['ring']} 0deg, {aqi_style['ring']}55 {gauge_deg}deg, rgba(15,23,42,0.06) {gauge_deg}deg 360deg);">
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
                        <span class="as-modelinfo-value as-modelinfo-highlight">0.9473</span>
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
        ("R² 0.9473", "Reported Accuracy"),
        ("MAE 12.02", "Mean Abs. Error (µg/m³)"),
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
                    <a href="https://github.com/RITIKAYADAV-6318/AirSense-AI" target="_blank" title="GitHub">{github_icon}</a>
                    <a href="https://www.linkedin.com/company/airsense-ai/" target="_blank" title="LinkedIn">{linkedin_icon}</a>
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