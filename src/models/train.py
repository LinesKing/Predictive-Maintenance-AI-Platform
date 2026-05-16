from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import METADATA_PATH, MODEL_PATH
from src.data.cmapss import add_rul_target, load_cmapss
from src.features.build_features import build_training_frame


def train_model(
    data_path: str | Path,
    model_path: str | Path = MODEL_PATH,
    metadata_path: str | Path = METADATA_PATH,
    window_size: int = 20,
) -> dict[str, float | int | str]:
    df = add_rul_target(load_cmapss(data_path))
    x, y = build_training_frame(df, window_size=window_size)

    x_train, x_valid, y_train, y_valid = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=150,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=1,
                ),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_valid)

    metrics = {
        "mae": float(mean_absolute_error(y_valid, predictions)),
        "rmse": float(root_mean_squared_error(y_valid, predictions)),
        "training_rows": int(len(x)),
        "feature_count": int(x.shape[1]),
        "window_size": int(window_size),
        "trained_at": datetime.now(UTC).isoformat(),
        "data_path": str(data_path),
    }

    model_path = Path(model_path)
    metadata_path = Path(metadata_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "feature_columns": list(x.columns), "window_size": window_size}, model_path)
    metadata_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def load_model(model_path: str | Path = MODEL_PATH) -> dict:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found at {path}. Run scripts/train_model.py first."
        )
    return joblib.load(path)
