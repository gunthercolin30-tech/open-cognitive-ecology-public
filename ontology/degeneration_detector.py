"""
AV5 — degeneration_detector.

Detect sustained multidimensional functional degeneration from ordered
longitudinal evidence. The detector distinguishes transient decline,
progressive degeneration and collapse without phenomenal inference.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

ROOT = Path.home() / "open-cognitive-ecology"


class DegenerationDetector:
    primitive = "DEGENERATION_DETECTOR"
    step_id = "AV5"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV5_degeneration_detector"
    dimensions = [
        "stability",
        "integration",
        "continuity",
        "governance",
        "complexity",
        "diversity",
        "recovery_capacity",
        "openness",
    ]

    DEFAULTS: Dict[str, float] = {
        "minimum_observations": 5.0,
        "minimum_data_quality": 0.50,
        "baseline_window": 2.0,
        "current_window": 2.0,
        "decline_threshold": 0.10,
        "severe_decline_threshold": 0.25,
        "collapse_decline_threshold": 0.45,
        "minimum_affected_dimensions": 3.0,
        "persistence_threshold": 0.66,
        "closure_pressure_threshold": 0.60,
        "recovery_tolerance": 0.08,
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if not math.isfinite(number):
            number = default
        return max(0.0, min(1.0, number))

    def _mean(self, values: Iterable[float], default: float = 0.0) -> float:
        clean = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
        return sum(clean) / len(clean) if clean else default

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _extract(self, raw: Dict[str, Any], aliases: Sequence[str], default: float) -> float:
        for key in aliases:
            if key in raw:
                return self._clip(raw.get(key), default)
        return self._clip(default)

    def _normalize_observation(self, record: Any, index: int) -> Dict[str, Any]:
        raw = dict(record) if isinstance(record, dict) else {}
        vector = raw.get("state_vector")
        if isinstance(vector, dict):
            merged = dict(raw)
            merged.update(vector)
            raw = merged
        fallback = self._extract(raw, ["rf_star_score", "score", "composite", "composite_score"], 0.0)
        aliases = {
            "stability": ["stability", "stability_score"],
            "integration": ["integration", "integration_score"],
            "continuity": ["continuity", "continuity_score", "temporal_continuity"],
            "governance": ["governance", "governance_score", "governance_consistency"],
            "complexity": ["complexity", "complexity_score", "structural_complexity"],
            "diversity": ["diversity", "diversity_score", "cognitive_diversity"],
            "recovery_capacity": ["recovery_capacity", "recovery", "recovery_score"],
            "openness": ["openness", "future_openness", "non_closure", "architectural_non_closure_index"],
        }
        result: Dict[str, Any] = {
            "index": index,
            "timestamp_utc": raw.get("timestamp_utc") or raw.get("timestamp") or f"index:{index:06d}",
            "data_quality": self._extract(raw, ["data_quality", "quality", "quality_score"], 1.0),
            "source": str(raw.get("source", "unspecified")),
            "synthetic": bool(raw.get("synthetic", False)),
        }
        for dimension, keys in aliases.items():
            result[dimension] = self._extract(raw, keys, fallback)
        result["composite"] = self._mean(result[d] for d in self.dimensions)
        return result

    def _collect_observations(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates: Any = inputs.get("observations")
        if not isinstance(candidates, list):
            candidates = inputs.get("longitudinal_records")
        if not isinstance(candidates, list):
            candidates = inputs.get("history")
        if not isinstance(candidates, list):
            candidates = []
        return [self._normalize_observation(item, i) for i, item in enumerate(candidates)]

    def _time_order_valid(self, observations: List[Dict[str, Any]]) -> bool:
        stamps = [str(item["timestamp_utc"]) for item in observations]
        if all(stamp.startswith("index:") for stamp in stamps):
            return True
        return all(left < right for left, right in zip(stamps, stamps[1:]))

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied = inputs.get("config")
        if isinstance(supplied, dict):
            for key in config:
                if key in supplied:
                    config[key] = float(supplied[key])

        observations = self._collect_observations(inputs)
        minimum_observations = max(3, int(config["minimum_observations"]))
        baseline_window = max(1, int(config["baseline_window"]))
        current_window = max(1, int(config["current_window"]))
        order_valid = self._time_order_valid(observations)
        quality = self._mean(item["data_quality"] for item in observations)

        baseline_slice = observations[:baseline_window]
        current_slice = observations[-current_window:]
        baseline_regime = {d: self._mean(item[d] for item in baseline_slice) for d in self.dimensions}
        current_regime = {d: self._mean(item[d] for item in current_slice) for d in self.dimensions}
        declines = {d: max(0.0, baseline_regime[d] - current_regime[d]) for d in self.dimensions}
        affected_dimensions = sorted(d for d, decline in declines.items() if decline >= config["decline_threshold"])
        degeneration_score = self._mean(declines.values())
        decline_velocity = 0.0
        if len(observations) >= 2:
            decline_velocity = max(-1.0, min(1.0, observations[0]["composite"] - observations[-1]["composite"]))

        late_threshold = max(0, len(observations) - current_window)
        persistent_points = 0
        for item in observations[late_threshold:]:
            point_decline = self._mean(max(0.0, baseline_regime[d] - item[d]) for d in self.dimensions)
            if point_decline >= config["decline_threshold"]:
                persistent_points += 1
        persistence_score = persistent_points / len(current_slice) if current_slice else 0.0

        continuity_loss = declines.get("continuity", 0.0)
        diversity_loss = declines.get("diversity", 0.0)
        recovery_deficit = declines.get("recovery_capacity", 0.0)
        openness_loss = declines.get("openness", 0.0)

        specialization_result = inputs.get("specialization_result")
        external_closure = 0.0
        if isinstance(specialization_result, dict):
            external_closure = self._clip(specialization_result.get("closure_pressure", 0.0))
        closure_pressure = self._clip(self._mean([diversity_loss, recovery_deficit, openness_loss, external_closure]))

        regression_result = inputs.get("regression_result")
        external_regression = isinstance(regression_result, dict) and (
            regression_result.get("regression_detected") is True
            or regression_result.get("regression") is True
        )
        recovery_result = inputs.get("recovery_result")
        external_recovery = isinstance(recovery_result, dict) and (
            recovery_result.get("recovery_detected") is True
            or self._clip(recovery_result.get("recovery_score", 0.0)) >= 0.70
        )
        maximum_excursion = 0.0
        for item in observations[baseline_window:]:
            maximum_excursion = max(
                maximum_excursion,
                self._mean(max(0.0, baseline_regime[d] - item[d]) for d in self.dimensions),
            )
        recovered = external_recovery or (
            bool(observations)
            and maximum_excursion >= config["decline_threshold"]
            and self._mean(abs(current_regime[d] - baseline_regime[d]) for d in self.dimensions)
            <= config["recovery_tolerance"]
        )

        conditions = {
            "longitudinal_data_present": len(observations) >= minimum_observations,
            "explicit_time_order": order_valid,
            "data_quality_sufficient": quality >= config["minimum_data_quality"],
            "multidimensional_decline": len(affected_dimensions) >= int(config["minimum_affected_dimensions"]),
            "decline_persistent": persistence_score >= config["persistence_threshold"],
            "not_recovered": not recovered,
        }
        missing_conditions = sorted(key for key, value in conditions.items() if not value)
        evidence_sufficient = all(conditions[key] for key in [
            "longitudinal_data_present",
            "explicit_time_order",
            "data_quality_sufficient",
        ])
        degeneration_detected = evidence_sufficient and all(conditions.values())

        if not observations or not order_valid or quality < config["minimum_data_quality"]:
            status = "FUNCTIONAL_DEGENERATION_UNDETERMINED"
            severity = "UNDETERMINED"
        elif recovered:
            status = "FUNCTIONAL_TRANSIENT_DECLINE_RECOVERED"
            severity = "TRANSIENT"
        elif degeneration_detected and degeneration_score >= config["collapse_decline_threshold"]:
            status = "FUNCTIONAL_COLLAPSE_DETECTED"
            severity = "COLLAPSE"
        elif degeneration_detected and degeneration_score >= config["severe_decline_threshold"]:
            status = "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED"
            severity = "SEVERE"
        elif degeneration_detected:
            status = "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED"
            severity = "MODERATE"
        elif external_regression or affected_dimensions:
            status = "FUNCTIONAL_DECLINE_DETECTED"
            severity = "MILD"
        else:
            status = "FUNCTIONAL_DEGENERATION_NOT_DETECTED"
            severity = "NONE"

        audit_payload = {
            "config": config,
            "observations": observations,
            "baseline_regime": baseline_regime,
            "current_regime": current_regime,
            "declines": declines,
            "conditions": conditions,
            "external_regression": external_regression,
            "external_recovery": external_recovery,
        }
        degeneration_hash = self._stable_hash(audit_payload)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "degeneration_detected": degeneration_detected,
            "degeneration_status": status,
            "degeneration_score": round(degeneration_score, 6),
            "severity": severity,
            "affected_dimensions": affected_dimensions,
            "dimension_declines": {k: round(v, 6) for k, v in declines.items()},
            "decline_velocity": round(decline_velocity, 6),
            "persistence_score": round(persistence_score, 6),
            "continuity_loss": round(continuity_loss, 6),
            "diversity_loss": round(diversity_loss, 6),
            "recovery_deficit": round(recovery_deficit, 6),
            "closure_pressure": round(closure_pressure, 6),
            "baseline_regime": {k: round(v, 6) for k, v in baseline_regime.items()},
            "current_regime": {k: round(v, 6) for k, v in current_regime.items()},
            "observation_count": len(observations),
            "data_quality_score": round(quality, 6),
            "condition_results": conditions,
            "missing_conditions": missing_conditions,
            "degeneration_hash": degeneration_hash,
            "audit_trace": audit_payload,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            latest = self.output_dir / "latest_degeneration_detection.json"
            latest.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            stamped = self.output_dir / f"degeneration_detection_{self._timestamp().replace(':', '').replace('-', '')}.json"
            stamped.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["output_path"] = str(latest)
        return result


def step(inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
    return DegenerationDetector().step(inputs=inputs, persist=persist)
