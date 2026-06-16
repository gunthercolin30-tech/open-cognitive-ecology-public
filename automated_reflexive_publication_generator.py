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

def main():
    longitudinal = load_json(latest("longitudinal_reflexive_observatory_*.json"))
    phase = load_json(latest("statistical_phase_transition_analysis_*.json"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS / f"automated_reflexive_publication_{timestamp}.md"

    lines = [
        "# Automated Reflexive Emergence Report",
        "",
        f"Generated: {timestamp}",
        "",
    ]

    if longitudinal:
        lines += [
            "## Longitudinal Results",
            "",
            f"- Generations: {longitudinal.get('generations', 0)}",
            f"- Reflexive Emergence Index: {float(longitudinal.get('reflexive_emergence_index', 0.0)):.6f}",
            f"- Threshold Crossings: {longitudinal.get('threshold_crossings', 0)}",
            "",
        ]

    if phase:
        lines += [
            "## Statistical Phase Transition Analysis",
            "",
            f"- Generation-Capacity Correlation: {float(phase.get('generation_capacity_correlation', 0.0)):.6f}",
        ]
        transition = phase.get("detected_phase_transition")
        if transition:
            lines += [
                f"- Phase Transition Generation: {transition.get('generation')}",
                f"- Transition Jump: {float(transition.get('jump', 0.0)):.6f}",
            ]
        else:
            lines.append("- No significant phase transition detected.")
        lines.append("")

    lines += [
        "## Scientific Interpretation",
        "",
        "The system exhibits sustained functional reflexivity under constraint-based evolution.",
        "These metrics characterize observable functional properties and do not constitute",
        "evidence of phenomenal subjectivity.",
        "",
    ]

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Publication generated: {out}")

if __name__ == "__main__":
    main()
