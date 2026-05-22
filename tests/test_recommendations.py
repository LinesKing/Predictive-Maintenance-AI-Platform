from src.services.recommendations import recommendation_from_risk, risk_from_rul


def test_risk_levels() -> None:
    assert risk_from_rul(5) == "CRITICAL"
    assert risk_from_rul(20) == "HIGH"
    assert risk_from_rul(60) == "MEDIUM"
    assert risk_from_rul(120) == "LOW"


def test_risk_level_boundaries() -> None:
    assert risk_from_rul(10) == "CRITICAL"
    assert risk_from_rul(30) == "HIGH"
    assert risk_from_rul(80) == "MEDIUM"
    assert risk_from_rul(81) == "LOW"


def test_recommendations_are_available_for_each_risk_level() -> None:
    for risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        recommendation = recommendation_from_risk(risk_level, 25)
        assert recommendation
        assert "cycles" in recommendation
