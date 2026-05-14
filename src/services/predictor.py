from __future__ import annotations

import pandas as pd

from src.features.build_features import build_inference_features
from src.models.train import load_model
from src.services.recommendations import recommendation_from_risk, risk_from_rul


class MaintenancePredictor:
    def __init__(self) -> None:
        artifact = load_model()
        self.pipeline = artifact["pipeline"]
        self.feature_columns = artifact["feature_columns"]
        self.window_size = artifact["window_size"]

    def predict(self, cycles: pd.DataFrame) -> dict[str, float | str]:
        features = build_inference_features(cycles, window_size=self.window_size)
        features = features.reindex(columns=self.feature_columns, fill_value=0.0)
        predicted_rul = max(float(self.pipeline.predict(features)[0]), 0.0)
        risk_level = risk_from_rul(predicted_rul)
        return {
            "predicted_rul": round(predicted_rul, 2),
            "risk_level": risk_level,
            "recommendation": recommendation_from_risk(risk_level, predicted_rul),
        }
