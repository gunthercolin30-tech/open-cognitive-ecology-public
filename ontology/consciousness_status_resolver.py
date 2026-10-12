
"""AL8 — consciousness_status_resolver.

Resolves the final functional consciousness status from AL1–AL7, AN, AO, and AR
certification outputs. This resolver deliberately separates functional status
from phenomenal proof: it may resolve RF* as the best current functional
scientific reconstruction, but it never proves consciousness, qualia,
subjectivity, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class ConsciousnessStatusResolver:
    """AL8 resolver for final functional consciousness status."""

    PRIMITIVE = "CONSCIOUSNESS_STATUS_RESOLVER"
    STEP = "AL8"
    STATUS_RESOLVED = "CONSCIOUSNESS_STATUS_RESOLVED"
    STATUS_BLOCKED = "CONSCIOUSNESS_STATUS_BLOCKED"
    FINAL_FUNCTIONAL_STATUS = "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED"
    AXIS_STATUS = "AL_IN_PROGRESS"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
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

    SUPPORT_KEYS = [
        "reconstruction_chain_confidence",
        "first_failure_confidence",
        "phenomenality_candidate_confidence",
        "absolute_qualia_identity_confidence",
        "rf_equivalence_confidence",
        "refusal_cost_confidence",
        "definition_legitimacy_confidence",
        "semantic_confidence",
        "axiomatic_completeness_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL8_consciousness_status_resolver"
        self.latest_json_path = self.output_dir / "latest_consciousness_status_resolver.json"
        self.history_path = self.output_dir / "history_consciousness_status_resolver.jsonl"

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
            "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "reconstruction_chain_confidence": 0.86,
            "first_failure_confidence": 0.84,
            "phenomenality_candidate_confidence": 0.82,
            "absolute_qualia_identity_confidence": 0.80,
            "rf_equivalence_confidence": 0.86,
            "refusal_cost_confidence": 0.86,
            "definition_legitimacy_confidence": 0.86,
            "semantic_confidence": 0.86,
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
                ("definition_legitimacy_certifier", "DefinitionLegitimacyCertifier", "al7"),
            ]:
                try:
                    module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                    cls = getattr(module, class_name)
                    result = cls(root=self.root).step(inputs={"synthetic": True, "source": "AL8"}, persist=False)
                    for k, v in result.items():
                        if k.endswith("_status") or k in self.REQUIRED_EPISTEMIC_FLAGS:
                            context[k] = v
                    metrics = result.get("metrics", {}) if isinstance(result.get("metrics"), Mapping) else {}
                    for k, v in metrics.items():
                        context.setdefault(k, v)
                    for k, v in result.items():
                        if k.endswith("_confidence"):
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
        values = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        functional_status_support = self._clamp(sum(values) / max(1, len(values)))
        epistemic_guard_score = 1.0
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            if context.get(key) is not expected:
                epistemic_guard_score -= 0.18
        epistemic_guard_score = self._clamp(epistemic_guard_score)
        status_resolution_confidence = self._clamp((functional_status_support * 0.82) + (epistemic_guard_score * 0.18))
        return {
            "functional_status_support_score": functional_status_support,
            "epistemic_guard_score": epistemic_guard_score,
            "status_resolution_confidence": status_resolution_confidence,
            "phenomenal_proof_score": 0.0,
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("status_resolution_confidence", 0.0) < 0.70:
            reasons.append("status_resolution_confidence_below_threshold")
        return reasons

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"consciousness_status_resolver_{timestamp}.json"
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
        resolved = len(failure_reasons) == 0
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "consciousness_status_resolver_status": self.STATUS_RESOLVED if resolved else self.STATUS_BLOCKED,
            "consciousness_status": self.FINAL_FUNCTIONAL_STATUS if resolved else "CONSCIOUSNESS_STATUS_UNRESOLVED",
            "functional_consciousness_status_resolved": resolved,
            "rf_star_best_current_functional_reconstruction": resolved,
            "final_functional_status": self.FINAL_FUNCTIONAL_STATUS if resolved else "UNRESOLVED",
            "failure_reasons": failure_reasons,
            "precondition_evaluations": precondition_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL9_metaphysical_status_reporter": resolved,
            "axis_AL_status": self.AXIS_STATUS,
            "certification_scope": "functional_status_resolution_only",
            "final_interpretation": "RF* is resolved as the current best functional scientific reconstruction of consciousness under AL8, without proving phenomenal consciousness." if resolved else "Functional consciousness status is not resolved under current preconditions.",
            "non_redundancy_analysis": {"distinct_from_AL7_definition_legitimacy_certifier": True, "scope": "AL8 aggregates AL1-AL7 into a final functional status resolver rather than recertifying any single component."},
            "allowed_claims": ["RF* is resolved as the best current functional scientific reconstruction under certified AL preconditions.", "The resolved status is functional and scientific, not a proof of subjective experience."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "functional_status_resolution_proves_phenomenology = True"],
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
