from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from src.config import DATABASE_PATH, METADATA_PATH, MODEL_PATH, RAW_DATA_DIR
from src.data.cmapss import SENSOR_COLUMNS, add_rul_target, latest_window, load_cmapss
from src.services.prediction_mode import normalize_prediction_mode
from src.services.predictor import MaintenancePredictor
from src.services.sensor_simulator import simulate_sensor_cycles

API_URL = os.getenv("PREDICTIVE_MAINTENANCE_API_URL", "http://127.0.0.1:8000")
PREDICTION_MODE_ENV = os.getenv("PREDICTION_MODE")
DEFAULT_DATA = RAW_DATA_DIR / "sample_train_FD001.txt"
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


st.set_page_config(page_title="Predictive Maintenance AI Platform", layout="wide")

try:
    PREDICTION_MODE = normalize_prediction_mode(PREDICTION_MODE_ENV)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

LOGGER.info("Prediction mode active: %s", PREDICTION_MODE)

st.markdown(
    """
    <style>
    :root {
        --pm-bg: #0e1117;
        --pm-surface: #161b24;
        --pm-surface-2: #1d2430;
        --pm-border: #2e3848;
        --pm-border-strong: #4b5c72;
        --pm-text: #f3f7fb;
        --pm-muted: #aeb9c8;
        --pm-soft: #d9e2ee;
        --pm-accent: #7aa2c7;
        --pm-shadow: rgba(0, 0, 0, 0.28);
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: var(--pm-text);
        letter-spacing: 0;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: var(--pm-soft);
    }
    .platform-header {
        border-bottom: 1px solid var(--pm-border);
        padding-bottom: 1rem;
        margin-bottom: 1.15rem;
    }
    .platform-kicker {
        color: var(--pm-accent);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08rem;
        text-transform: uppercase;
    }
    .platform-title {
        color: var(--pm-text);
        font-size: 2.05rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0.15rem 0;
    }
    .platform-subtitle {
        color: var(--pm-muted);
        font-size: 0.98rem;
        line-height: 1.55;
        max-width: 860px;
    }
    .health-card {
        border: 1px solid var(--pm-border);
        border-left: 5px solid var(--pm-accent);
        border-radius: 8px;
        padding: 1rem 1rem;
        background: linear-gradient(180deg, var(--pm-surface-2), var(--pm-surface));
        box-shadow: 0 10px 24px var(--pm-shadow);
        min-height: 104px;
    }
    .health-card strong {
        color: var(--pm-muted);
        display: block;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.05rem;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
    }
    .health-card span {
        color: var(--pm-text);
        display: block;
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.15;
    }
    .health-card small {
        color: var(--pm-muted);
        display: block;
        margin-top: 0.25rem;
        line-height: 1.35;
    }
    .risk-badge {
        border-radius: 999px;
        color: #ffffff;
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.06rem;
        padding: 0.32rem 0.72rem;
    }
    .risk-low { background: #147a3f; }
    .risk-medium { background: #9a6500; }
    .risk-high { background: #b23816; }
    .risk-critical { background: #991b1b; }
    .recommendation-panel {
        border: 1px solid var(--pm-border);
        border-left: 5px solid var(--pm-accent);
        border-radius: 8px;
        background: linear-gradient(180deg, var(--pm-surface-2), var(--pm-surface));
        box-shadow: 0 10px 24px var(--pm-shadow);
        margin-top: 0.8rem;
        padding: 1rem;
        min-height: 150px;
    }
    .recommendation-panel h3 {
        color: var(--pm-text);
        font-size: 1rem;
        font-weight: 800;
        margin: 0 0 0.55rem 0;
    }
    .recommendation-panel p {
        color: var(--pm-soft);
        line-height: 1.55;
        margin-bottom: 0;
    }
    div[data-testid="stMetric"] {
        border: 1px solid var(--pm-border);
        border-left: 4px solid var(--pm-border-strong);
        border-radius: 8px;
        background: linear-gradient(180deg, var(--pm-surface-2), var(--pm-surface));
        box-shadow: 0 8px 20px var(--pm-shadow);
        padding: 0.85rem 0.95rem;
    }
    div[data-testid="stMetricLabel"] {
        color: var(--pm-muted);
        font-size: 0.84rem;
        font-weight: 700;
    }
    div[data-testid="stMetricValue"] {
        color: var(--pm-text);
        font-size: 2rem;
        font-weight: 800;
    }
    div[data-testid="stMetricDelta"] {
        color: var(--pm-soft);
    }
    .stAlert {
        border-radius: 8px;
    }
    [data-testid="stDataFrame"],
    [data-testid="stJson"] {
        border: 1px solid var(--pm-border);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def risk_class(risk_level: str) -> str:
    return f"risk-{risk_level.lower()}"


def risk_score_from_rul(predicted_rul: float) -> int:
    capped_rul = max(min(predicted_rul, 125), 0)
    return int(round(100 - (capped_rul / 125 * 100)))


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return add_rul_target(load_cmapss(path))


def call_health_api(api_base_url: str) -> dict:
    response = requests.get(f"{api_base_url.rstrip('/')}/health", timeout=5)
    response.raise_for_status()
    return response.json()


def call_predict_api(api_base_url: str, unit_id: int, cycles: pd.DataFrame) -> dict:
    LOGGER.info("Routing prediction through FastAPI backend at %s", api_base_url)
    payload = {
        "unit_id": unit_id,
        "cycles": cycles.drop(columns=["unit_id", "rul"], errors="ignore").to_dict(orient="records"),
    }
    response = requests.post(f"{api_base_url.rstrip('/')}/predict", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_resource(show_spinner=False)
def get_direct_predictor() -> MaintenancePredictor:
    LOGGER.info("Loading trained model artifact directly from %s", MODEL_PATH)
    return MaintenancePredictor()


def predict_direct(unit_id: int, cycles: pd.DataFrame) -> dict:
    LOGGER.info("Routing prediction through direct model inference")
    predictor = get_direct_predictor()
    result = predictor.predict(cycles.drop(columns=["unit_id", "rul"], errors="ignore"))
    return {"unit_id": unit_id, **result}


def run_prediction(mode: str, api_base_url: str, unit_id: int, cycles: pd.DataFrame) -> dict:
    if mode == "api":
        return call_predict_api(api_base_url, unit_id, cycles)
    if mode == "direct":
        return predict_direct(unit_id, cycles)
    raise ValueError(f"Unsupported prediction mode: {mode}")


@st.cache_data(show_spinner=False)
def load_prediction_history(limit: int = 10) -> pd.DataFrame:
    if not DATABASE_PATH.exists():
        return pd.DataFrame()

    query = """
        SELECT created_at, unit_id, predicted_rul, risk_level, recommendation
        FROM prediction_history
        ORDER BY created_at DESC
        LIMIT ?
    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(query, connection, params=(limit,))


st.markdown(
    """
    <div class="platform-header">
        <div class="platform-kicker">Industrial AI Monitoring</div>
        <div class="platform-title">Predictive Maintenance AI Platform</div>
        <div class="platform-subtitle">
            Real-time style equipment health monitoring with RUL prediction, machine risk scoring,
            maintenance recommendations, and local prediction history.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    st.caption(f"Prediction mode: `{PREDICTION_MODE}`")
    data_path = st.text_input("C-MAPSS data path", value=str(DEFAULT_DATA))
    api_url = st.text_input("API URL", value=API_URL)
    window_size = st.slider("Prediction window", min_value=5, max_value=50, value=20)
    use_simulated_window = st.toggle("Use simulated live window", value=False)

path = Path(data_path)
health = None
health_error = None
if PREDICTION_MODE == "api":
    try:
        health = call_health_api(api_url)
    except requests.RequestException as exc:
        health_error = str(exc)
else:
    health = {
        "status": "ok",
        "service": "Direct model inference",
        "model_available": MODEL_PATH.exists(),
    }

if not path.exists():
    st.warning("Data file not found. Run `py -m scripts.create_sample_data` first, or provide a NASA C-MAPSS file.")
    st.stop()

df = load_data(str(path))
unit_ids = sorted(df["unit_id"].unique().tolist())

with st.sidebar:
    selected_unit = st.selectbox("Machine Unit", unit_ids)
    selected_sensors = st.multiselect(
        "Trend Sensors",
        SENSOR_COLUMNS,
        default=["sensor_2", "sensor_3", "sensor_4", "sensor_11"],
    )
    window_sensor = st.selectbox("Latest Window Sensor", SENSOR_COLUMNS, index=1)

unit_df = df[df["unit_id"] == selected_unit].sort_values("cycle")
if use_simulated_window:
    latest_cycles = simulate_sensor_cycles(
        unit_id=int(selected_unit),
        cycles=window_size,
        start_cycle=int(unit_df["cycle"].max()) + 1,
        degradation=0.85,
    )
else:
    latest_cycles = latest_window(df, selected_unit, window_size=window_size)

history_exists = DATABASE_PATH.exists()
health_cols = st.columns(4)
health_cols[0].markdown(
    f"""
    <div class="health-card">
        <strong>Prediction Mode</strong>
        <span>{PREDICTION_MODE.upper()}</span>
        <small>{api_url if PREDICTION_MODE == 'api' else 'Streamlit loads model artifact directly'}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
health_cols[1].markdown(
    f"""
    <div class="health-card">
        <strong>Model</strong>
        <span>{'READY' if health and health.get('model_available') else 'MISSING'}</span>
        <small>{'Artifact detected' if health and health.get('model_available') else 'Train model before prediction'}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
health_cols[2].markdown(
    f"""
    <div class="health-card">
        <strong>{'API Status' if PREDICTION_MODE == 'api' else 'Direct Inference'}</strong>
        <span>{'ONLINE' if health else 'OFFLINE'}</span>
        <small>{health.get('service', 'Unavailable') if health else 'Prediction service unavailable'}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
health_cols[3].markdown(
    f"""
    <div class="health-card">
        <strong>Machine Fleet</strong>
        <span>{len(unit_ids)}</span>
        <small>{'SQLite history is read-only in direct mode' if PREDICTION_MODE == 'direct' else 'Units loaded from sensor data'}</small>
    </div>
    """,
    unsafe_allow_html=True,
)

if health_error:
    st.error(f"Backend health check failed: {health_error}")

latest_true_rul = int(unit_df["rul"].iloc[-1])
observed_cycles = int(unit_df["cycle"].max())

overview_cols = st.columns(4)
overview_cols[0].metric("Selected Machine", selected_unit)
overview_cols[1].metric("Observed Cycles", observed_cycles)
overview_cols[2].metric("Current True RUL", latest_true_rul)
overview_cols[3].metric("Window Size", len(latest_cycles))

left, right = st.columns([1.7, 1])

with left:
    st.subheader("Sensor Trend Monitor")
    if selected_sensors:
        trend_df = unit_df.melt(
            id_vars=["cycle"],
            value_vars=selected_sensors,
            var_name="sensor",
            value_name="value",
        )
        fig = px.line(
            trend_df,
            x="cycle",
            y="value",
            color="sensor",
            template="plotly_white",
            labels={"cycle": "Operating Cycle", "value": "Sensor Value", "sensor": "Sensor"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one sensor to view trends.")

with right:
    st.subheader("Machine Risk")
    prediction_disabled = health is None or not bool(health.get("model_available"))
    if st.button("Run Risk Prediction", type="primary", use_container_width=True, disabled=prediction_disabled):
        try:
            with st.spinner("Analyzing latest sensor window..."):
                result = run_prediction(PREDICTION_MODE, api_url, int(selected_unit), latest_cycles)
            st.session_state["prediction"] = result
            load_prediction_history.clear()
            st.success("Prediction complete.")
        except (requests.RequestException, FileNotFoundError, ValueError) as exc:
            st.session_state.pop("prediction", None)
            st.error(f"Prediction request failed: {exc}")

    result = st.session_state.get("prediction")
    if result:
        risk = result["risk_level"]
        score = risk_score_from_rul(float(result["predicted_rul"]))
        st.metric("Risk Score", f"{score}/100")
        st.metric("Predicted RUL", f"{result['predicted_rul']:.1f} cycles")
        st.markdown(
            f'<span class="risk-badge {risk_class(risk)}">{risk}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="recommendation-panel">
                <h3>Maintenance Recommendation</h3>
                <p>{result["recommendation"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Run a prediction to calculate machine risk and maintenance guidance.")

st.subheader("Latest Sensor Window")
window_fig = px.line(
    latest_cycles,
    x="cycle",
    y=window_sensor,
    markers=True,
    template="plotly_white",
    title=f"{window_sensor} trend across latest {len(latest_cycles)} cycles",
    labels={"cycle": "Operating Cycle", window_sensor: "Sensor Value"},
)
window_fig.update_layout(margin=dict(l=10, r=10, t=45, b=10))
st.plotly_chart(window_fig, use_container_width=True)
st.dataframe(latest_cycles, use_container_width=True)

history_col, model_col = st.columns(2)
with history_col:
    st.subheader("Prediction History")
    try:
        history_df = load_prediction_history(limit=10)
        if history_df.empty:
            st.caption("No prediction history found yet. Run a prediction to create records.")
        else:
            st.dataframe(history_df, use_container_width=True)
    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        st.caption(f"Prediction history is unavailable: {exc}")

with model_col:
    st.subheader("Model Metadata")
    if METADATA_PATH.exists():
        st.json(json.loads(METADATA_PATH.read_text(encoding="utf-8")))
    else:
        st.caption("Train a model to create metadata.")
