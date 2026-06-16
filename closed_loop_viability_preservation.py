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

def latest(pattern: str):
    files = sorted(REPORTS.glob(pattern))
    return files[-1] if files else None

def load_json(path):
    if path is None:
        raise FileNotFoundError("Required report not found.")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

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
    controller = load_json(latest("adaptive_safeguard_controller_*.json"))

    emergency = [s for s in controller.get("safeguards", []) if s.get("action") == "emergency_reduce"]
    if not emergency:
        print("No emergency action required.")
        return

    target = emergency[0]
    original_amplitude = float(target["amplitude"])
    corrected_amplitude = float(target["recommended_amplitude"])

    print(
        f"Executing closed-loop correction: "
        f"{original_amplitude:.3f} -> {corrected_amplitude:.3f}"
    )

    verification = run_perturbation(corrected_amplitude)

    resilience_mean = float(
        verification.get("resilience", {}).get("mean", 0.0)
    )
    restored = resilience_mean >= 0.90

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"closed_loop_viability_preservation_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "original_amplitude": original_amplitude,
        "corrected_amplitude": corrected_amplitude,
        "verified_resilience_mean": resilience_mean,
        "viability_restored": restored,
        "verification_report": verification.get("timestamp"),
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Closed-loop viability preservation generated: {out}")
    print(f"Verified resilience mean: {resilience_mean:.6f}")
    print(f"Viability restored: {restored}")

if __name__ == "__main__":
    main()
