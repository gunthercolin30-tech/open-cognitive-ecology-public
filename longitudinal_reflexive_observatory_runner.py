#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

def compute_reflexive_emergence_index(records):
    if not records:
        return 0.0
    values = [float(r.get("reflexive_capacity", 0.0)) for r in records]
    threshold_hits = sum(1 for r in records if r.get("threshold_crossed", False))
    return 0.7 * mean(values) + 0.3 * (threshold_hits / len(records))

def simulate_generation(i):
    # Placeholder deterministic simulation; can be replaced by actual orchestrator calls.
    reflexive_capacity = min(1.0, i / 1000.0)
    threshold_crossed = reflexive_capacity >= 0.75
    return {
        "generation": i,
        "reflexive_capacity": reflexive_capacity,
        "threshold_crossed": threshold_crossed,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=1000)
    args = parser.parse_args()

    records = [simulate_generation(i + 1) for i in range(args.generations)]

    threshold_crossings = sum(1 for r in records if r["threshold_crossed"])
    rei = compute_reflexive_emergence_index(records)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORTS / f"longitudinal_reflexive_observatory_{timestamp}.json"

    report = {
        "timestamp": timestamp,
        "generations": args.generations,
        "threshold_crossings": threshold_crossings,
        "reflexive_emergence_index": rei,
        "records": records,
    }

    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Report generated: {path}")
    print(f"Reflexive Emergence Index: {rei:.6f}")
    print(f"Threshold crossings: {threshold_crossings}")

if __name__ == "__main__":
    main()
