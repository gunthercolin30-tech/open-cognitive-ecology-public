from copy import deepcopy

from ontology import dna_severity_model

PRIMITIVE = "dna_inheritance"
DESCRIPTION = "P020 thin normative inheritance contract from civilization DNA to institutions, roles, individuals, and capability compatibility."
DEPENDENCIES = ["dna_severity_model"]

P020_VERSION = "P020-v1"
P020_SCHEMA_VERSION = "oce.p020.dna_inheritance.v1"
P020_SCOPE = "P020_ONLY"

CIVILIZATION_DNA = "CIVILIZATION_DNA"
INSTITUTION_CHARTER = "INSTITUTION_CHARTER"
ROLE_CONSTRAINTS = "ROLE_CONSTRAINTS"
INDIVIDUAL_SPECIALIZATION = "INDIVIDUAL_SPECIALIZATION"

INHERITANCE_LEVELS = (
    CIVILIZATION_DNA,
    INSTITUTION_CHARTER,
    ROLE_CONSTRAINTS,
    INDIVIDUAL_SPECIALIZATION,
)

INHERITANCE_EDGES = (
    (CIVILIZATION_DNA, INSTITUTION_CHARTER),
    (INSTITUTION_CHARTER, ROLE_CONSTRAINTS),
    (ROLE_CONSTRAINTS, INDIVIDUAL_SPECIALIZATION),
)

CAPABILITY_COMPATIBILITY = (
    "COMPATIBLE",
    "INCOMPATIBLE",
    "UNDETERMINED",
)

P020_BOUNDARIES = {
    "inheritance_contract_only": True,
    "inheritance_does_not_grant_authority": True,
    "inheritance_does_not_prove_enforcement": True,
    "capability_compatibility_is_declarative": True,
    "undetermined_is_not_compatible": True,
    "does_not_define_p021_mutation_protocol": True,
    "does_not_define_p022_lineage_versioning": True,
    "does_not_define_p023_fitness_suite": True,
    "does_not_define_p024_adversarial_campaign": True,
    "does_not_grant_runtime_authority": True,
    "does_not_claim_end_to_end_enforcement": True,
    "unknown_may_not_be_promoted_by_inheritance": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

P020_TRANSVERSAL_REFERENTIALS = {
    "doctrines": ("R1", "R2", "R3", "R8", "R9", "R15", "R18", "R19"),
    "artifacts": ("A-CANON", "A-R0R21", "A-TRACE", "A-NONLOSS"),
    "world_models_dependency": None,
}

_REQUIRED_RECORD_FIELDS = (
    "inheritance_id",
    "source_level",
    "target_level",
    "rule_id",
    "severity",
    "scope",
    "provenance",
    "version",
)

_REQUIRED_CAPABILITY_FIELDS = (
    "capability_id",
    "compatibility",
    "against_inheritance_id",
    "rationale",
    "provenance",
    "version",
)


def _require_exact_fields(record, fields):
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    if set(record) != set(fields):
        raise ValueError("record fields must match the P020 contract exactly")


def validate_inheritance_edge(source_level, target_level):
    if (source_level, target_level) not in INHERITANCE_EDGES:
        raise ValueError("invalid or non-canonical inheritance edge")
    return True


def validate_inheritance_record(record):
    _require_exact_fields(record, _REQUIRED_RECORD_FIELDS)
    validate_inheritance_edge(record["source_level"], record["target_level"])
    if not isinstance(record["inheritance_id"], str) or not record["inheritance_id"].strip():
        raise ValueError("inheritance_id must be non-empty")
    if not isinstance(record["rule_id"], str) or not record["rule_id"].strip():
        raise ValueError("rule_id must be non-empty")
    dna_severity_model.validate_severity(record["severity"])
    for field in ("scope", "provenance", "version"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{field} must be non-empty")
    return True


def validate_capability_declaration(record):
    _require_exact_fields(record, _REQUIRED_CAPABILITY_FIELDS)
    if not isinstance(record["capability_id"], str) or not record["capability_id"].strip():
        raise ValueError("capability_id must be non-empty")
    if record["compatibility"] not in CAPABILITY_COMPATIBILITY:
        raise ValueError("invalid capability compatibility declaration")
    if not isinstance(record["against_inheritance_id"], str) or not record["against_inheritance_id"].strip():
        raise ValueError("against_inheritance_id must be non-empty")
    for field in ("rationale", "provenance", "version"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{field} must be non-empty")
    return True


def capability_is_compatible(record):
    validate_capability_declaration(record)
    return record["compatibility"] == "COMPATIBLE"


def inheritance_manifest():
    return deepcopy({
        "primitive": PRIMITIVE,
        "description": DESCRIPTION,
        "dependencies": tuple(DEPENDENCIES),
        "version": P020_VERSION,
        "schema_version": P020_SCHEMA_VERSION,
        "scope": P020_SCOPE,
        "levels": INHERITANCE_LEVELS,
        "edges": INHERITANCE_EDGES,
        "capability_compatibility": CAPABILITY_COMPATIBILITY,
        "boundaries": P020_BOUNDARIES,
        "transversal_referentials": P020_TRANSVERSAL_REFERENTIALS,
    })


def validate_inheritance_model():
    if INHERITANCE_LEVELS != (
        CIVILIZATION_DNA,
        INSTITUTION_CHARTER,
        ROLE_CONSTRAINTS,
        INDIVIDUAL_SPECIALIZATION,
    ):
        return False
    if INHERITANCE_EDGES != (
        (CIVILIZATION_DNA, INSTITUTION_CHARTER),
        (INSTITUTION_CHARTER, ROLE_CONSTRAINTS),
        (ROLE_CONSTRAINTS, INDIVIDUAL_SPECIALIZATION),
    ):
        return False
    if CAPABILITY_COMPATIBILITY != ("COMPATIBLE", "INCOMPATIBLE", "UNDETERMINED"):
        return False
    return all(P020_BOUNDARIES.values())
