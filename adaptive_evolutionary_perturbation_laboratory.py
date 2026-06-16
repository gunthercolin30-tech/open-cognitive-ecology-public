#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
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

def apply_perturbation(report: dict, amplitude: float, rng: random.Random):
    rei = float(report.get("reflexive_emergence_index", 0.0))
    crossings = int(report.get("threshold_crossings", 0))

    factor = max(0.0, 1.0 + rng.uniform(-amplitude, amplitude))
    perturbed_rei = max(0.0, min(1.0, rei * factor))
    perturbed_crossings = max(0, int(round(crossings * factor)))

    return {
        "base_rei": rei,
        "perturbed_rei": perturbed_rei,
        "base_crossings": crossings,
        "perturbed_crossings": perturbed_crossings,
        "perturbation_factor": factor,
        "resilience_score": 1.0 - abs(perturbed_rei - rei),
    }

def confidence_interval_95(values):
    if not values:
        return [0.0, 0.0]
    m = mean(values)
    if len(values) < 2:
        return [m, m]
    sd = pstdev(values)
    margin = 1.96 * sd / (len(values) ** 0.5)
    return [m - margin, m + margin]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--generations", type=int, default=10000)
    parser.add_argument("--amplitude", type=float, default=0.10,
                        help="Maximum relative perturbation amplitude.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    results = []

    for i in range(args.runs):
        print(f"Perturbation run {i + 1}/{args.runs}...")
        base_report = run_once(args.generations)
        results.append(apply_perturbation(base_report, args.amplitude, rng))

    resilience_scores = [r["resilience_score"] for r in results]
    perturbed_rei_values = [r["perturbed_rei"] for r in results]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"adaptive_evolutionary_perturbation_laboratory_{timestamp}.json"

    summary = {
        "timestamp": timestamp,
        "runs": args.runs,
        "generations_per_run": args.generations,
        "perturbation_amplitude": args.amplitude,
        "seed": args.seed,
        "resilience": {
            "mean": mean(resilience_scores),
            "std_dev": pstdev(resilience_scores) if len(resilience_scores) > 1 else 0.0,
            "confidence_interval_95": confidence_interval_95(resilience_scores),
        },
        "perturbed_reflexive_emergence_index": {
            "mean": mean(perturbed_rei_values),
            "confidence_interval_95": confidence_interval_95(perturbed_rei_values),
        },
        "results": results,
    }

    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Perturbation laboratory report generated: {out}")
    print(f"Mean resilience score: {summary['resilience']['mean']:.6f}")

if __name__ == "__main__":
    main()
