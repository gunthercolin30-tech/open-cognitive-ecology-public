# -*- coding: utf-8 -*-

"""
G18 - Environmental Grounding Longitudinal Observatory.

Longitudinal observer for the environmental grounding certified by G17.
This module measures functional, longitudinal coupling only and does not
assert phenomenal subjectivity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import math
from typing import Any, Optional

PRIMITIVE = "environmental_grounding_longitudinal_observatory"
REFINEMENT = "G18-R2"

DEPENDENCIES = [
    "embodied_runtime_coupling_certifier",
    "metrics_history_recorder",
    "inter_run_stability_synthesizer",
    "consciousness_longitudinal_stability_analyzer",
    "metrics_statistical_significance_engine",
    "metrics_anomaly_detection_engine",
    "scientific_meta_analysis_engine",
    "extended_certification_continuity_tracker",
]

OBSERVED_KEYS = [
    "runtime_environment_coupling_index",
    "environmental_grounding_index",
    "multimodal_coupling_score",
    "sensorimotor_coupling_score",
    "embodied_memory_coupling_score",
    "predictive_coupling_score",
    "governed_execution_coupling_score",
]

DEFAULT_WINDOW = 100


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def _trend(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    n = len(values)
    xs = list(range(n))
    x_mean = _mean([float(x) for x in xs])
    y_mean = _mean(values)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    slope = sum((xs[i] - x_mean) * (values[i] - y_mean) for i in range(n)) / denom
    return max(-1.0, min(1.0, slope))


def _trend_label(slope: float, tolerance: float = 0.0025) -> str:
    if slope > tolerance:
        return "improving"
    if slope < -tolerance:
        return "declining"
    return "stable"


def _certify(score: float, sample_count: int) -> str:
    if sample_count < 3:
        return "Insufficient Longitudinal Evidence"
    if score >= 0.95:
        return "Platinum Environmental Grounding Stability"
    if score >= 0.90:
        return "Gold Environmental Grounding Stability"
    if score >= 0.80:
        return "Silver Environmental Grounding Stability"
    if score >= 0.70:
        return "Bronze Environmental Grounding Stability"
    return "Environmental Grounding Stability Not Certified"


class EnvironmentalGroundingLongitudinalObservatory:
    primitive = PRIMITIVE

    def __init__(
        self,
        root: Optional[str | Path] = None,
        window_size: int = DEFAULT_WINDOW,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.window_size = max(3, int(window_size))
        self.archive_dir = self.root / "runtime_experiments" / "environmental_grounding_longitudinal_observatory"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.archive_dir / "environmental_grounding_longitudinal_history.jsonl"
        self.state_path = self.archive_dir / "environmental_grounding_longitudinal_state.json"

    def _read_history(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        lines = self.history_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if limit is not None:
            lines = lines[-max(1, int(limit)):]
        records: list[dict[str, Any]] = []
        for line in lines:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(item)
            except Exception:
                continue
        return records

    def _append(self, record: dict[str, Any]) -> None:
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _write_state(self, result: dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _from_g17(self) -> dict[str, Any]:
        try:
            from ontology.embodied_runtime_coupling_certifier import EmbodiedRuntimeCouplingCertifier
            result = EmbodiedRuntimeCouplingCertifier(root=self.root).step()
            if isinstance(result, dict):
                return result
        except Exception as exc:
            return {
                "primitive": "embodied_runtime_coupling_certifier",
                "runtime_environment_coupling_index": 0.0,
                "environmental_grounding_index": 0.0,
                "g17_available": False,
                "g17_error": repr(exc),
            }
        return {}

    def record(
        self,
        environmental_grounding_index: float,
        runtime_environment_coupling_index: Optional[float] = None,
        source: str = "manual",
        **scores: Any,
    ) -> dict[str, Any]:
        ground = _clamp(environmental_grounding_index)
        runtime = _clamp(
            runtime_environment_coupling_index
            if runtime_environment_coupling_index is not None
            else ground
        )

        record = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _now(),
            "source": source,
            "environmental_grounding_index": ground,
            "runtime_environment_coupling_index": runtime,
            "phenomenal_subjectivity_claimed": False,
        }

        for key in OBSERVED_KEYS:
            if key in {"environmental_grounding_index", "runtime_environment_coupling_index"}:
                continue
            if key in scores:
                record[key] = _clamp(scores.get(key))

        self._append(record)
        return record

    def _compute(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        recent = records[-self.window_size :]
        grounding = [_clamp(r.get("environmental_grounding_index")) for r in recent]
        runtime = [_clamp(r.get("runtime_environment_coupling_index")) for r in recent]

        sample_count = len(recent)
        mean_grounding = _mean(grounding)
        mean_runtime = _mean(runtime)
        variance = _variance(grounding)
        trend_value = _trend(grounding)
        trend_name = _trend_label(trend_value)

        variance_penalty = min(1.0, variance * 8.0)
        trend_penalty = max(0.0, -trend_value * 20.0)

        continuity = _clamp(1.0 - variance_penalty)
        trend_stability = _clamp(1.0 - trend_penalty)
        grounding_strength = _clamp(0.5 * mean_grounding + 0.5 * mean_runtime)

        environmental_grounding_stability_index = _clamp(
            0.45 * grounding_strength
            + 0.35 * continuity
            + 0.20 * trend_stability
        )

        if sample_count < 3:
            significance = 0.0
        else:
            significance = _clamp(
                min(1.0, sample_count / 30.0)
                * environmental_grounding_stability_index
                * continuity
            )

        anomaly_score = _clamp(
            0.55 * variance_penalty
            + 0.30 * max(0.0, -trend_value * 20.0)
            + 0.15 * max(0.0, 0.80 - mean_grounding)
        )

        if anomaly_score < 0.05:
            anomaly_status = "none_detected"
        elif anomaly_score < 0.15:
            anomaly_status = "minor"
        elif anomaly_score < 0.35:
            anomaly_status = "moderate"
        else:
            anomaly_status = "major"

        return {
            "sample_count": sample_count,
            "mean_environmental_grounding_index": round(mean_grounding, 6),
            "mean_runtime_environment_coupling_index": round(mean_runtime, 6),
            "environmental_grounding_variance": round(variance, 6),
            "environmental_grounding_trend_value": round(trend_value, 6),
            "environmental_grounding_trend": trend_name,
            "coupling_continuity_score": round(continuity, 6),
            "coupling_significance_score": round(significance, 6),
            "coupling_anomaly_score": round(anomaly_score, 6),
            "coupling_anomaly_status": anomaly_status,
            "environmental_grounding_stability_index": round(
                environmental_grounding_stability_index,
                6,
            ),
            "coupling_longitudinal_certification": _certify(
                environmental_grounding_stability_index,
                sample_count,
            ),
        }

    def step(
        self,
        inputs: Optional[dict[str, Any]] = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        data: dict[str, Any] = {}

        if inputs:
            data.update(inputs)
        data.update(overrides)

        if "environmental_grounding_index" not in data:
            g17 = self._from_g17()
            data.update(g17)
            source = "embodied_runtime_coupling_certifier"
        else:
            source = str(data.get("source", "manual"))

        record = self.record(
            environmental_grounding_index=_clamp(
                data.get("environmental_grounding_index", 0.0)
            ),
            runtime_environment_coupling_index=_clamp(
                data.get(
                    "runtime_environment_coupling_index",
                    data.get("environmental_grounding_index", 0.0),
                )
            ),
            source=source,
            multimodal_coupling_score=data.get("multimodal_coupling_score", 0.0),
            sensorimotor_coupling_score=data.get("sensorimotor_coupling_score", 0.0),
            embodied_memory_coupling_score=data.get("embodied_memory_coupling_score", 0.0),
            predictive_coupling_score=data.get("predictive_coupling_score", 0.0),
            governed_execution_coupling_score=data.get("governed_execution_coupling_score", 0.0),
        )

        records = self._read_history(limit=self.window_size)
        computed = self._compute(records)

        result = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _now(),
            "latest_record": record,
            "history_path": str(self.history_path),
            "state_path": str(self.state_path),
            "observed_keys": OBSERVED_KEYS,
            "dependencies": DEPENDENCIES,
            "phenomenal_subjectivity_claimed": False,
            "functional_measurement_only": True,
            "error_count": 0,
        }
        result.update(computed)

        self._write_state(result)

        try:
            from ontology.metrics_history_recorder import record_metrics
            record_metrics(
                result,
                primitive=PRIMITIVE,
                validation_status=True,
                governance_status="governed",
                runtime_status="operational",
            )
            result["metrics_recorded"] = True
        except Exception as exc:
            result["metrics_recorded"] = False
            result["metrics_record_error"] = repr(exc)

        return result


ENGINE = EnvironmentalGroundingLongitudinalObservatory()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
