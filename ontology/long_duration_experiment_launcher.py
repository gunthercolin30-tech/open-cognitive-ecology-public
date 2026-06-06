"""Long Duration Experiment Launcher."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
from typing import Any

from ontology.reference_runtime_freeze_protocol import (
    ReferenceRuntimeFreezeProtocol,
)


@dataclass
class LongDurationExperimentLauncher:
    root: Path | None = None

    def __post_init__(self) -> None:
        if self.root is None:
            self.root = Path.home() / "open-cognitive-ecology"

    def launch(
        self,
        duration_hours: int = 24,
        label: str = "baseline",
    ) -> dict[str, Any]:
        freeze_result = ReferenceRuntimeFreezeProtocol(
            self.root
        ).freeze()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        experiment_dir = (
            self.root
            / "runtime_experiments"
            / f"experiment_{timestamp}"
        )
        experiment_dir.mkdir(parents=True, exist_ok=True)

        plan = {
            "status": "success",
            "label": label,
            "planned_duration_hours": duration_hours,
            "freeze_status": freeze_result["status"],
            "freeze_manifest_path": freeze_result["manifest_path"],
            "created_at_utc": timestamp,
        }

        plan_path = experiment_dir / "experiment_plan.json"
        plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        plan["experiment_plan_path"] = str(plan_path)
        return plan


if __name__ == "__main__":
    launcher = LongDurationExperimentLauncher()
    print(launcher.launch())
