"""
RUNTIME_EXPERIMENT_MANAGER
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

PRIMITIVE = "RUNTIME_EXPERIMENT_MANAGER"


class RuntimeExperimentManager:
    primitive = PRIMITIVE

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.experiments_dir = self.root / "runtime_experiments"
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self):
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def _extract_metrics(self, result):
        cli = result.get("cli_result", {})
        latest = cli.get("latest_runtime_result", {})
        governance = latest.get("governance_result", {})
        return {
            "cycle_count": result.get("cycle_count"),
            "civilizational_autonomy_score": governance.get("civilizational_autonomy_score"),
            "executive_coherence_score": governance.get("executive_coherence_score"),
            "global_viability_score": governance.get("global_viability_score"),
            "unified_consciousness_score": governance.get("unified_consciousness_score"),
            "certification": governance.get("certification"),
        }

    def _detect_drift(self, history):
        if len(history) < 2:
            return {"drift_detected": False, "reason": "insufficient_history"}

        first = history[0]
        last = history[-1]
        monitored = [
            "civilizational_autonomy_score",
            "executive_coherence_score",
            "global_viability_score",
            "unified_consciousness_score",
        ]

        deltas = {}
        drift_detected = False

        for key in monitored:
            a = first.get(key)
            b = last.get(key)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                delta = round(b - a, 6)
                deltas[key] = delta
                if abs(delta) > 0.05:
                    drift_detected = True

        return {"drift_detected": drift_detected, "deltas": deltas}

    def step(self, max_cycles=10, sleep_seconds=0.0):
        from ontology.integrated_civilizational_runtime import IntegratedCivilizationalRuntime
        runtime = IntegratedCivilizationalRuntime()

        metrics_history = []

        for _ in range(max_cycles):
            result = runtime.step()
            metrics_history.append(self._extract_metrics(result))

            if sleep_seconds > 0:
                import time
                time.sleep(sleep_seconds)

        drift = self._detect_drift(metrics_history)

        report = {
            "primitive": self.primitive,
            "timestamp": self._timestamp(),
            "cycles_executed": max_cycles,
            "metrics_history": metrics_history,
            "drift_analysis": drift,
            "final_metrics": metrics_history[-1] if metrics_history else {},
            "status": "completed",
        }

        report_path = self.experiments_dir / f"experiment_{report['timestamp']}.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        report["report_path"] = str(report_path)
        return report
