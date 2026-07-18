"""
AirSense AI — Prediction Backend
=================================
This module contains ALL machine-learning / AQI logic for the app.

It is intentionally isolated from `app.py` (the Streamlit UI) so that:
  - `app.py` stays purely presentational.
  - The trained artifacts in `models/` are never touched, retrained,
    or re-fit. They are only loaded and used for inference.

Artifacts consumed (created by notebooks/InternProject (3).ipynb — untouched):
  - models/best_random_forest_model.pkl  -> sklearn RandomForestRegressor
  - models/feature_columns.pkl           -> exact ordered list of the
                                             15 features the model expects
  - models/imputer.pkl                   -> sklearn SimpleImputer(strategy
                                             ="median"), fitted ONLY on
                                             ["PM10", "NOx", "O3"]

Pipeline replicated here (mirrors the notebook's preprocessing exactly,
nothing added or changed):
  1. Build a single-row DataFrame with the 15 raw feature values.
  2. Reindex/reorder columns to match `feature_columns.pkl` exactly.
  3. Apply the saved imputer to the 3 columns it was fitted on
     (PM10, NOx, O3) — median fill for any missing values.
  4. Call model.predict() to get PM2.5 (µg/m³).
  5. Convert PM2.5 -> AQI using the official CPCB (Indian National AQI)
     PM2.5 sub-index breakpoint table.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

# ==========================================================
# PATHS
# ==========================================================

MODELS_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODELS_DIR / "best_random_forest_model.pkl"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.pkl"
IMPUTER_PATH = MODELS_DIR / "imputer.pkl"


# ==========================================================
# 1. LOAD MODEL + ARTIFACTS
# ==========================================================

@st.cache_resource(show_spinner=False)
def load_model() -> tuple[Any, list[str], Any]:
    """
    Load the pre-trained Random Forest model plus the two companion
    artifacts (feature column order + fitted imputer) that were saved
    from the notebook. Cached so the ~26MB model is only deserialized
    once per app session.

    Returns
    -------
    (model, feature_columns, imputer)
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. Make sure "
            "best_random_forest_model.pkl exists inside app/models/."
        )
    if not FEATURE_COLUMNS_PATH.exists():
        raise FileNotFoundError(
            f"feature_columns.pkl not found at {FEATURE_COLUMNS_PATH}."
        )
    if not IMPUTER_PATH.exists():
        raise FileNotFoundError(f"imputer.pkl not found at {IMPUTER_PATH}.")

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    imputer = joblib.load(IMPUTER_PATH)
    return model, feature_columns, imputer


# ==========================================================
# 2. BUILD MODEL INPUT (same feature order + same imputer)
# ==========================================================

def build_input_frame(raw_inputs: dict[str, float], feature_columns: list[str]) -> pd.DataFrame:
    """
    Turn the raw UI input dict into a single-row DataFrame whose columns
    are ordered EXACTLY as `feature_columns.pkl` specifies. Raises a
    clear error if any required feature is missing from `raw_inputs`.
    """
    missing = [c for c in feature_columns if c not in raw_inputs]
    if missing:
        raise KeyError(f"Missing required feature(s) for the model: {missing}")

    row = {col: raw_inputs[col] for col in feature_columns}
    return pd.DataFrame([row], columns=feature_columns)


def apply_imputer(df: pd.DataFrame, imputer: Any) -> pd.DataFrame:
    """
    Apply the notebook's fitted SimpleImputer to the exact columns it
    was originally fitted on (PM10, NOx, O3), leaving every other
    column untouched. Operates on a copy so the caller's frame isn't
    mutated in place.
    """
    df = df.copy()
    imputed_cols = list(getattr(imputer, "feature_names_in_", ["PM10", "NOx", "O3"]))
    df[imputed_cols] = imputer.transform(df[imputed_cols])
    return df


# ==========================================================
# 3. PREDICT PM2.5
# ==========================================================

def predict_pm25(model: Any, feature_columns: list[str], imputer: Any, raw_inputs: dict[str, float]) -> float:
    """
    Full inference pipeline: build frame -> impute -> predict.
    Returns the predicted PM2.5 concentration (µg/m³) as a float,
    clipped at 0 (PM2.5 cannot be negative).
    """
    frame = build_input_frame(raw_inputs, feature_columns)
    frame = apply_imputer(frame, imputer)
    prediction = model.predict(frame)[0]
    return max(0.0, float(prediction))


# ==========================================================
# 4. PM2.5 -> AQI (CPCB Indian National AQI breakpoints)
# ==========================================================

# (PM2.5_low, PM2.5_high, AQI_low, AQI_high) — 24-hr avg, µg/m³
_PM25_BREAKPOINTS = [
    (0.0, 30.0, 0, 50),
    (30.0, 60.0, 51, 100),
    (60.0, 90.0, 101, 200),
    (90.0, 120.0, 201, 300),
    (120.0, 250.0, 301, 400),
    (250.0, 380.0, 401, 500),
]


