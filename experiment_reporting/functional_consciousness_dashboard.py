"""
Runtime-Integrated Functional Consciousness Dashboard.

Provides a helper to compute and persist the functional consciousness
benchmark and return dashboard-ready data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from ontology.functional_consciousness_behavioral_benchmark import evaluate


def build_functional_consciousness_report(state, output_dir="experiment_reports"):
    report = evaluate(state)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = (
        Path(output_dir)
        / f"functional_consciousness_benchmark_{timestamp}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": timestamp,
        "functional_consciousness": report,
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "functional_consciousness_report_file": str(output_path),
        "functional_consciousness": report,
    }


def dashboard_fragment(state):
    return build_functional_consciousness_report(state)["functional_consciousness"]
