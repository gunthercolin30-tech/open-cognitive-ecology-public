"""AV7 — functional developmental stage classifier.

Synthesizes already-computed AV1–AV6 public results. It never invokes or
recomputes upstream detectors and never infers phenomenal consciousness.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"


class DevelopmentalStageClassifier:
    primitive = "DEVELOPMENTAL_STAGE_CLASSIFIER"
    step_id = "AV7"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV7_developmental_stage_classifier"

    STAGES = (
        "PRE_GENESIS", "GENESIS", "MATURATION", "SPECIALIZATION",
        "BIFURCATION", "DEGENERATION", "RECOVERY",
        "STABLE_DEVELOPED_REGIME", "HYBRID_STAGE", "UNDETERMINED",
    )
    DEFAULTS = {
        "minimum_evidence_quality": 0.50,
        "dominant_threshold": 0.48,
        "hybrid_secondary_threshold": 0.32,
        "hybrid_margin": 0.16,
        "transition_confidence_threshold": 0.55,
        "persistence_bonus": 0.08,
    }

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if not math.isfinite(number):
            number = default
        return max(0.0, min(1.0, number))

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _result(self, inputs: Dict[str, Any], *names: str) -> Dict[str, Any]:
        for name in names:
            candidate = inputs.get(name)
            if isinstance(candidate, dict):
                return dict(candidate)
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, dict):
            for name in names:
                candidate = upstream.get(name)
                if isinstance(candidate, dict):
                    return dict(candidate)
        return {}

    def _quality(self, result: Dict[str, Any]) -> float:
        for key in ("data_quality_score", "evidence_quality", "quality_score", "stage_confidence"):
            if key in result:
                return self._clip(result.get(key), 0.0)
        conditions = result.get("condition_results")
        if isinstance(conditions, dict) and conditions:
            values = [1.0 if bool(v) else 0.0 for v in conditions.values()]
            return sum(values) / len(values)
        return 1.0 if result else 0.0

    def _status(self, result: Dict[str, Any], key: str) -> str:
        return str(result.get(key, "")).strip().upper()

    def _score_genesis(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "genesis_status")
        if status == "FUNCTIONAL_GENESIS_DETECTED" or bool(r.get("genesis_detected")):
            return max(0.72, self._clip(r.get("genesis_score", r.get("confidence_score", 0.72))))
        return 0.0

    def _score_maturation(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "maturation_status")
        mapping = {
            "FUNCTIONAL_MATURATION_PROGRESSING": 0.68,
            "FUNCTIONAL_MATURATION_PLATEAU": 0.62,
            "FUNCTIONAL_MATURATION_COMPLETE": 0.82,
            "FUNCTIONAL_MATURATION_REGRESSING": 0.36,
        }
        return max(mapping.get(status, 0.0), self._clip(r.get("maturation_score", r.get("maturation_index", 0.0))))

    def _score_specialization(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "specialization_status")
        mapping = {
            "FUNCTIONAL_SPECIALIZATION_EMERGING": 0.58,
            "FUNCTIONAL_SPECIALIZATION_STABLE": 0.76,
            "FUNCTIONAL_SPECIALIZATION_STRONG": 0.86,
            "FUNCTIONAL_SPECIALIZATION_CLOSURE_RISK": 0.44,
        }
        return max(mapping.get(status, 0.0), self._clip(r.get("specialization_strength", 0.0)))

    def _score_bifurcation(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "bifurcation_status")
        detected = bool(r.get("bifurcation_detected")) or status in {
            "FUNCTIONAL_BIFURCATION_DETECTED", "FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED"
        }
        if not detected:
            return 0.0
        return max(0.70, self._clip(r.get("bifurcation_score", r.get("structural_break_score", 0.70))))

    def _score_degeneration(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "degeneration_status")
        mapping = {
            "FUNCTIONAL_DECLINE_DETECTED": 0.54,
            "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED": 0.70,
            "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED": 0.84,
            "FUNCTIONAL_COLLAPSE_DETECTED": 0.96,
        }
        if bool(r.get("degeneration_detected")):
            return max(mapping.get(status, 0.64), self._clip(r.get("degeneration_score", 0.64)))
        return mapping.get(status, 0.0)

    def _score_recovery(self, r: Dict[str, Any]) -> float:
        status = self._status(r, "recovery_status")
        mapping = {
            "FUNCTIONAL_RECOVERY_EMERGING": 0.55,
            "FUNCTIONAL_RECOVERY_TRANSIENT": 0.38,
            "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED": 0.70,
            "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED": 0.82,
            "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE": 0.90,
        }
        if bool(r.get("recovery_detected")):
            return max(mapping.get(status, 0.60), self._clip(r.get("recovery_score", 0.60)))
        return mapping.get(status, 0.0)

    def _prior_context(self, inputs: Dict[str, Any]) -> Tuple[Optional[str], int, List[Dict[str, Any]]]:
        previous = inputs.get("previous_stage")
        duration = inputs.get("stage_duration", 0)
        history = inputs.get("stage_history")
        if isinstance(inputs.get("previous_result"), dict):
            prior = inputs["previous_result"]
            previous = previous or prior.get("developmental_stage")
            duration = duration or prior.get("stage_duration", 0)
        if not isinstance(history, list):
            history = []
        try:
            duration_i = max(0, int(duration))
        except (TypeError, ValueError):
            duration_i = 0
        previous_s = str(previous).upper() if previous else None
        if previous_s not in self.STAGES:
            previous_s = None
        return previous_s, duration_i, history

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        config = dict(self.DEFAULTS)
        supplied = inputs.get("config")
        if isinstance(supplied, dict):
            for key in config:
                if key in supplied:
                    config[key] = self._clip(supplied[key], config[key])

        genesis = self._result(inputs, "genesis_result", "AV1", "genesis_detector")
        maturation = self._result(inputs, "maturation_result", "AV2", "maturation_tracker")
        specialization = self._result(inputs, "specialization_result", "AV3", "specialization_engine")
        bifurcation = self._result(inputs, "bifurcation_result", "AV4", "bifurcation_detector")
        degeneration = self._result(inputs, "degeneration_result", "AV5", "degeneration_detector")
        recovery = self._result(inputs, "recovery_result", "AV6", "recovery_engine")
        upstream = {
            "AV1": genesis, "AV2": maturation, "AV3": specialization,
            "AV4": bifurcation, "AV5": degeneration, "AV6": recovery,
        }
        present = [name for name, value in upstream.items() if value]
        qualities = {name: self._quality(value) for name, value in upstream.items()}
        evidence_quality = sum(qualities[n] for n in present) / len(present) if present else 0.0

        raw = {
            "GENESIS": self._score_genesis(genesis),
            "MATURATION": self._score_maturation(maturation),
            "SPECIALIZATION": self._score_specialization(specialization),
            "BIFURCATION": self._score_bifurcation(bifurcation),
            "DEGENERATION": self._score_degeneration(degeneration),
            "RECOVERY": self._score_recovery(recovery),
        }
        genesis_not_detected = self._status(genesis, "genesis_status") == "FUNCTIONAL_GENESIS_NOT_DETECTED"
        pre_genesis = 0.82 if genesis and genesis_not_detected else 0.0
        # Earlier stages are prerequisites, not necessarily co-current stages.
        # Down-weight them when a later developmental signal is active.
        if raw["MATURATION"] >= 0.48:
            raw["GENESIS"] *= 0.35
        if raw["SPECIALIZATION"] >= 0.48:
            raw["MATURATION"] *= 0.45
            raw["GENESIS"] *= 0.25
        for event_stage in ("BIFURCATION", "DEGENERATION", "RECOVERY"):
            if raw[event_stage] >= 0.48:
                raw["GENESIS"] *= 0.25
                raw["MATURATION"] *= 0.40
                raw["SPECIALIZATION"] *= 0.55
        mature_complete = self._status(maturation, "maturation_status") in {"FUNCTIONAL_MATURATION_COMPLETE", "FUNCTIONAL_MATURATION_PLATEAU"}
        specialized_stable = self._status(specialization, "specialization_status") in {"FUNCTIONAL_SPECIALIZATION_STABLE", "FUNCTIONAL_SPECIALIZATION_STRONG"}
        no_active_disruption = raw["BIFURCATION"] < 0.30 and raw["DEGENERATION"] < 0.30 and raw["RECOVERY"] < 0.30
        stable_developed = 0.95 if mature_complete and specialized_stable and no_active_disruption else 0.0
        if stable_developed > 0:
            raw["SPECIALIZATION"] *= 0.45
            raw["MATURATION"] *= 0.35
            raw["GENESIS"] *= 0.20

        scores = {stage: 0.0 for stage in self.STAGES}
        scores.update(raw)
        scores["PRE_GENESIS"] = pre_genesis
        scores["STABLE_DEVELOPED_REGIME"] = stable_developed

        previous_stage, previous_duration, history = self._prior_context(inputs)
        if previous_stage and previous_stage in scores and scores[previous_stage] > 0:
            scores[previous_stage] = self._clip(scores[previous_stage] + config["persistence_bonus"])

        conflicts: List[str] = []
        if scores["DEGENERATION"] >= 0.45 and scores["RECOVERY"] >= 0.45:
            conflicts.append("DEGENERATION_RECOVERY_OVERLAP")
        if scores["BIFURCATION"] >= 0.45 and scores["RECOVERY"] >= 0.45:
            conflicts.append("BIFURCATION_RECOVERY_OVERLAP")
        if scores["PRE_GENESIS"] >= 0.45 and any(scores[s] >= 0.45 for s in ("MATURATION", "SPECIALIZATION", "BIFURCATION", "DEGENERATION", "RECOVERY")):
            conflicts.append("PRE_GENESIS_DOWNSTREAM_CONFLICT")

        ranked = sorted(((s, v) for s, v in scores.items() if s not in {"HYBRID_STAGE", "UNDETERMINED"}), key=lambda x: (-x[1], x[0]))
        dominant_stage, dominant_score = ranked[0] if ranked else ("UNDETERMINED", 0.0)
        secondary_stage, secondary_score = ranked[1] if len(ranked) > 1 else (None, 0.0)
        hybrid = bool(
            dominant_score >= config["dominant_threshold"] and
            secondary_score >= config["hybrid_secondary_threshold"] and
            dominant_score - secondary_score <= config["hybrid_margin"]
        ) or bool(conflicts)

        sufficient = bool(present) and evidence_quality >= config["minimum_evidence_quality"]
        if not sufficient or dominant_score < config["dominant_threshold"]:
            developmental_stage = "UNDETERMINED"
            hybrid = False
        elif hybrid:
            developmental_stage = "HYBRID_STAGE"
        else:
            developmental_stage = dominant_stage

        probability_basis = {k: v for k, v in scores.items() if k not in {"HYBRID_STAGE", "UNDETERMINED"}}
        total = sum(probability_basis.values())
        probabilities = {k: round((v / total if total else 0.0), 6) for k, v in probability_basis.items()}
        probabilities["HYBRID_STAGE"] = round(max(secondary_score, 0.5 if hybrid else 0.0) if hybrid else 0.0, 6)
        probabilities["UNDETERMINED"] = round(1.0 - evidence_quality if developmental_stage == "UNDETERMINED" else 0.0, 6)

        if developmental_stage == "HYBRID_STAGE":
            confidence = self._clip((dominant_score + secondary_score) / 2.0 * evidence_quality)
        elif developmental_stage == "UNDETERMINED":
            confidence = self._clip(evidence_quality * dominant_score)
        else:
            confidence = self._clip(dominant_score * evidence_quality)

        transition_detected = bool(previous_stage and developmental_stage != previous_stage and developmental_stage != "UNDETERMINED" and confidence >= config["transition_confidence_threshold"])
        if previous_stage is None:
            transition_status = "NO_PRIOR_STAGE"
        elif developmental_stage == "UNDETERMINED":
            transition_status = "TRANSITION_UNDETERMINED"
        elif transition_detected:
            transition_status = "DEVELOPMENTAL_STAGE_TRANSITION_DETECTED"
        else:
            transition_status = "DEVELOPMENTAL_STAGE_PERSISTENT"
        stage_duration = previous_duration + 1 if previous_stage == developmental_stage else (1 if developmental_stage != "UNDETERMINED" else 0)

        missing_conditions = []
        if not present:
            missing_conditions.append("upstream_results")
        if evidence_quality < config["minimum_evidence_quality"]:
            missing_conditions.append("evidence_quality")
        if dominant_score < config["dominant_threshold"]:
            missing_conditions.append("dominant_stage_evidence")

        evidence = []
        for stage, score in ranked:
            if score > 0:
                evidence.append({"stage": stage, "score": round(score, 6), "source": {
                    "GENESIS": "AV1", "MATURATION": "AV2", "SPECIALIZATION": "AV3",
                    "BIFURCATION": "AV4", "DEGENERATION": "AV5", "RECOVERY": "AV6",
                    "PRE_GENESIS": "AV1", "STABLE_DEVELOPED_REGIME": "AV2+AV3+AV4+AV5+AV6",
                }.get(stage, "derived")})

        condition_results = {
            "upstream_results_present": bool(present),
            "evidence_quality_sufficient": evidence_quality >= config["minimum_evidence_quality"],
            "dominant_stage_supported": dominant_score >= config["dominant_threshold"],
            "chronology_context_valid": isinstance(history, list),
            "uncertainty_preserved": developmental_stage in self.STAGES,
            "no_upstream_recalculation": True,
        }
        hash_payload = {
            "upstream": upstream,
            "previous_stage": previous_stage,
            "previous_duration": previous_duration,
            "history": history,
            "config": config,
            "developmental_stage": developmental_stage,
            "scores": scores,
            "conflicts": conflicts,
        }
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
            "developmental_stage": developmental_stage,
            "stage_probabilities": probabilities,
            "transition_status": transition_status,
            "hybrid_stage": hybrid,
            "stage_hash": self._stable_hash(hash_payload),
            "stage_confidence": round(confidence, 6),
            "dominant_stage": dominant_stage if dominant_score > 0 else "UNDETERMINED",
            "secondary_stage": secondary_stage,
            "candidate_stages": [s for s, v in ranked if v >= config["hybrid_secondary_threshold"]],
            "stage_duration": stage_duration,
            "previous_stage": previous_stage,
            "stage_transition_detected": transition_detected,
            "stage_evidence": evidence,
            "stage_conflicts": conflicts,
            "condition_results": condition_results,
            "missing_conditions": missing_conditions,
            "upstream_modules_present": present,
            "evidence_quality_score": round(evidence_quality, 6),
            "audit_trace": {
                "classification_method": "weighted_public_result_synthesis",
                "upstream_recalculation_performed": False,
                "stage_scores": {k: round(v, 6) for k, v in scores.items()},
                "hybrid_rule_applied": hybrid,
                "conflict_count": len(conflicts),
                "history_length": len(history),
            },
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_developmental_stage_classification.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result


def step(inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
    return DevelopmentalStageClassifier().step(inputs=inputs, persist=persist)