def calculate_aqi(pm25: float) -> int:
    """
    Convert a PM2.5 concentration (µg/m³) into an AQI score using the
    CPCB (Central Pollution Control Board) linear sub-index formula:

        AQI = ((AQI_hi - AQI_lo) / (BP_hi - BP_lo)) * (Cp - BP_lo) + AQI_lo

    Values above the top official breakpoint (380 µg/m³) are
    extrapolated using the same slope as the final "Severe" segment,
    since PM2.5 in some Indian cities regularly exceeds it.
    """
    pm25 = max(0.0, float(pm25))

    for bp_lo, bp_hi, aqi_lo, aqi_hi in _PM25_BREAKPOINTS:
        if bp_lo <= pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi)

    # Beyond the official table (>380 µg/m³): extrapolate past 500 using
    # the same slope as the last official segment.
    bp_lo, bp_hi, aqi_lo, aqi_hi = _PM25_BREAKPOINTS[-1]
    slope = (aqi_hi - aqi_lo) / (bp_hi - bp_lo)
    aqi = aqi_hi + slope * (pm25 - bp_hi)
    return round(aqi)


# ==========================================================
# 5. AQI -> CATEGORY
# ==========================================================

def get_aqi_category(aqi: int) -> str:
    """Map a numeric AQI score to its official CPCB category label."""
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Satisfactory"
    if aqi <= 200:
        return "Moderate"
    if aqi <= 300:
        return "Poor"
    if aqi <= 400:
        return "Very Poor"
    return "Severe"


# ==========================================================
# 6. HEALTH ADVISORY
# ==========================================================

_HEALTH_ADVISORY = {
    "Good": (
        "Air quality is considered satisfactory, and air pollution poses "
        "little or no risk. Enjoy your usual outdoor activities."
    ),
    "Satisfactory": (
        "Air quality is acceptable. Unusually sensitive individuals should "
        "consider limiting prolonged outdoor exertion."
    ),
    "Moderate": (
        "May cause breathing discomfort to people with lung disease such as "
        "asthma, and discomfort to children, older adults, and those with "
        "heart disease."
    ),
    "Poor": (
        "May cause breathing discomfort to most people on prolonged "
        "exposure. People with respiratory conditions should reduce "
        "prolonged outdoor activity."
    ),
    "Very Poor": (
        "May cause respiratory illness on prolonged exposure. Avoid "
        "outdoor activity, especially if you have heart or lung disease; "
        "children and older adults should stay indoors."
    ),
    "Severe": (
        "Affects healthy people and seriously impacts those with existing "
        "diseases. Avoid all outdoor physical activity; keep windows "
        "closed and use an air purifier indoors if possible."
    ),
}


def get_health_advisory(category: str) -> str:
    """Return a plain-language health advisory string for an AQI category."""
    return _HEALTH_ADVISORY.get(
        category,
        "No specific advisory available for this AQI category.",
    )


# ==========================================================
# 7. AQI -> DISPLAY STYLE (color / emoji / CSS badge class)
# ==========================================================

AQI_STYLE = {
    "Good":         {"emoji": "🟢", "badge": "as-badge-good",         "ring": "#2F855A"},
    "Satisfactory": {"emoji": "🟡", "badge": "as-badge-satisfactory", "ring": "#C9A227"},
    "Moderate":     {"emoji": "🟠", "badge": "as-badge-moderate",     "ring": "#C05621"},
    "Poor":         {"emoji": "🔴", "badge": "as-badge-poor",         "ring": "#C53030"},
    "Very Poor":    {"emoji": "🟣", "badge": "as-badge-verypoor",     "ring": "#805AD5"},
    "Severe":       {"emoji": "🟤", "badge": "as-badge-severe",       "ring": "#7B3F00"},
}


def get_aqi_style(category: str) -> dict[str, str]:
    """Return the emoji / CSS badge class / gauge ring color for a category."""
    return AQI_STYLE.get(category, AQI_STYLE["Moderate"])


# ==========================================================
# 8. END-TO-END CONVENIENCE WRAPPER
# ==========================================================

def run_full_prediction(raw_inputs: dict[str, float]) -> dict[str, Any]:
    """
    Convenience wrapper used by the UI: loads artifacts (cached), runs
    the full PM2.5 -> AQI pipeline, and returns everything the frontend
    needs to render in one dict.
    """
    model, feature_columns, imputer = load_model()

    predicted_pm25 = predict_pm25(model, feature_columns, imputer, raw_inputs)
    aqi_score = calculate_aqi(predicted_pm25)
    aqi_category = get_aqi_category(aqi_score)
    health_advisory = get_health_advisory(aqi_category)
    style = get_aqi_style(aqi_category)

    return {
        "predicted_pm25": round(predicted_pm25, 2),
        "aqi_score": aqi_score,
        "aqi_category": aqi_category,
        "health_advisory": health_advisory,
        "style": style,
    }
