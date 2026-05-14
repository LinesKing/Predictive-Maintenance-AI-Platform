from __future__ import annotations

from pathlib import Path

import pandas as pd


SETTING_COLUMNS = ["setting_1", "setting_2", "setting_3"]
SENSOR_COLUMNS = [f"sensor_{idx}" for idx in range(1, 22)]
COLUMN_NAMES = ["unit_id", "cycle", *SETTING_COLUMNS, *SENSOR_COLUMNS]


def load_cmapss(path: str | Path) -> pd.DataFrame:
    """Load a NASA C-MAPSS train/test text file into a typed DataFrame."""
    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=COLUMN_NAMES,
        engine="python",
    )
    return df.dropna(axis=1, how="all")


def add_rul_target(df: pd.DataFrame, max_rul: int = 125) -> pd.DataFrame:
    """Add capped RUL target for training data."""
    result = df.copy()
    max_cycle = result.groupby("unit_id")["cycle"].transform("max")
    result["rul"] = (max_cycle - result["cycle"]).clip(upper=max_rul)
    return result


def latest_window(df: pd.DataFrame, unit_id: int, window_size: int) -> pd.DataFrame:
    unit_df = df[df["unit_id"] == unit_id].sort_values("cycle")
    if unit_df.empty:
        raise ValueError(f"No records found for unit_id={unit_id}")
    return unit_df.tail(window_size)
