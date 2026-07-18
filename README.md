# 🌤️ AirSense AI

**AI/ML Internship Project** — Predicting PM2.5 air pollution levels and translating them into an official Indian National AQI (CPCB) score, category, and health advisory using a Random Forest model trained on Delhi's air quality data.

🔗 **Repo:** [github.com/RITIKAYADAV-6318/AirSense-AI](https://github.com/RITIKAYADAV-6318/AirSense-AI)

---

## 📖 Overview

AirSense AI uses a **Random Forest Regressor**, trained exclusively on Delhi's historical air quality data, to forecast PM2.5 concentration from pollutant and time-based inputs. The predicted PM2.5 value is then converted into an **AQI score and category** using the official CPCB (Central Pollution Control Board) breakpoint formula, along with a matching health advisory.

The model was validated on unseen data from three other major Indian cities to test real-world generalization:

- 📍 Bengaluru
- 📍 Chennai
- 📍 Kolkata

## ✨ Features

- 🧪 Interactive Streamlit UI to enter pollutant readings (PM10, NO, NO₂, NOx, CO, SO₂, O₃), date, and recent PM2.5 history
- 🤖 Real-time PM2.5 prediction from a pre-trained Random Forest model — no retraining, the model runs purely for inference
- 🌍 Predicted PM2.5 converted to AQI using the official CPCB linear breakpoint formula
- 🎨 Color-coded AQI badge across all six CPCB categories: Good, Satisfactory, Moderate, Poor, Very Poor, Severe
- 💡 Category-specific health advisory
- 📊 Model information panel (architecture, training city, reported accuracy)

## 📈 Model Performance

| Metric | Value |
|---|---|
| Model | Random Forest Regressor |
| Training City | Delhi |
| Test Cities | Bengaluru, Chennai, Kolkata |
| R² Score | 0.9473 |
| MAE | 12.02 µg/m³ |

## 🗂️ Project Structure

```
AirSense-AI/
├── app/
│   ├── app.py                 # Streamlit UI (presentational layer)
│   ├── backend.py             # Model loading, prediction, AQI logic
│   ├── style.css              # Custom styling
│   ├── assets/                # Logo and static assets
│   └── models/
│       ├── best_random_forest_model.pkl   # Trained Random Forest model
│       ├── feature_columns.pkl            # Exact feature order the model expects
│       └── imputer.pkl                    # Fitted SimpleImputer (median strategy)
├── notebooks/
│   └── InternProject (3).ipynb    # Full data cleaning, feature engineering & training pipeline
├── data/
│   └── city_day.csv           # Raw source dataset (city-wise daily air quality)
├── .streamlit/
│   └── config.toml            # Forces light theme for consistent UI rendering
├── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

- **Python 3**
- **Streamlit** — frontend/UI
- **scikit-learn** — Random Forest model + imputer
- **pandas / numpy** — data handling
- **joblib** — model serialization

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/RITIKAYADAV-6318/AirSense-AI.git
cd AirSense-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `scikit-learn` is pinned to `1.6.1` to match the version the model and imputer `.pkl` files were saved with, to avoid version-mismatch errors when unpickling.

### 3. Run the app

```bash
cd app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## 🧮 How a Prediction Works

1. User enters pollutant readings, date, and recent PM2.5 history in the UI
2. Inputs are assembled into a single-row DataFrame, ordered exactly as `feature_columns.pkl` specifies
3. The saved `imputer.pkl` fills any missing values in `PM10`, `NOx`, and `O3` using their training-time medians
4. The saved `best_random_forest_model.pkl` predicts PM2.5 (µg/m³)
5. Predicted PM2.5 is converted to an AQI score via the CPCB linear breakpoint formula
6. The AQI score is mapped to a category, color, and health advisory

## 📊 Dataset

Trained on [`city_day.csv`](data/city_day.csv) — daily air quality readings (PM2.5, PM10, NO, NO₂, NOx, CO, SO₂, O₃, etc.) across major Indian cities. Full preprocessing, feature engineering, and model training is documented in [`notebooks/InternProject (3).ipynb`](<notebooks/InternProject (3).ipynb>).

## 🔗 Connect

- **GitHub:** [RITIKAYADAV-6318/AirSense-AI](https://github.com/RITIKAYADAV-6318/AirSense-AI)
- **LinkedIn:** [AirSense AI](https://www.linkedin.com/company/airsense-ai/)

## 📄 License

This project was built as part of an AI/ML internship program.
