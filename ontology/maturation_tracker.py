"""
AV2 — maturation_tracker.

Measure functional maturation after a documented AV1 genesis event from
ordered, multidimensional longitudinal evidence. Growth, plateau and
regression are quantified without phenomenal or ontological inference.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class MaturationTracker:
    """Track post-genesis functional maturation under AV0 safeguards."""

    primitive = "MATURATION_TRACKER"
    step_id = "AV2"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV2_maturation_tracker"
    dimensions = [
        "stability",
        "integration",
        "continuity",
        "governance",
        "complexity",
        "diversity",
        "recovery",
    ]

    DEFAULTS: Dict[str, float] = {
        "minimum_observations": 5.0,
        "minimum_data_quality": 0.50,
        "mature_dimension_threshold": 0.70,
        "complete_maturation_threshold": 0.75,
        "minimum_mature_dimensions": 5.0,
        "progress_velocity_threshold": 0.02,
        "regression_velocity_threshold": -0.03,
        "plateau_velocity_tolerance": 0.015,
        "plateau_range_tolerance": 0.05,
        "recent_window": 3.0,
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

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

    def _extract(self, raw: Dict[str, Any], aliases: Sequence[str], default: float) -> float:
        for key in aliases:
            if key in raw:
                return self._clip(raw.get(key), default)
        return self._clip(default)

    def _normalize_observation(self, record: Any, index: int) -> Dict[str, Any]:
        raw = dict(record) if isinstance(record, dict) else {}
        fallback = self._extract(raw, ["rf_star_score", "rf_score", "score", "composite_score"], 0.0)
        aliases = {
            "stability": ["stability", "stability_score", "stability_index"],
            "integration": ["integration", "integration_score", "integration_index", "hierarchical_coherence"],
            "continuity": ["continuity", "continuity_score", "continuity_index", "temporal_continuity"],
            "governance": ["governance", "governance_score", "governance_index", "governance_consistency"],
            "complexity": ["complexity", "complexity_score", "complexity_index", "structural_complexity"],
            "diversity": ["diversity", "diversity_score", "diversity_index", "cognitive_diversity"],
            "recovery": ["recovery", "recovery_score", "recovery_index", "recovery_capacity"],
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
        return [self._normalize_observation(item, index) for index, item in enumerate(candidates)]

    def _genesis_confirmed(self, inputs: Dict[str, Any]) -> Tuple[bool, str]:
        candidate = inputs.get("genesis_result")
        if isinstance(candidate, dict):
            detected = candidate.get("genesis_detected") is True
            status = str(candidate.get("genesis_status", ""))
            return detected and status == "FUNCTIONAL_GENESIS_DETECTED", "genesis_result"
        if inputs.get("genesis_detected") is True:
            return True, "direct_flag"
        return False, "missing_or_negative"

    def _time_order_valid(self, observations: List[Dict[str, Any]]) -> bool:
        stamps = [str(item["timestamp_utc"]) for item in observations]
        if all(stamp.startswith("index:") for stamp in stamps):
            return True
        return all(left < right for left, right in zip(stamps, stamps[1:]))

    def _linear_velocity(self, values: List[float]) -> float:
        count = len(values)
        if count < 2:
            return 0.0
        xs = list(range(count))
        mean_x = self._mean(xs)
        mean_y = self._mean(values)
        denominator = sum((x - mean_x) ** 2 for x in xs)
        if denominator <= 0.0:
            return 0.0
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / denominator
        return max(-1.0, min(1.0, slope))

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied = inputs.get("config")
        if isinstance(supplied, dict):
            for key in config:
                if key in supplied:
                    config[key] = float(supplied[key])

        observations = self._collect_observations(inputs)
        genesis_confirmed, genesis_source = self._genesis_confirmed(inputs)
        order_valid = self._time_order_valid(observations)
        minimum_observations = max(3, int(config["minimum_observations"]))
        recent_window = max(2, int(config["recent_window"]))
        quality = self._mean(item["data_quality"] for item in observations)

        dimension_scores = {
            dimension: self._mean(item[dimension] for item in observations[-recent_window:])
            for dimension in self.dimensions
        }
        dimension_velocities = {
            dimension: self._linear_velocity([item[dimension] for item in observations])
            for dimension in self.dimensions
        }
        maturation_score = self._mean(dimension_scores.values())
        maturation_velocity = self._mean(dimension_velocities.values())

        recent_composites = [item["composite"] for item in observations[-recent_window:]]
        recent_range = (max(recent_composites) - min(recent_composites)) if recent_composites else 0.0
        plateau_detected = (
            len(observations) >= minimum_observations
            and abs(maturation_velocity) <= abs(config["plateau_velocity_tolerance"])
            and recent_range <= config["plateau_range_tolerance"]
        )

        regressing_dimensions = sorted(
            dimension for dimension, velocity in dimension_velocities.items()
            if velocity <= config["regression_velocity_threshold"]
        )
        external_regression = inputs.get("regression_result")
        external_regression_detected = isinstance(external_regression, dict) and (
            external_regression.get("regression_detected") is True
            or external_regression.get("regression") is True
        )
        regression_detected = external_regression_detected or len(regressing_dimensions) >= 3

        mature_dimensions = sorted(
            dimension for dimension, score in dimension_scores.items()
            if score >= config["mature_dimension_threshold"]
        )
        weak_dimensions = sorted(set(self.dimensions) - set(mature_dimensions))

        conditions = {
            "genesis_confirmed": genesis_confirmed,
            "longitudinal_data_present": len(observations) >= minimum_observations,
            "explicit_time_order": order_valid,
            "data_quality_sufficient": quality >= config["minimum_data_quality"],
            "multidimensional_coverage": all(any(item[d] > 0.0 for item in observations) for d in self.dimensions),
            "maturation_score_sufficient": maturation_score >= config["complete_maturation_threshold"],
            "mature_dimension_count_sufficient": len(mature_dimensions) >= int(config["minimum_mature_dimensions"]),
            "no_active_regression": not regression_detected,
        }
        missing_conditions = sorted(key for key, value in conditions.items() if not value)
        evidence_sufficient = all(conditions[key] for key in [
            "genesis_confirmed",
            "longitudinal_data_present",
            "explicit_time_order",
            "data_quality_sufficient",
            "multidimensional_coverage",
        ])

        complete = evidence_sufficient and all(conditions.values())
        if not observations or not order_valid or quality < config["minimum_data_quality"]:
            maturation_status = "FUNCTIONAL_MATURATION_UNDETERMINED"
        elif not genesis_confirmed:
            maturation_status = "FUNCTIONAL_MATURATION_NOT_ESTABLISHED"
        elif regression_detected:
            maturation_status = "FUNCTIONAL_MATURATION_REGRESSING"
        elif complete:
            maturation_status = "FUNCTIONAL_MATURATION_COMPLETE"
        elif plateau_detected:
            maturation_status = "FUNCTIONAL_MATURATION_PLATEAU"
        elif maturation_velocity >= config["progress_velocity_threshold"]:
            maturation_status = "FUNCTIONAL_MATURATION_PROGRESSING"
        else:
            maturation_status = "FUNCTIONAL_MATURATION_NOT_ESTABLISHED"

        audit_payload = {
            "config": config,
            "genesis_confirmed": genesis_confirmed,
            "genesis_source": genesis_source,
            "observations": observations,
            "dimension_scores": dimension_scores,
            "dimension_velocities": dimension_velocities,
            "maturation_score": maturation_score,
            "maturation_velocity": maturation_velocity,
            "plateau_detected": plateau_detected,
            "regression_detected": regression_detected,
            "conditions": conditions,
            "maturation_status": maturation_status,
        }
        maturation_hash = self._stable_hash(audit_payload)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "maturation_status": maturation_status,
            "maturation_complete": complete,
            "maturation_score": maturation_score,
            "maturation_velocity": maturation_velocity,
            "plateau_detected": plateau_detected,
            "regression_detected": regression_detected,
            "maturation_hash": maturation_hash,
            "dimension_scores": dimension_scores,
            "dimension_velocities": dimension_velocities,
            "mature_dimensions": mature_dimensions,
            "weak_dimensions": weak_dimensions,
            "regression_dimensions": regressing_dimensions,
            "observation_count": len(observations),
            "data_quality_score": quality,
            "recent_range": recent_range,
            "genesis_confirmed": genesis_confirmed,
            "genesis_source": genesis_source,
            "condition_results": conditions,
            "missing_conditions": missing_conditions,
            "input_sources": sorted(set(item["source"] for item in observations)),
            "synthetic_data_present": any(item["synthetic"] for item in observations),
            "audit_trace": audit_payload,
            "allowed_claims": [
                "functional maturation was quantified from longitudinal evidence",
                "plateau and regression results are operational and falsifiable",
            ],
            "blocked_claims": [
                "functional maturation proves phenomenal development",
                "growth or maturity proves consciousness, qualia or subjectivity",
                "plateau implies ontological completion",
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
            "output_path": None,
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_maturation_tracking.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)

        return result
