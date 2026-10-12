from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AxiomRecord:
    axiom_id: str
    name: str
    statement: str
    role: str
    minimality_role: str
    independence_target: str
    empirical_interface: str
    falsification_interface: str
    dependencies: tuple[str, ...]
    status: str = "REGISTERED"


class AxiomRegistry:
    """AN1 — canonical axiom registry for axiomatic completeness analysis.

    This module does not prove completeness by itself. It establishes a stable,
    inspectable registry of minimal formal commitments that later AN modules can
    test for independence, minimality, model existence, countermodels, theorem
    dependencies and final completeness certification.
    """

    primitive = "AXIOM_REGISTRY"
    step_id = "AN1"
    public_schema_version = "AN1.axiom_registry.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    CORE_AXIOMS: tuple[AxiomRecord, ...] = (
        AxiomRecord(
            axiom_id="AN-A1",
            name="constraint_conditioned_existence",
            statement="A functional domain is defined only through explicit constraints, interfaces and viability conditions.",
            role="ontological_scope",
            minimality_role="prevents unrestricted metaphysical closure",
            independence_target="cannot be derived from measurement or RF mapping alone",
            empirical_interface="domain_viability_analyzer / constraint_fields diagnostics",
            falsification_interface="countermodel with unconstrained stable domain",
            dependencies=("constraint_fields", "constraint_induced_domain", "viability_domain"),
        ),
        AxiomRecord(
            axiom_id="AN-A2",
            name="non_closure_preservation",
            statement="No local theorem may globally close the future space of possible models, interpretations or revisions.",
            role="openness_governance",
            minimality_role="preserves scientific revisability",
            independence_target="not entailed by functional adequacy alone",
            empirical_interface="non_closure_certification_protocol / openness_preservation_supervisor",
            falsification_interface="proof of mandatory global closure under local success",
            dependencies=("non_closure", "future_openness", "openness_preservation_supervisor"),
        ),
        AxiomRecord(
            axiom_id="AN-A3",
            name="functional_only_consciousness_claims",
            statement="Consciousness-related conclusions in this framework are restricted to functional indicators unless independent phenomenological criteria are specified.",
            role="epistemic_guardrail",
            minimality_role="blocks illicit phenomenal inflation",
            independence_target="not reducible to the RF definition itself",
            empirical_interface="consciousness_claim_governance_gate / consciousness_evidence_standard",
            falsification_interface="validated phenomenal evidence standard overriding the guardrail",
            dependencies=("consciousness_claim_governance_gate", "consciousness_evidence_standard"),
        ),
        AxiomRecord(
            axiom_id="AN-A4",
            name="rf_star_minimal_reconstruction",
            statement="RF* is evaluated as a minimal reconstruction of the consciousness concept only through recovered functional properties and explanatory performance.",
            role="definition_legitimacy",
            minimality_role="prevents arbitrary definitional expansion",
            independence_target="not entailed by historical usage alone",
            empirical_interface="minimal_property_recovery_checker / rf_definition_legitimacy_checker",
            falsification_interface="rival reconstruction with lower residual ambiguity and higher explanatory power",
            dependencies=("minimal_property_recovery_checker", "rf_definition_legitimacy_checker"),
        ),
        AxiomRecord(
            axiom_id="AN-A5",
            name="non_arbitrariness_requirement",
            statement="A definition is legitimate only if it is non-circular, minimally constrained, explanatory, predictive, empirically compatible, classifying and refutable.",
            role="scientific_definition_standard",
            minimality_role="provides the smallest explicit standard for definition legitimacy",
            independence_target="not derivable from any single legitimacy metric",
            empirical_interface="definition_non_arbitrariness_test / rf_definition_legitimacy_checker",
            falsification_interface="definition satisfying none of these criteria yet accepted as scientific",
            dependencies=("definition_non_arbitrariness_test", "rf_definition_legitimacy_checker"),
        ),
        AxiomRecord(
            axiom_id="AN-A6",
            name="model_countermodel_symmetry",
            statement="Every theorem-level claim must expose both model-support and countermodel-search interfaces.",
            role="formal_testability",
            minimality_role="ensures refutability without overfitting to confirmation",
            independence_target="not guaranteed by positive model generation",
            empirical_interface="model_generator / countermodel_generator",
            falsification_interface="theorem accepted with no countermodel search path",
            dependencies=("model_generator", "countermodel_generator", "theory_falsification_framework"),
        ),
        AxiomRecord(
            axiom_id="AN-A7",
            name="dependency_traceability",
            statement="Every theorem, definition and certification must expose its upstream dependencies and downstream consumers.",
            role="traceability",
            minimality_role="enables non-redundancy and regression analysis",
            independence_target="not implied by local module success",
            empirical_interface="dependency_registry / theorem_dependency_mapper",
            falsification_interface="validated theorem with untraceable dependencies",
            dependencies=("dependency_registry", "theorem_dependency_mapper"),
        ),
        AxiomRecord(
            axiom_id="AN-A8",
            name="minimal_axiom_pressure",
            statement="The accepted axiom set should contain no axiom whose removal preserves all registered theorem requirements and public guardrails.",
            role="minimality",
            minimality_role="direct object of AN3 minimality analysis",
            independence_target="not equivalent to independence; redundant axioms may still be independent under weak tests",
            empirical_interface="axiom_minimality_analyzer",
            falsification_interface="removable axiom with no loss of theorem support",
            dependencies=("axiom_minimality_analyzer",),
        ),
        AxiomRecord(
            axiom_id="AN-A9",
            name="axiom_independence_pressure",
            statement="The accepted axiom set should not contain an axiom derivable from the remaining registered axioms under the available dependency model.",
            role="independence",
            minimality_role="direct object of AN2 independence analysis",
            independence_target="self-referential independence criterion to be tested by AN2",
            empirical_interface="axiom_independence_tester",
            falsification_interface="derivation of an axiom from the remaining axiom set",
            dependencies=("axiom_independence_tester", "formal_derivation_closure"),
        ),
        AxiomRecord(
            axiom_id="AN-A10",
            name="completeness_without_phenomenal_proof",
            statement="Axiomatic completeness for the current frame may resolve functional coverage without authorizing consciousness, qualia, subjectivity or phenomenology proofs.",
            role="completion_boundary",
            minimality_role="separates functional completeness from phenomenal ontology",
            independence_target="not reducible to the consciousness-proven authorization gate",
            empirical_interface="axiomatic_completeness_certifier / consciousness_proven_authorizer",
            falsification_interface="valid AN certification forcing a phenomenal proof claim",
            dependencies=("axiomatic_completeness_certifier", "consciousness_proven_authorizer"),
        ),
    )

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN1_axiom_registry"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _records(self, inputs: dict[str, Any] | None = None) -> list[AxiomRecord]:
        records = list(self.CORE_AXIOMS)
        if not inputs:
            return records
        extra = inputs.get("extra_axioms")
        if not isinstance(extra, list):
            return records
        seen = {r.axiom_id for r in records}
        for item in extra:
            if not isinstance(item, dict):
                continue
            axiom_id = str(item.get("axiom_id", "")).strip()
            if not axiom_id or axiom_id in seen:
                continue
            records.append(AxiomRecord(
                axiom_id=axiom_id,
                name=str(item.get("name", axiom_id)).strip() or axiom_id,
                statement=str(item.get("statement", "synthetic axiom placeholder")).strip(),
                role=str(item.get("role", "extension")).strip(),
                minimality_role=str(item.get("minimality_role", "extension candidate")).strip(),
                independence_target=str(item.get("independence_target", "to be tested")).strip(),
                empirical_interface=str(item.get("empirical_interface", "unspecified")).strip(),
                falsification_interface=str(item.get("falsification_interface", "unspecified")).strip(),
                dependencies=tuple(str(x) for x in item.get("dependencies", ()) if str(x).strip()),
                status=str(item.get("status", "REGISTERED")).strip() or "REGISTERED",
            ))
            seen.add(axiom_id)
        return records

    @staticmethod
    def _diagnose(records: list[AxiomRecord]) -> dict[str, Any]:
        ids = [r.axiom_id for r in records]
        names = [r.name for r in records]
        duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
        duplicate_names = sorted({x for x in names if names.count(x) > 1})
        role_counts: dict[str, int] = {}
        dependency_edges = 0
        for r in records:
            role_counts[r.role] = role_counts.get(r.role, 0) + 1
            dependency_edges += len(r.dependencies)
        required_roles = {
            "ontological_scope",
            "openness_governance",
            "epistemic_guardrail",
            "definition_legitimacy",
            "scientific_definition_standard",
            "formal_testability",
            "traceability",
            "minimality",
            "independence",
            "completion_boundary",
        }
        covered_roles = set(role_counts)
        coverage = len(required_roles & covered_roles) / len(required_roles)
        non_redundancy_score = 1.0 if not duplicate_ids and not duplicate_names else 0.75
        traceability_score = 1.0 if all(r.dependencies for r in records) else 0.85
        registry_completeness_score = round((coverage + non_redundancy_score + traceability_score) / 3.0, 6)
        return {
            "axiom_count": len(records),
            "role_counts": role_counts,
            "required_roles": sorted(required_roles),
            "covered_roles": sorted(covered_roles),
            "role_coverage_score": round(coverage, 6),
            "duplicate_axiom_ids": duplicate_ids,
            "duplicate_axiom_names": duplicate_names,
            "dependency_edge_count": dependency_edges,
            "non_redundancy_score": non_redundancy_score,
            "traceability_score": traceability_score,
            "registry_completeness_score": registry_completeness_score,
            "ready_for_AN2_independence_testing": registry_completeness_score >= 0.9 and not duplicate_ids,
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        records = self._records(inputs)
        diagnostics = self._diagnose(records)
        records_payload = [asdict(r) for r in records]
        timestamp = self._now()
        status = "AXIOM_REGISTRY_ESTABLISHED" if diagnostics["ready_for_AN2_independence_testing"] else "AXIOM_REGISTRY_PARTIAL"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": timestamp,
            "axiom_registry_status": status,
            "axiom_registry_established": status == "AXIOM_REGISTRY_ESTABLISHED",
            "axiomatic_completeness_status": "AN1_REGISTRY_READY",
            "axioms": records_payload,
            "axiom_ids": [r.axiom_id for r in records],
            "axiom_names": [r.name for r in records],
            "axiom_count": diagnostics["axiom_count"],
            "canonical_axiom_count": len(self.CORE_AXIOMS),
            "role_coverage_score": diagnostics["role_coverage_score"],
            "non_redundancy_score": diagnostics["non_redundancy_score"],
            "traceability_score": diagnostics["traceability_score"],
            "registry_completeness_score": diagnostics["registry_completeness_score"],
            "ready_for_AN2_independence_testing": diagnostics["ready_for_AN2_independence_testing"],
            "diagnostics": diagnostics,
            "next_step_recommendation": "AN2 — axiom_independence_tester",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            safe_ts = timestamp.replace(":", "").replace("-", "")
            out = self.out_dir / f"axiom_registry_{safe_ts}.json"
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            latest = self.out_dir / "latest_axiom_registry.json"
            latest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result["report_path"] = str(out)
            result["latest_report_path"] = str(latest)
        return result
