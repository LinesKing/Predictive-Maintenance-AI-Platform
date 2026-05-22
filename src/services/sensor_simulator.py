from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.cmapss import COLUMN_NAMES


def simulate_sensor_cycles(
    unit_id: int = 1,
    cycles: int = 20,
    start_cycle: int = 1,
    degradation: float = 0.65,
    seed: int = 42,
) -> pd.DataFrame:
    """Create deterministic C-MAPSS-shaped sensor cycles for demo/API use."""
    if cycles < 1:
        raise ValueError("cycles must be at least 1")

    rng = np.random.default_rng(seed + unit_id)
    rows = []
    for offset in range(cycles):
        cycle = start_cycle + offset
        age = offset / max(cycles - 1, 1)
        load = degradation * age
        settings = [rng.normal(0, 0.002), rng.normal(0, 0.0003), 100.0]
        sensors = [
            518.67,
            642 + 4.2 * load + rng.normal(0, 0.45),
            1580 + 31 * load + rng.normal(0, 2.5),
            1400 + 42 * load + rng.normal(0, 3.5),
            14.62,
            21.61,
            554 - 7.5 * load + rng.normal(0, 0.6),
            2388 + rng.normal(0, 0.06),
            9040 + 58 * load + rng.normal(0, 6.0),
            1.3,
            47 + 3.7 * load + rng.normal(0, 0.35),
            522 - 6.5 * load + rng.normal(0, 0.55),
            2388 + rng.normal(0, 0.06),
            8130 + 54 * load + rng.normal(0, 5.5),
            8.4 + 0.11 * load + rng.normal(0, 0.025),
            0.03,
            392 + 2.7 * load + rng.normal(0, 0.55),
            2388,
            100,
            39 - 2.3 * load + rng.normal(0, 0.2),
            23.3 - 1.3 * load + rng.normal(0, 0.16),
        ]
        rows.append([unit_id, cycle, *settings, *sensors])

    return pd.DataFrame(rows, columns=COLUMN_NAMES)


def simulate_prediction_payload(unit_id: int = 1, cycles: int = 20) -> dict:
    """Return an API-ready payload for the FastAPI /predict endpoint."""
    df = simulate_sensor_cycles(unit_id=unit_id, cycles=cycles)
    return {
        "unit_id": unit_id,
        "cycles": df.drop(columns=["unit_id"]).to_dict(orient="records"),
    }
