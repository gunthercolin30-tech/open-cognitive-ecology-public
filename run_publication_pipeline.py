#!/usr/bin/env python3
"""
Automated scientific publication pipeline.

Runs the full reporting pipeline:
1. Global meta-analysis
2. Inter-version regression
3. Scientific dashboard

Uses only the Python standard library.
"""

from pathlib import Path
from datetime import datetime
import subprocess
import sys


SCRIPTS = [
    "run_global_meta_analysis.py",
    "run_inter_version_regression.py",
    "generate_scientific_dashboard.py",
]


def run_script(root: Path, script_name: str):
    script_path = root / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_name}")

    print(f"\n=== Running {script_name} ===")
    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(root),
        check=True,
    )


def run_functional_benchmark():
    try:
        from run_functional_consciousness_pipeline import main as run_benchmark

        result = run_benchmark()
        print("Functional Consciousness Benchmark executed successfully.")
        return result
    except Exception as exc:
        print(f"Warning: Functional Consciousness Benchmark failed: {exc}")
        return None


def main():
    root = Path(__file__).resolve().parent

    for script_name in SCRIPTS:
        run_script(root, script_name)

    run_functional_benchmark()

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    marker = root / "experiment_reports" / f"publication_pipeline_completed_{timestamp}.txt"
    marker.write_text(
        "Automated scientific publication pipeline completed successfully.\n",
        encoding="utf-8",
    )

    print("\n=== Automated Publication Pipeline Completed ===")
    print("\nSaved marker:")
    print(marker)


if __name__ == "__main__":
    main()
