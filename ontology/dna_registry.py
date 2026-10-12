from __future__ import annotations
from copy import deepcopy
from typing import Any
from ontology import minimal_dna
from ontology import dna_stack

PRIMITIVE = "dna_registry"
DESCRIPTION = "Logical, versioned discovery registry for currently explicit OCE DNA rules (P017)."
DEPENDENCIES = ["minimal_architectural_dna", "dna_stack"]
P017_VERSION = "P017-v1"
P017_SCHEMA_VERSION = "oce.p017.dna_registry.v1"
P017_SCOPE = "P017_ONLY"

P017_BOUNDARIES = {
    "registry_only": True,
    "does_not_define_p018_rule_contract": True,
    "does_not_define_severity": True,
    "does_not_define_inheritance": True,
    "does_not_define_mutation_protocol": True,
    "does_not_define_lineage_versioning": True,
    "does_not_grant_runtime_authority": True,
    "does_not_claim_end_to_end_enforcement": True,
    "unknown_enforcement_preserved": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
VALID_LAYERS = tuple(dna_stack.DNA_STACK_ORDER)

_DNA_RULE_REGISTRY = (
    {"registry_key":"P015:official_definition","layer":"DNA-0",
     "scope":"OCE DNA structural identity semantics","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_official_dna_definition","validation.p015_functional_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION",
     "dependencies":tuple(minimal_dna.DEPENDENCIES)},
    {"registry_key":"P015:identity_relation","layer":"DNA-0",
     "scope":"shared DNA identity compatibility without cognitive uniformity","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_official_dna_definition","validation.p015_non_regression_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION.identity_relation",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P015:epistemic_boundary","layer":"DNA-1",
     "scope":"evidence boundary against enforcement overclaim","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_official_dna_definition","validation.p015_adversarial_test","validation.p016_non_regression_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION.epistemic_boundary",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P015:change_boundary","layer":"DNA-6",
     "scope":"DNA change must remain explicit, governed, traceable and historized","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_official_dna_definition","validation.p015_non_mutation_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION.change_boundary",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P015:normative_hierarchy_boundary","layer":"DNA-4",
     "scope":"no implicit extension of DNA/Constitution/CCAD/runtime authority","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_non_regression_test","validation.p016_non_regression_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION.normative_hierarchy_boundary",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P015:non_loss_boundary","layer":"DNA-X",
     "scope":"preserve provenance, evidentiary scope and limits under reuse","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_non_regression_test","validation.p016_non_regression_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_OFFICIAL_DEFINITION.non_loss_boundary",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P015:canonical_composition","layer":"DNA-0",
     "scope":"DNA_OCE composition references without importing later semantics","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p015_official_dna_definition","validation.p015_adversarial_test"),
     "version":minimal_dna.OCE_DNA_DEFINITION_VERSION,
     "provenance":"ontology.minimal_dna:OCE_DNA_CANONICAL_COMPOSITION",
     "dependencies":("minimal_architectural_dna",)},
    {"registry_key":"P016:canonical_stack_shape","layer":"DNA-0",
     "scope":"canonical nine-layer DNA organization and order","enforcement_status":"UNKNOWN",
     "test_coverage":("validation.p016_dna_stack","validation.p016_functional_test","validation.p016_degradation_test","validation.p016_adversarial_test"),
     "version":dna_stack.P016_VERSION,
     "provenance":"ontology.dna_stack:DNA_STACK",
     "dependencies":("minimal_architectural_dna","dna_stack")},
)

def registry_entries() -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(entry) for entry in _DNA_RULE_REGISTRY)

def registry_manifest() -> dict[str, Any]:
    entries = registry_entries()
    return {"primitive":PRIMITIVE,"schema_version":P017_SCHEMA_VERSION,
            "version":P017_VERSION,"scope":P017_SCOPE,"entry_count":len(entries),
            "entries":entries,"valid_layers":VALID_LAYERS,
            "boundaries":deepcopy(P017_BOUNDARIES),
            "discovery_basis":"P015 explicit DNA definition/boundaries and P016 canonical stack only; later P018-P024/P088-P090 semantics are not silently materialized.",
            "functional_conclusion_only":True,"phenomenology_undetermined":True}

def find_entry(registry_key: str) -> dict[str, Any] | None:
    for entry in _DNA_RULE_REGISTRY:
        if entry["registry_key"] == registry_key:
            return deepcopy(entry)
    return None

def validate_registry(entries: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    records = registry_entries() if entries is None else tuple(deepcopy(entries))
    required=("registry_key","layer","scope","enforcement_status","test_coverage","version","provenance","dependencies")
    keys=[r.get("registry_key") for r in records if isinstance(r,dict)]
    valid=bool(records) and len(keys)==len(records) and len(keys)==len(set(keys))
    valid=valid and all(
        isinstance(r,dict) and all(f in r for f in required)
        and isinstance(r["registry_key"],str) and bool(r["registry_key"])
        and r["layer"] in VALID_LAYERS
        and isinstance(r["scope"],str) and bool(r["scope"])
        and r["enforcement_status"]=="UNKNOWN"
        and isinstance(r["test_coverage"],tuple) and bool(r["test_coverage"])
        and isinstance(r["version"],str) and bool(r["version"])
        and isinstance(r["provenance"],str) and bool(r["provenance"])
        and isinstance(r["dependencies"],tuple)
        for r in records)
    return {"primitive":PRIMITIVE,"valid":bool(valid),"entry_count":len(records),
            "unique_registry_keys":len(keys)==len(set(keys)),
            "unknown_enforcement_preserved":all(isinstance(r,dict) and r.get("enforcement_status")=="UNKNOWN" for r in records),
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
