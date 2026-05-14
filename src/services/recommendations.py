from __future__ import annotations

from src.config import RISK_THRESHOLDS


def risk_from_rul(rul: float) -> str:
    if rul <= RISK_THRESHOLDS["high"]:
        return "high"
    if rul <= RISK_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def recommendation_from_risk(risk_level: str, predicted_rul: float) -> str:
    rounded_rul = max(int(round(predicted_rul)), 0)
    if risk_level == "high":
        return (
            f"Schedule immediate inspection. Predicted RUL is about {rounded_rul} cycles, "
            "so defer non-critical operation until maintenance is reviewed."
        )
    if risk_level == "medium":
        return (
            f"Plan maintenance within the next service window. Predicted RUL is about "
            f"{rounded_rul} cycles; monitor high-trend sensors closely."
        )
    return (
        f"Continue normal operation. Predicted RUL is about {rounded_rul} cycles; "
        "keep routine monitoring active."
    )
