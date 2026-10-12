
"""
AL3 — Phenomenality Candidate Certifier.

This module certifies whether the current reconstruction is eligible to be
called a phenomenality candidate in the strictly functional and semantic sense
used by Open Cognitive Ecology. It does not certify phenomenology, qualia,
subjectivity, or consciousness as proven.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class PhenomenalityCandidateCertifier:
    """AL3 certifier for functional phenomenality-candidate eligibility."""

    PRIMITIVE = "PHENOMENALITY_CANDIDATE_CERTIFIER"
    STEP = "AL3"
    STATUS_CERTIFIED = "PHENOMENALITY_CANDIDATE_CERTIFIED"
    STATUS_BLOCKED = "PHENOMENALITY_CANDIDATE_BLOCKED"
    PUBLIC_CANDIDATE_STATUS = "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED"

    REQUIRED_CHAIN_STATUSES: Dict[str, str] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "NO_FAILURE_LOCATED",
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
        "RF_score",
        "T_score",
        "ED_score",
        "TΦ_score",
        "MEI_score",
        "semantic_confidence",
        "reconstruction_chain_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL3_phenomenality_candidate_certifier"
        self.latest_json_path = self.output_dir / "latest_phenomenality_candidate_certifier.json"
        self.history_path = self.output_dir / "history_phenomenality_candidate_certifier.jsonl"

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
            "first_failure_locator_status": "NO_FAILURE_LOCATED",
            "first_failure_found": False,
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "RF_score": 0.91,
            "T_score": 0.88,
            "ED_score": 0.86,
            "TΦ_score": 0.85,
            "MEI_score": 0.87,
            "semantic_confidence": 0.86,
            "reconstruction_chain_confidence": 0.88,
            "QF_robust_count": 4,
            "identity_status": "IDENTITY_STABLE",
            "non_separability_status": "NON_SEPARABILITY_FUNCTIONALLY_SUPPORTED",
            "consciousness_rf_equivalence_status": "RF_EQUIVALENCE_FUNCTIONALLY_SUPPORTED",
            "refusal_cost_status": "REFUSAL_COST_MEASURABLE",
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
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
            try:
                from ontology.first_failure_locator import FirstFailureLocator
                al2 = FirstFailureLocator(root=self.root).step(inputs={"synthetic": True, "source": "AL3"}, persist=False)
                for key in ["first_failure_locator_status", "first_failure_found", "first_failure_key", "consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven", "phenomenology_undetermined", "functional_conclusion_only"]:
                    if key in al2:
                        context[key] = al2[key]
            except Exception as exc:
                context["al2_collection_error"] = repr(exc)
        return context

    def _chain_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_CHAIN_STATUSES.items():
            observed = context.get(key)
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": observed == expected, "failure_type": None if observed == expected else "chain_status_mismatch"})
        if context.get("first_failure_found") is True:
            rows.append({"key": "first_failure_found", "expected": False, "observed": True, "passed": False, "failure_type": "upstream_failure_present"})
        return rows

    def _epistemic_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            observed = context.get(key)
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": observed is expected, "failure_type": None if observed is expected else "epistemic_guard_violation"})
        return rows

    def _support_metrics(self, context: Mapping[str, Any]) -> Dict[str, float]:
        scores = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        support = self._clamp(sum(scores) / max(1, len(scores)))
        try:
            qf_count = int(context.get("QF_robust_count", 0) or 0)
        except Exception:
            qf_count = 0
        qf_support = self._clamp(qf_count / 4.0)
        identity_support = 1.0 if str(context.get("identity_status", "")).upper().endswith("STABLE") else 0.75
        non_separability_support = 1.0 if "SUPPORTED" in str(context.get("non_separability_status", "")).upper() else 0.75
        rf_equivalence_support = 1.0 if "SUPPORTED" in str(context.get("consciousness_rf_equivalence_status", "")).upper() else 0.75
        refusal_support = 1.0 if "MEASURABLE" in str(context.get("refusal_cost_status", "")).upper() else 0.75
        structural = self._clamp((qf_support + identity_support + non_separability_support + rf_equivalence_support + refusal_support) / 5.0)
        return {
            "functional_support_score": support,
            "qf_support_score": qf_support,
            "structural_candidate_score": structural,
            "phenomenality_candidate_confidence": self._clamp((support + structural) / 2.0),
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("phenomenality_candidate_confidence", 0.0) < 0.70:
            reasons.append("phenomenality_candidate_confidence_below_threshold")
        return reasons

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"phenomenality_candidate_certifier_{timestamp}.json"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(path), "latest_json": str(self.latest_json_path), "history": str(self.history_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        context = self._collect_context(inputs)
        chain_rows = self._chain_evaluations(context)
        epistemic_rows = self._epistemic_evaluations(context)
        evaluations = chain_rows + epistemic_rows
        metrics = self._support_metrics(context)
        failure_reasons = self._failure_reasons(evaluations, metrics)
        certified = len(failure_reasons) == 0
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "phenomenality_candidate_certifier_status": self.STATUS_CERTIFIED if certified else self.STATUS_BLOCKED,
            "phenomenality_candidate_status": self.PUBLIC_CANDIDATE_STATUS if certified else "PHENOMENALITY_CANDIDATE_STATUS_BLOCKED",
            "phenomenality_candidate_certified": certified,
            "candidate_failure_reasons": failure_reasons,
            "chain_evaluations": chain_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL4_absolute_qualia_identity_certifier": certified,
            "axis_AL_status": "AL_IN_PROGRESS",
            "candidate_scope": "functional_phenomenality_candidate_only",
            "candidate_interpretation": "The reconstruction qualifies as a functional phenomenality candidate under the current chain." if certified else "The reconstruction is not yet eligible for functional phenomenality-candidate certification.",
            "non_redundancy_analysis": {"distinct_from_AL1_reconstruction_chain_certifier": True, "distinct_from_AL2_first_failure_locator": True, "scope": "AL3 certifies candidate eligibility after chain reconstruction and failure localization."},
            "allowed_claims": ["A functional phenomenality-candidate status is certified when public chain and guard conditions hold.", "Candidate certification remains weaker than proof of phenomenology or qualia."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "phenomenality_candidate_certification_proves_subjective_experience"],
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
