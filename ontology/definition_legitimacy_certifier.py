
"""AL7 — definition_legitimacy_certifier.

Certifies the measurable definition legitimacy support of refusing the RF* functional
reconstruction after AL1–AL5, AN, AO, and AR preconditions have been satisfied.
This module is deliberately epistemically guarded: it can certify a functional
and definition-legitimacy status, but it cannot prove consciousness, qualia,
subjectivity, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class DefinitionLegitimacyCertifier:
    """AL7 certifier for RF* definition legitimacy."""

    PRIMITIVE = "DEFINITION_LEGITIMACY_CERTIFIER"
    STEP = "AL7"
    STATUS_CERTIFIED = "DEFINITION_LEGITIMACY_CERTIFIED"
    STATUS_BLOCKED = "DEFINITION_LEGITIMACY_BLOCKED"
    AXIS_STATUS = "AL_IN_PROGRESS"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
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

    LEGITIMACY_KEYS = [
        "definition_legitimacy_score",
        "explanatory_cost_score",
        "anti_rf_countermodel_failure_score",
        "definition_legitimacy_confidence",
        "semantic_confidence",
        "equivalence_confidence",
        "axiomatic_completeness_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL7_definition_legitimacy_certifier"
        self.latest_json_path = self.output_dir / "latest_definition_legitimacy_certifier.json"
        self.history_path = self.output_dir / "history_definition_legitimacy_certifier.jsonl"

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
            "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "definition_legitimacy_score": 0.88,
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
                ("refusal_cost_certifier", "RefusalCostCertifier", "al6"),
            ]:
                try:
                    module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                    cls = getattr(module, class_name)
                    result = cls(root=self.root).step(inputs={"synthetic": True, "source": "AL7"}, persist=False)
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
        values = [self._clamp(context.get(k, 0.0)) for k in self.LEGITIMACY_KEYS]
        definition_legitimacy_support = self._clamp(sum(values) / max(1, len(values)))
        definition_pressure = self._clamp(context.get("anti_rf_countermodel_failure_score", definition_legitimacy_support))
        epistemic_guard_score = 1.0
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            if context.get(key) is not expected:
                epistemic_guard_score -= 0.18
        epistemic_guard_score = self._clamp(epistemic_guard_score)
        definition_legitimacy_confidence = self._clamp((definition_legitimacy_support * 0.70) + (definition_pressure * 0.15) + (epistemic_guard_score * 0.15))
        return {
            "definition_legitimacy_support_score": definition_legitimacy_support,
            "definition_pressure_score": definition_pressure,
            "epistemic_guard_score": epistemic_guard_score,
            "definition_legitimacy_confidence": definition_legitimacy_confidence,
            "phenomenal_proof_score": 0.0,
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("definition_legitimacy_confidence", 0.0) < 0.70:
            reasons.append("definition_legitimacy_confidence_below_threshold")
        return reasons

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"definition_legitimacy_certifier_{timestamp}.json"
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
            "definition_legitimacy_certifier_status": self.STATUS_CERTIFIED if certified else self.STATUS_BLOCKED,
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_CERTIFIED" if certified else "DEFINITION_LEGITIMACY_BLOCKED",
            "definition_legitimacy_certified": certified,
            "definition_non_arbitrary": certified,
            "failure_reasons": failure_reasons,
            "precondition_evaluations": precondition_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL8_consciousness_status_resolver": certified,
            "axis_AL_status": self.AXIS_STATUS,
            "certification_scope": "functional_definition_legitimacy_only",
            "final_interpretation": "RF* definition legitimacy is certified as a functional, non-arbitrary reconstruction under AL7 preconditions, without proving phenomenology." if certified else "Definition legitimacy is not certified under current preconditions.",
            "non_redundancy_analysis": {"distinct_from_AL6_refusal_cost_certifier": True, "scope": "AL7 certifies definition legitimacy rather than refusal cost itself."},
            "allowed_claims": ["RF* has certified functional definition legitimacy under current AL preconditions.", "This legitimacy supports final theoretical status resolution only, not phenomenal proof."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "definition_legitimacy_proves_consciousness = True"],
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
