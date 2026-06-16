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

PIPELINE = [
    "longitudinal_reflexive_observatory_runner.py",
    "statistical_phase_transition_analyzer.py",
    "automated_reflexive_publication_generator.py",
    "multi_run_statistical_meta_analysis.py",
    "adaptive_evolutionary_perturbation_laboratory.py",
    "stability_basin_cartography.py",
    "attractor_regime_classification.py",
    "dynamic_regime_transition_network.py",
    "reflexive_criticality_monitor.py",
    "adaptive_safeguard_controller.py",
    "closed_loop_viability_preservation.py",
    "iterative_viability_recovery_controller.py",
]

def run_script(script_name: str) -> dict:
    script_path = ROOT / script_name
    if not script_path.exists():
        return {
            "script": script_name,
            "status": "missing",
            "return_code": None,
        }

    print(f"Running {script_name}...")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    return {
        "script": script_name,
        "status": "success" if result.returncode == 0 else "failed",
        "return_code": result.returncode,
        "stdout_tail": result.stdout[-400:],
        "stderr_tail": result.stderr[-400:],
    }

def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    executions = []
    for script in PIPELINE:
        executions.append(run_script(script))

    successful = sum(1 for e in executions if e["status"] == "success")
    failed = sum(1 for e in executions if e["status"] == "failed")
    missing = sum(1 for e in executions if e["status"] == "missing")

    summary = {
        "timestamp": timestamp,
        "pipeline": PIPELINE,
        "successful": successful,
        "failed": failed,
        "missing": missing,
        "fully_operational": failed == 0 and missing == 0,
        "executions": executions,
    }

    out = REPORTS / f"autonomous_reflexive_ecosystem_supervisor_{timestamp}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Autonomous reflexive ecosystem supervisor report generated: {out}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Missing: {missing}")
    print(f"Fully operational: {summary['fully_operational']}")

if __name__ == "__main__":
    main()
