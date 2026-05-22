import pytest

from src.services.prediction_mode import normalize_prediction_mode


def test_prediction_mode_defaults_to_api() -> None:
    assert normalize_prediction_mode(None) == "api"
    assert normalize_prediction_mode("") == "api"


def test_prediction_mode_accepts_api_and_direct_case_insensitive() -> None:
    assert normalize_prediction_mode("api") == "api"
    assert normalize_prediction_mode(" DIRECT ") == "direct"


def test_prediction_mode_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="Invalid PREDICTION_MODE"):
        normalize_prediction_mode("cloud")
