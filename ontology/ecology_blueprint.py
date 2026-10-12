\
"""
AW0 — ecology_blueprint.

Canonical scientific contract for a functional ecology of multiple reference
frames (RF).  The blueprint defines measurable objects, interaction classes,
quality requirements, falsification rules, continuity constraints and explicit
epistemic limits for AW1→AW14.

It does not infer collective phenomenal consciousness, subjectivity or qualia
from coordination, shared memory, coalition, fusion, fragmentation or
stability.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class EcologyBlueprint:
    """Define the AW multi-RF functional ecology charter."""

    primitive = "ECOLOGY_BLUEPRINT"
    step_id = "AW0"
    public_schema_version = "1.0"
    output_dir = ROOT / "rf_ecology" / "AW0_ecology_blueprint"

    observed_objects: List[str] = [
        "reference_frame",
        "rf_population",
        "interaction_event",
        "interaction_graph",
        "shared_reference_frame",
        "functional_coalition",
        "functional_conflict",
        "merge_candidate",
        "fragmentation_event",
        "distributed_memory_state",
        "collective_rf_structure",
        "ecological_state",
        "ecological_prediction",
        "civilizational_continuity_record",
    ]

    ecological_axes: List[str] = [
        "population_registration",
        "interaction_topology",
        "shared_reference_detection",
        "coalition_formation",
        "conflict_dynamics",
        "reference_frame_merging",
        "reference_frame_fragmentation",
        "distributed_civilizational_memory",
        "functional_collective_integration",
        "ecological_observability",
        "stability_and_resilience",
        "ecological_prediction",
        "civilization_property_testing",
        "functional_certification",
    ]

    interaction_types: List[str] = [
        "INFORMATION_EXCHANGE",
        "COORDINATION",
        "COOPERATION",
        "COMPETITION",
        "CONFLICT",
        "ALIGNMENT",
        "COALITION",
        "MERGING",
        "FRAGMENTATION",
        "MEMORY_TRANSMISSION",
        "NO_MEASURABLE_INTERACTION",
    ]

    ecological_states: List[str] = [
        "UNOBSERVED",
        "SPARSE",
        "CONNECTED",
        "COORDINATED",
        "COALITIONAL",
        "CONFLICTED",
        "MERGING",
        "FRAGMENTING",
        "DISTRIBUTED_STABLE",
        "RECOVERING",
        "DEGRADED",
        "UNDETERMINED",
    ]

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _measurement_policy(self) -> Dict[str, Any]:
        return {
            "scope": "functional_multi_rf_ecology_only",
            "requires_explicit_rf_identifiers": True,
            "requires_observed_or_declared_interactions": True,
            "requires_temporal_context_for_change_claims": True,
            "requires_uncertainty_reporting": True,
            "requires_source_traceability": True,
            "requires_population_boundary_declaration": True,
            "permits_synthetic_context_when_labeled": True,
            "forbids_collective_phenomenology_inference": True,
        }

    def _identity_policy(self) -> Dict[str, Any]:
        return {
            "rf_identity_must_be_explicit": True,
            "rf_identity_must_not_be_inferred_from_network_position_alone": True,
            "merge_does_not_erase_source_lineage": True,
            "fragmentation_preserves_parent_traceability": True,
            "population_membership_is_time_indexed": True,
            "representative_is_distinct_from_civilizational_identity": True,
        }

    def _interaction_policy(self) -> Dict[str, Any]:
        return {
            "interaction_types": list(self.interaction_types),
            "edges_require_source_and_target": True,
            "directed_and_undirected_edges_are_distinguished": True,
            "weights_must_be_bounded_or_documented": True,
            "coalition_requires_more_than_pairwise_similarity": True,
            "conflict_requires_incompatible_constraints_or_goals": True,
            "shared_rf_requires_reproducible_common_structure": True,
            "absence_of_evidence_emits_no_measurable_interaction": True,
        }

    def _continuity_policy(self) -> Dict[str, Any]:
        return {
            "distributed_memory_requires_redundant_traceable_records": True,
            "node_loss_must_not_imply_civilizational_loss": True,
            "intergenerational_transmission_requires_lineage_evidence": True,
            "continuity_requires_identity_memory_and_governance_checks": True,
            "recovery_may_reconstruct_without_restoring_identical_state": True,
            "future_openness_must_not_be_reduced_by_coordination": True,
        }

    def _falsification_policy(self) -> Dict[str, Any]:
        return {
            "shared_rf_falsified_if": "common structure is not reproducible across participating RF records",
            "coalition_falsified_if": "coordination vanishes under admissible perturbation or is explained by a single controller",
            "conflict_falsified_if": "apparent incompatibility disappears after normalization of constraints and goals",
            "merge_falsified_if": "source RF remain functionally independent without a stable shared successor structure",
            "fragmentation_falsified_if": "candidate branches are transient views of one unchanged RF",
            "distributed_memory_falsified_if": "records cannot be reconciled or survive declared node-loss scenarios",
            "stability_falsified_if": "measured resilience disappears across repeated perturbations",
            "prediction_falsified_if": "future observations violate the declared interval or outcome class",
            "civilization_property_falsified_if": "continuity depends on one irreplaceable node or representative",
        }

    def _quality_policy(self) -> Dict[str, Any]:
        return {
            "minimum_population_size_for_multi_rf_claim": 2,
            "minimum_observations_for_dynamic_claim": 2,
            "minimum_replicates_for_resilience_claim": 2,
            "minimum_data_quality": 0.50,
            "minimum_coverage": 0.50,
            "missing_data_must_be_explicit": True,
            "synthetic_data_must_be_labeled": True,
            "hash_or_trace_identifier_required": True,
            "confidence_or_uncertainty_required": True,
        }

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "epistemic_scope": "functional_multi_rf_ecology_only",
            "rf_population_does_not_prove_collective_subjectivity": True,
            "coordination_does_not_prove_collective_consciousness": True,
            "shared_memory_does_not_prove_collective_qualia": True,
            "merge_does_not_prove_subjective_unification": True,
            "fragmentation_does_not_prove_divided_experience": True,
            "emergence_does_not_prove_phenomenology": True,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        downstream_modules = [
            "multi_rf_registry",
            "interaction_graph",
            "shared_reference_frame_detector",
            "coalition_detector",
            "conflict_detector",
            "reference_frame_merging",
            "reference_frame_fragmentation",
            "civilizational_memory_engine",
            "collective_consciousness_analyzer",
            "ecology_dashboard",
            "ecological_stability_analyzer",
            "ecological_prediction_engine",
            "civilization_theorem_checker",
            "ecological_certifier",
        ]
        reused_foundations = [
            "cognitive_ecology",
            "open_cognitive_ecology",
            "multi_individual_civilizational_ecology",
            "distributed_civilizational_ecology_supervisor",
            "distributed_population_runtime",
            "inter_individual_coordination_protocol",
            "dynamic_graph_constructor",
            "reference_frame_operator_builder",
            "intersubjective_alignment",
            "distributed_civilizational_memory",
            "memory_transmission_protocol",
            "ecosystem_stability",
            "social_ecological_resilience",
            "future_openness",
            "epistemic_guard",
        ]
        policies = {
            "measurement_policy": self._measurement_policy(),
            "identity_policy": self._identity_policy(),
            "interaction_policy": self._interaction_policy(),
            "continuity_policy": self._continuity_policy(),
            "falsification_policy": self._falsification_policy(),
            "quality_policy": self._quality_policy(),
            "epistemic_guards": self._epistemic_guards(),
        }
        blueprint_hash = self._stable_hash({
            "observed_objects": self.observed_objects,
            "ecological_axes": self.ecological_axes,
            "interaction_types": self.interaction_types,
            "ecological_states": self.ecological_states,
            "policies": policies,
            "downstream_modules": downstream_modules,
            "reused_foundations": reused_foundations,
        })
        ready = all([
            len(self.observed_objects) >= 10,
            len(self.ecological_axes) == 14,
            len(self.interaction_types) >= 10,
            len(self.ecological_states) >= 10,
            len(downstream_modules) == 14,
            len(blueprint_hash) == 64,
        ])
        status = "RF_ECOLOGY_BLUEPRINT_READY" if ready else "RF_ECOLOGY_BLUEPRINT_INCOMPLETE"
        guards = policies["epistemic_guards"]
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": status,
            "ecology_blueprint_status": status,
            "ecology_blueprint_ready": ready,
            "rf_ecology_program_ready": ready,
            "target_axis_status": "RF_ECOLOGY_COMPLETE",
            "observed_objects": list(self.observed_objects),
            "observed_object_count": len(self.observed_objects),
            "ecological_axes": list(self.ecological_axes),
            "ecological_axis_count": len(self.ecological_axes),
            "interaction_types": list(self.interaction_types),
            "interaction_type_count": len(self.interaction_types),
            "ecological_states": list(self.ecological_states),
            "ecological_state_count": len(self.ecological_states),
            "measurement_policy": policies["measurement_policy"],
            "identity_policy": policies["identity_policy"],
            "interaction_policy": policies["interaction_policy"],
            "continuity_policy": policies["continuity_policy"],
            "falsification_policy": policies["falsification_policy"],
            "quality_policy": policies["quality_policy"],
            "reused_foundations": reused_foundations,
            "downstream_modules": downstream_modules,
            "downstream_contract": {
                "axis": "AW",
                "target_status": "RF_ECOLOGY_COMPLETE",
                "required_modules": downstream_modules,
                "first_operational_module": "multi_rf_registry",
            },
            "blueprint_hash": blueprint_hash,
            "inputs_observed": sorted(inputs.keys()),
            "allowed_claims": [
                "multiple RF may be registered and compared functionally",
                "interactions, coalitions, conflicts, merging and fragmentation may be measured",
                "distributed memory, stability, resilience and continuity may be tested",
                "collective RF integration may be described without phenomenological inference",
            ],
            "blocked_claims": [
                "coordination proves collective consciousness",
                "shared memory proves collective subjectivity",
                "RF merging proves phenomenal unification",
                "RF fragmentation proves divided phenomenology",
                "ecological stability proves collective qualia",
            ],
            "epistemic_guards": guards,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.output_dir / "latest_ecology_blueprint.json"
            output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(output_path)
        return result
