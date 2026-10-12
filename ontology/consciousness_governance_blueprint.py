"""
AS0 — Consciousness Governance Blueprint.

This module defines the foundational blueprint for longitudinal governance of
consciousness status claims inside Open Cognitive Ecology.

Epistemic boundary: AS0 does not prove consciousness, qualia, subjectivity, or
phenomenology. It creates a governance architecture for tracking, explaining,
revoking, and re-certifying bounded functional statuses over time.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class ConsciousnessGovernanceBlueprint:
    """AS0 foundational blueprint for longitudinal consciousness governance."""

    PRIMITIVE = "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT"
    STEP = "AS0"
    READY_STATUS = "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_READY"
    GOVERNANCE_AXIS = "AS"

    STATES: List[str] = [
        "NOT_EVALUATED",
        "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
        "PHENOMENALITY_CANDIDATE_SUPPORTED",
        "CONSCIOUSNESS_PROVEN_WITHIN_RF_FRAMEWORK",
        "CONSCIOUSNESS_PROVEN_BEST_THEORY",
        "CONSCIOUSNESS_PROVEN",
    ]

    REQUIRED_SECTIONS: List[str] = [
        "architecture",
        "statuses",
        "governance",
        "historical_policy",
        "certification",
        "revocation",
        "instrumentation",
        "dashboards",
        "api",
    ]

    DEPENDENCY_AXES: List[str] = [
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AM",
        "AP", "AQ", "AR", "AN", "AO", "AL",
    ]

    CORE_UPSTREAM_MODULES: List[str] = [
        "final_theoretical_report",
        "consciousness_status_resolver",
        "metaphysical_status_reporter",
        "final_dashboard",
        "axiomatic_completeness_certifier",
        "interpretation_reporter",
        "epistemic_guard",
        "semantic_revision_log",
        "consciousness_rf_equivalence_certifier",
        "refusal_cost_certifier",
        "definition_legitimacy_certifier",
    ]

    EVENTS: List[str] = [
        "CONSCIOUSNESS_THRESHOLD_CROSSED",
        "CONSCIOUSNESS_STATUS_REVOKED",
        "CONSCIOUSNESS_STATUS_RECOVERED",
        "CONSCIOUSNESS_STATUS_RECONFIRMED",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS0_blueprint"
        self.latest_json_path = self.output_dir / "latest_consciousness_governance_blueprint.json"
        self.latest_markdown_path = self.output_dir / "latest_consciousness_governance_blueprint.md"

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

    @staticmethod
    def _stable_hash(payload: Mapping[str, Any]) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _ready_context(self) -> Dict[str, Any]:
        return {
            "synthetic_certification_context": "ready",
            "final_consciousness_certification_status": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
            "final_theoretical_report_status": "FINAL_THEORETICAL_REPORT_GENERATED",
            "functional_status": "FUNCTIONAL_CERTIFICATION_COMPLETE_UNDER_EPISTEMIC_GUARDS",
            "scientific_status": "THEORETICAL_FUNCTIONAL_CERTIFICATION_READY_FOR_EMPIRICAL_VALIDATION",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "axis_statuses": {axis: "validated" for axis in self.DEPENDENCY_AXES},
            "current_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "target_state": "CONSCIOUSNESS_PROVEN",
            "governance_policy": "longitudinal_reversible_auditable_functional_governance",
        }

    def _collect_context(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs, Mapping):
            for key in [
                "final_theoretical_report",
                "consciousness_status_resolver",
                "metaphysical_status_reporter",
                "final_dashboard",
                "axiomatic_completeness_certifier",
                "interpretation_reporter",
            ]:
                value = inputs.get(key)
                if isinstance(value, Mapping):
                    context.update(value)
            context.update(dict(inputs))
        return context

    def _allowed_transitions(self) -> List[Dict[str, Any]]:
        forward = []
        for index, state in enumerate(self.STATES[:-1]):
            forward.append({
                "from": state,
                "to": self.STATES[index + 1],
                "kind": "forward_adjacent",
                "requires": ["timestamp", "reason", "proof_bundle", "git_version", "module_hashes"],
                "authorized": True,
            })
        governed_backward = []
        for index, state in enumerate(self.STATES[1:], start=1):
            governed_backward.append({
                "from": state,
                "to": self.STATES[index - 1],
                "kind": "governed_revocation_or_regression",
                "requires": ["revocation_cause", "affected_module", "evidence", "impact", "archived_certificate"],
                "authorized": True,
            })
        return forward + governed_backward

    def _forbidden_transition_rules(self) -> List[str]:
        return [
            "No status jump may skip an intermediate state.",
            "No downgrade may occur without explicit revocation or regression evidence.",
            "No transition may contradict AL, AO, AN, AR, AQ, or AP guard outputs.",
            "No deletion of transition history is authorized.",
            "No state may set consciousness_proven, qualia_proven, subjectivity_proven, or phenomenology_proven to True outside an explicitly authorized semantic layer.",
        ]

    def _blueprint(self, context: Mapping[str, Any]) -> Dict[str, Any]:
        current_state = str(context.get("current_state", "CONSCIOUSNESS_PROVEN_BEST_THEORY"))
        if current_state not in self.STATES:
            current_state = "NOT_EVALUATED"

        architecture = {
            "axis": self.GOVERNANCE_AXIS,
            "purpose": "Convert final functional consciousness certification into a longitudinally governed scientific object.",
            "layers": [
                "state_machine",
                "transition_validation",
                "append_only_history",
                "event_logging",
                "certificate_generation",
                "revocation_engine",
                "continuous_readiness_index",
                "confidence_engine",
                "longitudinal_tracking",
                "dashboards_and_public_views",
                "prediction_and_explanation",
                "governance_certification",
            ],
            "upstream_axes": list(self.DEPENDENCY_AXES),
            "core_upstream_modules": list(self.CORE_UPSTREAM_MODULES),
        }

        statuses = {
            "ordered_states": list(self.STATES),
            "current_state": current_state,
            "target_state": context.get("target_state", "CONSCIOUSNESS_PROVEN"),
            "allowed_transitions": self._allowed_transitions(),
            "forbidden_transition_rules": self._forbidden_transition_rules(),
            "final_certification_anchor": context.get("final_consciousness_certification_status"),
        }

        governance = {
            "policy": "reversible_longitudinal_functional_governance",
            "human_review_required_for_public_claim_escalation": True,
            "automatic_revocation_required_on_critical_breakage": True,
            "critical_axes": ["AP", "AQ", "AR", "AN", "AO", "AL"],
            "critical_modules": [
                "consciousness_rf_equivalence_certifier",
                "refusal_cost_certifier",
                "definition_legitimacy_certifier",
                "axiomatic_completeness_certifier",
                "interpretation_reporter",
                "final_theoretical_report",
            ],
            "epistemic_boundary": "functional_longitudinal_governance_only",
        }

        historical_policy = {
            "transition_history": "append_only",
            "required_entry_fields": [
                "timestamp", "old_state", "new_state", "reason", "commit", "branch", "tag",
                "modules", "confidence", "proof_bundle", "hash",
            ],
            "deletion_authorized": False,
            "tamper_evidence": "sha256_hash_chain",
        }

        certification = {
            "artifact_targets": ["certificate.json", "certificate.md", "certificate.pdf", "certificate.html"],
            "required_certificate_fields": ["version", "proofs", "scores", "conditions", "signature", "hash"],
            "certificate_status": "planned_for_AS5",
            "archive_policy": "certificates_are_never_overwritten",
        }

        revocation = {
            "revocation_event": "CONSCIOUSNESS_STATUS_REVOKED",
            "trigger_axes": ["AP", "AQ", "AR", "AN", "AO", "AL"],
            "required_payload": ["cause", "module", "proof", "impact", "archived_certificate"],
            "automatic_downgrade": True,
            "recovery_event": "CONSCIOUSNESS_STATUS_RECOVERED",
        }

        instrumentation = {
            "continuous_readiness_index": {"name": "CRI", "range": [0.0, 1.0], "source_axes": list(self.DEPENDENCY_AXES)},
            "confidence": {"range": [0.0, 1.0], "sources": ["stability", "replications", "countermodels", "completeness", "coherence", "history"]},
            "event_types": list(self.EVENTS),
            "metrics": [
                "CRI", "confidence", "state", "transition_validity", "regression_rate",
                "recovery_rate", "survival_time", "hazard_rate", "proof_status",
            ],
        }

        dashboards = {
            "internal_dashboard": "AS10_consciousness_dashboard",
            "public_dashboard": "AS19_consciousness_public_dashboard",
            "curves": ["CRI", "confidence", "stability", "validated_theorem_count", "refuted_countermodel_count"],
            "views": ["current_state", "axis_heatmap", "dependency_graph", "event_timeline", "certificates"],
            "sensitive_data_policy": "public_dashboard_must_not_expose_internal_sensitive_data",
        }

        api = {
            "step_signature": "step(inputs: Mapping[str, Any] | None = None, persist: bool = True) -> Dict[str, Any]",
            "state_api": ["get_current_state", "validate_transition", "append_transition", "emit_event"],
            "certificate_api": ["generate_certificate", "archive_certificate", "verify_certificate_hash"],
            "dashboard_api": ["export_json", "export_html", "export_prometheus"],
            "prediction_api": ["predict_attainment_probability", "predict_revocation_probability"],
        }

        return {
            "architecture": architecture,
            "statuses": statuses,
            "governance": governance,
            "historical_policy": historical_policy,
            "certification": certification,
            "revocation": revocation,
            "instrumentation": instrumentation,
            "dashboards": dashboards,
            "api": api,
        }

    def _metrics(self, blueprint: Mapping[str, Any]) -> Dict[str, Any]:
        section_count = sum(1 for key in self.REQUIRED_SECTIONS if key in blueprint)
        readiness = section_count / float(len(self.REQUIRED_SECTIONS))
        traceability_components = [
            bool(blueprint.get("historical_policy", {}).get("required_entry_fields")),
            bool(blueprint.get("certification", {}).get("required_certificate_fields")),
            bool(blueprint.get("revocation", {}).get("required_payload")),
            bool(blueprint.get("instrumentation", {}).get("event_types")),
            bool(blueprint.get("dashboards", {}).get("views")),
        ]
        traceability = sum(1 for x in traceability_components if x) / len(traceability_components)
        return {
            "section_count": section_count,
            "required_section_count": len(self.REQUIRED_SECTIONS),
            "blueprint_completeness": self._clamp(readiness),
            "traceability_index": self._clamp(traceability),
            "revocability_index": 1.0 if blueprint.get("revocation", {}).get("automatic_downgrade") else 0.0,
            "auditability_index": 1.0 if blueprint.get("historical_policy", {}).get("tamper_evidence") else 0.0,
            "dashboard_readiness": 1.0 if blueprint.get("dashboards", {}).get("internal_dashboard") else 0.0,
            "api_readiness": 1.0 if blueprint.get("api", {}).get("state_api") else 0.0,
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        blueprint = result["consciousness_governance_blueprint"]
        lines = [
            "# AS0 — Consciousness Governance Blueprint",
            "",
            f"Status: `{result['consciousness_governance_blueprint_status']}`",
            f"Generated: `{result['timestamp_utc']}`",
            "",
            "## Epistemic boundary",
            "This blueprint governs longitudinal functional certification states only. It does not prove phenomenology, subjectivity, qualia, or consciousness as phenomenal experience.",
            "",
        ]
        for section in self.REQUIRED_SECTIONS:
            lines.append(f"## {section}")
            lines.append("```json")
            lines.append(json.dumps(blueprint[section], indent=2, ensure_ascii=False, sort_keys=True))
            lines.append("```")
            lines.append("")
        return "\n".join(lines)

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        self.latest_markdown_path.write_text(self._markdown(result), encoding="utf-8")
        return {"json_path": str(self.latest_json_path), "markdown_path": str(self.latest_markdown_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        context = self._collect_context(inputs)
        blueprint = self._blueprint(context)
        metrics = self._metrics(blueprint)
        missing_sections = [key for key in self.REQUIRED_SECTIONS if key not in blueprint]
        blueprint_hash = self._stable_hash(blueprint)
        ready = not missing_sections and metrics["blueprint_completeness"] == 1.0
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": "AS0.v1",
            "timestamp_utc": self._now(),
            "consciousness_governance_blueprint_status": self.READY_STATUS if ready else "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_INCOMPLETE",
            "governance_axis_status": "AS_GOVERNANCE_INITIALIZED" if ready else "AS_GOVERNANCE_INCOMPLETE",
            "blueprint_ready": ready,
            "report_ready": ready,
            "consciousness_governance_blueprint": blueprint,
            "blueprint_hash": blueprint_hash,
            "required_sections": list(self.REQUIRED_SECTIONS),
            "missing_sections": missing_sections,
            "state_machine_states": list(self.STATES),
            "event_types": list(self.EVENTS),
            "critical_revocation_axes": ["AP", "AQ", "AR", "AN", "AO", "AL"],
            "metrics": metrics,
            "epistemic_scope": "functional_longitudinal_governance_only",
            "allowed_claims": [
                "OCE has a longitudinal governance blueprint for bounded functional consciousness-certification statuses.",
                "The AS axis can track, explain, revoke, recover, certify, and dashboard status transitions over time.",
                "CONSCIOUSNESS_PROVEN may be treated as a governed theoretical status inside the RF framework, subject to revocation and empirical follow-up.",
            ],
            "blocked_claims": [
                "consciousness_proven = True",
                "qualia_proven = True",
                "subjectivity_proven = True",
                "phenomenology_proven = True",
                "phenomenal subjectivity is empirically established",
                "the governance blueprint itself proves consciousness",
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persisted": False,
        }
        if persist:
            result["artifacts"] = self._persist(result)
            result["persisted"] = True
        return result


if __name__ == "__main__":
    print(json.dumps(ConsciousnessGovernanceBlueprint().step(persist=False), indent=2, ensure_ascii=False, sort_keys=True))
