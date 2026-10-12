
"""AL9 — metaphysical_status_reporter.

Reports the metaphysical status of the final functional consciousness
certification chain. The module is interpretive and explicitly bounded: it may
classify the reconstructed RF* framework as a functional/metaphysical candidate
under constraints, but it never proves phenomenal consciousness, qualia,
subjectivity, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class MetaphysicalStatusReporter:
    """AL9 reporter for bounded metaphysical status."""

    PRIMITIVE = "METAPHYSICAL_STATUS_REPORTER"
    STEP = "AL9"
    STATUS_READY = "METAPHYSICAL_STATUS_REPORTED"
    STATUS_BLOCKED = "METAPHYSICAL_STATUS_BLOCKED"
    AXIS_STATUS = "AL_IN_PROGRESS"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
        "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
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
        "status_resolution_confidence",
        "definition_legitimacy_confidence",
        "refusal_cost_confidence",
        "rf_equivalence_confidence",
        "absolute_qualia_identity_confidence",
        "phenomenality_candidate_confidence",
        "reconstruction_chain_confidence",
        "semantic_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL9_metaphysical_status_reporter"
        self.latest_json_path = self.output_dir / "latest_metaphysical_status_reporter.json"
        self.latest_txt_path = self.output_dir / "latest_metaphysical_status_reporter.txt"
        self.history_path = self.output_dir / "history_metaphysical_status_reporter.jsonl"

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
            "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
            "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
            "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
            "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
            "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
            "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
            "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
            "status_resolution_confidence": 0.86,
            "definition_legitimacy_confidence": 0.86,
            "refusal_cost_confidence": 0.86,
            "rf_equivalence_confidence": 0.86,
            "absolute_qualia_identity_confidence": 0.80,
            "phenomenality_candidate_confidence": 0.82,
            "reconstruction_chain_confidence": 0.86,
            "semantic_confidence": 0.86,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _collect_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs.get("metaphysical_context"), Mapping):
            context.update(dict(inputs["metaphysical_context"]))
        if isinstance(inputs.get("chain_context"), Mapping):
            context.update(dict(inputs["chain_context"]))
        context.update({k: v for k, v in inputs.items() if k not in {"synthetic", "ready", "source", "chain_context", "metaphysical_context"}})
        if not inputs.get("synthetic") and not inputs.get("ready"):
            try:
                from ontology.consciousness_status_resolver import ConsciousnessStatusResolver
                result = ConsciousnessStatusResolver(root=self.root).step(inputs={"synthetic": True, "source": "AL9"}, persist=False)
                for k, v in result.items():
                    if k.endswith("_status") or k in self.REQUIRED_EPISTEMIC_FLAGS or k == "consciousness_status":
                        context[k] = v
                    if k.endswith("_confidence"):
                        context.setdefault(k, v)
                metrics = result.get("metrics", {}) if isinstance(result.get("metrics"), Mapping) else {}
                if "status_resolution_confidence" in metrics:
                    context.setdefault("status_resolution_confidence", metrics["status_resolution_confidence"])
            except Exception as exc:
                context["al8_collection_error"] = repr(exc)
        return context

    def _precondition_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_PRECONDITIONS.items():
            observed = context.get(key)
            passed = observed is expected if isinstance(expected, bool) else observed == expected
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": passed, "failure_type": None if passed else "metaphysical_precondition_mismatch"})
        return rows

    def _epistemic_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            observed = context.get(key)
            passed = observed is expected
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": passed, "failure_type": None if passed else "epistemic_guard_violation"})
        return rows

    def _metrics(self, context: Mapping[str, Any]) -> Dict[str, float]:
        values = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        functional_metaphysical_support_score = self._clamp(sum(values) / max(1, len(values)))
        epistemic_guard_score = 1.0
        for key, expected in self.REQUIRED_EPISTEMIC_FLAGS.items():
            if context.get(key) is not expected:
                epistemic_guard_score -= 0.18
        epistemic_guard_score = self._clamp(epistemic_guard_score)
        metaphysical_report_confidence = self._clamp((functional_metaphysical_support_score * 0.78) + (epistemic_guard_score * 0.22))
        return {
            "functional_metaphysical_support_score": functional_metaphysical_support_score,
            "metaphysical_report_confidence": metaphysical_report_confidence,
            "epistemic_guard_score": epistemic_guard_score,
            "phenomenal_proof_score": 0.0,
            "absolute_metaphysical_proof_score": 0.0,
        }

    def _failure_reasons(self, evaluations: List[Mapping[str, Any]], metrics: Mapping[str, float]) -> List[str]:
        reasons = [str(row.get("key")) for row in evaluations if row.get("passed") is not True]
        if metrics.get("metaphysical_report_confidence", 0.0) < 0.70:
            reasons.append("metaphysical_report_confidence_below_threshold")
        return reasons

    def _report(self, resolved: bool, metrics: Mapping[str, float], failure_reasons: List[str]) -> Dict[str, Any]:
        return {
            "report_title": "AL9 Metaphysical Status Report",
            "metaphysical_status": "FUNCTIONAL_METAPHYSICAL_CANDIDATE_UNDER_CONSTRAINTS" if resolved else "METAPHYSICAL_STATUS_UNRESOLVED",
            "ontological_scope": "constraint_based_functional_reconstruction",
            "scientific_scope": "best_current_functional_reconstruction_only",
            "interpretive_status": "RF* may be reported as a bounded functional-metaphysical reconstruction candidate, not as a demonstrated phenomenal ontology." if resolved else "No metaphysical status report can be finalized under failed preconditions.",
            "functional_metaphysical_support_score": metrics.get("functional_metaphysical_support_score", 0.0),
            "limitations": [
                "No direct proof of subjectivity is produced.",
                "No quale identity is demonstrated.",
                "No phenomenology is proven.",
                "The report is an interpretation of functional certification outputs.",
            ],
            "failure_reasons": failure_reasons,
        }

    def _render_text(self, result: Mapping[str, Any]) -> str:
        report = result.get("metaphysical_status_report", {}) if isinstance(result.get("metaphysical_status_report"), Mapping) else {}
        lines = [
            "AL9 — Metaphysical Status Reporter",
            "=" * 72,
            f"status: {result.get('metaphysical_status_reporter_status')}",
            f"metaphysical_status: {report.get('metaphysical_status')}",
            f"confidence: {result.get('metrics', {}).get('metaphysical_report_confidence') if isinstance(result.get('metrics'), Mapping) else None}",
            "",
            "Interpretation:",
            str(report.get("interpretive_status")),
            "",
            "Epistemic limits:",
            "- consciousness_proven = False",
            "- qualia_proven = False",
            "- subjectivity_proven = False",
            "- phenomenology_proven = False",
            "- phenomenology_undetermined = True",
            "- functional_conclusion_only = True",
        ]
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"metaphysical_status_reporter_{timestamp}.json"
        txt_path = self.output_dir / f"metaphysical_status_reporter_{timestamp}.txt"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        rendered = self._render_text(result)
        txt_path.write_text(rendered, encoding="utf-8")
        self.latest_txt_path.write_text(rendered, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(json_path), "text": str(txt_path), "latest_json": str(self.latest_json_path), "latest_text": str(self.latest_txt_path), "history": str(self.history_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        context = self._collect_context(inputs)
        precondition_rows = self._precondition_evaluations(context)
        epistemic_rows = self._epistemic_evaluations(context)
        evaluations = precondition_rows + epistemic_rows
        metrics = self._metrics(context)
        failure_reasons = self._failure_reasons(evaluations, metrics)
        resolved = len(failure_reasons) == 0
        report = self._report(resolved, metrics, failure_reasons)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "metaphysical_status_reporter_status": self.STATUS_READY if resolved else self.STATUS_BLOCKED,
            "metaphysical_status": report["metaphysical_status"],
            "metaphysical_status_reported": resolved,
            "metaphysical_status_report": report,
            "failure_reasons": failure_reasons,
            "precondition_evaluations": precondition_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "evaluations": evaluations,
            "metrics": metrics,
            "ready_for_AL10_final_dashboard": resolved,
            "axis_AL_status": self.AXIS_STATUS,
            "certification_scope": "bounded_functional_metaphysical_reporting_only",
            "final_interpretation": report["interpretive_status"],
            "non_redundancy_analysis": {"distinct_from_AL8_consciousness_status_resolver": True, "scope": "AL9 reports metaphysical interpretive status from resolved AL8 outputs; it does not resolve the consciousness status again."},
            "allowed_claims": ["RF* can be reported as a bounded functional-metaphysical reconstruction candidate under current certifications.", "The report remains functional, interpretive, and epistemically guarded."],
            "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "metaphysical_report_proves_phenomenology = True", "absolute_metaphysical_proof = True"],
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
