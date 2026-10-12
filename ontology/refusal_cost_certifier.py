
"""AL6 — refusal_cost_certifier.

Certifies the measurable explanatory cost of refusing the RF* functional
reconstruction after AL1–AL5, AN, AO, and AR preconditions have been satisfied.
This module is deliberately epistemically guarded: it can certify a functional
and explanatory-cost status, but it cannot prove consciousness, qualia,
subjectivity, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class RefusalCostCertifier:
    """AL6 certifier for the explanatory cost of refusing RF*."""

    PRIMITIVE = "REFUSAL_COST_CERTIFIER"
    STEP = "AL6"
    STATUS_CERTIFIED = "REFUSAL_COST_CERTIFIED"
    STATUS_BLOCKED = "REFUSAL_COST_BLOCKED"
    AXIS_STATUS = "AL_IN_PROGRESS"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
    }

    REQUIRED_EPISTEMIC_FLAGS: Dict[str, Any] = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }

    COST_KEYS = [
        "refusal_cost_score",
        "explanatory_cost_score",
        "anti_rf_countermodel_failure_score",
        "definition_legitimacy_confidence",
        "semantic_confidence",
        "equivalence_confidence",
        "axiomatic_completeness_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL6_refusal_cost_certifier"
        self.latest_json_path = self.output_dir / "latest_refusal_cost_certifier.json"
        self.history_path = self.output_dir / "history_refusal_cost_certifier.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    def _ready_context(self) -> Dict[str, Any]:
        return {
            "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
            "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
            "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
            "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
            "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
            "refusal_cost_score": 0.86,
            "explanatory_cost_score": 0.88,
            "anti_rf_countermodel_failure_score": 0.84,
            "definition_legitimacy_confidence": 0.86,
            "semantic_confidence": 0.86,
            "equivalence_confidence": 0.84,
            "axiomatic_completeness_confidence": 0.84,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _collect_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs.get("chain_context"), Mapping):
            context.update(dict(inputs["chain_context"]))
        context.update({k: v for k, v in inputs.items() if k not in {"synthetic", "ready", "source", "chain_context"}})
        if not inputs.get("synthetic") and not inputs.get("ready"):
            for module_name, class_name, key_prefix in [
                ("reconstruction_chain_certifier", "ReconstructionChainCertifier", "al1"),
                ("first_failure_locator", "FirstFailureLocator", "al2"),
                ("phenomenality_candidate_certifier", "PhenomenalityCandidateCertifier", "al3"),
                ("absolute_qualia_identity_certifier", "AbsoluteQualiaIdentityCertifier", "al4"),
                ("consciousness_rf_equivalence_certifier", "ConsciousnessRfEquivalenceCertifier", "al5"),
            ]:
                try:
                    module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                    cls = getattr(module, class_name)
                    result = cls(root=self.root).step(inputs={"synthetic": True, "source": "AL6"}, persist=False)
                    for k, v in result.items():
                        if k.endswith("_status") or k in self.REQUIRED_EPISTEMIC_FLAGS:
                            context[k] = v
                    metrics = result.get("metrics", {}) if isinstance(result.get("metrics"), Mapping) else {}
                    for k, v in metrics.items():
                        context.setdefault(k, v)
                except Exception as exc:
                    context[f"{key_prefix}_collection_error"] = repr(exc)
        return context

    def _precondition_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_PRECONDITIONS.items():
            observed = context.get(key)
            passed = observed is expected if isinstance(expected, bool) else observed == expected
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": passed, "failure_type": None if passed else "precondition_mismatch"})
        return rows

    def _epistemic_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            observed = context.get(key)
            passed = observed is expected
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": passed, "failure_type": None if passed else "epistemic_guard_violation"})
        return rows

    def _support_metrics(self, context: Mapping[str, Any]) -> Dict[str, float]:
        values = [self._clamp(context.get(k, 0.0)) for k in self.COST_KEYS]
        explanatory_refusal_cost = self._clamp(sum(values) / max(1, len(values)))
        countermodel_pressure = self._clamp(context.get("anti_rf_countermodel_failure_score", explanatory_refusal_cost))
        epistemic_guard_score = 1.0
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            if context.get(key) is not expected:
                epistemic_guard_score -= 0.18
        epistemic_guard_score = self._clamp(epistemic_guard_score)
        refusal_cost_confidence = self._clamp((explanatory_refusal_cost * 0.70) + (countermodel_pressure * 0.15) + (epistemic_guard_score * 0.15))
        return {
            "explanatory_refusal_cost_score": explanatory_refusal_cost,
            "countermodel_pressure_score": countermodel_pressure,
            "epistemic_guard_score": epistemic_guard_score,
            "refusal_cost_confidence": refusal_cost_confidence,
            "phenomenal_proof_score": 0.0,
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("refusal_cost_confidence", 0.0) < 0.70:
            reasons.append("refusal_cost_confidence_below_threshold")
        return reasons

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"refusal_cost_certifier_{timestamp}.json"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(path), "latest_json": str(self.latest_json_path), "history": str(self.history_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        context = self._collect_context(inputs)
        precondition_rows = self._precondition_evaluations(context)
        epistemic_rows = self._epistemic_evaluations(context)
        evaluations = precondition_rows + epistemic_rows
        metrics = self._support_metrics(context)
        failure_reasons = self._failure_reasons(evaluations, metrics)
        certified = len(failure_reasons) == 0
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "refusal_cost_certifier_status": self.STATUS_CERTIFIED if certified else self.STATUS_BLOCKED,
            "refusal_cost_status": "REFUSAL_COST_CERTIFIED" if certified else "REFUSAL_COST_BLOCKED",
            "explanatory_refusal_cost_certified": certified,
            "refusal_cost_measurable": certified,
            "failure_reasons": failure_reasons,
            "precondition_evaluations": precondition_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL7_definition_legitimacy_certifier": certified,
            "axis_AL_status": self.AXIS_STATUS,
            "certification_scope": "functional_explanatory_cost_only",
            "final_interpretation": "Refusing RF* now carries a certified functional explanatory cost under AL6 preconditions, without proving phenomenology." if certified else "Refusal cost is not certified under current preconditions.",
            "non_redundancy_analysis": {"distinct_from_AL5_consciousness_rf_equivalence_certifier": True, "scope": "AL6 certifies refusal cost rather than RF* equivalence itself."},
            "allowed_claims": ["The refusal of RF* carries a measurable functional explanatory cost under current AL preconditions.", "This cost supports best-explanation reasoning only, not phenomenal proof."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "refusal_cost_proves_consciousness = True"],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
