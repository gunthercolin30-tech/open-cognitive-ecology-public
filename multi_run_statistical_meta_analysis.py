#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

def run_once(generations: int):
    cmd = [
        sys.executable,
        str(ROOT / "longitudinal_reflexive_observatory_runner.py"),
        "--generations",
        str(generations),
    ]
    subprocess.run(cmd, check=True)

    files = sorted(REPORTS.glob("longitudinal_reflexive_observatory_*.json"))
    if not files:
        raise FileNotFoundError("No longitudinal report generated.")
    with files[-1].open("r", encoding="utf-8") as f:
        return json.load(f)

def confidence_interval_95(values):
    if not values:
        return (0.0, 0.0)
    m = mean(values)
    if len(values) < 2:
        return (m, m)
    sd = pstdev(values)
    margin = 1.96 * sd / (len(values) ** 0.5)
    return (m - margin, m + margin)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--generations", type=int, default=10000)
    args = parser.parse_args()

    rei_values = []
    crossing_values = []

    for i in range(args.runs):
        print(f"Running experiment {i+1}/{args.runs}...")
        report = run_once(args.generations)
        rei_values.append(float(report.get("reflexive_emergence_index", 0.0)))
        crossing_values.append(int(report.get("threshold_crossings", 0)))

    rei_mean = mean(rei_values)
    rei_sd = pstdev(rei_values) if len(rei_values) > 1 else 0.0
    rei_ci = confidence_interval_95(rei_values)

    crossings_mean = mean(crossing_values)
    crossings_ci = confidence_interval_95(crossing_values)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"multi_run_statistical_meta_analysis_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "runs": args.runs,
        "generations_per_run": args.generations,
        "reflexive_emergence_index": {
            "values": rei_values,
            "mean": rei_mean,
            "std_dev": rei_sd,
            "confidence_interval_95": list(rei_ci),
        },
        "threshold_crossings": {
            "values": crossing_values,
            "mean": crossings_mean,
            "confidence_interval_95": list(crossings_ci),
        },
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Meta-analysis generated: {out}")
    print(f"REI mean: {rei_mean:.6f}")
    print(f"REI 95% CI: [{rei_ci[0]:.6f}, {rei_ci[1]:.6f}]")

if __name__ == "__main__":
    main()
