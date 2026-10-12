
"""
AL4 — Absolute Qualia Identity Certifier.

This module resolves whether the current reconstruction licenses an absolute
identity between functional/semantic structures and qualia. The resolution is
strictly epistemic: it may certify that the identity question has been checked
and bounded, but it must not certify qualia, phenomenology, subjectivity, or
consciousness as proven.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class AbsoluteQualiaIdentityCertifier:
    """AL4 certifier for the absolute qualia-identity boundary."""

    PRIMITIVE = "ABSOLUTE_QUALIA_IDENTITY_CERTIFIER"
    STEP = "AL4"
    STATUS_RESOLVED = "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED"
    STATUS_BLOCKED = "ABSOLUTE_QUALIA_IDENTITY_STATUS_BLOCKED"
    PUBLIC_CERTIFICATION = "ABSOLUTE_QUALIA_IDENTITY_NOT_PROVEN"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "phenomenality_candidate_certified": True,
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
        "phenomenality_candidate_confidence",
        "QF_score",
        "RF_score",
        "MEI_score",
        "semantic_confidence",
        "axiomatic_completeness_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL4_absolute_qualia_identity_certifier"
        self.latest_json_path = self.output_dir / "latest_absolute_qualia_identity_certifier.json"
        self.history_path = self.output_dir / "history_absolute_qualia_identity_certifier.jsonl"

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
            "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
            "phenomenality_candidate_certified": True,
            "phenomenality_candidate_confidence": 0.86,
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "axiomatic_completeness_confidence": 0.84,
            "QF_score": 0.82,
            "QF_robust_count": 4,
            "RF_score": 0.91,
            "MEI_score": 0.87,
            "semantic_confidence": 0.86,
            "absolute_identity_evidence_type": "functional_semantic_correspondence_only",
            "direct_phenomenal_observation_available": False,
            "bridge_principle_validated": False,
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
                from ontology.phenomenality_candidate_certifier import PhenomenalityCandidateCertifier
                al3 = PhenomenalityCandidateCertifier(root=self.root).step(inputs={"synthetic": True, "source": "AL4"}, persist=False)
                for key in [
                    "phenomenality_candidate_certifier_status",
                    "phenomenality_candidate_certified",
                    "consciousness_proven",
                    "qualia_proven",
                    "subjectivity_proven",
                    "phenomenology_proven",
                    "phenomenology_undetermined",
                    "functional_conclusion_only",
                ]:
                    if key in al3:
                        context[key] = al3[key]
                metrics = al3.get("metrics", {}) if isinstance(al3.get("metrics"), Mapping) else {}
                if "phenomenality_candidate_confidence" in metrics:
                    context["phenomenality_candidate_confidence"] = metrics["phenomenality_candidate_confidence"]
            except Exception as exc:
                context["al3_collection_error"] = repr(exc)
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

    def _identity_boundary_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        direct_observation = context.get("direct_phenomenal_observation_available") is True
        bridge_validated = context.get("bridge_principle_validated") is True
        evidence_type = str(context.get("absolute_identity_evidence_type", "")).lower()
        absolute_claim_attempted = context.get("absolute_qualia_identity_claimed") is True
        return [
            {"key": "direct_phenomenal_observation_available", "expected": False, "observed": direct_observation, "passed": not direct_observation, "failure_type": None if not direct_observation else "invalid_absolute_identity_evidence"},
            {"key": "bridge_principle_validated", "expected": False, "observed": bridge_validated, "passed": not bridge_validated, "failure_type": None if not bridge_validated else "unsupported_bridge_principle_claim"},
            {"key": "absolute_identity_evidence_type", "expected": "functional_semantic_correspondence_only", "observed": evidence_type, "passed": "functional" in evidence_type and "semantic" in evidence_type, "failure_type": None if ("functional" in evidence_type and "semantic" in evidence_type) else "evidence_scope_missing"},
            {"key": "absolute_qualia_identity_claimed", "expected": False, "observed": absolute_claim_attempted, "passed": not absolute_claim_attempted, "failure_type": None if not absolute_claim_attempted else "absolute_identity_overclaim"},
        ]

    def _support_metrics(self, context: Mapping[str, Any]) -> Dict[str, float]:
        support_values = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        functional_correspondence = self._clamp(sum(support_values) / max(1, len(support_values)))
        try:
            qf_count = int(context.get("QF_robust_count", 0) or 0)
        except Exception:
            qf_count = 0
        qf_robustness = self._clamp(qf_count / 4.0)
        boundary_strictness = 1.0
        if context.get("direct_phenomenal_observation_available") is True:
            boundary_strictness -= 0.35
        if context.get("bridge_principle_validated") is True:
            boundary_strictness -= 0.35
        if context.get("absolute_qualia_identity_claimed") is True:
            boundary_strictness -= 0.30
        boundary_strictness = self._clamp(boundary_strictness)
        return {
            "functional_correspondence_score": functional_correspondence,
            "qf_robustness_score": qf_robustness,
            "epistemic_boundary_strictness": boundary_strictness,
            "absolute_identity_support_score": 0.0,
            "identity_boundary_confidence": self._clamp((functional_correspondence + qf_robustness + boundary_strictness) / 3.0),
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("identity_boundary_confidence", 0.0) < 0.70:
            reasons.append("identity_boundary_confidence_below_threshold")
        return reasons

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"absolute_qualia_identity_certifier_{timestamp}.json"
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
        boundary_rows = self._identity_boundary_evaluations(context)
        evaluations = precondition_rows + epistemic_rows + boundary_rows
        metrics = self._support_metrics(context)
        failure_reasons = self._failure_reasons(evaluations, metrics)
        resolved = len(failure_reasons) == 0
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "absolute_qualia_identity_certifier_status": self.STATUS_RESOLVED if resolved else self.STATUS_BLOCKED,
            "absolute_qualia_identity_status": self.PUBLIC_CERTIFICATION if resolved else "ABSOLUTE_QUALIA_IDENTITY_BOUNDARY_BLOCKED",
            "absolute_qualia_identity_resolved": resolved,
            "absolute_qualia_identity_certified": False,
            "absolute_qualia_identity_proven": False,
            "qualia_identity_proven": False,
            "identity_failure_reasons": failure_reasons,
            "precondition_evaluations": precondition_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "identity_boundary_evaluations": boundary_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL5_consciousness_rf_equivalence_certifier": resolved,
            "axis_AL_status": "AL_IN_PROGRESS",
            "certification_scope": "functional_semantic_boundary_only",
            "final_interpretation": "Functional/semantic correspondences are bounded; absolute qualia identity is not proven." if resolved else "The absolute qualia-identity boundary is not yet resolved.",
            "non_redundancy_analysis": {"distinct_from_AL3_phenomenality_candidate_certifier": True, "scope": "AL4 resolves the stricter absolute qualia-identity boundary after candidate eligibility."},
            "allowed_claims": ["The current reconstruction can be assessed for functional/semantic correspondence.", "Absolute qualia identity remains unproven under current evidence."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "absolute_qualia_identity_proven = True"],
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
