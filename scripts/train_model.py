from __future__ import annotations

import argparse
from pathlib import Path

from src.config import RAW_DATA_DIR
from src.models.train import train_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a turbofan RUL model.")
    parser.add_argument("--data", type=Path, default=RAW_DATA_DIR / "sample_train_FD001.txt")
    parser.add_argument("--window-size", type=int, default=20)
    args = parser.parse_args()

    metrics = train_model(args.data, window_size=args.window_size)
    print("Training complete")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
