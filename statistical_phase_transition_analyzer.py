#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

def load_latest_report():
    files = sorted(REPORTS.glob("longitudinal_reflexive_observatory_*.json"))
    if not files:
        raise FileNotFoundError("No longitudinal_reflexive_observatory report found.")
    path = files[-1]
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return path, data

def moving_average(values, window):
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        chunk = values[start:i+1]
        result.append(sum(chunk) / len(chunk))
    return result

def detect_phase_transition(values, threshold=0.01):
    if len(values) < 2:
        return None
    diffs = [values[i] - values[i-1] for i in range(1, len(values))]
    max_jump = max(diffs)
    idx = diffs.index(max_jump) + 1
    if max_jump >= threshold:
        return {
            "generation": idx + 1,
            "jump": max_jump,
        }
    return None

def correlation(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    sx = pstdev(xs)
    sy = pstdev(ys)
    if sx == 0 or sy == 0:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
    return cov / (sx * sy)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=50)
    args = parser.parse_args()

    source_path, report = load_latest_report()
    records = report.get("records", [])
    values = [float(r.get("reflexive_capacity", 0.0)) for r in records]
    generations = [int(r.get("generation", i + 1)) for i, r in enumerate(records)]

    ma = moving_average(values, max(1, args.window))
    transition = detect_phase_transition(ma)
    corr = correlation(generations, values)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"statistical_phase_transition_analysis_{timestamp}.json"

    analysis = {
        "timestamp": timestamp,
        "source_report": str(source_path),
        "num_records": len(records),
        "mean_reflexive_capacity": mean(values) if values else 0.0,
        "max_reflexive_capacity": max(values) if values else 0.0,
        "generation_capacity_correlation": corr,
        "detected_phase_transition": transition,
        "moving_average_window": args.window,
    }

    out.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    print(f"Analysis generated: {out}")
    if transition:
        print(
            f"Phase transition detected near generation "
            f"{transition['generation']} (jump={transition['jump']:.6f})"
        )
    else:
        print("No significant phase transition detected.")
    print(f"Generation-capacity correlation: {corr:.6f}")

if __name__ == "__main__":
    main()
