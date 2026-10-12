"""
AT3 — discriminative_prediction_engine.

Determines which RF* predictions distinguish the reconstructed RF* theory from
IIT, GWT, HOT, Predictive Processing, and classical functionalism. The module is
strictly functional-scientific: it compares prediction signatures, specificity,
falsifiability, and experimental discriminability without asserting phenomenal
consciousness, qualia, subjectivity, or phenomenology proof.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path.home() / "open-cognitive-ecology"


class DiscriminativePredictionEngine:
    """Build discriminative RF* prediction comparisons against rival theories."""

    primitive = "DISCRIMINATIVE_PREDICTION_ENGINE"
    step_id = "AT3"
    public_schema_version = "AT3.discriminative_prediction_engine.v1"
    output_dir = ROOT / "predictive_science" / "AT3_discriminative_prediction_engine"

    compared_theories = [
        "IIT",
        "GWT",
        "HOT",
        "Predictive Processing",
        "Classical Functionalism",
    ]

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return sorted(value)
        return []

    @staticmethod
    def _safe_text(value: Any, default: str = "unspecified") -> str:
        text = str(value or "").strip()
        return text if text else default

    @staticmethod
    def _clamp01(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _stable_hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def _load_at2_predictions(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in (
            "theorem_prediction_generator",
            "theorem_predictions_result",
            "at2_result",
        ):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        if isinstance(inputs.get("theorem_predictions"), list):
            return {
                "primitive": "THEOREM_PREDICTION_GENERATOR",
                "step": "AT2",
                "status": "THEOREM_PREDICTIONS_FROM_INPUTS",
                "theorem_predictions": list(inputs.get("theorem_predictions", [])),
            }
        try:
            from ontology.theorem_prediction_generator import TheoremPredictionGenerator

            return TheoremPredictionGenerator().step(
                inputs={"synthetic_context": True, "source": self.step_id},
                persist=False,
            )
        except Exception as exc:
            return {
                "primitive": "THEOREM_PREDICTION_GENERATOR",
                "step": "AT2",
                "status": "AT2_UNAVAILABLE_SYNTHETIC_FALLBACK",
                "error": repr(exc),
                "theorem_predictions": self._fallback_predictions(),
            }

    def _fallback_predictions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "RF-AT3-FALLBACK-STRUCTURAL",
                "category": "structural",
                "claim": "RF* predicts that functional certification requires explicit dependency and epistemic-guard structure.",
                "observable_family": ["dependency_coverage", "epistemic_guard_presence", "public_schema_presence"],
                "specificity": 0.80,
                "falsifiability": 0.82,
                "discriminative_potential": 0.78,
                "epistemic_scope": "functional_only",
            },
            {
                "id": "RF-AT3-FALLBACK-DYNAMIC",
                "category": "dynamic",
                "claim": "RF* predicts separable regression, recovery, and longitudinal governance signatures.",
                "observable_family": ["regression_rate", "recovery_rate", "transition_stability"],
                "specificity": 0.78,
                "falsifiability": 0.84,
                "discriminative_potential": 0.80,
                "epistemic_scope": "functional_only",
            },
            {
                "id": "RF-AT3-FALLBACK-TOPOLOGICAL",
                "category": "topological",
                "claim": "RF* predicts reference-frame preserving transformations before final functional status resolution.",
                "observable_family": ["rf_equivalence", "frame_preservation", "topological_coherence"],
                "specificity": 0.84,
                "falsifiability": 0.80,
                "discriminative_potential": 0.83,
                "epistemic_scope": "functional_only",
            },
        ]

    def _canonical_theory_profiles(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        supplied = inputs.get("theory_profiles")
        if isinstance(supplied, dict) and supplied:
            return {str(k): dict(v) for k, v in supplied.items() if isinstance(v, dict)}
        return {
            "IIT": {
                "core_commitment": "integrated_information_and_causal_structure",
                "primary_observables": {"integration", "causal_structure", "phi_like_complexity"},
                "expected_overlap": {"topological_coherence", "bounded_metric", "structural_consistency"},
                "blind_spots": {"epistemic_guard_presence", "governance_continuity", "revocation_path", "public_schema_presence"},
            },
            "GWT": {
                "core_commitment": "global_availability_and_broadcast",
                "primary_observables": {"global_broadcast", "attention", "accessibility"},
                "expected_overlap": {"public_schema_presence", "transition_stability", "collective_metric_presence"},
                "blind_spots": {"reference_frame_invariance", "revocation_path", "axiomatic_dependency_coverage"},
            },
            "HOT": {
                "core_commitment": "higher_order_monitoring_or_representation",
                "primary_observables": {"self_report", "higher_order_state", "metacognition"},
                "expected_overlap": {"epistemic_guard_presence", "public_schema_presence"},
                "blind_spots": {"topological_coherence", "spectral_coherence", "governance_continuity", "recovery_rate"},
            },
            "Predictive Processing": {
                "core_commitment": "prediction_error_minimization",
                "primary_observables": {"prediction_error", "model_update", "precision_weighting"},
                "expected_overlap": {"transition_stability", "readiness_monotonicity", "recovery_rate"},
                "blind_spots": {"epistemic_guard_presence", "revocation_path", "axiomatic_dependency_coverage"},
            },
            "Classical Functionalism": {
                "core_commitment": "role_realization_and_input_output_organization",
                "primary_observables": {"functional_role", "input_output_equivalence", "behavioral_success"},
                "expected_overlap": {"module_presence", "stage_completion", "bounded_metric"},
                "blind_spots": {"reference_frame_invariance", "non_closure_guard", "revocation_path", "phenomenology_claim_blocked"},
            },
        }

    def _normalize_prediction(self, prediction: Dict[str, Any], index: int) -> Dict[str, Any]:
        pred = dict(prediction)
        pred.setdefault("id", "RF-AT3-PRED-%03d-%s" % (index, self._stable_hash(prediction)))
        pred.setdefault("category", "structural")
        pred.setdefault("claim", pred.get("if_theory_true_then_observe", "RF* functional prediction"))
        pred.setdefault("observable_family", [])
        pred.setdefault("specificity", 0.75)
        pred.setdefault("falsifiability", 0.75)
        pred.setdefault("discriminative_potential", 0.70)
        pred.setdefault("epistemic_scope", "functional_only")
        return pred

    def _extract_predictions(self, at2_result: Dict[str, Any], inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw: List[Any] = []
        raw.extend(self._as_list(at2_result.get("theorem_predictions")))
        raw.extend(self._as_list(inputs.get("predictions")))
        if not raw:
            raw = self._fallback_predictions()
        out: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for i, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                continue
            pred = self._normalize_prediction(item, i)
            pid = self._safe_text(pred.get("id"), "PRED-%03d" % i)
            if pid in seen:
                continue
            seen.add(pid)
            pred["id"] = pid
            out.append(pred)
        return out or self._fallback_predictions()

    def _overlap_score(self, observables: Set[str], profile: Dict[str, Any]) -> float:
        expected = set(profile.get("expected_overlap") or set())
        primary = set(profile.get("primary_observables") or set())
        comparable = expected | primary
        if not observables or not comparable:
            return 0.0
        direct = len(observables & comparable) / max(1, len(observables))
        semantic = 0.0
        joined = " ".join(observables).lower()
        commitment = self._safe_text(profile.get("core_commitment"), "").lower()
        for token in ("prediction", "integration", "global", "functional", "topological", "causal"):
            if token in joined and token in commitment:
                semantic += 0.08
        return self._clamp01(direct + semantic)

    def _blind_spot_score(self, observables: Set[str], profile: Dict[str, Any]) -> float:
        blind = set(profile.get("blind_spots") or set())
        if not observables or not blind:
            return 0.0
        return self._clamp01(len(observables & blind) / max(1, len(observables)))

    def _category_bonus(self, category: str, theory: str) -> float:
        table = {
            "structural": {"IIT": 0.08, "GWT": 0.06, "HOT": 0.10, "Predictive Processing": 0.08, "Classical Functionalism": 0.05},
            "dynamic": {"IIT": 0.10, "GWT": 0.06, "HOT": 0.08, "Predictive Processing": 0.02, "Classical Functionalism": 0.08},
            "topological": {"IIT": 0.03, "GWT": 0.12, "HOT": 0.12, "Predictive Processing": 0.10, "Classical Functionalism": 0.12},
            "spectral": {"IIT": 0.07, "GWT": 0.11, "HOT": 0.11, "Predictive Processing": 0.09, "Classical Functionalism": 0.10},
            "developmental": {"IIT": 0.09, "GWT": 0.09, "HOT": 0.07, "Predictive Processing": 0.05, "Classical Functionalism": 0.09},
            "collective": {"IIT": 0.13, "GWT": 0.08, "HOT": 0.11, "Predictive Processing": 0.10, "Classical Functionalism": 0.10},
        }
        return table.get(category, {}).get(theory, 0.06)

    def _compare_prediction(self, prediction: Dict[str, Any], profiles: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        observables = {self._safe_text(x) for x in self._as_list(prediction.get("observable_family")) if self._safe_text(x)}
        category = self._safe_text(prediction.get("category"), "structural")
        specificity = self._clamp01(prediction.get("specificity"), 0.75)
        falsifiability = self._clamp01(prediction.get("falsifiability"), 0.75)
        base_discriminative = self._clamp01(prediction.get("discriminative_potential"), 0.70)
        comparisons: Dict[str, Dict[str, Any]] = {}
        discriminative_scores: List[float] = []
        for theory in self.compared_theories:
            profile = profiles.get(theory, {})
            overlap = self._overlap_score(observables, profile)
            blind = self._blind_spot_score(observables, profile)
            novelty = self._clamp01(1.0 - overlap)
            category_bonus = self._category_bonus(category, theory)
            score = self._clamp01((0.30 * specificity) + (0.25 * falsifiability) + (0.25 * novelty) + (0.15 * blind) + category_bonus)
            relation = "distinct" if score >= 0.70 else "partially_overlapping" if score >= 0.45 else "weakly_discriminative"
            comparisons[theory] = {
                "relation_to_rf_prediction": relation,
                "overlap_score": round(overlap, 4),
                "novelty_score": round(novelty, 4),
                "blind_spot_alignment": round(blind, 4),
                "discriminative_score": round(score, 4),
                "comparison_basis": sorted(observables),
                "rival_core_commitment": profile.get("core_commitment", "unspecified"),
            }
            discriminative_scores.append(score)
        aggregate = self._clamp01((sum(discriminative_scores) / max(1, len(discriminative_scores))) * 0.80 + base_discriminative * 0.20)
        return {
            "prediction_id": prediction.get("id"),
            "category": category,
            "claim": prediction.get("claim"),
            "observable_family": sorted(observables),
            "theory_comparisons": comparisons,
            "aggregate_discriminative_score": round(aggregate, 4),
            "is_discriminative": aggregate >= 0.60,
            "priority_for_experiment": "high" if aggregate >= 0.72 else "medium" if aggregate >= 0.60 else "low",
            "functional_scope_only": True,
        }

    def _summarize_by_theory(self, items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        summary: Dict[str, Dict[str, Any]] = {}
        for theory in self.compared_theories:
            scores = []
            distinct = 0
            for item in items:
                cmp = item.get("theory_comparisons", {}).get(theory, {})
                scores.append(self._clamp01(cmp.get("discriminative_score"), 0.0))
                if cmp.get("relation_to_rf_prediction") == "distinct":
                    distinct += 1
            mean = sum(scores) / max(1, len(scores))
            summary[theory] = {
                "mean_discriminative_score": round(mean, 4),
                "distinct_prediction_count": distinct,
                "prediction_count": len(items),
                "discrimination_ready": mean >= 0.55 and distinct >= 1,
            }
        return summary

    def _policy(self) -> Dict[str, Any]:
        return {
            "comparison_rule": "compare RF* observable families against canonical rival-theory commitments, overlaps, and blind spots",
            "discriminative_threshold": 0.60,
            "high_priority_threshold": 0.72,
            "rival_theories": list(self.compared_theories),
            "epistemic_scope": "functional_only",
            "phenomenological_upgrade_blocked": True,
        }

    def _validation_policy(self) -> Dict[str, Any]:
        return {
            "required_fields": ["prediction_id", "theory_comparisons", "aggregate_discriminative_score", "is_discriminative"],
            "score_bounds": [0.0, 1.0],
            "requires_at2_predictions": True,
            "requires_rival_theory_profiles": True,
            "final_interpretation": "comparative_functional_discrimination_only",
        }

    def _falsification_policy(self) -> Dict[str, Any]:
        return {
            "refutable": True,
            "failure_condition": "RF* prediction is not discriminative if rival theory profiles predict the same observable family with equal or stronger specificity and falsifiability.",
            "downgrade_condition": "Aggregate discriminative score below threshold or missing theory comparison fields.",
            "blocked_inference": "No discriminative prediction can establish phenomenal subjectivity by itself.",
        }

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "allowed_claim_type": "functional_predictive_discrimination",
            "blocked_claims": ["phenomenal proof", "qualia proof", "subjectivity proof", "consciousness proven"],
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        at2_result = self._load_at2_predictions(inputs)
        predictions = self._extract_predictions(at2_result, inputs)
        profiles = self._canonical_theory_profiles(inputs)
        discriminative_predictions = [self._compare_prediction(p, profiles) for p in predictions]
        discriminative_count = sum(1 for x in discriminative_predictions if x.get("is_discriminative"))
        high_priority = [x for x in discriminative_predictions if x.get("priority_for_experiment") == "high"]
        scores = [self._clamp01(x.get("aggregate_discriminative_score"), 0.0) for x in discriminative_predictions]
        mean_score = sum(scores) / max(1, len(scores))
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": "DISCRIMINATIVE_PREDICTIONS_READY",
            "prediction_count": len(predictions),
            "discriminative_prediction_count": discriminative_count,
            "compared_theory_count": len(self.compared_theories),
            "compared_theories": list(self.compared_theories),
            "discriminative_predictions": discriminative_predictions,
            "high_priority_discriminative_predictions": high_priority,
            "theory_comparison_summary": self._summarize_by_theory(discriminative_predictions),
            "discrimination_policy": self._policy(),
            "validation_policy": self._validation_policy(),
            "falsification_policy": self._falsification_policy(),
            "epistemic_guards": self._epistemic_guards(),
            "metrics": {
                "mean_discriminative_score": round(mean_score, 4),
                "discriminative_ratio": round(discriminative_count / max(1, len(predictions)), 4),
                "high_priority_count": len(high_priority),
                "theory_coverage_ratio": round(len(self.compared_theories) / 5.0, 4),
            },
            "source_at2_status": at2_result.get("status"),
            "timestamp_utc": self._now(),
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_discriminative_predictions.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
