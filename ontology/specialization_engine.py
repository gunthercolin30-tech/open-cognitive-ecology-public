"""AV3 — specialization_engine.

Quantify post-maturation functional specialization from ordered longitudinal
profiles. All conclusions are functional, quantitative, auditable and falsifiable.
"""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"

class SpecializationEngine:
    primitive = "SPECIALIZATION_ENGINE"
    step_id = "AV3"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV3_specialization_engine"
    DEFAULTS = {
        "minimum_observations": 5.0,
        "minimum_data_quality": 0.50,
        "emerging_threshold": 0.35,
        "stable_threshold": 0.55,
        "strong_threshold": 0.72,
        "persistence_threshold": 0.70,
        "closure_risk_threshold": 0.65,
        "low_diversity_threshold": 0.40,
        "high_cost_threshold": 0.70,
        "low_reversibility_threshold": 0.35,
        "recent_window": 3.0,
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

    def _maturation_confirmed(self, inputs: Dict[str, Any]) -> Tuple[bool, str]:
        result = inputs.get("maturation_result")
        if isinstance(result, dict):
            status = str(result.get("maturation_status", ""))
            complete = result.get("maturation_complete") is True
            return complete or status == "FUNCTIONAL_MATURATION_COMPLETE", "maturation_result"
        direct = inputs.get("maturation_complete") is True
        return direct, "direct_flag" if direct else "missing_or_negative"

    def _normalize_observation(self, raw_value: Any, index: int) -> Dict[str, Any]:
        raw = dict(raw_value) if isinstance(raw_value, dict) else {}
        profile = raw.get("functional_profile") or raw.get("profile") or raw.get("dimensions") or {}
        profile = {str(k): self._clip(v) for k, v in profile.items()} if isinstance(profile, dict) else {}
        total = sum(profile.values())
        shares = {k: (v / total if total > 0.0 else 0.0) for k, v in profile.items()}
        ranked = sorted(shares.items(), key=lambda item: (-item[1], item[0]))
        top = ranked[0] if ranked else (None, 0.0)
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        concentration = sum(value * value for value in shares.values()) if shares else 0.0
        dominance = self._clip(0.55 * top[1] + 0.25 * max(0.0, top[1] - second) + 0.20 * concentration)
        return {
            "index": index,
            "timestamp_utc": raw.get("timestamp_utc") or raw.get("timestamp") or f"index:{index:06d}",
            "functional_profile": profile,
            "profile_shares": shares,
            "dominant_dimension": top[0],
            "dominance": dominance,
            "diversity": self._clip(raw.get("diversity", raw.get("diversity_score", 1.0 - concentration))),
            "resource_cost": self._clip(raw.get("resource_cost", raw.get("cost", raw.get("specialization_cost", 0.0)))),
            "reversibility": self._clip(raw.get("reversibility", raw.get("reversibility_score", 1.0))),
            "openness": self._clip(raw.get("openness", raw.get("future_openness", 1.0))),
            "data_quality": self._clip(raw.get("data_quality", raw.get("quality", 1.0))),
            "source": str(raw.get("source", "unspecified")),
            "synthetic": bool(raw.get("synthetic", False)),
        }

    def _collect_observations(self, inputs: Dict[str, Any]):
        candidates = inputs.get("observations")
        if not isinstance(candidates, list):
            candidates = inputs.get("longitudinal_records")
        if not isinstance(candidates, list):
            candidates = inputs.get("history")
        if not isinstance(candidates, list):
            candidates = []
        return [self._normalize_observation(item, index) for index, item in enumerate(candidates)]

    def _time_order_valid(self, observations) -> bool:
        stamps = [str(item["timestamp_utc"]) for item in observations]
        if all(stamp.startswith("index:") for stamp in stamps):
            return True
        return all(left < right for left, right in zip(stamps, stamps[1:]))

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        if isinstance(inputs.get("config"), dict):
            for key in config:
                if key in inputs["config"]:
                    config[key] = float(inputs["config"][key])

        observations = self._collect_observations(inputs)
        maturation_confirmed, maturation_source = self._maturation_confirmed(inputs)
        order_valid = self._time_order_valid(observations)
        minimum = max(3, int(config["minimum_observations"]))
        recent_window = max(2, int(config["recent_window"]))
        recent = observations[-recent_window:]
        quality = self._mean(item["data_quality"] for item in observations)

        counts: Dict[str, int] = {}
        for item in observations:
            name = item["dominant_dimension"]
            if name:
                counts[name] = counts.get(name, 0) + 1
        dominant = max(counts, key=lambda key: (counts[key], key)) if counts else None
        raw_persistence = counts.get(dominant, 0) / len(observations) if dominant and observations else 0.0
        dominance = self._mean(item["dominance"] for item in recent)
        persistence = self._clip(raw_persistence * dominance)
        diversity = self._mean(item["diversity"] for item in recent)
        cost = self._mean(item["resource_cost"] for item in recent)
        reversibility = self._mean(item["reversibility"] for item in recent)
        openness = self._mean(item["openness"] for item in recent)

        specialization_strength = self._clip(0.45 * dominance + 0.30 * persistence + 0.25 * (1.0 - diversity))
        closure_pressure = self._clip(
            0.30 * specialization_strength
            + 0.25 * (1.0 - diversity)
            + 0.20 * (1.0 - reversibility)
            + 0.15 * cost
            + 0.10 * (1.0 - openness)
        )

        profile_values: Dict[str, list] = {}
        for item in recent:
            for key, value in item["profile_shares"].items():
                profile_values.setdefault(key, []).append(value)
        specialization_profile = {key: self._mean(values) for key, values in sorted(profile_values.items())}

        conditions = {
            "maturation_confirmed": maturation_confirmed,
            "longitudinal_data_present": len(observations) >= minimum,
            "explicit_time_order": order_valid,
            "data_quality_sufficient": quality >= config["minimum_data_quality"],
            "functional_profiles_present": all(bool(item["functional_profile"]) for item in observations) if observations else False,
            "specialization_persistent": persistence >= config["persistence_threshold"],
        }
        evidence_sufficient = all(conditions[key] for key in [
            "maturation_confirmed", "longitudinal_data_present", "explicit_time_order",
            "data_quality_sufficient", "functional_profiles_present",
        ])

        if not observations or not order_valid or quality < config["minimum_data_quality"]:
            status = "FUNCTIONAL_SPECIALIZATION_UNDETERMINED"
        elif not maturation_confirmed:
            status = "FUNCTIONAL_SPECIALIZATION_NOT_ESTABLISHED"
        elif closure_pressure >= config["closure_risk_threshold"]:
            status = "FUNCTIONAL_SPECIALIZATION_CLOSURE_RISK"
        elif specialization_strength >= config["strong_threshold"] and persistence >= config["persistence_threshold"]:
            status = "FUNCTIONAL_SPECIALIZATION_STRONG"
        elif specialization_strength >= config["stable_threshold"] and persistence >= config["persistence_threshold"]:
            status = "FUNCTIONAL_SPECIALIZATION_STABLE"
        elif specialization_strength >= config["emerging_threshold"]:
            status = "FUNCTIONAL_SPECIALIZATION_EMERGING"
        else:
            status = "FUNCTIONAL_SPECIALIZATION_ABSENT"
        if not evidence_sufficient and status not in {
            "FUNCTIONAL_SPECIALIZATION_UNDETERMINED", "FUNCTIONAL_SPECIALIZATION_NOT_ESTABLISHED"
        }:
            status = "FUNCTIONAL_SPECIALIZATION_UNDETERMINED"

        payload = {
            "config": config,
            "observations": observations,
            "maturation_confirmed": maturation_confirmed,
            "specialization_profile": specialization_profile,
            "dominance_score": dominance,
            "persistence_score": persistence,
            "diversity_score": diversity,
            "specialization_cost": cost,
            "reversibility_score": reversibility,
            "openness_score": openness,
            "specialization_strength": specialization_strength,
            "closure_pressure": closure_pressure,
            "conditions": conditions,
            "specialization_status": status,
        }
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "specialization_status": status,
            "specialization_profile": specialization_profile,
            "specialization_strength": specialization_strength,
            "closure_pressure": closure_pressure,
            "specialization_hash": self._stable_hash(payload),
            "dominant_dimensions": [dominant] if dominant else [],
            "dominance_score": dominance,
            "persistence_score": persistence,
            "diversity_score": diversity,
            "specialization_cost": cost,
            "reversibility_score": reversibility,
            "openness_score": openness,
            "loss_of_diversity_detected": diversity < config["low_diversity_threshold"],
            "irreversible_specialization_detected": reversibility < config["low_reversibility_threshold"] and specialization_strength >= config["stable_threshold"],
            "high_cost_detected": cost >= config["high_cost_threshold"],
            "observation_count": len(observations),
            "data_quality_score": quality,
            "maturation_confirmed": maturation_confirmed,
            "maturation_source": maturation_source,
            "condition_results": conditions,
            "missing_conditions": sorted(key for key, value in conditions.items() if not value),
            "audit_trace": payload,
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
            path = self.output_dir / "latest_specialization_analysis.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
