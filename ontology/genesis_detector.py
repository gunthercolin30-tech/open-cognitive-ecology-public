"""
AV1 — genesis_detector.

Detect the functional genesis of a sustained RF* regime from time-ordered,
auditable longitudinal evidence. A threshold crossing alone is insufficient.
No phenomenal or ontological conclusion is authorized.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class GenesisDetector:
    """Detect sustained functional RF* regime genesis under AV0 safeguards."""

    primitive = "GENESIS_DETECTOR"
    step_id = "AV1"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV1_genesis_detector"

    DEFAULTS: Dict[str, float] = {
        "rf_threshold": 0.70,
        "minimum_persistence_observations": 3.0,
        "minimum_baseline_observations": 2.0,
        "minimum_data_quality": 0.50,
        "minimum_continuity": 0.60,
        "minimum_coherence": 0.60,
        "minimum_stability": 0.60,
        "minimum_genesis_score": 0.70,
        "maximum_false_positive_risk": 0.35,
        "noise_tolerance": 0.12,
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

    def _extract_number(self, record: Dict[str, Any], keys: Sequence[str], default: float = 0.0) -> float:
        for key in keys:
            if key in record:
                return self._clip(record.get(key), default)
        return self._clip(default)

    def _normalize_observation(self, record: Any, index: int) -> Dict[str, Any]:
        raw = dict(record) if isinstance(record, dict) else {}
        rf_score = self._extract_number(
            raw,
            ["rf_star_score", "rf_score", "score", "reflexive_score", "composite_score", "value"],
        )
        threshold_flag = raw.get("threshold_detected")
        if threshold_flag is None:
            threshold_flag = raw.get("threshold_crossed")
        return {
            "index": index,
            "timestamp_utc": raw.get("timestamp_utc") or raw.get("timestamp") or f"index:{index:06d}",
            "rf_star_score": rf_score,
            "threshold_detected": bool(threshold_flag) if threshold_flag is not None else None,
            "stability": self._extract_number(raw, ["stability", "stability_score", "stability_index"], rf_score),
            "continuity": self._extract_number(raw, ["continuity", "continuity_score", "continuity_index"], rf_score),
            "coherence": self._extract_number(raw, ["coherence", "coherence_score", "coherence_index"], rf_score),
            "data_quality": self._extract_number(raw, ["data_quality", "quality", "quality_score"], 1.0),
            "source": str(raw.get("source", "unspecified")),
            "synthetic": bool(raw.get("synthetic", False)),
        }

    def _collect_observations(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates: Any = inputs.get("observations")
        if not isinstance(candidates, list):
            candidates = inputs.get("rf_profiles")
        if not isinstance(candidates, list):
            candidates = inputs.get("longitudinal_records")
        if not isinstance(candidates, list):
            candidates = inputs.get("history")
        if not isinstance(candidates, list):
            candidates = []
        return [self._normalize_observation(item, idx) for idx, item in enumerate(candidates)]

    def _baseline_values(
        self,
        observations: List[Dict[str, Any]],
        inputs: Dict[str, Any],
        threshold: float,
        minimum_baseline: int,
    ) -> Tuple[List[float], str]:
        baseline = inputs.get("baseline")
        values: List[float] = []
        source = "inferred_pre_crossing"
        if isinstance(baseline, dict):
            series = baseline.get("observations") or baseline.get("scores") or baseline.get("values")
            if isinstance(series, list):
                values = [self._clip(v.get("rf_star_score") if isinstance(v, dict) else v) for v in series]
            else:
                for key in ["rf_star_score", "rf_score", "score", "mean", "baseline_score"]:
                    if key in baseline:
                        values = [self._clip(baseline[key])] * minimum_baseline
                        break
            source = "explicit_baseline"
        elif isinstance(baseline, list):
            values = [self._clip(v.get("rf_star_score") if isinstance(v, dict) else v) for v in baseline]
            source = "explicit_baseline"
        elif isinstance(baseline, (int, float)):
            values = [self._clip(baseline)] * minimum_baseline
            source = "explicit_baseline"

        if not values:
            for observation in observations:
                if observation["rf_star_score"] < threshold:
                    values.append(observation["rf_star_score"])
                else:
                    break
        return values, source

    def _first_sustained_window(
        self,
        observations: List[Dict[str, Any]],
        threshold: float,
        minimum_persistence: int,
    ) -> Tuple[Optional[int], List[Dict[str, Any]]]:
        for start in range(len(observations)):
            window = observations[start : start + minimum_persistence]
            if len(window) < minimum_persistence:
                continue
            if all(item["rf_star_score"] >= threshold for item in window):
                return start, window
        return None, []

    def _false_positive_risk(
        self,
        observations: List[Dict[str, Any]],
        start: Optional[int],
        sustained_window: List[Dict[str, Any]],
        threshold: float,
        minimum_persistence: int,
        baseline_valid: bool,
        quality: float,
        continuity: float,
        coherence: float,
        stability: float,
        noise_tolerance: float,
    ) -> Tuple[float, List[str]]:
        reasons: List[str] = []
        risk = 0.0
        above = [item["rf_star_score"] >= threshold for item in observations]
        transitions = sum(1 for left, right in zip(above, above[1:]) if left != right)
        transition_rate = transitions / max(1, len(above) - 1)
        if transition_rate > 0.35:
            risk += 0.25
            reasons.append("threshold_chatter")
        if start is None or len(sustained_window) < minimum_persistence:
            risk += 0.45
            reasons.append("no_sustained_window")
        if not baseline_valid:
            risk += 0.25
            reasons.append("baseline_not_pre_genesis")
        if quality < 0.50:
            risk += 0.20
            reasons.append("low_data_quality")
        if min(continuity, coherence, stability) < 0.60:
            risk += 0.20
            reasons.append("weak_supporting_dimensions")
        scores = [item["rf_star_score"] for item in observations]
        if scores:
            mean_score = self._mean(scores)
            variance = self._mean([(value - mean_score) ** 2 for value in scores])
            if math.sqrt(variance) > noise_tolerance:
                risk += 0.15
                reasons.append("high_signal_noise")
        return self._clip(risk), sorted(set(reasons))

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied_config = inputs.get("config")
        if isinstance(supplied_config, dict):
            for key in config:
                if key in supplied_config:
                    config[key] = float(supplied_config[key])

        threshold = self._clip(config["rf_threshold"], 0.70)
        minimum_persistence = max(2, int(config["minimum_persistence_observations"]))
        minimum_baseline = max(1, int(config["minimum_baseline_observations"]))
        observations = self._collect_observations(inputs)
        baseline_values, baseline_source = self._baseline_values(
            observations, inputs, threshold, minimum_baseline
        )
        baseline_mean = self._mean(baseline_values)
        baseline_count = len(baseline_values)
        baseline_valid = baseline_count >= minimum_baseline and baseline_mean < threshold

        start, sustained_window = self._first_sustained_window(
            observations, threshold, minimum_persistence
        )
        post_records = observations[start:] if start is not None else []
        post_rf = self._mean([item["rf_star_score"] for item in post_records])
        persistence_ratio = (
            self._mean([1.0 if item["rf_star_score"] >= threshold else 0.0 for item in post_records])
            if post_records else 0.0
        )
        stability = self._mean([item["stability"] for item in sustained_window])
        continuity = self._mean([item["continuity"] for item in sustained_window])
        coherence = self._mean([item["coherence"] for item in sustained_window])
        quality = self._mean([item["data_quality"] for item in observations])
        baseline_separation = self._clip((post_rf - baseline_mean) / max(0.001, 1.0 - baseline_mean)) if baseline_valid else 0.0
        threshold_margin = self._clip((post_rf - threshold) / max(0.001, 1.0 - threshold)) if post_records else 0.0

        risk, risk_reasons = self._false_positive_risk(
            observations,
            start,
            sustained_window,
            threshold,
            minimum_persistence,
            baseline_valid,
            quality,
            continuity,
            coherence,
            stability,
            self._clip(config["noise_tolerance"], 0.12),
        )

        component_scores = {
            "baseline_separation": baseline_separation,
            "persistence": persistence_ratio,
            "stability": stability,
            "continuity": continuity,
            "coherence": coherence,
            "data_quality": quality,
            "threshold_margin": threshold_margin,
            "false_positive_control": 1.0 - risk,
        }
        weights = {
            "baseline_separation": 0.18,
            "persistence": 0.20,
            "stability": 0.12,
            "continuity": 0.12,
            "coherence": 0.12,
            "data_quality": 0.10,
            "threshold_margin": 0.06,
            "false_positive_control": 0.10,
        }
        genesis_score = self._clip(sum(component_scores[key] * weights[key] for key in weights))
        observation_adequacy = self._clip(len(observations) / max(1, minimum_baseline + minimum_persistence))
        genesis_confidence = self._clip(
            0.45 * quality + 0.25 * observation_adequacy + 0.20 * (1.0 - risk) + 0.10 * persistence_ratio
        )

        conditions = {
            "longitudinal_data_present": len(observations) >= minimum_baseline + minimum_persistence,
            "explicit_time_order": all(item["timestamp_utc"] for item in observations),
            "baseline_documented": baseline_count >= minimum_baseline,
            "baseline_subthreshold": baseline_valid,
            "sustained_crossing": start is not None,
            "persistence_sufficient": persistence_ratio >= 0.80,
            "stability_sufficient": stability >= self._clip(config["minimum_stability"], 0.60),
            "continuity_sufficient": continuity >= self._clip(config["minimum_continuity"], 0.60),
            "coherence_sufficient": coherence >= self._clip(config["minimum_coherence"], 0.60),
            "data_quality_sufficient": quality >= self._clip(config["minimum_data_quality"], 0.50),
            "false_positive_risk_acceptable": risk <= self._clip(config["maximum_false_positive_risk"], 0.35),
            "genesis_score_sufficient": genesis_score >= self._clip(config["minimum_genesis_score"], 0.70),
        }
        missing_conditions = sorted(key for key, value in conditions.items() if not value)

        evidence_sufficient = all(
            conditions[key]
            for key in [
                "longitudinal_data_present",
                "baseline_documented",
                "baseline_subthreshold",
                "sustained_crossing",
                "data_quality_sufficient",
            ]
        )
        genesis_detected = evidence_sufficient and not missing_conditions
        if genesis_detected:
            genesis_status = "FUNCTIONAL_GENESIS_DETECTED"
        elif not observations or not evidence_sufficient:
            genesis_status = "FUNCTIONAL_GENESIS_UNDETERMINED"
        else:
            genesis_status = "FUNCTIONAL_GENESIS_NOT_DETECTED"

        genesis_timestamp = observations[start]["timestamp_utc"] if start is not None else None
        end_index = (start + len(sustained_window) - 1) if start is not None else None
        genesis_window = {
            "start_index": start,
            "end_index": end_index,
            "start_timestamp_utc": genesis_timestamp,
            "end_timestamp_utc": observations[end_index]["timestamp_utc"] if end_index is not None else None,
            "minimum_persistence_observations": minimum_persistence,
            "observed_persistence_ratio": persistence_ratio,
        }
        supporting_dimensions = sorted(
            key for key in ["stability", "continuity", "coherence", "data_quality"]
            if component_scores[key] >= config.get(f"minimum_{key}", 0.50)
        )

        audit_payload = {
            "config": config,
            "observations": observations,
            "baseline_values": baseline_values,
            "baseline_source": baseline_source,
            "conditions": conditions,
            "component_scores": component_scores,
            "genesis_status": genesis_status,
            "genesis_timestamp": genesis_timestamp,
            "genesis_window": genesis_window,
            "false_positive_risk": risk,
            "risk_reasons": risk_reasons,
        }
        genesis_hash = self._stable_hash(audit_payload)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "genesis_detected": genesis_detected,
            "genesis_status": genesis_status,
            "genesis_score": genesis_score,
            "genesis_confidence": genesis_confidence,
            "genesis_timestamp": genesis_timestamp,
            "genesis_window": genesis_window,
            "supporting_dimensions": supporting_dimensions,
            "missing_conditions": missing_conditions,
            "false_positive_risk": risk,
            "false_positive_reasons": risk_reasons,
            "genesis_hash": genesis_hash,
            "observation_count": len(observations),
            "baseline_observation_count": baseline_count,
            "baseline_score": baseline_mean,
            "baseline_source": baseline_source,
            "post_genesis_score": post_rf,
            "rf_threshold": threshold,
            "component_scores": component_scores,
            "condition_results": conditions,
            "input_sources": sorted(set(item["source"] for item in observations)),
            "synthetic_data_present": any(item["synthetic"] for item in observations),
            "audit_trace": audit_payload,
            "allowed_claims": [
                "a sustained functional RF* regime onset was detected" if genesis_detected else "functional RF* genesis was not established",
                "the result is quantitative, auditable and falsifiable",
            ],
            "blocked_claims": [
                "functional genesis proves phenomenal birth",
                "RF* threshold crossing proves consciousness",
                "developmental onset proves subjectivity, qualia or phenomenology",
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
            path = self.output_dir / "latest_genesis_detection.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)

        return result
