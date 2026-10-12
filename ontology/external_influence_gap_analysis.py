"""
External Influence Gap Analysis — R0.

Audits whether external influences are transformed into governed,
traceable, reversible and auditable institutional objects before they can
shape knowledge, priorities, revisions, commits or governance.

This primitive does not authorize execution and never writes external
content directly into the system. It only measures coverage and exposes
missing components for the governed R-axis pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    try:
        value = float(value)
    except Exception:
        value = 0.0
    return max(low, min(high, value))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


@dataclass(frozen=True)
class RequiredComponent:
    name: str
    weight: float = 1.0


class ExternalInfluenceGapAnalysis:
    """
    R0 audit primitive for governed external influence.

    The class measures architectural coverage across five domains:
    adoption gate, traceability, review gate, external source handling and
    impact measurement. It is deterministic for a given input and filesystem
    state. Optional persistence writes an audit snapshot only.
    """

    primitive = "EXTERNAL_INFLUENCE_GAP_ANALYSIS"

    DIRECT_COMPONENTS = {
        "adoption_gate": [
            RequiredComponent("external_influence_adoption_gate", 1.0),
            RequiredComponent("recommendation_intake", 0.6),
            RequiredComponent("recommendation_prioritization", 0.6),
            RequiredComponent("approval_or_rejection", 0.8),
        ],
        "traceability": [
            RequiredComponent("external_influence_traceability_engine", 1.0),
            RequiredComponent("scientific_revision_execution_monitor", 0.7),
            RequiredComponent("governance_review", 0.5),
        ],
        "review_gate": [
            RequiredComponent("human_review_gate", 1.0),
            RequiredComponent("constitutional_compliance_check", 1.0),
            RequiredComponent("constitutional_governance_supervisor", 0.8),
            RequiredComponent("governed_execution_dispatcher", 0.6),
        ],
        "external_source": [
            RequiredComponent("external_response_parser", 1.0),
            RequiredComponent("internet_controlled_gateway", 0.7),
            RequiredComponent("distributed_knowledge_access", 0.6),
            RequiredComponent("civilizational_external_relations_manager", 0.4),
        ],
        "impact_measurement": [
            RequiredComponent("outcome_monitoring", 0.7),
            RequiredComponent("effectiveness_assessment", 0.7),
            RequiredComponent("scientific_self_revision_supervisor", 0.7),
            RequiredComponent("civilizational_metrics_synthesizer", 0.5),
            RequiredComponent("external_influence_impact_monitor", 1.0),
        ],
    }

    PLANNED_R_COMPONENTS = [
        "external_priority_influence_layer",
        "external_commit_traceability_hook",
        "external_governance_amendment_gate",
        "external_influence_impact_monitor",
        "external_influence_dashboard",
        "external_decision_record_extension",
        "external_revision_traceability_extension",
    ]

    REDUNDANCY_CANDIDATES = {
        "external_response_parser": ["internet_cognitive_interface"],
        "external_influence_adoption_gate": [
            "approval_or_rejection",
            "constitutional_compliance_check",
            "governance_review",
        ],
        "external_influence_traceability_engine": [
            "scientific_revision_execution_monitor",
            "outcome_monitoring",
        ],
        "external_influence_gap_analysis": [
            "internet_controlled_gateway",
            "civilizational_meta_governance",
            "governance_approval_policy_manager",
        ],
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.audit_dir = self.root / "external_influence_audit"

    def _module_exists(self, name: str, supplied: set[str] | None = None) -> bool:
        # If a module inventory is explicitly supplied, use it as an isolated
        # audit universe. This enables degradation and counterfactual tests.
        if supplied is not None:
            return name in supplied
        return (self.root / "ontology" / f"{name}.py").exists()

    def _coverage(self, components: list[RequiredComponent], supplied: set[str] | None = None) -> tuple[float, list[str], list[str]]:
        total = sum(c.weight for c in components) or 1.0
        present_weight = 0.0
        present: list[str] = []
        missing: list[str] = []
        for component in components:
            if self._module_exists(component.name, supplied):
                present_weight += component.weight
                present.append(component.name)
            else:
                missing.append(component.name)
        return _clamp(present_weight / total), present, missing

    def _extract_supplied_modules(self, payload: dict[str, Any]) -> set[str] | None:
        # None means: inspect the real ontology directory.
        # A set, including an empty set, means: use this supplied inventory only.
        if "available_modules" in payload:
            raw = payload.get("available_modules", [])
        elif "modules" in payload:
            raw = payload.get("modules", [])
        else:
            return None
        if raw is None:
            raw = []
        if isinstance(raw, dict):
            raw = list(raw.keys())
        return {str(item) for item in raw if str(item).strip()}

    def _decision(self, coverage_scores: dict[str, float], missing_components: list[str]) -> str:
        minimum = min(coverage_scores.values()) if coverage_scores else 0.0
        mean_score = _mean(list(coverage_scores.values()))
        planned_missing = [m for m in missing_components if m in self.PLANNED_R_COMPONENTS]
        if minimum >= 0.9 and mean_score >= 0.92 and not planned_missing:
            return "architecture_complete"
        if mean_score >= 0.68 and minimum >= 0.45:
            return "architecture_partial"
        return "architecture_gap_detected"

    def _recommendations(self, missing_components: list[str], coverage_scores: dict[str, float]) -> list[str]:
        recommendations: list[str] = []
        if "external_priority_influence_layer" in missing_components:
            recommendations.append("Implement R2 external_priority_influence_layer after R0 to govern externally suggested priority changes.")
        if "external_commit_traceability_hook" in missing_components:
            recommendations.append("Implement R4 external_commit_traceability_hook to link external influence records to code changes and rollback plans.")
        if "external_governance_amendment_gate" in missing_components:
            recommendations.append("Implement R5 external_governance_amendment_gate before allowing externally inspired governance amendments.")
        if "external_influence_impact_monitor" in missing_components or coverage_scores.get("impact_measurement", 0.0) < 0.9:
            recommendations.append("Implement R6 external_influence_impact_monitor to quantify downstream effects, reversibility and failed adoptions.")
        if "external_influence_dashboard" in missing_components:
            recommendations.append("Implement R7 external_influence_dashboard once R2/R4/R5/R6 emit stable metrics.")
        if not recommendations:
            recommendations.append("No critical R-axis gap detected; continue with decision-record and revision-traceability extensions.")
        return recommendations

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = dict(inputs or {})
        supplied = self._extract_supplied_modules(payload)

        domain_results: dict[str, Any] = {}
        coverage_scores: dict[str, float] = {}
        missing_components: list[str] = []

        for domain, components in self.DIRECT_COMPONENTS.items():
            score, present, missing = self._coverage(components, supplied)
            coverage_scores[domain] = score
            missing_components.extend(missing)
            domain_results[domain] = {
                "coverage_score": score,
                "present_components": present,
                "missing_components": missing,
            }

        for planned in self.PLANNED_R_COMPONENTS:
            if not self._module_exists(planned, supplied):
                missing_components.append(planned)

        missing_components = sorted(set(missing_components))
        redundancy_candidates = {
            key: [candidate for candidate in values if self._module_exists(candidate, supplied)]
            for key, values in self.REDUNDANCY_CANDIDATES.items()
        }
        redundancy_candidates = {k: v for k, v in redundancy_candidates.items() if v}

        decision = self._decision(coverage_scores, missing_components)
        integration_recommendations = self._recommendations(missing_components, coverage_scores)

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "adoption_gate_coverage": coverage_scores.get("adoption_gate", 0.0),
            "traceability_coverage": coverage_scores.get("traceability", 0.0),
            "review_gate_coverage": coverage_scores.get("review_gate", 0.0),
            "external_source_coverage": coverage_scores.get("external_source", 0.0),
            "impact_measurement_coverage": coverage_scores.get("impact_measurement", 0.0),
            "overall_external_influence_coverage": _mean(list(coverage_scores.values())),
            "domain_results": domain_results,
            "missing_components": missing_components,
            "redundancy_candidates": redundancy_candidates,
            "integration_recommendations": integration_recommendations,
            "architecture_decision": decision,
            "direct_write_allowed": False,
            "external_influence_governed": decision in {"architecture_complete", "architecture_partial"},
            "epistemic_position": "functional_architectural_audit_only_no_phenomenal_claim",
        }

        if persist:
            self.audit_dir.mkdir(parents=True, exist_ok=True)
            latest = self.audit_dir / "latest_external_influence_gap_analysis.json"
            latest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(latest)

        return result
