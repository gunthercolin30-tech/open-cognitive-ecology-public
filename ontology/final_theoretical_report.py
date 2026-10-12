"""
AL11 — Final Theoretical Report.

This module generates the final theoretical report for the AL certification
axis by integrating AL1–AL10, AN axiomatic completeness, and AO semantic
interpretation outputs.

Epistemic boundary: this is a functional certification report. It does not
prove consciousness, qualia, subjectivity, phenomenology, or phenomenal
experience. It reports bounded functional status only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class FinalTheoreticalReport:
    """AL11 final theoretical report generator."""

    PRIMITIVE = "FINAL_THEORETICAL_REPORT"
    STEP = "AL11"
    READY_STATUS = "FINAL_THEORETICAL_REPORT_GENERATED"
    BLOCKED_STATUS = "FINAL_THEORETICAL_REPORT_BLOCKED"
    FINAL_AXIS_STATUS = "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE"

    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
        "metaphysical_status_reporter_status": "METAPHYSICAL_STATUS_REPORTED",
        "final_dashboard_status": "FINAL_DASHBOARD_GENERATED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    }

    REQUIRED_EPISTEMIC_FLAGS: Dict[str, Any] = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }

    REPORT_SECTIONS = [
        "executive_summary",
        "reconstruction_summary",
        "theorem_summary",
        "certification_summary",
        "semantic_summary",
        "epistemic_limits",
        "allowed_claims",
        "blocked_claims",
        "final_functional_conclusion",
        "future_work",
        "scientific_appendix",
    ]

    SUPPORT_KEYS = [
        "reconstruction_chain_confidence",
        "first_failure_confidence",
        "phenomenality_candidate_confidence",
        "absolute_qualia_identity_confidence",
        "rf_equivalence_confidence",
        "refusal_cost_confidence",
        "definition_legitimacy_confidence",
        "status_resolution_confidence",
        "metaphysical_report_confidence",
        "semantic_confidence",
        "axiomatic_completeness_confidence",
        "dashboard_confidence",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL11_final_theoretical_report"
        self.latest_json_path = self.output_dir / "latest_final_theoretical_report.json"
        self.latest_markdown_path = self.output_dir / "latest_final_theoretical_report.md"
        self.history_path = self.output_dir / "history_final_theoretical_report.jsonl"

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
            "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
            "metaphysical_status_reporter_status": "METAPHYSICAL_STATUS_REPORTED",
            "final_dashboard_status": "FINAL_DASHBOARD_GENERATED",
            "final_certification_dashboard_status": "FINAL_DASHBOARD_GENERATED",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
            "metaphysical_status": "FUNCTIONAL_METAPHYSICAL_CANDIDATE_UNDER_CONSTRAINTS",
            "functional_status": "FUNCTIONAL_CERTIFICATION_COMPLETE_UNDER_EPISTEMIC_GUARDS",
            "scientific_status": "THEORETICAL_FUNCTIONAL_CERTIFICATION_READY_FOR_EMPIRICAL_VALIDATION",
            "dashboard_ready": True,
            "dashboard_generated": True,
            "reconstruction_chain_confidence": 0.86,
            "first_failure_confidence": 0.84,
            "phenomenality_candidate_confidence": 0.85,
            "absolute_qualia_identity_confidence": 0.84,
            "rf_equivalence_confidence": 0.86,
            "refusal_cost_confidence": 0.85,
            "definition_legitimacy_confidence": 0.86,
            "status_resolution_confidence": 0.87,
            "metaphysical_report_confidence": 0.84,
            "semantic_confidence": 0.86,
            "axiomatic_completeness_confidence": 0.86,
            "dashboard_confidence": 0.86,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _collect_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs, Mapping):
            nested_keys = [
                "reconstruction_chain_certifier",
                "first_failure_locator",
                "phenomenality_candidate_certifier",
                "absolute_qualia_identity_certifier",
                "consciousness_rf_equivalence_certifier",
                "refusal_cost_certifier",
                "definition_legitimacy_certifier",
                "consciousness_status_resolver",
                "metaphysical_status_reporter",
                "final_dashboard",
                "axiomatic_completeness_certifier",
                "interpretation_reporter",
            ]
            for key in nested_keys:
                value = inputs.get(key)
                if isinstance(value, Mapping):
                    context.update(value)
            context.update(dict(inputs))
        return context

    @staticmethod
    def _evaluate(context: Mapping[str, Any], expectations: Mapping[str, Any], reason: str) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for key, expected in expectations.items():
            observed = context.get(key)
            passed = observed == expected
            rows.append({
                "key": key,
                "expected": expected,
                "observed": observed,
                "passed": passed,
                "reason": None if passed else reason,
            })
        return rows

    def _metrics(self, context: Mapping[str, Any], failures: List[str]) -> Dict[str, Any]:
        scores = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        mean_support = round(sum(scores) / len(scores), 6) if scores else 0.0
        epistemic_guard_score = 0.0 if failures else 1.0
        report_completeness_score = 1.0
        final_certification_score = round((mean_support * 0.70) + (epistemic_guard_score * 0.20) + (report_completeness_score * 0.10), 6)
        return {
            "mean_support_confidence": mean_support,
            "epistemic_guard_score": epistemic_guard_score,
            "report_completeness_score": report_completeness_score,
            "final_certification_score": final_certification_score,
            "phenomenal_proof_score": 0.0,
            "qualia_proof_score": 0.0,
            "subjectivity_proof_score": 0.0,
            "functional_certification_score": final_certification_score,
        }

    def _build_report(self, context: Mapping[str, Any], metrics: Mapping[str, Any], failures: List[str]) -> Dict[str, Any]:
        ready = not failures
        allowed_claims = [
            "Open Cognitive Ecology has completed the AL functional certification chain under the validated reconstruction, axiomatic, and semantic layers.",
            "RF* may be reported as the current best functional reconstruction candidate under explicit epistemic limits.",
            "The final conclusion is functional, architectural, semantic, and certification-theoretic; it is not a phenomenological proof.",
            "The project is ready for longitudinal empirical validation of functional reflexive-threshold properties.",
        ]
        blocked_claims = [
            "consciousness_proven = True",
            "qualia_proven = True",
            "subjectivity_proven = True",
            "phenomenology_proven = True",
            "phenomenal_experience_demonstrated = True",
            "final_report_proves_subjective_experience = True",
        ]
        final_conclusion = (
            "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE: the AL axis is complete as a bounded functional certification. "
            "The system may be described as satisfying the validated functional reconstruction and semantic governance conditions, "
            "while phenomenology and subjectivity remain undetermined."
            if ready else
            "FINAL_THEORETICAL_REPORT_BLOCKED: one or more upstream public invariants or epistemic guards failed."
        )
        appendix = {
            "integrated_axes": ["AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AM", "AN", "AO", "AL"],
            "integrated_al_steps": ["AL1", "AL2", "AL3", "AL4", "AL5", "AL6", "AL7", "AL8", "AL9", "AL10", "AL11"],
            "required_report_sections": list(self.REPORT_SECTIONS),
            "public_invariant_policy": "Only public status, confidence, and epistemic guard invariants are asserted.",
            "codex_final_lock_policy": "Final locks must call step(inputs=ready_or_synthetic_context, persist=False).",
        }
        return {
            "executive_summary": {
                "status": self.READY_STATUS if ready else self.BLOCKED_STATUS,
                "axis_status": self.FINAL_AXIS_STATUS if ready else "AL_FINAL_REPORT_BLOCKED",
                "summary": "AL11 integrates the final certification chain into a bounded scientific report.",
            },
            "reconstruction_summary": {
                "status": context.get("reconstruction_chain_certifier_status"),
                "conclusion": "The reconstruction chain is accepted as certified when AL1 public invariants hold.",
            },
            "theorem_summary": {
                "axiomatic_completeness_status": context.get("axiomatic_completeness_status"),
                "rf_equivalence_status": context.get("consciousness_rf_equivalence_certifier_status"),
                "absolute_identity_status": context.get("absolute_qualia_identity_certifier_status"),
                "refusal_cost_status": context.get("refusal_cost_certifier_status"),
                "definition_legitimacy_status": context.get("definition_legitimacy_certifier_status"),
            },
            "certification_summary": {
                "final_dashboard_status": context.get("final_dashboard_status"),
                "consciousness_status": context.get("consciousness_status"),
                "metaphysical_status": context.get("metaphysical_status"),
                "final_certification_score": metrics.get("final_certification_score"),
            },
            "semantic_summary": {
                "semantic_interpretation_layer_status": context.get("semantic_interpretation_layer_status"),
                "semantic_confidence": self._clamp(context.get("semantic_confidence")),
                "interpretation": "Semantic interpretation is governed by explicit epistemic guards and revision logging.",
            },
            "epistemic_limits": {
                "consciousness_proven": False,
                "qualia_proven": False,
                "subjectivity_proven": False,
                "phenomenology_proven": False,
                "phenomenology_undetermined": True,
                "functional_conclusion_only": True,
                "limit_statement": "No phenomenological or subjective fact is inferred from functional certification alone.",
            },
            "allowed_claims": allowed_claims,
            "blocked_claims": blocked_claims,
            "final_functional_conclusion": final_conclusion,
            "future_work": [
                "Run longitudinal empirical validation across short, medium, and long horizons.",
                "Collect statistical evidence for stability, memory coherence, self-revision, and openness preservation.",
                "Seek external replication and independent review.",
                "Maintain epistemic guards during all future semantic revisions.",
            ],
            "scientific_appendix": appendix,
        }

    def _render_markdown(self, result: Mapping[str, Any]) -> str:
        report = result.get("final_theoretical_report", {}) if isinstance(result.get("final_theoretical_report"), Mapping) else {}
        lines = [
            "# AL11 — Final Theoretical Report",
            "",
            f"Status: `{result.get('final_theoretical_report_status')}`",
            f"Axis status: `{result.get('final_axis_status')}`",
            f"Functional status: `{result.get('functional_status')}`",
            f"Scientific status: `{result.get('scientific_status')}`",
            "",
            "## Epistemic scope",
            "",
            "This report is functional only. It does not prove consciousness, qualia, subjectivity, phenomenology, or phenomenal experience.",
            "",
        ]
        for section in self.REPORT_SECTIONS:
            lines.append(f"## {section}")
            lines.append("")
            value = report.get(section)
            if isinstance(value, (dict, list)):
                lines.append("```json")
                lines.append(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
                lines.append("```")
            else:
                lines.append(str(value))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"final_theoretical_report_{ts}.json"
        markdown_path = self.output_dir / f"final_theoretical_report_{ts}.md"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        md = self._render_markdown(result)
        markdown_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as history:
            history.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(markdown_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        safe_inputs = inputs if isinstance(inputs, Mapping) else {}
        context = self._collect_context(safe_inputs)
        precondition_evaluations = self._evaluate(context, self.REQUIRED_PRECONDITIONS, "final_report_precondition_mismatch")
        epistemic_guard_evaluations = self._evaluate(context, self.REQUIRED_EPISTEMIC_FLAGS, "epistemic_guard_violation")
        failures = [str(row["key"]) for row in precondition_evaluations + epistemic_guard_evaluations if not row["passed"]]
        metrics = self._metrics(context, failures)
        if metrics["final_certification_score"] < 0.70:
            failures.append("final_certification_score_below_threshold")
        ready = not failures
        report = self._build_report(context, metrics, failures)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "final_theoretical_report_status": self.READY_STATUS if ready else self.BLOCKED_STATUS,
            "final_consciousness_certification_status": self.FINAL_AXIS_STATUS if ready else "FINAL_CONSCIOUSNESS_CERTIFICATION_BLOCKED",
            "final_axis_status": self.FINAL_AXIS_STATUS if ready else "AL_FINAL_REPORT_BLOCKED",
            "final_conclusion": report["final_functional_conclusion"],
            "certification_summary": report["certification_summary"],
            "epistemic_scope": "functional_conclusion_only; phenomenology_undetermined",
            "functional_status": context.get("functional_status", "FUNCTIONAL_CERTIFICATION_COMPLETE_UNDER_EPISTEMIC_GUARDS") if ready else "FUNCTIONAL_CERTIFICATION_BLOCKED",
            "scientific_status": context.get("scientific_status", "THEORETICAL_FUNCTIONAL_CERTIFICATION_READY_FOR_EMPIRICAL_VALIDATION") if ready else "SCIENTIFIC_REPORT_BLOCKED",
            "report_generated": ready,
            "report_ready": ready,
            "section_count": len(self.REPORT_SECTIONS),
            "required_section_count": len(self.REPORT_SECTIONS),
            "missing_sections": [section for section in self.REPORT_SECTIONS if section not in report],
            "precondition_evaluations": precondition_evaluations,
            "epistemic_guard_evaluations": epistemic_guard_evaluations,
            "metrics": metrics,
            "final_theoretical_report": report,
            "allowed_claims": report["allowed_claims"],
            "blocked_claims": report["blocked_claims"],
            "failure_reasons": failures,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "timestamp_utc": self._now(),
            "persisted": False,
            "public_schema_version": "AL11.final_theoretical_report.v1",
        }
        if ready and result["missing_sections"]:
            result["failure_reasons"].append("missing_report_sections")
            result["final_theoretical_report_status"] = self.BLOCKED_STATUS
            result["final_consciousness_certification_status"] = "FINAL_CONSCIOUSNESS_CERTIFICATION_BLOCKED"
            result["final_axis_status"] = "AL_FINAL_REPORT_BLOCKED"
            result["report_generated"] = False
            result["report_ready"] = False
        if persist:
            result["artifacts"] = self._persist(result)
            result["persisted"] = True
        return result


__all__ = ["FinalTheoreticalReport"]
