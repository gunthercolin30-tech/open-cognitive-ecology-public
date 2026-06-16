#!/usr/bin/env python3
"""
Global comparative meta-analysis of all consciousness experiment results.
Uses only the Python standard library.
"""

from pathlib import Path
from datetime import datetime
import glob
import json
import math


def mean(values):
    return sum(values) / len(values) if values else 0.0


def variance(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


def stddev(values):
    return math.sqrt(variance(values))


def extract_report(payload):
    return payload.get("report", payload)


def scenario_name(report, path):
    return (
        report.get("perturbation_scenario")
        or report.get("experiment_status")
        or path.stem
    )


def summarize(path):
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    report = extract_report(payload)
    metrics = report.get("cycle_metrics", [])

    if metrics:
        scores = [m.get("global_experience_score", 0.0) for m in metrics]
        regulation_count = sum(
            1 for m in metrics if m.get("needs_regulation", False)
        )
        cycles = len(metrics)
        regulation_frequency = regulation_count / cycles if cycles else 0.0
    else:
        cycles = report.get("cycles", 0)
        scores = [report.get("average_global_experience_score", 0.0)]
        regulation_frequency = report.get("regulation_frequency", 0.0)

    avg = mean(scores)
    min_score = min(scores) if scores else 0.0

    if avg >= 0.85 and regulation_frequency <= 0.20 and min_score >= 0.70:
        classification = "High Stability"
    elif avg >= 0.75 and regulation_frequency <= 0.35 and min_score >= 0.60:
        classification = "Moderate Stability"
    elif avg >= 0.60:
        classification = "Unstable"
    else:
        classification = "Collapse Risk"

    return {
        "file": str(path),
        "scenario": scenario_name(report, path),
        "cycles": cycles,
        "average_global_experience_score": round(avg, 6),
        "standard_deviation": round(stddev(scores), 6),
        "minimum_global_experience_score": round(min_score, 6),
        "regulation_frequency": round(regulation_frequency, 6),
        "classification": classification,
    }


def main():
    root = Path(__file__).resolve().parent
    results_dir = root / "experiment_results"
    reports_dir = root / "experiment_reports"
    reports_dir.mkdir(exist_ok=True)

    files = sorted(Path(p) for p in glob.glob(str(results_dir / "*.json")))
    if not files:
        raise FileNotFoundError("No JSON experiment results found.")

    summaries = [summarize(path) for path in files]
    summaries.sort(
        key=lambda s: (
            s["average_global_experience_score"],
            -s["regulation_frequency"],
        ),
        reverse=True,
    )

    global_summary = {
        "experiments_analyzed": len(summaries),
        "best_scenario": summaries[0]["scenario"],
        "best_average_global_experience_score":
            summaries[0]["average_global_experience_score"],
        "classification_counts": {},
    }

    for s in summaries:
        c = s["classification"]
        global_summary["classification_counts"][c] = (
            global_summary["classification_counts"].get(c, 0) + 1
        )

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = reports_dir / (
        f"global_meta_analysis_{timestamp}.json"
    )

    result = {
        "timestamp_utc": timestamp,
        "global_summary": global_summary,
        "ranked_experiments": summaries,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n=== Global Comparative Meta-Analysis ===")
    print("Experiments analyzed:", global_summary["experiments_analyzed"])
    print("Best scenario:", global_summary["best_scenario"])
    print(
        "Best average score:",
        global_summary["best_average_global_experience_score"],
    )
    print("Classification counts:", global_summary["classification_counts"])
    print("\nSaved to:")
    print(output_path)


if __name__ == "__main__":
    main()
