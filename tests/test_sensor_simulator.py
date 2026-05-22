from src.data.cmapss import COLUMN_NAMES
from src.services.sensor_simulator import simulate_prediction_payload, simulate_sensor_cycles


def test_simulated_sensor_cycles_match_cmapss_columns() -> None:
    cycles = simulate_sensor_cycles(unit_id=7, cycles=5)

    assert list(cycles.columns) == COLUMN_NAMES
    assert len(cycles) == 5
    assert cycles["unit_id"].nunique() == 1
    assert cycles["unit_id"].iloc[0] == 7


def test_simulated_prediction_payload_is_api_shaped() -> None:
    payload = simulate_prediction_payload(unit_id=3, cycles=4)

    assert payload["unit_id"] == 3
    assert len(payload["cycles"]) == 4
    assert "unit_id" not in payload["cycles"][0]
    assert "cycle" in payload["cycles"][0]
    assert "sensor_21" in payload["cycles"][0]
