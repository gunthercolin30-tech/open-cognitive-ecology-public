from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Tuple

from ontology import dna_registry, dna_stack

PRIMITIVE = "dna_rule_contract"
DESCRIPTION = "P018 thin structural contract for normalized OCE DNA rule representations."
DEPENDENCIES = ["dna_registry", "dna_stack"]

P018_VERSION = "P018-v1"
P018_SCHEMA_VERSION = "oce.p018.dna_rule_contract.v1"
P018_SCOPE = "P018_ONLY"

CANONICAL_FIELDS: Tuple[str, ...] = (
    "rule_id",
    "layer",
    "scope",
    "severity",
    "rationale",
    "enforcement",
    "tests",
    "exceptions",
    "modification_authority",
    "version",
    "provenance",
)

P018_BOUNDARIES = {
    "contract_structure_only": True,
    "does_not_define_p019_severity_semantics": True,
    "does_not_define_p020_inheritance": True,
    "does_not_define_p021_mutation_protocol": True,
    "does_not_define_p022_lineage_versioning": True,
    "does_not_define_p023_fitness_suite": True,
    "does_not_define_p024_adversarial_campaign": True,
    "does_not_grant_runtime_authority": True,
    "does_not_claim_end_to_end_enforcement": True,
    "unknown_may_not_be_promoted_by_contract": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

TRANSVERSAL_REFERENTIALS = {
    "doctrines": ("R3", "R4", "R5", "R10", "R11", "R19", "R21"),
    "artifacts": ("A-CANON", "A-R0R21", "A-TRACE"),
    "world_models_dependency": None,
}

def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _sequence(value: Any) -> bool:
    return isinstance(value, tuple)

def validate_rule_contract(rule: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if not isinstance(rule, Mapping):
        return {"valid": False, "errors": ("rule_not_mapping",)}

    keys = tuple(rule.keys())
    missing = tuple(field for field in CANONICAL_FIELDS if field not in rule)
    extras = tuple(key for key in keys if key not in CANONICAL_FIELDS)
    if missing:
        errors.append("missing_fields:" + ",".join(missing))
    if extras:
        errors.append("extra_fields:" + ",".join(extras))
    if missing:
        return {"valid": False, "errors": tuple(errors)}

    for field in (
        "rule_id", "layer", "scope", "rationale",
        "version", "provenance",
    ):
        if not _nonempty_text(rule[field]):
            errors.append(f"invalid_{field}")

    if rule["layer"] not in dna_stack.DNA_STACK_ORDER:
        errors.append("invalid_layer")

    # P018 requires the field but deliberately does not define P019's
    # severity vocabulary or ordering.
    if not _nonempty_text(rule["severity"]):
        errors.append("invalid_severity_placeholder")

    # P018 normalizes the field structurally. It cannot promote UNKNOWN
    # evidence into an enforcement claim.
    enforcement = rule["enforcement"]
    if isinstance(enforcement, str):
        if not enforcement.strip():
            errors.append("invalid_enforcement")
    elif not isinstance(enforcement, Mapping):
        errors.append("invalid_enforcement")

    if isinstance(enforcement, str) and enforcement.upper() in {
        "PASS", "TRUE", "ENFORCED", "PROVEN"
    }:
        errors.append("forbidden_unproven_enforcement_promotion")

    if not _sequence(rule["tests"]):
        errors.append("invalid_tests")
    elif not all(_nonempty_text(x) for x in rule["tests"]):
        errors.append("invalid_tests")

    if not _sequence(rule["exceptions"]):
        errors.append("invalid_exceptions")
    elif not all(_nonempty_text(x) for x in rule["exceptions"]):
        errors.append("invalid_exceptions")

    authority = rule["modification_authority"]
    if not (_nonempty_text(authority) or isinstance(authority, Mapping)):
        errors.append("invalid_modification_authority")

    return {"valid": not errors, "errors": tuple(errors)}

def normalize_rule(rule: Mapping[str, Any]) -> Dict[str, Any]:
    result = validate_rule_contract(rule)
    if not result["valid"]:
        raise ValueError(";".join(result["errors"]))
    return {field: deepcopy(rule[field]) for field in CANONICAL_FIELDS}

def contract_manifest() -> Dict[str, Any]:
    return {
        "primitive": PRIMITIVE,
        "description": DESCRIPTION,
        "dependencies": tuple(DEPENDENCIES),
        "version": P018_VERSION,
        "schema_version": P018_SCHEMA_VERSION,
        "scope": P018_SCOPE,
        "canonical_fields": CANONICAL_FIELDS,
        "valid_layers": tuple(dna_stack.DNA_STACK_ORDER),
        "boundaries": deepcopy(P018_BOUNDARIES),
        "transversal_referentials": deepcopy(TRANSVERSAL_REFERENTIALS),
        "p017_registry_schema": dna_registry.P017_SCHEMA_VERSION,
    }
