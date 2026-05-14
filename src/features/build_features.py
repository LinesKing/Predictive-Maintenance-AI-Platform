from __future__ import annotations

import pandas as pd

from src.data.cmapss import SENSOR_COLUMNS, SETTING_COLUMNS


BASE_FEATURE_COLUMNS = ["cycle", *SETTING_COLUMNS, *SENSOR_COLUMNS]
WINDOW_FEATURE_COLUMNS = SENSOR_COLUMNS


def build_training_frame(df: pd.DataFrame, window_size: int = 20) -> tuple[pd.DataFrame, pd.Series]:
    """Create supervised features from all available cycles."""
    if "rul" not in df.columns:
        raise ValueError("Training data must include a 'rul' column.")

    features = []
    targets = []
    for _, unit_df in df.groupby("unit_id"):
        unit_df = unit_df.sort_values("cycle")
        for idx in range(len(unit_df)):
            window = unit_df.iloc[max(0, idx + 1 - window_size) : idx + 1]
            features.append(_features_from_window(window))
            targets.append(unit_df.iloc[idx]["rul"])

    return pd.DataFrame(features), pd.Series(targets, name="rul")


def build_inference_features(cycles: pd.DataFrame, window_size: int = 20) -> pd.DataFrame:
    """Create a single inference row from the latest cycles for one machine."""
    if cycles.empty:
        raise ValueError("At least one cycle is required for prediction.")
    window = cycles.sort_values("cycle").tail(window_size)
    return pd.DataFrame([_features_from_window(window)])


def _features_from_window(window: pd.DataFrame) -> dict[str, float]:
    latest = window.iloc[-1]
    row: dict[str, float] = {
        "cycle": float(latest["cycle"]),
    }

    for column in SETTING_COLUMNS:
        row[column] = float(latest[column])

    for column in SENSOR_COLUMNS:
        series = window[column].astype(float)
        row[f"{column}_latest"] = float(series.iloc[-1])
        row[f"{column}_mean"] = float(series.mean())
        row[f"{column}_std"] = float(series.std(ddof=0))
        row[f"{column}_min"] = float(series.min())
        row[f"{column}_max"] = float(series.max())
        row[f"{column}_trend"] = _trend(series)

    return row


def _trend(series: pd.Series) -> float:
    if len(series) < 2:
        return 0.0
    return float(series.iloc[-1] - series.iloc[0]) / max(len(series) - 1, 1)
