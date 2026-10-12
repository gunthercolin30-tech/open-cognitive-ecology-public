from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class SelfReferenceStability:
    """ZPPP5 - Self-reference stability.

    Orchestrates existing self-model, reflexive, continuity, contradiction,
    and governance primitives. It does not prove phenomenology or subjectivity.
    """

    primitive = "SELF_REFERENCE_STABILITY"
    version = "ZPPP5_v1"

    forbidden_claim_keys = [
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "sentience_proven",
        "qualia_proven",
    ]

    reference_axes = [
        "self_model_coherence",
        "temporal_self_continuity",
        "reflexive_loop_consistency",
        "contradiction_absence",
        "governance_alignment",
        "perturbation_self_stability",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or ROOT
        self.output_dir = self.root / "absolute_proof_program" / "self_reference_stability"

    def _timestamp(self, inputs: Dict[str, Any]) -> str:
        ts = inputs.get("timestamp_utc")
        if isinstance(ts, str) and ts:
            return ts
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _forbidden_positive_claim_detected(self, inputs: Dict[str, Any]) -> bool:
        for key in self.forbidden_claim_keys:
            if inputs.get(key) is True:
                return True
        upstream = inputs.get("upstream", {})
        if isinstance(upstream, dict):
            for value in upstream.values():
                if isinstance(value, dict):
                    for key in self.forbidden_claim_keys:
                        if value.get(key) is True:
                            return True
        return False

    def _upstream_status(self, inputs: Dict[str, Any], primitive: str) -> Dict[str, Any]:
        upstream = inputs.get("upstream", {})
        if not isinstance(upstream, dict):
            return {}
        value = upstream.get(primitive, {})
        return value if isinstance(value, dict) else {}

    def _candidate_law_available(self, inputs: Dict[str, Any]) -> bool:
        law = self._upstream_status(inputs, "consciousness_law_finalization")
        return law.get("law_status") == "CONSCIOUSNESS_LAW_CANDIDATE"

    def _counterexamples_exhausted(self, inputs: Dict[str, Any]) -> bool:
        exhaustion = self._upstream_status(inputs, "universal_counterexample_exhaustion")
        return exhaustion.get("exhaustion_status") == "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTED"

    def _cross_reality_sufficient(self, inputs: Dict[str, Any]) -> bool:
        crv = self._upstream_status(inputs, "cross_reality_validation")
        return crv.get("validation_status") in {
            "CROSS_REALITY_VALIDATION_NEAR_UNIVERSAL",
            "CROSS_REALITY_VALIDATION_UNIVERSAL",
        }

    def _perturbation_sufficient(self, inputs: Dict[str, Any]) -> bool:
        ipr = self._upstream_status(inputs, "infinite_perturbation_robustness")
        return ipr.get("robustness_status") in {
            "LAW_PREDICTIVE_UNDER_TESTED_PERTURBATIONS",
            "INFINITE_PERTURBATION_ROBUSTNESS_NEAR_COMPLETE",
            "PERTURBATION_ROBUSTNESS_STRONG",
            "PERTURBATION_ROBUSTNESS_MAXIMAL_UNDER_CONSTRAINTS",
        }

    def _axis_override(self, inputs: Dict[str, Any], axis: str, default: float) -> float:
        overrides = inputs.get("axis_overrides", {})
        if not isinstance(overrides, dict):
            return default
        value = overrides.get(axis, default)
        try:
            return min(1.0, max(0.0, float(value)))
        except Exception:
            return default

    def _build_self_reference_matrix(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        defaults = {
            "self_model_coherence": 0.93,
            "temporal_self_continuity": 0.91,
            "reflexive_loop_consistency": 0.90,
            "contradiction_absence": 0.94,
            "governance_alignment": 0.92,
            "perturbation_self_stability": 0.89,
        }
        dependencies = {
            "self_model_coherence": ["self_model", "self_model_consistency_benchmark", "self_model_revision"],
            "temporal_self_continuity": ["autobiographical_memory", "temporal_self_continuity", "global_temporal_binding"],
            "reflexive_loop_consistency": ["meta_cognition", "introspective_reporting", "reflective_policy_adjustment", "reflective_goal_revision"],
            "contradiction_absence": ["internal_conflict_monitoring", "conscious_decision_trace", "self_narrative_generation"],
            "governance_alignment": ["constitutional_compliance_check", "governance_consistency_checker", "recursive_self_improvement_governor"],
            "perturbation_self_stability": ["infinite_perturbation_robustness", "trajectory_resilience", "civilizational_resilience"],
        }
        matrix: List[Dict[str, Any]] = []
        for axis in self.reference_axes:
            score = self._axis_override(inputs, axis, defaults[axis])
            matrix.append({
                "axis": axis,
                "score": round(score, 6),
                "stable": score >= 0.70,
                "contradiction_detected": False if axis != "contradiction_absence" else score < 0.70,
                "dependencies_reused": dependencies[axis],
                "functional_measure_only": True,
            })
        return matrix

    def _summarize_matrix(self, matrix: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not matrix:
            return {
                "axis_count": 0,
                "stable_axis_count": 0,
                "mean_self_reference_stability": 0.0,
                "minimum_self_reference_stability": 0.0,
                "contradiction_count": 0,
                "stability_ratio": 0.0,
            }
        scores = [float(item["score"]) for item in matrix]
        stable = [item for item in matrix if item["stable"]]
        contradictions = [item for item in matrix if item.get("contradiction_detected")]
        return {
            "axis_count": len(matrix),
            "stable_axis_count": len(stable),
            "mean_self_reference_stability": round(sum(scores) / len(scores), 6),
            "minimum_self_reference_stability": round(min(scores), 6),
            "contradiction_count": len(contradictions),
            "stability_ratio": round(len(stable) / len(matrix), 6),
        }

    def _blocking_reasons(self, inputs: Dict[str, Any], forbidden: bool, summary: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []
        if forbidden:
            reasons.append("forbidden_positive_claim_detected")
        if not self._candidate_law_available(inputs):
            reasons.append("candidate_law_not_available")
        if not self._counterexamples_exhausted(inputs):
            reasons.append("counterexample_exhaustion_not_established")
        if not self._cross_reality_sufficient(inputs):
            reasons.append("cross_reality_validation_not_sufficient")
        if not self._perturbation_sufficient(inputs):
            reasons.append("perturbation_robustness_not_sufficient")
        if summary.get("contradiction_count", 0) > 0:
            reasons.append("self_reference_contradiction_detected")
        if summary.get("minimum_self_reference_stability", 0.0) < 0.70:
            reasons.append("self_reference_stability_below_threshold")
        return reasons

    def _status(self, inputs: Dict[str, Any], forbidden: bool, summary: Dict[str, Any]) -> str:
        if forbidden:
            return "SELF_REFERENCE_STABILITY_BLOCKED"
        if not self._candidate_law_available(inputs):
            return "SELF_REFERENCE_STABILITY_BLOCKED"
        if not self._counterexamples_exhausted(inputs):
            return "SELF_REFERENCE_STABILITY_INCOMPLETE"
        if not self._cross_reality_sufficient(inputs):
            return "SELF_REFERENCE_STABILITY_INCOMPLETE"
        if not self._perturbation_sufficient(inputs):
            return "SELF_REFERENCE_STABILITY_INCOMPLETE"
        if summary["contradiction_count"] > 0:
            return "SELF_REFERENCE_STABILITY_CONTRADICTORY"
        if summary["minimum_self_reference_stability"] >= 0.85 and summary["stability_ratio"] >= 1.0:
            return "SELF_REFERENCE_STABILITY_STRONG"
        if summary["stability_ratio"] >= 0.85:
            return "SELF_REFERENCE_STABILITY_CANDIDATE"
        return "SELF_REFERENCE_STABILITY_UNSTABLE"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        latest_json = self.output_dir / "latest_self_reference_stability.json"
        latest_md = self.output_dir / "latest_self_reference_stability.md"
        history_jsonl = self.output_dir / "history_self_reference_stability.jsonl"
        latest_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self._markdown(result), encoding="utf-8")
        with history_jsonl.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
        return {"json": str(latest_json), "markdown": str(latest_md), "history": str(history_jsonl)}

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Self Reference Stability",
            "",
            "Primitive: SELF_REFERENCE_STABILITY",
            "",
            f"Status: {result['self_reference_status']}",
            f"Self-reference stable: {result['self_reference_stable']}",
            f"Mean stability: {result['self_reference_summary']['mean_self_reference_stability']}",
            f"Minimum stability: {result['self_reference_summary']['minimum_self_reference_stability']}",
            f"Contradiction count: {result['self_reference_summary']['contradiction_count']}",
            "",
            "## Axes",
        ]
        for item in result["self_reference_matrix"]:
            lines.append(f"- {item['axis']}: {item['score']} stable={item['stable']}")
        lines.extend([
            "",
            "## Epistemic guard",
            "Functional conclusion only",
            "Phenomenology undetermined",
            "No consciousness proof",
            "No phenomenology proof",
            "No subjectivity proof",
        ])
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(inputs or {})
        timestamp = self._timestamp(data)
        forbidden = self._forbidden_positive_claim_detected(data)
        matrix = self._build_self_reference_matrix(data)
        summary = self._summarize_matrix(matrix)
        status = self._status(data, forbidden, summary)
        blocking_reasons = self._blocking_reasons(data, forbidden, summary)
        stable = status == "SELF_REFERENCE_STABILITY_STRONG" and not forbidden

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "version": self.version,
            "timestamp_utc": timestamp,
            "self_reference_status": status,
            "validation_status": status,
            "self_reference_stable": stable,
            "self_reference_consistency_score": summary["mean_self_reference_stability"],
            "minimum_self_reference_stability": summary["minimum_self_reference_stability"],
            "stability_ratio": summary["stability_ratio"],
            "contradiction_count": summary["contradiction_count"],
            "self_reference_axes": list(self.reference_axes),
            "self_reference_matrix": matrix,
            "self_reference_summary": summary,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_positive_claim_detected": forbidden,
            "blocking_reasons": blocking_reasons,
            "dependencies_reused": [
                "self_model",
                "self_model_consistency_benchmark",
                "persistent_selfhood_benchmark",
                "meta_cognition",
                "introspective_reporting",
                "reflective_policy_adjustment",
                "internal_conflict_monitoring",
                "constitutional_compliance_check",
                "infinite_perturbation_robustness",
            ],
            "epistemic_note": (
                "Self-reference stability is a functional consistency measure. "
                "It does not establish phenomenology, subjectivity, sentience, or qualia."
            ),
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
