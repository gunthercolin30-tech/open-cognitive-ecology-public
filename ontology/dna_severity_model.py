from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

from ontology import dna_rule_contract

PRIMITIVE = "dna_severity_model"
DESCRIPTION = "P019 thin normative severity vocabulary for OCE DNA rules."
DEPENDENCIES = ["dna_rule_contract"]

P019_VERSION = "P019-v1"
P019_SCHEMA_VERSION = "oce.p019.dna_severity_model.v1"
P019_SCOPE = "P019_ONLY"

ADVISORY = "ADVISORY"
STANDARD = "STANDARD"
STRICT = "STRICT"
CONSTITUTIONAL = "CONSTITUTIONAL"

SEVERITY_LEVELS: Tuple[str, ...] = (
    ADVISORY,
    STANDARD,
    STRICT,
    CONSTITUTIONAL,
)

SEVERITY_RANK = {level: index for index, level in enumerate(SEVERITY_LEVELS)}

P019_BOUNDARIES = {
    "severity_classification_only": True,
    "does_not_define_p020_inheritance": True,
    "does_not_define_p021_mutation_protocol": True,
    "does_not_define_p022_lineage_versioning": True,
    "does_not_define_p023_fitness_suite": True,
    "does_not_define_p024_adversarial_campaign": True,
    "does_not_grant_runtime_authority": True,
    "constitutional_severity_is_not_execution_authority": True,
    "does_not_claim_end_to_end_enforcement": True,
    "unknown_may_not_be_promoted_by_severity": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

TRANSVERSAL_REFERENTIALS = {
    "doctrines": ("R0", "R5", "R6", "R17", "R21"),
    "artifacts": ("A-CANON", "A-TRACE"),
    "world_models_dependency": None,
}

def validate_severity(value: Any) -> Dict[str, Any]:
    if not isinstance(value, str):
        return {"valid": False, "errors": ("severity_not_string",)}
    if value not in SEVERITY_LEVELS:
        return {"valid": False, "errors": ("unknown_severity",)}
    return {"valid": True, "errors": ()}

def severity_rank(value: Any) -> int:
    result = validate_severity(value)
    if not result["valid"]:
        raise ValueError(";".join(result["errors"]))
    return SEVERITY_RANK[value]

def compare_severity(left: Any, right: Any) -> int:
    lrank = severity_rank(left)
    rrank = severity_rank(right)
    return (lrank > rrank) - (lrank < rrank)

def validate_rule_severity(rule: Any) -> Dict[str, Any]:
    contract = dna_rule_contract.validate_rule_contract(rule)
    if not contract["valid"]:
        return {"valid": False, "errors": ("invalid_rule_contract",) + tuple(contract["errors"])}
    severity = validate_severity(rule["severity"])
    if not severity["valid"]:
        return {"valid": False, "errors": tuple(severity["errors"])}
    return {"valid": True, "errors": ()}

def severity_manifest() -> Dict[str, Any]:
    return {
        "primitive": PRIMITIVE,
        "description": DESCRIPTION,
        "dependencies": tuple(DEPENDENCIES),
        "version": P019_VERSION,
        "schema_version": P019_SCHEMA_VERSION,
        "scope": P019_SCOPE,
        "levels": SEVERITY_LEVELS,
        "rank": deepcopy(SEVERITY_RANK),
        "boundaries": deepcopy(P019_BOUNDARIES),
        "transversal_referentials": deepcopy(TRANSVERSAL_REFERENTIALS),
        "p018_contract_schema": dna_rule_contract.P018_SCHEMA_VERSION,
    }
