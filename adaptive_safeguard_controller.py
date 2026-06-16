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
        raise FileNotFoundError("Required report not found.")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def recommended_action(alert_level: str, amplitude: float) -> dict:
    if alert_level == "stable":
        return {"action": "maintain", "recommended_amplitude": amplitude}
    if alert_level == "watch":
        return {"action": "monitor", "recommended_amplitude": amplitude * 0.95}
    if alert_level == "warning":
        return {"action": "reduce", "recommended_amplitude": amplitude * 0.75}
    return {"action": "emergency_reduce", "recommended_amplitude": amplitude * 0.50}

def main():
    monitor = load_json(latest("reflexive_criticality_monitor_*.json"))

    safeguards = []
    for entry in monitor.get("monitoring", []):
        amplitude = float(entry.get("amplitude", 0.0))
        alert_level = entry.get("alert_level", "stable")

        action = recommended_action(alert_level, amplitude)

        safeguards.append({
            "amplitude": amplitude,
            "alert_level": alert_level,
            "action": action["action"],
            "recommended_amplitude": round(action["recommended_amplitude"], 6),
        })

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"adaptive_safeguard_controller_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "safeguards": safeguards,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Adaptive safeguard controller generated: {out}")

    critical_actions = [s for s in safeguards if s["action"] == "emergency_reduce"]
    if critical_actions:
        first = critical_actions[0]
        print(
            "Emergency reduction recommended at amplitude "
            f"{first['amplitude']:.3f} -> {first['recommended_amplitude']:.3f}"
        )
    else:
        print("No emergency reduction required.")

if __name__ == "__main__":
    main()
