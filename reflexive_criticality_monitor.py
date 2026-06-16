#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "experiment_reports"
REPORTS.mkdir(exist_ok=True)

VIABILITY_THRESHOLD = 0.90

def latest(pattern: str):
    files = sorted(REPORTS.glob(pattern))
    return files[-1] if files else None

def load_json(path):
    if path is None:
        raise FileNotFoundError("Required report not found.")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def classify_alert(margin: float) -> str:
    if margin >= 0.05:
        return "stable"
    if margin >= 0.0:
        return "watch"
    if margin >= -0.05:
        return "warning"
    return "critical"

def main():
    basin = load_json(latest("stability_basin_cartography_*.json"))

    monitoring = []
    for entry in basin.get("basin", []):
        amplitude = float(entry.get("amplitude", 0.0))
        mean_resilience = float(entry.get("mean_resilience", 0.0))
        margin = mean_resilience - VIABILITY_THRESHOLD

        monitoring.append({
            "amplitude": amplitude,
            "mean_resilience": mean_resilience,
            "viability_margin": margin,
            "alert_level": classify_alert(margin),
        })

    critical_entries = [m for m in monitoring if m["alert_level"] == "critical"]
    first_critical = critical_entries[0]["amplitude"] if critical_entries else None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"reflexive_criticality_monitor_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "viability_threshold": VIABILITY_THRESHOLD,
        "monitoring": monitoring,
        "first_critical_amplitude": first_critical,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Reflexive criticality monitor generated: {out}")
    if first_critical is None:
        print("No critical region detected.")
    else:
        print(f"First critical amplitude: {first_critical:.3f}")

if __name__ == "__main__":
    main()
