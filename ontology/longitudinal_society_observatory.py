
from __future__ import annotations

from pathlib import Path
import json

PRIMITIVE = "longitudinal_society_observatory"

DEPENDENCIES = [
    "artificial_society_runtime",
    "civilizational_dashboard",
    "supreme_representative_runtime",
    "genealogical_continuity",
    "architectural_non_closure_index",
    "constitutional_alignment_field",
    "global_viability_certificate",
    "monitoring",
    "persistent_multi_scale_memory",
]

class LongitudinalSocietyObservatory:

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.storage_dir = self.root / "longitudinal_observatory"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.storage_dir / "society_history.jsonl"
        self.history = []
        self._load_history()

    def _load_history(self):
        if not self.history_path.exists():
            return

        raw = self.history_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        # Convert legacy literal \n sequences into real newlines
        raw = raw.replace("\\n", "\n")

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue

            try:
                self.history.append(json.loads(line))
            except Exception:
                pass

    def record(self, snapshot):
        snapshot = dict(snapshot)
        self.history.append(snapshot)

        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(snapshot, ensure_ascii=False))
            fh.write("\n")



    def record_longitudinal_metrics(
        self,
        stability_result=None,
        drift_result=None,
        monitoring_result=None,
        certification_result=None,
        recovery_result=None,
    ):

        snapshot = {
            "record_type": "longitudinal_metrics"
        }

        if stability_result:
            snapshot["stability"] = stability_result

        if drift_result:
            snapshot["drift"] = drift_result

        if monitoring_result:
            snapshot["monitoring"] = monitoring_result

        if certification_result:
            snapshot["certification"] = certification_result

        if recovery_result:
            snapshot["recovery"] = recovery_result

        self.record(snapshot)

        return {
            "persisted": True,
            "history_length": len(self.history),
        }



    def aggregate_longitudinal_metrics(self):

        stability_values = []
        drift_values = []
        certification_values = []
        recovery_values = []

        for item in self.history:

            stability = item.get("stability", {})
            drift = item.get("drift", {})
            certification = item.get("certification", {})
            recovery = item.get("recovery", {})

            s = stability.get(
                "civilizational_longitudinal_stability_index"
            )
            d = drift.get(
                "civilizational_drift_index"
            )
            c = certification.get(
                "certified"
            )
            r = recovery.get(
                "longitudinal_recovery_index"
            )

            if isinstance(s, (int, float)):
                stability_values.append(float(s))

            if isinstance(d, (int, float)):
                drift_values.append(float(d))

            if isinstance(r, (int, float)):
                recovery_values.append(float(r))

            if isinstance(c, bool):
                certification_values.append(c)

        def mean(values):
            return sum(values) / len(values) if values else None

        stability_mean = mean(stability_values)
        drift_mean = mean(drift_values)
        recovery_mean = mean(recovery_values)

        certification_ratio = None
        if certification_values:
            certification_ratio = (
                sum(1 for x in certification_values if x)
                / len(certification_values)
            )

        aggregated_index_components = [
            x for x in [
                stability_mean,
                recovery_mean,
                (1.0 - drift_mean) if drift_mean is not None else None,
                certification_ratio,
            ] if x is not None
        ]

        aggregated_longitudinal_stability_index = None

        if aggregated_index_components:
            aggregated_longitudinal_stability_index = (
                sum(aggregated_index_components)
                / len(aggregated_index_components)
            )

        return {
            "aggregated_history_points": len(self.history),
            "stability_mean": stability_mean,
            "stability_min": min(stability_values) if stability_values else None,
            "stability_max": max(stability_values) if stability_values else None,
            "drift_mean": drift_mean,
            "drift_max": max(drift_values) if drift_values else None,
            "recovery_mean": recovery_mean,
            "certification_ratio": certification_ratio,
            "aggregated_longitudinal_stability_index":
                aggregated_longitudinal_stability_index,
            "longitudinal_aggregation_ready": True,
        }



    def observe_real_drift(self):

        stability_series = []

        for item in self.history:

            stability = item.get("stability", {})

            value = stability.get(
                "civilizational_longitudinal_stability_index"
            )

            if isinstance(value, (int, float)):
                stability_series.append(float(value))

        if len(stability_series) < 2:
            return {
                "success": False,
                "reason": "insufficient_real_history",
                "history_points": len(stability_series),
            }

        drift_rate = abs(
            stability_series[-1]
            - stability_series[-2]
        )

        cumulative_drift = abs(
            stability_series[-1]
            - stability_series[0]
        )

        relative_drift = (
            cumulative_drift
            / max(stability_series[0], 1e-9)
        )

        deltas = [
            stability_series[i + 1]
            - stability_series[i]
            for i in range(
                len(stability_series) - 1
            )
        ]

        drift_acceleration = (
            abs(deltas[-1] - deltas[-2])
            if len(deltas) >= 2
            else 0.0
        )

        if relative_drift >= 0.25:
            classification = (
                "critical_longitudinal_drift"
            )
        elif cumulative_drift < 0.10:
            classification = (
                "stable_longitudinal_trajectory"
            )
        else:
            classification = (
                "controlled_longitudinal_drift"
            )

        return {
            "success": True,
            "history_points": len(stability_series),
            "real_drift_rate": round(drift_rate, 4),
            "real_drift_acceleration":
                round(drift_acceleration, 4),
            "real_cumulative_drift":
                round(cumulative_drift, 4),
            "real_relative_drift":
                round(relative_drift, 4),
            "trajectory_classification":
                classification,
            "real_drift_observation_ready": True,
        }



    def certify_real_longitudinal_stability(self):

        aggregation = self.aggregate_longitudinal_metrics()
        drift = self.observe_real_drift()

        stability_index = aggregation.get(
            "aggregated_longitudinal_stability_index"
        )

        relative_drift = drift.get(
            "real_relative_drift"
        )

        if stability_index is None:
            return {
                "success": False,
                "reason": "missing_aggregated_metrics",
            }

        if relative_drift is None:
            return {
                "success": False,
                "reason": "missing_real_drift_metrics",
            }

        certification_score = (
            0.70 * stability_index +
            0.30 * (1.0 - min(relative_drift, 1.0))
        )

        certified = (
            stability_index >= 0.90 and
            relative_drift <= 0.10
        )

        if certified and certification_score >= 0.90:
            certification_class = (
                "certified_longitudinal_civilization"
            )
        elif certification_score >= 0.75:
            certification_class = (
                "provisionally_stable_civilization"
            )
        else:
            certification_class = (
                "longitudinal_certification_failed"
            )

        return {
            "success": True,
            "history_points":
                aggregation.get(
                    "aggregated_history_points",
                    0,
                ),
            "aggregated_longitudinal_stability_index":
                round(stability_index, 4),
            "real_relative_drift":
                round(relative_drift, 4),
            "certification_score":
                round(certification_score, 4),
            "certified": certified,
            "certification_class":
                certification_class,
            "real_longitudinal_certification_ready":
                True,
        }

    def step(self):
        if not self.history:
            self.record({
                "time_index": 0,
                "global_viability_score": 0.918,
                "constitutional_alignment_score": 0.92,
                "architectural_non_closure_index": 0.92,
                "genealogical_continuity_score": 0.93,
            })

        latest = self.history[-1]

        return {
            "primitive": PRIMITIVE,
            "history_length": len(self.history),
            "latest_snapshot": latest,
            "history_path": str(self.history_path),
            "trend_analysis_ready": True,
            "archival_ready": True,
            "classification": "Persistent Longitudinal Society Observatory",
            "diagnostics": {
                "historical_monitoring_enabled": True,
                "persistent_history_enabled": True,
            },
        }
