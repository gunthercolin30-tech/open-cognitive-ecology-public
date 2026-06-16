#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime

from ontology.controlled_evolution_orchestrator import ControlledEvolutionOrchestrator


def main():
    orchestrator = ControlledEvolutionOrchestrator()

    cycle_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cycle": 1,
        "best_score": 0.95,
        "unified_consciousness_composite_index": 0.917,
        "threshold_crossed": False,
    }

    orchestrator.register_cycle(cycle_record)

    report = {
        "diagnostics": orchestrator.diagnostics(),
        "latest_cycle": orchestrator.latest_cycle(),
    }

    output_dir = Path("experiment_reports")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / (
        "controlled_evolution_runner_" +
        datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") +
        ".json"
    )

    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Rapport généré : {output_path}")


if __name__ == "__main__":
    main()
