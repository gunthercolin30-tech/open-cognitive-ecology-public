from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Any


PRIMITIVE = "cognitive_gap_detector"

DEPENDENCIES = [
    "ontology_gap_detector",
    "meta_cognition",
    "epistemic_humility",
    "self_confidence_calibration",
    "monitoring",
    "evaluation",
    "autonomous_capability_discovery",
    "scientific_anomaly_detector",
    "metrics_anomaly_detection_engine",
    "interaction_queue_manager",
]


class CognitiveGapDetector:
    """
    O1 — Cognitive Gap Detector.

    Detects cognitive situations that justify possible external assistance:
    - high uncertainty;
    - repeated failure;
    - missing knowledge;
    - improvement blockage;
    - unresolved contradiction.

    This primitive is not a duplicate of ontology_gap_detector.
    ontology_gap_detector identifies missing ontology primitives.
    cognitive_gap_detector identifies operational cognitive gaps that may feed
    the external collaboration pipeline.
    """

    def __init__(
        self,
        root: Path | None = None,
        history_file: Path | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.history_file = (
            Path(history_file)
            if history_file is not None
            else self.root / "cognitive_gap_history.jsonl"
        )
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _safe_signal(self, inputs: dict[str, Any], key: str, default: float = 0.0) -> float:
        return self._bounded(inputs.get(key, default))

    def _signal_from_recent_failures(self, inputs: dict[str, Any]) -> float:
        explicit = inputs.get("repeated_failure_score")
        if explicit is not None:
            return self._bounded(explicit)

        failures = inputs.get("recent_failures", [])
        attempts = inputs.get("recent_attempts", None)

        if isinstance(failures, int) or isinstance(failures, float):
            failure_count = max(0.0, float(failures))
        elif isinstance(failures, list):
            failure_count = float(len(failures))
        else:
            failure_count = 0.0

        if attempts is None:
            return self._bounded(failure_count / 3.0)

        try:
            attempt_count = max(float(attempts), 1.0)
            return self._bounded(failure_count / attempt_count)
        except Exception:
            return self._bounded(failure_count / 3.0)

    def _signal_from_missing_knowledge(self, inputs: dict[str, Any]) -> float:
        explicit = inputs.get("knowledge_absence_score")
        if explicit is not None:
            return self._bounded(explicit)

        missing = inputs.get("missing_knowledge", [])
        unknown_terms = inputs.get("unknown_terms", [])

        missing_count = len(missing) if isinstance(missing, list) else (1 if missing else 0)
        unknown_count = len(unknown_terms) if isinstance(unknown_terms, list) else (1 if unknown_terms else 0)

        return self._bounded((missing_count + unknown_count) / 5.0)

    def _signal_from_blockage(self, inputs: dict[str, Any]) -> float:
        explicit = inputs.get("improvement_blockage_score")
        if explicit is not None:
            return self._bounded(explicit)

        stalled = bool(inputs.get("improvement_stalled", False))
        no_progress_cycles = inputs.get("no_progress_cycles", 0)
        try:
            cycles_score = self._bounded(float(no_progress_cycles) / 5.0)
        except Exception:
            cycles_score = 0.0

        return self._bounded(max(0.65 if stalled else 0.0, cycles_score))

    def _signal_from_contradiction(self, inputs: dict[str, Any]) -> float:
        explicit = inputs.get("contradiction_score")
        if explicit is not None:
            return self._bounded(explicit)

        contradictions = inputs.get("unresolved_contradictions", [])
        if isinstance(contradictions, list):
            return self._bounded(len(contradictions) / 3.0)
        return self._bounded(1.0 if contradictions else 0.0)

    def detect(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})

        uncertainty_pressure = self._safe_signal(inputs, "uncertainty_score", 0.0)
        failure_pressure = self._signal_from_recent_failures(inputs)
        knowledge_absence_pressure = self._signal_from_missing_knowledge(inputs)
        improvement_blockage_pressure = self._signal_from_blockage(inputs)
        contradiction_pressure = self._signal_from_contradiction(inputs)

        weights = {
            "uncertainty": 0.24,
            "failure": 0.21,
            "knowledge_absence": 0.23,
            "improvement_blockage": 0.19,
            "contradiction": 0.13,
        }

        knowledge_gap_index = self._bounded(
            weights["uncertainty"] * uncertainty_pressure
            + weights["failure"] * failure_pressure
            + weights["knowledge_absence"] * knowledge_absence_pressure
            + weights["improvement_blockage"] * improvement_blockage_pressure
            + weights["contradiction"] * contradiction_pressure
        )

        dominant_signal = max(
            {
                "uncertainty": uncertainty_pressure,
                "failure": failure_pressure,
                "knowledge_absence": knowledge_absence_pressure,
                "improvement_blockage": improvement_blockage_pressure,
                "contradiction": contradiction_pressure,
            }.items(),
            key=lambda item: item[1],
        )[0]

        external_assistance_candidate = bool(
            knowledge_gap_index >= 0.45
            or uncertainty_pressure >= 0.75
            or failure_pressure >= 0.70
            or knowledge_absence_pressure >= 0.70
            or improvement_blockage_pressure >= 0.70
            or contradiction_pressure >= 0.75
        )

        severity = (
            "high" if knowledge_gap_index >= 0.70
            else "moderate" if knowledge_gap_index >= 0.45
            else "low"
        )

        recommended_action = (
            "prepare_external_assistance_request"
            if external_assistance_candidate
            else "continue_internal_resolution"
        )

        result = {
            "primitive": PRIMITIVE,
            "timestamp_utc": self._utc_now(),
            "knowledge_gap_index": knowledge_gap_index,
            "uncertainty_pressure": uncertainty_pressure,
            "failure_pressure": failure_pressure,
            "knowledge_absence_pressure": knowledge_absence_pressure,
            "improvement_blockage_pressure": improvement_blockage_pressure,
            "contradiction_pressure": contradiction_pressure,
            "dominant_gap_signal": dominant_signal,
            "gap_severity": severity,
            "external_assistance_candidate": external_assistance_candidate,
            "recommended_action": recommended_action,
            "diagnostics": {
                "weights": weights,
                "input_keys": sorted(inputs.keys()),
                "specialization": "external_cognitive_collaboration_gap_detection",
                "non_redundancy": (
                    "Detects operational external-assistance gaps rather than "
                    "missing ontology modules."
                ),
            },
        }

        self._append_jsonl(self.history_file, result)
        return result

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        if isinstance(inputs, dict):
            merged.update(inputs)
        merged.update(kwargs)
        return self.detect(merged)


if __name__ == "__main__":
    detector = CognitiveGapDetector()
    print(json.dumps(detector.step({
        "uncertainty_score": 0.82,
        "recent_failures": 3,
        "recent_attempts": 4,
        "missing_knowledge": ["external response validation"],
        "improvement_stalled": True,
    }), ensure_ascii=False, indent=2))
