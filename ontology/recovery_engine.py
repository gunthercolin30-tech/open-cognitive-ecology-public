"""
AV6 — recovery_engine.

Quantify functional recovery after sustained degeneration. The engine
separates transient rebound, partial recovery, baseline restoration and
viable reconstruction in a new regime. All conclusions remain functional.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

ROOT = Path.home() / "open-cognitive-ecology"


class RecoveryEngine:
    primitive = "RECOVERY_ENGINE"
    step_id = "AV6"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV6_recovery_engine"
    dimensions = [
        "stability", "integration", "continuity", "governance",
        "complexity", "diversity", "recovery_capacity", "openness",
    ]

    DEFAULTS: Dict[str, float] = {
        "minimum_observations": 5.0,
        "minimum_data_quality": 0.50,
        "baseline_window": 2.0,
        "current_window": 2.0,
        "minimum_loss": 0.10,
        "partial_recovery_threshold": 0.35,
        "complete_recovery_threshold": 0.80,
        "baseline_tolerance": 0.08,
        "persistence_threshold": 0.66,
        "new_regime_viability_threshold": 0.60,
        "transient_drop_threshold": 0.15,
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

    def _regime(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        return {d: self._mean(item[d] for item in records) for d in self.dimensions}

    def _explicit_baseline(self, inputs: Dict[str, Any]) -> Optional[Dict[str, float]]:
        raw = inputs.get("baseline")
        if isinstance(raw, dict):
            normalized = self._normalize_observation(raw, -1)
            return {d: normalized[d] for d in self.dimensions}
        if isinstance(raw, list) and raw:
            records = [self._normalize_observation(item, i) for i, item in enumerate(raw)]
            return self._regime(records)
        degeneration = inputs.get("degeneration_result")
        if isinstance(degeneration, dict) and isinstance(degeneration.get("baseline_regime"), dict):
            base = degeneration["baseline_regime"]
            return {d: self._clip(base.get(d, 0.0)) for d in self.dimensions}
        return None

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied = inputs.get("config")
        if isinstance(supplied, dict):
            for key in config:
                if key in supplied:
                    config[key] = float(supplied[key])

        observations = self._collect_observations(inputs)
        minimum_observations = max(4, int(config["minimum_observations"]))
        baseline_window = max(1, int(config["baseline_window"]))
        current_window = max(1, int(config["current_window"]))
        order_valid = self._time_order_valid(observations)
        quality = self._mean(item["data_quality"] for item in observations)

        explicit_baseline = self._explicit_baseline(inputs)
        baseline_regime = explicit_baseline or self._regime(observations[:baseline_window])
        current_slice = observations[-current_window:]
        current_regime = self._regime(current_slice)

        trough_index = None
        if observations:
            search_start = min(len(observations) - 1, baseline_window)
            candidates = observations[search_start:] or observations
            trough = min(candidates, key=lambda item: item["composite"])
            trough_index = int(trough["index"])
        trough_record = observations[trough_index] if trough_index is not None and 0 <= trough_index < len(observations) else None
        trough_regime = {d: (trough_record[d] if trough_record else 0.0) for d in self.dimensions}

        losses = {d: max(0.0, baseline_regime.get(d, 0.0) - trough_regime[d]) for d in self.dimensions}
        affected_dimensions = sorted(d for d, loss in losses.items() if loss >= config["minimum_loss"])
        restoration_by_dimension: Dict[str, float] = {}
        for d in self.dimensions:
            loss = losses[d]
            if loss >= config["minimum_loss"]:
                restoration_by_dimension[d] = self._clip((current_regime[d] - trough_regime[d]) / loss)
            else:
                restoration_by_dimension[d] = 1.0 if current_regime[d] >= baseline_regime.get(d, 0.0) - config["baseline_tolerance"] else 0.0

        recovery_score = self._mean(restoration_by_dimension[d] for d in affected_dimensions) if affected_dimensions else 0.0
        baseline_distance = self._mean(abs(current_regime[d] - baseline_regime.get(d, 0.0)) for d in self.dimensions)
        # Continuous restoration is the fraction of the degeneration loss that has
        # been recovered. Proximity to the original baseline remains a separate
        # criterion for complete restoration.
        baseline_restoration = self._clip(recovery_score)
        baseline_restored = (
            bool(affected_dimensions)
            and recovery_score >= config["complete_recovery_threshold"]
            and baseline_distance <= config["baseline_tolerance"]
        )

        post_trough = observations[trough_index + 1:] if trough_index is not None else []
        recovery_velocity = 0.0
        if trough_record is not None and current_slice:
            recovery_velocity = max(-1.0, min(1.0, (self._mean(item["composite"] for item in current_slice) - trough_record["composite"]) / max(1, len(observations) - trough_index - 1)))

        final_composite = self._mean(current_regime.values())
        trough_composite = self._mean(trough_regime.values())
        target_gain = max(config["minimum_loss"], (self._mean(baseline_regime.values()) - trough_composite) * config["partial_recovery_threshold"])
        persistent_points = sum(1 for item in current_slice if item["composite"] >= trough_composite + target_gain)
        persistence_score = persistent_points / len(current_slice) if current_slice else 0.0

        max_post_composite = max((item["composite"] for item in post_trough), default=trough_composite)
        transient_rebound = (
            max_post_composite - trough_composite >= config["minimum_loss"]
            and max_post_composite - final_composite >= config["transient_drop_threshold"]
        )

        continuity_restoration = restoration_by_dimension.get("continuity", 0.0)
        new_regime_viability = self._mean([
            current_regime.get("stability", 0.0),
            current_regime.get("continuity", 0.0),
            current_regime.get("recovery_capacity", 0.0),
            current_regime.get("openness", 0.0),
        ])
        bifurcation_result = inputs.get("bifurcation_result")
        structural_reorganization_evidence = isinstance(bifurcation_result, dict) and (
            bifurcation_result.get("bifurcation_detected") is True
            or str(bifurcation_result.get("bifurcation_status", "")) in {
                "FUNCTIONAL_BIFURCATION_DETECTED",
                "FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED",
                "FUNCTIONAL_STRUCTURAL_BREAK_DETECTED",
            }
        )
        new_regime_reconstruction = (
            bool(affected_dimensions)
            and not baseline_restored
            and structural_reorganization_evidence
            and recovery_score >= config["partial_recovery_threshold"]
            and new_regime_viability >= config["new_regime_viability_threshold"]
            and persistence_score >= config["persistence_threshold"]
        )

        degeneration_result = inputs.get("degeneration_result")
        explicit_degeneration = isinstance(degeneration_result, dict) and (
            degeneration_result.get("degeneration_detected") is True
            or str(degeneration_result.get("degeneration_status", "")).startswith("FUNCTIONAL_") and "DEGENERATION" in str(degeneration_result.get("degeneration_status", ""))
            or str(degeneration_result.get("degeneration_status", "")) == "FUNCTIONAL_COLLAPSE_DETECTED"
        )
        inferred_degeneration = bool(affected_dimensions)
        degeneration_evidence = explicit_degeneration or inferred_degeneration

        recovery_detected = (
            len(observations) >= minimum_observations
            and order_valid
            and quality >= config["minimum_data_quality"]
            and degeneration_evidence
            and not transient_rebound
            and persistence_score >= config["persistence_threshold"]
            and (recovery_score >= config["partial_recovery_threshold"] or baseline_restored or new_regime_reconstruction)
        )

        if not observations or not order_valid or quality < config["minimum_data_quality"]:
            status = "FUNCTIONAL_RECOVERY_UNDETERMINED"
        elif not degeneration_evidence:
            status = "FUNCTIONAL_RECOVERY_NOT_DETECTED"
        elif transient_rebound:
            status = "FUNCTIONAL_RECOVERY_TRANSIENT"
        elif baseline_restored and recovery_detected:
            status = "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE"
        elif new_regime_reconstruction and recovery_detected:
            status = "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED"
        elif recovery_detected:
            status = "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED"
        elif recovery_score > 0.0:
            status = "FUNCTIONAL_RECOVERY_EMERGING"
        else:
            status = "FUNCTIONAL_RECOVERY_NOT_DETECTED"

        restored_dimensions = sorted(d for d in affected_dimensions if restoration_by_dimension[d] >= config["complete_recovery_threshold"])
        unrestored_dimensions = sorted(d for d in affected_dimensions if d not in restored_dimensions)
        conditions = {
            "longitudinal_data_present": len(observations) >= minimum_observations,
            "explicit_time_order": order_valid,
            "data_quality_sufficient": quality >= config["minimum_data_quality"],
            "degeneration_evidence_present": degeneration_evidence,
            "recovery_persistent": persistence_score >= config["persistence_threshold"],
            "not_transient_rebound": not transient_rebound,
        }
        missing_conditions = sorted(key for key, value in conditions.items() if not value)

        payload = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "recovery_detected": bool(recovery_detected),
            "recovery_status": status,
            "recovery_score": round(self._clip(recovery_score), 6),
            "baseline_restoration": round(baseline_restoration, 6),
            "baseline_restored": bool(baseline_restored),
            "new_regime_reconstruction": bool(new_regime_reconstruction),
            "new_regime_viability": round(self._clip(new_regime_viability), 6),
            "recovery_velocity": round(recovery_velocity, 6),
            "persistence_score": round(self._clip(persistence_score), 6),
            "continuity_restoration": round(self._clip(continuity_restoration), 6),
            "baseline_distance": round(self._clip(baseline_distance), 6),
            "affected_dimensions": affected_dimensions,
            "restored_dimensions": restored_dimensions,
            "unrestored_dimensions": unrestored_dimensions,
            "dimension_restoration": {k: round(v, 6) for k, v in sorted(restoration_by_dimension.items())},
            "baseline_regime": {k: round(v, 6) for k, v in sorted(baseline_regime.items())},
            "trough_regime": {k: round(v, 6) for k, v in sorted(trough_regime.items())},
            "current_regime": {k: round(v, 6) for k, v in sorted(current_regime.items())},
            "trough_index": trough_index,
            "recovery_timestamp": observations[trough_index + 1]["timestamp_utc"] if trough_index is not None and trough_index + 1 < len(observations) else None,
            "recovery_window": {
                "start_index": trough_index,
                "end_index": len(observations) - 1 if observations else None,
            },
            "observation_count": len(observations),
            "data_quality_score": round(self._clip(quality), 6),
            "condition_results": conditions,
            "missing_conditions": missing_conditions,
            "transient_rebound_detected": bool(transient_rebound),
            "audit_trace": [
                "baseline_established",
                "degeneration_trough_located",
                "dimension_restoration_measured",
                "recovery_persistence_checked",
                "baseline_vs_new_regime_classified",
            ],
            "epistemic_scope": "functional_developmental_science_only",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "persist_requested": bool(persist),
            "persisted": False,
            "persistence_path": None,
        }
        hash_payload = dict(payload)
        hash_payload.pop("persist_requested", None)
        hash_payload.pop("persisted", None)
        hash_payload.pop("persistence_path", None)
        payload["recovery_hash"] = self._stable_hash(hash_payload)

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_recovery_engine.json"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            payload["persisted"] = True
            payload["persistence_path"] = str(path)
        return payload


def step(inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
    return RecoveryEngine().step(inputs=inputs, persist=persist)
