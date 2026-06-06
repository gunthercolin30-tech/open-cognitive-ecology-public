"""Continuous Long Duration Runtime Executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
from typing import Any

from ontology.long_duration_experiment_launcher import LongDurationExperimentLauncher
from ontology.autonomous_runtime_service import AutonomousRuntimeService
from ontology.alerting_and_notification_system import AlertingAndNotificationSystem
from ontology.experiment_stability_dashboard import ExperimentStabilityDashboard


@dataclass
class ContinuousLongDurationRuntimeExecutor:
    root: Path | None = None

    def __post_init__(self) -> None:
        if self.root is None:
            self.root = Path.home() / "open-cognitive-ecology"

    def run(
        self,
        duration_hours: float = 24.0,
        interval_seconds: float = 3600.0,
        max_cycles: int = 10,
    ) -> dict[str, Any]:
        plan = LongDurationExperimentLauncher(self.root).launch(
            duration_hours=duration_hours,
            label="continuous_run",
        )

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_dir = (
            self.root
            / "runtime_experiments"
            / "continuous_runs"
            / f"run_{timestamp}"
        )
        run_dir.mkdir(parents=True, exist_ok=True)

        service = AutonomousRuntimeService(root=self.root)
        alerter = AlertingAndNotificationSystem()

        end_time = datetime.utcnow() + timedelta(hours=duration_hours)
        iterations = 0
        all_alerts = []

        metrics_history_path = (
            run_dir / "metrics_history.jsonl"
        )

        while datetime.utcnow() < end_time:
            iterations += 1

            step_result = service.step(max_cycles=max_cycles)

            metrics = (
                step_result
                .get("last_result", {})
                .get("final_metrics", {})
            )

            metrics_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iterations,
                "metrics": metrics,
            }


            # A10.10 ECOLOGICAL RUNTIME WIRING
            try:
                from ontology.civilizational_metrics_synthesizer import (
                    persist_ecological_metrics,
                    ecological_governance_signal,
                    ecological_self_revision_recommendations,
                )

                ecological_metrics = persist_ecological_metrics()
                ecological_signal = ecological_governance_signal()
                ecological_recommendations = (
                    ecological_self_revision_recommendations()
                )
            except Exception as exc:
                ecological_metrics = {"error": str(exc)}
                ecological_signal = {}
                ecological_recommendations = {}
            with open(
                metrics_history_path,
                "a",
                encoding="utf-8",
            ) as history_file:
                import json as _json

                history_file.write(
                    _json.dumps(
                        metrics_entry,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            alert_result = alerter.step(metrics)

            all_alerts.extend(
                alert_result.get("alerts", [])
            )

            if interval_seconds > 0:
                time.sleep(interval_seconds)

        dashboard = ExperimentStabilityDashboard(root=self.root).step()

        summary = {
            "status": "completed",
            "planned_duration_hours": duration_hours,
            "iterations": iterations,
            "alert_count": len(all_alerts),
            "alerts": all_alerts,
            "experiment_plan_path": plan["experiment_plan_path"],
            "dashboard_path": dashboard["dashboard_path"],
        }

        summary_path = run_dir / "run_summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        summary["summary_path"] = str(summary_path)
        return summary


if __name__ == "__main__":
    executor = ContinuousLongDurationRuntimeExecutor()
    print(executor.run(duration_hours=0.001, interval_seconds=1))
