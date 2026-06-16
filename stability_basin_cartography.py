#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

def run_perturbation(amplitude: float, runs: int, generations: int):
    cmd = [
        sys.executable,
        str(ROOT / "adaptive_evolutionary_perturbation_laboratory.py"),
        "--runs", str(runs),
        "--generations", str(generations),
        "--amplitude", str(amplitude),
    ]
    subprocess.run(cmd, check=True)

    files = sorted(REPORTS.glob("adaptive_evolutionary_perturbation_laboratory_*.json"))
    if not files:
        raise FileNotFoundError("No perturbation laboratory report found.")
    with files[-1].open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--generations", type=int, default=10000)
    parser.add_argument(
        "--amplitudes",
        type=str,
        default="0.01,0.05,0.10,0.20,0.30,0.50",
        help="Comma-separated perturbation amplitudes.",
    )
    args = parser.parse_args()

    amplitudes = [float(x.strip()) for x in args.amplitudes.split(",") if x.strip()]
    basin = []

    for amplitude in amplitudes:
        print(f"Exploring amplitude {amplitude:.3f}...")
        report = run_perturbation(amplitude, args.runs, args.generations)
        resilience = report.get("resilience", {})
        basin.append({
            "amplitude": amplitude,
            "mean_resilience": resilience.get("mean", 0.0),
            "confidence_interval_95": resilience.get("confidence_interval_95", [0.0, 0.0]),
        })

    viable = [b for b in basin if b["mean_resilience"] >= 0.90]
    critical = min((b["amplitude"] for b in basin if b["mean_resilience"] < 0.90), default=None)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"stability_basin_cartography_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "runs_per_amplitude": args.runs,
        "generations_per_run": args.generations,
        "basin": basin,
        "viability_threshold": 0.90,
        "viable_amplitudes": [b["amplitude"] for b in viable],
        "critical_amplitude": critical,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Stability basin cartography generated: {out}")
    if critical is None:
        print("No critical amplitude detected within explored range.")
    else:
        print(f"Critical amplitude detected near {critical:.3f}.")

if __name__ == "__main__":
    main()
