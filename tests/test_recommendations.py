from src.services.recommendations import risk_from_rul


def test_risk_levels() -> None:
    assert risk_from_rul(10) == "high"
    assert risk_from_rul(60) == "medium"
    assert risk_from_rul(120) == "low"
