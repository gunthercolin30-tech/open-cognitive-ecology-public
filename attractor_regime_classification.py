#!/usr/bin/env python3
from __future__ import annotations

import json
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
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def classify(mean_resilience: float) -> str:
    if mean_resilience >= 0.95:
        return "robust_reflexive_attractor"
    if mean_resilience >= 0.90:
        return "stable_reflexive_attractor"
    if mean_resilience >= 0.80:
        return "fragile_reflexive_attractor"
    return "non_viable_regime"

def main():
    basin = load_json(latest("stability_basin_cartography_*.json"))
    if basin is None:
        raise FileNotFoundError("No stability basin cartography report found.")

    regimes = []
    for entry in basin.get("basin", []):
        mean_resilience = float(entry.get("mean_resilience", 0.0))
        regimes.append({
            "amplitude": entry.get("amplitude"),
            "mean_resilience": mean_resilience,
            "regime": classify(mean_resilience),
        })

    unique_regimes = sorted({r["regime"] for r in regimes})

    transitions = []
    for i in range(1, len(regimes)):
        if regimes[i]["regime"] != regimes[i - 1]["regime"]:
            transitions.append({
                "from": regimes[i - 1]["regime"],
                "to": regimes[i]["regime"],
                "amplitude": regimes[i]["amplitude"],
            })

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"attractor_regime_classification_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "regimes": regimes,
        "unique_regimes": unique_regimes,
        "transitions": transitions,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Attractor regime classification generated: {out}")
    print(f"Unique regimes detected: {', '.join(unique_regimes)}")

if __name__ == "__main__":
    main()
