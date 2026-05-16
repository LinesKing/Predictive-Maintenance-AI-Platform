from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from src.config import DATABASE_PATH, METADATA_PATH, RAW_DATA_DIR
from src.data.cmapss import SENSOR_COLUMNS, add_rul_target, latest_window, load_cmapss

# Streamlit entrypoint:
# Run this file from the project root with:
#   py -m streamlit run app/dashboard.py
#
# Streamlit and FastAPI run as separate local web apps, so the frontend port
# and backend port must match the URL used here. Streamlit sends HTTP requests
# to FastAPI, and FastAPI returns the RUL prediction, risk level, and
# recommendation that Streamlit displays.
API_URL = os.getenv("PREDICTIVE_MAINTENANCE_API_URL", "http://127.0.0.1:8000")
DEFAULT_DATA = RAW_DATA_DIR / "sample_train_FD001.txt"


st.set_page_config(page_title="Predictive Maintenance Dashboard", layout="wide")
st.title("Predictive Maintenance Dashboard")

with st.sidebar:
    st.header("Data")
    data_path = st.text_input("C-MAPSS data path", value=str(DEFAULT_DATA))
    api_url = st.text_input("API URL", value=API_URL)
    window_size = st.slider("Prediction window", min_value=5, max_value=50, value=20)


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return add_rul_target(load_cmapss(path))


def call_predict_api(api_base_url: str, unit_id: int, cycles: pd.DataFrame) -> dict:
    # API request flow:
    # 1. Streamlit prepares recent sensor cycles for the selected unit.
    # 2. The frontend POSTs those cycles to FastAPI /predict.
    # 3. FastAPI runs feature engineering + model inference, stores history,
    #    and returns RUL, risk level, and recommendation for display here.
    payload = {
        "unit_id": unit_id,
        "cycles": cycles.drop(columns=["unit_id", "rul"], errors="ignore").to_dict(orient="records"),
    }
    response = requests.post(f"{api_base_url.rstrip('/')}/predict", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


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


path = Path(data_path)
if not path.exists():
    st.warning("Data file not found. Run `py -m scripts.create_sample_data` first, or provide a NASA C-MAPSS file.")
    st.stop()

df = load_data(str(path))
unit_ids = sorted(df["unit_id"].unique().tolist())
selected_unit = st.sidebar.selectbox("Unit", unit_ids)
selected_sensors = st.sidebar.multiselect(
    "Sensors",
    SENSOR_COLUMNS,
    default=["sensor_2", "sensor_3", "sensor_4", "sensor_11"],
)
window_sensor = st.sidebar.selectbox("Latest window sensor", SENSOR_COLUMNS, index=1)

unit_df = df[df["unit_id"] == selected_unit].sort_values("cycle")
latest_cycles = latest_window(df, selected_unit, window_size=window_size)

summary_cols = st.columns(4)
summary_cols[0].metric("Selected Unit", selected_unit)
summary_cols[1].metric("Observed Cycles", int(unit_df["cycle"].max()))
summary_cols[2].metric("Current True RUL", int(unit_df["rul"].iloc[-1]))
summary_cols[3].metric("Window Size", len(latest_cycles))

left, right = st.columns([2, 1])
with left:
    st.subheader("Sensor Trends")
    if selected_sensors:
        trend_df = unit_df.melt(
            id_vars=["cycle"],
            value_vars=selected_sensors,
            var_name="sensor",
            value_name="value",
        )
        fig = px.line(trend_df, x="cycle", y="value", color="sensor")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one sensor to view trends.")

with right:
    st.subheader("Prediction")
    if st.button("Predict Failure Risk", type="primary", use_container_width=True):
        try:
            result = call_predict_api(api_url, int(selected_unit), latest_cycles)
            st.session_state["prediction"] = result
            load_prediction_history.clear()
        except requests.RequestException as exc:
            st.error(f"Prediction request failed: {exc}")

    result = st.session_state.get("prediction")
    if result:
        risk = result["risk_level"]
        st.metric("Predicted RUL", f"{result['predicted_rul']:.1f} cycles")
        if risk == "high":
            st.error("High risk")
        elif risk == "medium":
            st.warning("Medium risk")
        else:
            st.success("Low risk")
        st.write(result["recommendation"])
    else:
        st.caption("Start the FastAPI server, then run a prediction.")

st.subheader("Latest Sensor Window")

# Trend visualization matters in predictive maintenance because changes over
# recent cycles can reveal degradation before a machine actually fails.
window_fig = px.line(
    latest_cycles,
    x="cycle",
    y=window_sensor,
    markers=True,
    title=f"{window_sensor} trend over latest {len(latest_cycles)} cycles",
)
st.plotly_chart(window_fig, use_container_width=True)

st.dataframe(latest_cycles, use_container_width=True)

history_col, model_col = st.columns(2)
with history_col:
    st.subheader("Prediction History")
    try:
        # This dashboard reads the local SQLite history directly so beginners
        # can see exactly where saved prediction records are stored.
        history_df = load_prediction_history(limit=10)
        if history_df.empty:
            st.caption("No prediction history found yet. Run a prediction to create the database records.")
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
