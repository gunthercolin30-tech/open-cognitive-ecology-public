#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

VIABILITY_THRESHOLD = 0.90

def run_perturbation(amplitude: float, runs: int = 5, generations: int = 5000):
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
        raise FileNotFoundError("No perturbation report found.")
    with files[-1].open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    amplitude = 0.50
    attempts = []
    max_iterations = 10
    reduction_factor = 0.75
    restored = False
    final_resilience = 0.0

    for iteration in range(1, max_iterations + 1):
        print(f"Recovery iteration {iteration}: amplitude={amplitude:.6f}")
        report = run_perturbation(amplitude)
        final_resilience = float(report.get("resilience", {}).get("mean", 0.0))

        attempts.append({
            "iteration": iteration,
            "amplitude": amplitude,
            "resilience_mean": final_resilience,
            "viable": final_resilience >= VIABILITY_THRESHOLD,
        })

        if final_resilience >= VIABILITY_THRESHOLD:
            restored = True
            break

        amplitude *= reduction_factor

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"iterative_viability_recovery_controller_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "viability_threshold": VIABILITY_THRESHOLD,
        "max_iterations": max_iterations,
        "reduction_factor": reduction_factor,
        "attempts": attempts,
        "viability_restored": restored,
        "iterations_used": len(attempts),
        "final_amplitude": amplitude,
        "final_resilience_mean": final_resilience,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Iterative viability recovery report generated: {out}")
    print(f"Viability restored: {restored}")
    print(f"Iterations used: {len(attempts)}")
    print(f"Final resilience mean: {final_resilience:.6f}")

if __name__ == "__main__":
    main()
