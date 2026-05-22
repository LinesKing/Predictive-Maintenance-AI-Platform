from __future__ import annotations


VALID_PREDICTION_MODES = {"api", "direct"}


def normalize_prediction_mode(value: str | None) -> str:
    mode = (value or "api").strip().lower()
    if mode not in VALID_PREDICTION_MODES:
        valid_modes = ", ".join(sorted(VALID_PREDICTION_MODES))
        raise ValueError(f"Invalid PREDICTION_MODE={value!r}. Expected one of: {valid_modes}.")
    return mode
