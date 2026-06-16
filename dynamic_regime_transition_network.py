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

def main():
    classification = load_json(latest("attractor_regime_classification_*.json"))

    regimes = classification.get("regimes", [])
    transitions = {}

    for i in range(1, len(regimes)):
        source = regimes[i - 1]["regime"]
        target = regimes[i]["regime"]
        key = f"{source} -> {target}"
        transitions[key] = transitions.get(key, 0) + 1

    nodes = sorted({r["regime"] for r in regimes})
    edges = []

    total = sum(transitions.values())
    for key, count in sorted(transitions.items()):
        source, target = key.split(" -> ")
        probability = count / total if total else 0.0
        edges.append({
            "source": source,
            "target": target,
            "count": count,
            "probability": probability,
        })

    outgoing_sources = {e["source"] for e in edges}
    absorbing_states = [node for node in nodes if node not in outgoing_sources]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"dynamic_regime_transition_network_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "nodes": nodes,
        "edges": edges,
        "absorbing_states": absorbing_states,
    }

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Dynamic regime transition network generated: {out}")
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print(f"Absorbing states: {', '.join(absorbing_states) if absorbing_states else 'None'}")

if __name__ == "__main__":
    main()
