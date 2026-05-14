from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DATA_DIR
from src.data.cmapss import COLUMN_NAMES


def create_sample_data(output_path: Path, units: int = 40, min_cycles: int = 90, max_cycles: int = 180) -> None:
    rng = np.random.default_rng(42)
    rows = []
    for unit_id in range(1, units + 1):
        total_cycles = int(rng.integers(min_cycles, max_cycles + 1))
        degradation_rate = rng.uniform(0.7, 1.5)
        for cycle in range(1, total_cycles + 1):
            age = cycle / total_cycles
            settings = [rng.normal(0, 0.002), rng.normal(0, 0.0003), 100.0]
            sensors = [
                518.67,
                642 + 4.5 * age * degradation_rate + rng.normal(0, 0.6),
                1580 + 35 * age * degradation_rate + rng.normal(0, 3.0),
                1400 + 45 * age * degradation_rate + rng.normal(0, 4.0),
                14.62,
                21.61,
                554 - 8 * age * degradation_rate + rng.normal(0, 0.8),
                2388 + rng.normal(0, 0.08),
                9040 + 65 * age * degradation_rate + rng.normal(0, 8.0),
                1.3,
                47 + 4 * age * degradation_rate + rng.normal(0, 0.4),
                522 - 7 * age * degradation_rate + rng.normal(0, 0.7),
                2388 + rng.normal(0, 0.08),
                8130 + 60 * age * degradation_rate + rng.normal(0, 7.0),
                8.4 + 0.12 * age * degradation_rate + rng.normal(0, 0.03),
                0.03,
                392 + 3 * age * degradation_rate + rng.normal(0, 0.7),
                2388,
                100,
                39 - 2.5 * age * degradation_rate + rng.normal(0, 0.25),
                23.3 - 1.5 * age * degradation_rate + rng.normal(0, 0.2),
            ]
            rows.append([unit_id, cycle, *settings, *sensors])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=COLUMN_NAMES)
    df.to_csv(output_path, sep=" ", header=False, index=False, float_format="%.5f")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RAW_DATA_DIR / "sample_train_FD001.txt")
    args = parser.parse_args()
    create_sample_data(args.output)
    print(f"Created sample data at {args.output}")


if __name__ == "__main__":
    main()
