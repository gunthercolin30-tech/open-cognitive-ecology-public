from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Optional

PRIMITIVE = "minimal_architectural_dna"
DESCRIPTION = "Minimal architectural DNA."
DEPENDENCIES = [
    "anti_closure_metaconstraint",
    "genealogical_responsibility",
    "human_non_replacement",
    "future_openness",
]


class MinimalDNAPrimitive:
    def __init__(
        self,
        invariants: Dict[str, Any],
        mutable_traits: Optional[Dict[str, Any]] = None,
        viability_function: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        if not invariants:
            raise ValueError("Minimal DNA requires at least one invariant.")

        self._invariants = deepcopy(invariants)
        self._mutable_traits = deepcopy(mutable_traits or {})
        self._viability_function = viability_function

        if not self.is_viable():
            raise ValueError("Initial Minimal DNA configuration is not viable.")

    def genome(self) -> Dict[str, Any]:
        genome = deepcopy(self._invariants)
        genome.update(deepcopy(self._mutable_traits))
        return genome

    def is_viable(self) -> bool:
        genome = self.genome()

        for key, value in self._invariants.items():
            if genome.get(key) != value:
                return False

        if self._viability_function is not None:
            return bool(self._viability_function(genome))

        return True

    def step(self) -> Dict[str, Any]:
        viable = self.is_viable()
        return {
            "primitive": "MINIMAL_ARCHITECTURAL_DNA",
            "minimal_dna_integrity_score": 1.0 if viable else 0.0,
            "viable": viable,
            "ready_for_transmission": viable,
            "diagnostics": {
                "invariant_count": len(self._invariants),
                "mutable_trait_count": len(self._mutable_traits),
                "dependencies": DEPENDENCIES,
            },
        }

# === OCE P015 OFFICIAL DNA DEFINITION START ===
# P015 defines OCE DNA semantically/structurally; it does not implement P016-P024.
OCE_DNA_DEFINITION_VERSION = "P015-v3"

OCE_DNA_OFFICIAL_DEFINITION = {
    "kind": "structural_constraint_system",
    "definition": (
        "OCE DNA is the minimal, provider-independent, model-independent, "
        "prompt-independent and UI-independent set of structural invariants "
        "and governed constraints whose preservation is required for an OCE "
        "entity to remain structurally compatible with OCE identity."
    ),
    "constraint_domains": (
        "architectural", "epistemic", "cognitive", "resources", "governance",
        "evolution", "individuals", "economics", "evidence",
    ),
    "properties": (
        "structural", "provider_independent", "model_independent",
        "prompt_independent", "ui_independent", "testable", "traceable",
        "versionable", "governed_change_only", "non_silent_mutation",
        "plurality_preserving",
    ),
    "identity_relation": (
        "Shared OCE DNA constrains admissible structure and transformation; "
        "it does not require uniform beliefs, strategies, specializations, "
        "representations, or individual cognitive states."
    ),
    "epistemic_boundary": (
        "A declared DNA rule, module name, token, score, documentation entry, "
        "or local test result is not by itself evidence of end-to-end runtime "
        "or civilizational enforcement."
    ),
    "change_boundary": (
        "DNA change must be explicit, governed, traceable and historized; "
        "P015 does not define the later mutation protocol."
    ),
    "scope_boundary": (
        "P015 defines DNA identity semantics only. P016-P024 define the "
        "operational stack, registry, contracts, severity, inheritance, "
        "mutation, lineage, fitness and adversarial enforcement."
    ),
    "normative_hierarchy_boundary": (
        "P015 does not grant new runtime authority; applicable DNA, Constitution, "
        "CCAD, authorization and runtime authority chains remain controlling."
    ),
    "non_loss_boundary": (
        "Reused canonical or evidentiary acquisitions retain provenance, scope "
        "and limits; local evidence is not generalized without proof."
    ),
}

OCE_DNA_CANONICAL_COMPOSITION = {
    "formula": "DNA_OCE = MetaRules + DNA_values + DNA_machinery",
    "meta_rules": ("M1", "M2", "M3", "M4", "M5", "M6"),
    "dna_values": {
        "adopted_reference": "F1-F12 + F17 + F18",
        "proposed_pending_canonical_review": None,
    },
    "dna_machinery_reference": "F13-F16",
    "f18_gate": "F18_CANONICAL_REVIEW_OK",
    "semantic_boundary": (
        "P015 records composition references only; detailed semantics, stacking, "
        "registry and enforcement belong to later milestones."
    ),
    "provenance_note": (
        "Targeted canonical updates dated 2026-09-13 supersede older local "
        "F1-F16 formulations for explicitly modified P089 content; F18 was "
        "subsequently adopted by governed human canonical review and is no "
        "longer pending."
    ),
}

OCE_DNA_TRANSVERSAL_REFERENTIALS = {
    "doctrines": ("R0", "R1", "R2", "R4", "R11", "R14", "R17", "R18", "R19", "R21"),
    "artifacts": ("A-CANON", "A-R0R21", "A-TRACE", "A-NONLOSS"),
    "world_models_dependency_required": False,
}

OCE_DNA_EPISTEMIC_STATUS = {
    "native_end_to_end_civilizational_enforcement": "UNKNOWN",
    "end_to_end_constitutional_state_persistence": "UNKNOWN",
    "native_direct_succession_component_chain": "NOT_OBSERVED",
    "phenomenology": "UNDETERMINED",
    "functional_conclusion_only": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
}
# === OCE P015 OFFICIAL DNA DEFINITION END ===
