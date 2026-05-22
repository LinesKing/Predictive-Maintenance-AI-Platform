from __future__ import annotations

from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException

from api.schemas import PredictionRequest, PredictionResponse
from src.config import MODEL_PATH
from src.database.db import fetch_recent_predictions, init_db, insert_prediction
from src.services.predictor import MaintenancePredictor

app = FastAPI(
    title="Predictive Maintenance AI Platform API",
    description="Industrial RUL prediction service for maintenance risk monitoring.",
    version="0.2.0",
)


@lru_cache(maxsize=1)
def get_predictor() -> MaintenancePredictor:
    return MaintenancePredictor()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "Predictive Maintenance AI Platform API",
        "model_available": MODEL_PATH.exists(),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        predictor = get_predictor()
        cycles = pd.DataFrame([cycle.model_dump() for cycle in payload.cycles])
        result = predictor.predict(cycles)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    insert_prediction(
        unit_id=payload.unit_id,
        predicted_rul=float(result["predicted_rul"]),
        risk_level=str(result["risk_level"]),
        recommendation=str(result["recommendation"]),
    )
    return PredictionResponse(unit_id=payload.unit_id, **result)


@app.get("/history")
def history(limit: int = 25) -> list[dict]:
    return fetch_recent_predictions(limit=limit)
