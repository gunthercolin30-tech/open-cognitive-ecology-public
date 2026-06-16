#!/usr/bin/env python3
"""
Inter-version regression benchmark.

Compares current global meta-analysis results against the most recent
previous global meta-analysis report to detect regressions or improvements.
Uses only the Python standard library.
"""

from pathlib import Path
from datetime import datetime
import glob
import json


def load_meta_reports(reports_dir: Path):
    paths = sorted(
        Path(p) for p in glob.glob(str(reports_dir / "global_meta_analysis_*.json"))
    )
    if len(paths) < 2:
        raise RuntimeError(
            "At least two global_meta_analysis_*.json files are required."
        )
    return paths[-2], paths[-1]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    root = Path(__file__).resolve().parent
    reports_dir = root / "experiment_reports"
    reports_dir.mkdir(exist_ok=True)

    previous_path, current_path = load_meta_reports(reports_dir)

    previous = load_json(previous_path)
    current = load_json(current_path)

    prev_summary = previous["global_summary"]
    curr_summary = current["global_summary"]

    prev_score = prev_summary["best_average_global_experience_score"]
    curr_score = curr_summary["best_average_global_experience_score"]
    delta = round(curr_score - prev_score, 6)

    if delta > 0.0001:
        status = "Improvement"
    elif delta < -0.0001:
        status = "Regression"
    else:
        status = "Stable"

    result = {
        "timestamp_utc": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "previous_report": str(previous_path),
        "current_report": str(current_path),
        "previous_best_average_score": prev_score,
        "current_best_average_score": curr_score,
        "delta": delta,
        "status": status,
    }

    output_path = reports_dir / (
        f"inter_version_regression_{result['timestamp_utc']}.json"
    )

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n=== Inter-Version Regression Benchmark ===")
    print("Previous best score:", prev_score)
    print("Current best score :", curr_score)
    print("Delta              :", delta)
    print("Status             :", status)
    print("\nSaved to:")
    print(output_path)


if __name__ == "__main__":
    main()
