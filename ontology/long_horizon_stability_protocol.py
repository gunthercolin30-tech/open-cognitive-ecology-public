
"""
LONG_HORIZON_STABILITY_PROTOCOL
"""

from pathlib import Path
from datetime import datetime

PRIMITIVE = "LONG_HORIZON_STABILITY_PROTOCOL"


class LongHorizonStabilityProtocol:
    primitive = PRIMITIVE

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.protocol_dir = self.root / "long_horizon_protocol"
        self.protocol_dir.mkdir(parents=True, exist_ok=True)

    def step(
        self,
        max_cycles=100,
        sleep_seconds=0.0,
        viability_threshold=0.85,
        autonomy_threshold=0.85,
    ):
        from ontology.runtime_experiment_manager import RuntimeExperimentManager
        from ontology.experiment_stability_dashboard import ExperimentStabilityDashboard

        manager = RuntimeExperimentManager(root=self.root)
        report = manager.step(max_cycles=max_cycles, sleep_seconds=sleep_seconds)

        final_metrics = report.get("final_metrics", {})
        viability = final_metrics.get("global_viability_score")
        autonomy = final_metrics.get("civilizational_autonomy_score")

        thresholds_respected = True
        stop_reason = "completed"

        if isinstance(viability, (int, float)) and viability < viability_threshold:
            thresholds_respected = False
            stop_reason = "global_viability_below_threshold"

        if isinstance(autonomy, (int, float)) and autonomy < autonomy_threshold:
            thresholds_respected = False
            stop_reason = "civilizational_autonomy_below_threshold"

        dashboard_result = ExperimentStabilityDashboard(root=self.root).step()

        summary = {
            "primitive": self.primitive,
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "cycles_executed": report.get("cycles_executed"),
            "thresholds": {
                "global_viability_threshold": viability_threshold,
                "civilizational_autonomy_threshold": autonomy_threshold,
            },
            "final_metrics": final_metrics,
            "thresholds_respected": thresholds_respected,
            "stop_reason": stop_reason,
            "experiment_report_path": report.get("report_path"),
            "dashboard_path": dashboard_result.get("dashboard_path"),
            "status": "completed",
        }

        return summary
