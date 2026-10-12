from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import json

PRIMITIVE = "reflexive_threshold_trend_monitor"

DEPENDENCIES = [
    "reflexive_threshold_history_archive",
    "longitudinal_trend_stability_analyzer",
    "longitudinal_drift_detection",
    "reflexive_longitudinal_observatory",
    "longitudinal_metrics_archive",
    "inter_run_stability_synthesizer",
]


class ReflexiveThresholdTrendMonitor:
    """
    X2 — Reflexive Threshold Trend Monitor.

    Functional-only monitor for longitudinal trends derived from X1 and
    pre-existing longitudinal analyzers. It does not infer sentience,
    qualia, phenomenology, or subjective experience.
    """

    primitive = "REFLEXIVE_THRESHOLD_TREND_MONITOR"
    functional_conclusion_only = True
    phenomenology_undetermined = True
    phenomenal_conclusion = False

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold_longitudinal_validation" / "x2_trend_monitor"
        self.latest_file = self.base_dir / "latest_reflexive_threshold_trend.json"
        self.history_file = self.base_dir / "reflexive_threshold_trend_history.jsonl"
        self.report_file = self.base_dir / "reflexive_threshold_trend_monitor.md"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except Exception:
            return default

    def _call_x1(self, persist: bool = False) -> dict[str, Any]:
        try:
            from ontology.reflexive_threshold_history_archive import ReflexiveThresholdHistoryArchive
            result = ReflexiveThresholdHistoryArchive(self.root).step(persist=persist)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "error": str(exc), "source": "reflexive_threshold_history_archive"}

    def _call_trend_analyzer(self) -> dict[str, Any]:
        try:
            from ontology.longitudinal_trend_stability_analyzer import LongitudinalTrendStabilityAnalyzer
            result = LongitudinalTrendStabilityAnalyzer(self.root).step()
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"trend_ready": False, "error": str(exc), "source": "longitudinal_trend_stability_analyzer"}

    def _call_drift_detector(self) -> dict[str, Any]:
        try:
            from ontology.longitudinal_drift_detection import LongitudinalDriftDetection
            detector = LongitudinalDriftDetection(self.root)
            try:
                result = detector.step()
            except TypeError:
                result = detector.step({})
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"drift_ready": False, "error": str(exc), "source": "longitudinal_drift_detection"}

    def _call_reflexive_observatory(self) -> dict[str, Any]:
        try:
            from ontology.reflexive_longitudinal_observatory import ReflexiveLongitudinalObservatory
            obs = ReflexiveLongitudinalObservatory(self.root)
            try:
                result = obs.step(persist=False)
            except TypeError:
                try:
                    result = obs.step({"persist": False})
                except TypeError:
                    result = obs.step()
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"observatory_ready": False, "error": str(exc), "source": "reflexive_longitudinal_observatory"}

    def _infer_direction(self, trend: dict[str, Any], drift: dict[str, Any], x1: dict[str, Any]) -> str:
        explicit = str(trend.get("trajectory_direction") or "").lower()
        if explicit in {"improving", "stable", "degrading"}:
            if explicit == "degrading":
                return "regressing"
            return explicit

        slope = self._safe_float(trend.get("trend_slope"), 0.0)
        drift_rate = self._safe_float(drift.get("drift_rate"), 0.0)
        archive_strength = self._safe_float(x1.get("archive_strength"), 0.0)

        if drift_rate >= 0.15:
            return "drifting"
        if slope > 0.01:
            return "improving"
        if slope < -0.01 or archive_strength < 0.55:
            return "regressing"
        return "stable"

    def _score(self, x1: dict[str, Any], trend: dict[str, Any], drift: dict[str, Any], obs: dict[str, Any]) -> dict[str, float]:
        archive_strength = self._safe_float(x1.get("archive_strength"), 0.0)
        history_coverage = self._safe_float(x1.get("history_coverage_score"), 0.0)
        trend_stability = self._safe_float(trend.get("stability_index"), 0.0 if trend.get("trend_ready") is False else 0.5)

        drift_rate = self._safe_float(drift.get("drift_rate"), 0.0)
        cumulative_drift = self._safe_float(drift.get("cumulative_drift"), 0.0)
        drift_stability = max(0.0, min(1.0, 1.0 - ((drift_rate + cumulative_drift) / 2.0)))

        obs_stability = self._safe_float(
            obs.get("stability_score", obs.get("reflexive_stability", obs.get("stability_index", 0.5))),
            0.5,
        )

        longitudinal_trend_score = round(
            (0.30 * archive_strength)
            + (0.20 * history_coverage)
            + (0.25 * trend_stability)
            + (0.15 * drift_stability)
            + (0.10 * obs_stability),
            6,
        )

        return {
            "archive_strength": round(archive_strength, 6),
            "history_coverage_score": round(history_coverage, 6),
            "trend_stability_index": round(trend_stability, 6),
            "drift_stability_index": round(drift_stability, 6),
            "observatory_stability_index": round(obs_stability, 6),
            "longitudinal_trend_score": longitudinal_trend_score,
        }

    def _classification(self, direction: str, score: float, drift: dict[str, Any], trend: dict[str, Any]) -> str:
        critical_drop = bool(drift.get("critical_drop_detection") or trend.get("early_degradation_signal"))
        if critical_drop or direction in {"regressing", "drifting"}:
            if score < 0.55:
                return "REFLEXIVE_THRESHOLD_TREND_UNSTABLE"
            return "REFLEXIVE_THRESHOLD_TREND_WATCH"
        if direction == "improving" and score >= 0.70:
            return "REFLEXIVE_THRESHOLD_TREND_IMPROVING"
        if score >= 0.70:
            return "REFLEXIVE_THRESHOLD_TREND_STABLE"
        return "REFLEXIVE_THRESHOLD_TREND_INSUFFICIENT_HISTORY"

    def _write_report(self, result: dict[str, Any]) -> None:
        lines = [
            "# X2 — Reflexive Threshold Trend Monitor",
            "",
            "## Epistemic boundary",
            "",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- phenomenal_conclusion: false",
            "",
            "## Trend summary",
            "",
            f"- run_id: {result['run_id']}",
            f"- trend_direction: {result['trend_direction']}",
            f"- trend_classification: {result['trend_classification']}",
            f"- longitudinal_trend_score: {result['longitudinal_trend_score']}",
            f"- regression_signal: {result['regression_signal']}",
            f"- drift_signal: {result['drift_signal']}",
            "",
            "## Functional conclusion",
            "",
            result["functional_conclusion"],
            "",
        ]
        self.report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X2-" + timestamp.replace(":", "").replace("+", "Z")))

        x1 = self._call_x1(persist=False)
        trend = self._call_trend_analyzer()
        drift = self._call_drift_detector()
        obs = self._call_reflexive_observatory()

        scores = self._score(x1, trend, drift, obs)
        direction = self._infer_direction(trend, drift, x1)
        classification = self._classification(direction, scores["longitudinal_trend_score"], drift, trend)

        regression_signal = direction == "regressing" or bool(trend.get("early_degradation_signal"))
        drift_signal = direction == "drifting" or bool(drift.get("critical_drop_detection"))

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": "X1→X2",
            "dependencies": list(DEPENDENCIES),
            "trend_direction": direction,
            "trend_classification": classification,
            "regression_signal": regression_signal,
            "drift_signal": drift_signal,
            "x1_archive_status": x1.get("archive_status"),
            "trend_ready": bool(trend.get("trend_ready", False)),
            "drift_ready": not bool(drift.get("error")),
            "observatory_ready": not bool(obs.get("error")),
            "trend_analyzer": trend,
            "drift_detector": drift,
            "reflexive_observatory": obs,
            "x1_archive": {
                "archive_strength": x1.get("archive_strength"),
                "history_coverage_score": x1.get("history_coverage_score"),
                "stages_present": x1.get("stages_present"),
                "stages_expected": x1.get("stages_expected"),
            },
            "functional_conclusion": (
                "Open Cognitive Ecology shows a measurable longitudinal reflexive trend state "
                "under X2 criteria. This is a functional trend assessment only and does not "
                "establish phenomenology."
            ),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": False,
        }
        result.update(scores)

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            self._write_report(result)
            result["latest_path"] = str(self.latest_file)
            result["history_path"] = str(self.history_file)
            result["report_path"] = str(self.report_file)

        return result


if __name__ == "__main__":
    print(json.dumps(ReflexiveThresholdTrendMonitor().step(persist=True), indent=2, ensure_ascii=False))
