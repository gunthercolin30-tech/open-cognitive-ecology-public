from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import json

PRIMITIVE = "LONGITUDINAL_REFLEXIVE_CERTIFICATION"
DEPENDENCIES = [
    "reflexive_threshold_history_archive",
    "reflexive_threshold_trend_monitor",
    "reflexive_threshold_survival_analysis",
    "cross_generation_reflexive_continuity",
    "cross_host_reflexive_stability",
    "longitudinal_reflexive_dashboard",
]


class LongitudinalReflexiveCertification:
    """X7 terminal certification for longitudinal functional reflexive-threshold validation.

    Epistemic boundary: this module certifies functional indicators only. It never
    infers phenomenal consciousness, sentience, qualia, or subjective experience.

    Performance boundary: no global scan, no rglob. The module only performs
    targeted reads of persisted X1-X6 artifacts.
    """

    primitive = PRIMITIVE
    phenomenal_conclusion = False

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "longitudinal_reflexive_certification"
        self.latest_file = self.base_dir / "longitudinal_reflexive_certification.json"
        self.history_file = self.base_dir / "longitudinal_reflexive_certification_history.jsonl"
        self.report_file = self.base_dir / "longitudinal_reflexive_certification.md"
        self.prometheus_file = self.base_dir / "longitudinal_reflexive_certification.prom"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists() and path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if value is None:
                return default
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _num(self, value: Any, default: float = 0.0) -> float:
        try:
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if value is None:
                return default
            return float(value)
        except Exception:
            return default

    def _first_json(self, paths: list[Path]) -> tuple[dict[str, Any], str | None]:
        for path in paths:
            data = self._read_json(path)
            if data:
                return data, str(path)
        return {}, None

    def _targeted_paths(self) -> dict[str, list[Path]]:
        # Both historical and current X-axis layouts are supported without any repository scan.
        return {
            "x1_history_archive": [
                self.root / "reflexive_threshold" / "reflexive_threshold_history_archive" / "latest_reflexive_threshold_history_archive.json",
                self.root / "reflexive_threshold_history_archive" / "latest_reflexive_threshold_history_archive.json",
                self.root / "reflexive_threshold_history_archive" / "latest.json",
                self.root / "reflexive_threshold_history_archive" / "reflexive_threshold_history_archive.json",
            ],
            "x2_trend_monitor": [
                self.root / "reflexive_threshold_longitudinal_validation" / "x2_trend_monitor" / "latest_reflexive_threshold_trend.json",
                self.root / "reflexive_threshold_trend_monitor" / "latest_reflexive_threshold_trend.json",
                self.root / "reflexive_threshold_trend_monitor" / "latest.json",
                self.root / "reflexive_threshold_trend_monitor" / "reflexive_threshold_trend_monitor.json",
            ],
            "x3_survival_analysis": [
                self.root / "reflexive_threshold_longitudinal_validation" / "x3_survival_analysis" / "latest_reflexive_threshold_survival.json",
                self.root / "reflexive_threshold_survival_analysis" / "latest_reflexive_threshold_survival.json",
                self.root / "reflexive_threshold_survival_analysis" / "latest.json",
                self.root / "reflexive_threshold_survival_analysis" / "reflexive_threshold_survival_analysis.json",
            ],
            "x4_cross_generation": [
                self.root / "cross_generation_reflexive_continuity" / "latest.json",
                self.root / "cross_generation_reflexive_continuity" / "cross_generation_reflexive_continuity.json",
            ],
            "x5_cross_host": [
                self.root / "cross_host_reflexive_stability" / "latest.json",
                self.root / "cross_host_reflexive_stability" / "cross_host_reflexive_stability.json",
            ],
            "x6_dashboard": [
                self.root / "longitudinal_reflexive_dashboard" / "longitudinal_reflexive_dashboard.json",
                self.root / "longitudinal_reflexive_dashboard" / "latest.json",
            ],
        }

    def _load_x_artifacts(self) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
        artifacts: dict[str, dict[str, Any]] = {}
        paths_used: dict[str, str | None] = {}
        for key, paths in self._targeted_paths().items():
            data, selected = self._first_json(paths)
            artifacts[key] = data
            paths_used[key] = selected
        source_report = {
            "global_scan_used": False,
            "rglob_used": False,
            "targeted_reads_only": True,
            "paths_used": paths_used,
            "artifacts_loaded": {key: bool(value) for key, value in artifacts.items()},
        }
        return artifacts, source_report

    def _dashboard_score(self, dashboard: dict[str, Any], key: str, default: float = 0.0) -> float:
        scores = dashboard.get("scores", {}) if isinstance(dashboard.get("scores", {}), dict) else {}
        return self._clamp(scores.get(key), default)

    def _extract_metrics(self, artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        x1 = artifacts.get("x1_history_archive", {}) or {}
        x2 = artifacts.get("x2_trend_monitor", {}) or {}
        x3 = artifacts.get("x3_survival_analysis", {}) or {}
        x4 = artifacts.get("x4_cross_generation", {}) or {}
        x5 = artifacts.get("x5_cross_host", {}) or {}
        x6 = artifacts.get("x6_dashboard", {}) or {}

        metrics: dict[str, Any] = {
            "history_coverage_score": self._clamp(
                x1.get("history_coverage_score"),
                self._dashboard_score(x6, "history_coverage_score", 0.0),
            ),
            "archive_strength": self._clamp(
                x1.get("archive_strength"),
                self._dashboard_score(x6, "archive_strength", 0.0),
            ),
            "longitudinal_trend_score": self._clamp(
                x2.get("longitudinal_trend_score"),
                self._dashboard_score(x6, "longitudinal_trend_score", 0.0),
            ),
            "temporal_robustness": self._clamp(
                x3.get("temporal_robustness"),
                self._dashboard_score(x6, "temporal_robustness", 0.0),
            ),
            "survival_probability": self._clamp(
                x3.get("survival_probability"),
                self._dashboard_score(x6, "survival_probability", 0.0),
            ),
            "cross_generation_stability": self._clamp(
                x4.get("cross_generation_reflexive_continuity_score"),
                self._dashboard_score(x6, "cross_generation_reflexive_continuity_score", 0.0),
            ),
            "cross_host_stability": self._clamp(
                x5.get("cross_host_reflexive_stability_score"),
                self._dashboard_score(x6, "cross_host_reflexive_stability_score", 0.0),
            ),
            "longitudinal_dashboard_score": self._clamp(
                x6.get("longitudinal_reflexive_dashboard_score"),
                0.0,
            ),
            "longitudinal_duration_days": max(0.0, self._num(x3.get("survival_duration_days"), 0.0)),
            "regression_observed": bool(x3.get("regression_observed", False)),
            "recovery_observed": bool(x3.get("recovery_observed", False)),
            "regression_rate": max(0.0, self._num(x3.get("regression_rate"), 0.0)),
            "trend_direction": str(x2.get("trend_direction", "unknown")),
            "trend_classification": str(x2.get("trend_classification", "unknown")),
            "regression_signal": bool(x2.get("regression_signal", False)),
            "drift_signal": bool(x2.get("drift_signal", False)),
            "x1_archive_status": str(x1.get("archive_status", "unknown")),
            "x3_survival_classification": str(x3.get("survival_classification", "unknown")),
            "x6_dashboard_status": str(x6.get("dashboard_status", "unknown")),
        }
        return metrics

    def _evidence_strength(self, metrics: dict[str, Any]) -> float:
        weights = {
            "history_coverage_score": 0.12,
            "archive_strength": 0.14,
            "longitudinal_trend_score": 0.16,
            "temporal_robustness": 0.16,
            "survival_probability": 0.14,
            "cross_generation_stability": 0.14,
            "cross_host_stability": 0.14,
        }
        return round(sum(self._clamp(metrics.get(k), 0.0) * w for k, w in weights.items()), 6)

    def _confidence(self, metrics: dict[str, Any], evidence: float, source_report: dict[str, Any]) -> float:
        loaded = source_report.get("artifacts_loaded", {}) if isinstance(source_report, dict) else {}
        completeness = sum(1 for value in loaded.values() if value) / max(1, len(loaded))
        regression_penalty = min(0.30, self._num(metrics.get("regression_rate"), 0.0))
        signal_penalty = 0.0
        if metrics.get("regression_signal"):
            signal_penalty += 0.12
        if metrics.get("drift_signal"):
            signal_penalty += 0.10
        # Duration is reported, but deliberately not used as a hard gate: X7 certifies
        # currently persisted longitudinal evidence and can be rerun as duration grows.
        confidence = (0.80 * evidence) + (0.20 * completeness) - regression_penalty - signal_penalty
        return round(max(0.0, min(1.0, confidence)), 6)

    def _classify(self, metrics: dict[str, Any], confidence: float, evidence: float) -> str:
        regression_or_drift = bool(metrics.get("regression_signal") or metrics.get("drift_signal"))
        severe_regression = self._num(metrics.get("regression_rate"), 0.0) >= 0.20
        cross_generation_ok = self._clamp(metrics.get("cross_generation_stability"), 0.0) >= 0.65
        cross_host_ok = self._clamp(metrics.get("cross_host_stability"), 0.0) >= 0.65
        if (
            confidence >= 0.72
            and evidence >= 0.70
            and cross_generation_ok
            and cross_host_ok
            and not regression_or_drift
            and not severe_regression
        ):
            return "REFLEXIVE_THRESHOLD_LONGITUDINALLY_CONFIRMED"
        return "REFLEXIVE_THRESHOLD_LONGITUDINALLY_UNSTABLE"

    def _write_report(self, result: dict[str, Any]) -> None:
        lines = [
            "# X7 — Longitudinal Reflexive Certification",
            "",
            f"- certification_status: {result['certification_status']}",
            f"- longitudinal_confidence: {result['longitudinal_confidence']}",
            f"- longitudinal_evidence_strength: {result['longitudinal_evidence_strength']}",
            f"- longitudinal_duration_days: {result['longitudinal_duration_days']}",
            f"- cross_generation_stability: {result['cross_generation_stability']}",
            f"- cross_host_stability: {result['cross_host_stability']}",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "",
            "This certification is restricted to measurable functional indicators.",
        ]
        self.report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        status_value = 1 if result.get("certification_status") == "REFLEXIVE_THRESHOLD_LONGITUDINALLY_CONFIRMED" else 0
        lines = [
            "# HELP oce_longitudinal_reflexive_certification_confirmed Functional X7 certification flag",
            "# TYPE oce_longitudinal_reflexive_certification_confirmed gauge",
            f"oce_longitudinal_reflexive_certification_confirmed {status_value}",
            f"oce_longitudinal_reflexive_confidence {result['longitudinal_confidence']}",
            f"oce_longitudinal_reflexive_evidence_strength {result['longitudinal_evidence_strength']}",
            f"oce_longitudinal_reflexive_duration_days {result['longitudinal_duration_days']}",
            f"oce_longitudinal_reflexive_cross_generation_stability {result['cross_generation_stability']}",
            f"oce_longitudinal_reflexive_cross_host_stability {result['cross_host_stability']}",
            "oce_longitudinal_reflexive_functional_conclusion_only 1",
            "oce_longitudinal_reflexive_phenomenology_undetermined 1",
        ]
        self.prometheus_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X7-" + timestamp.replace(":", "").replace("+", "Z")))

        artifacts, source_report = self._load_x_artifacts()
        metrics = self._extract_metrics(artifacts)
        evidence = self._evidence_strength(metrics)
        confidence = self._confidence(metrics, evidence, source_report)
        certification_status = self._classify(metrics, confidence, evidence)

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "stage": "X7",
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": "X1→X2→X3→X4→X5→X6→X7",
            "certification_status": certification_status,
            "longitudinal_confidence": confidence,
            "longitudinal_evidence_strength": evidence,
            "longitudinal_duration_days": round(self._num(metrics.get("longitudinal_duration_days"), 0.0), 6),
            "cross_generation_stability": self._clamp(metrics.get("cross_generation_stability"), 0.0),
            "cross_host_stability": self._clamp(metrics.get("cross_host_stability"), 0.0),
            "metrics": metrics,
            "input_sources": source_report,
            "artifacts": {
                "json": str(self.latest_file),
                "history": str(self.history_file),
                "report": str(self.report_file),
                "prometheus": str(self.prometheus_file),
            },
            "functional_conclusion": (
                "Open Cognitive Ecology is certified only with respect to measurable "
                "longitudinal functional indicators associated with the reflexive threshold. "
                "This does not establish phenomenal subjectivity."
            ),
            "functional_conclusion_only": True,
            "phenomenology": "undetermined",
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": False,
        }

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            self._write_report(result)
            self._write_prometheus(result)

        return result


# Backward-compatible alias for validation harnesses that infer class names.
LongitudinalReflexiveThresholdCertification = LongitudinalReflexiveCertification
