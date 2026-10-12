from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict
from ontology import dna_fundamental

PRIMITIVE = "normative_hierarchy"
DESCRIPTION = "P087 canonical normative hierarchy with explicit Genesis/DNA/CCAD/Constitution/Governance and downstream normative levels; precedence only."
VERSION = "P087-v2-canonical-reconciliation"
SCHEMA_VERSION = "oce.p087.normative_hierarchy.v2"
SCOPE = "P087_ONLY"
PASS, FAIL, CONFLICT, UNDETERMINED = "PASS", "FAIL", "CONFLICT", "UNDETERMINED"

# Historical public sequence retained for compatibility with already-locked callers.
NORMATIVE_LEVELS = (
    "DNA_Fundamental", "Constitution_Operational", "Governance_Contextual",
    "Policy", "Procedure", "Decision", "Action",
)

# Members of one tuple have equal precedence. DNA_H and DNA_L0 are parallel
# constitutive branches under GENESIS. DNA_Fundamental is the G2 umbrella alias.
CANONICAL_LEVEL_GROUPS = (
    ("GENESIS",),
    ("DNA_H", "DNA_L0", "DNA_Fundamental"),
    ("DNA_L1",),
    ("CCAD",),
    ("Constitution_Operational", "Constitution"),
    ("Governance_Contextual", "Applicable_Governance_Context"),
    ("Institution_Rules", "Policy"),
    ("Mission_Policy", "Procedure"),
    ("Local_Procedure",),
    ("Individual_Preference",),
    ("Decision",),
    ("Action", "Runtime"),
)

ALIASES = {
    "GENESIS": "GENESIS", "DNA-H": "DNA_H", "DNA_H": "DNA_H",
    "DNA-L0": "DNA_L0", "DNA_L0": "DNA_L0",
    "DNA-FUNDAMENTAL": "DNA_Fundamental", "DNA_FUNDAMENTAL": "DNA_Fundamental",
    "DNA-L1": "DNA_L1", "DNA_L1": "DNA_L1", "CCAD": "CCAD",
    "CONSTITUTION": "Constitution_Operational", "CONSTITUTION_OPERATIONAL": "Constitution_Operational",
    "GOVERNANCE": "Governance_Contextual", "GOVERNANCE_CONTEXTUAL": "Governance_Contextual",
    "APPLICABLE_GOVERNANCE_CONTEXT": "Applicable_Governance_Context",
    "INSTITUTION_RULES": "Institution_Rules", "POLICY": "Policy",
    "MISSION_POLICY": "Mission_Policy", "MISSION_POLICIES": "Mission_Policy",
    "PROCEDURE": "Procedure", "LOCAL_PROCEDURE": "Local_Procedure",
    "LOCAL_PROCEDURES": "Local_Procedure", "INDIVIDUAL_PREFERENCE": "Individual_Preference",
    "INDIVIDUAL_PREFERENCES": "Individual_Preference", "DECISION": "Decision",
    "ACTION": "Action", "RUNTIME": "Runtime",
}

BOUNDARIES = {
    "formal_precedence_only": True, "lower_may_specify_higher": True,
    "lower_may_strengthen_higher": True, "lower_may_not_contradict_higher": True,
    "genesis_explicitly_represented": True, "dna_h_and_dna_l0_parallel_branches": True,
    "dna_l1_explicitly_represented": True, "ccad_explicitly_represented": True,
    "p098_extended_normative_levels_representable": True,
    "does_not_resolve_normative_conflicts": True, "does_not_authorize_execution": True,
    "does_not_implement_non_circumvention": True,
    "does_not_claim_end_to_end_runtime_enforcement": True,
    "p061_p086_are_downstream_integration_interfaces": True,
    "p061_p086_are_not_execution_prerequisites": True,
    "functional_conclusion_only": True, "phenomenology_undetermined": True,
}
EXECUTION_DEPENDENCIES = ("W1/G1_REUSE_ACQUIRED", "G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENTIALS = {"doctrines": ("R20", "R21"), "canonical_non_loss": ("4B", "4C", "4D", "4E")}

def _canonical_name(level: str):
    raw = str(level or "").strip()
    if not raw:
        return None
    key = raw.upper().replace(" ", "_")
    return ALIASES.get(key, raw if any(raw in group for group in CANONICAL_LEVEL_GROUPS) else None)

def _rank_map() -> Dict[str, int]:
    ranks = {}
    for rank, group in enumerate(CANONICAL_LEVEL_GROUPS):
        for name in group:
            ranks[name] = rank
    return ranks

def level_rank(level: str) -> Dict[str, Any]:
    canonical = _canonical_name(level)
    ranks = _rank_map()
    if canonical not in ranks:
        return {"status": UNDETERMINED, "level": level, "canonical_level": None, "rank": None,
                "reason": "unknown_normative_level"}
    return {"status": PASS, "level": level, "canonical_level": canonical, "rank": ranks[canonical],
            "reason": "known_normative_level"}

def compare_levels(first: str, second: str) -> Dict[str, Any]:
    a, b = level_rank(first), level_rank(second)
    if a["status"] != PASS or b["status"] != PASS:
        return {"status": UNDETERMINED, "first": first, "second": second, "relation": "UNKNOWN",
                "reason": "unknown_normative_level"}
    relation = "HIGHER" if a["rank"] < b["rank"] else ("LOWER" if a["rank"] > b["rank"] else "EQUAL")
    return {"status": PASS, "first": first, "second": second, "relation": relation,
            "first_rank": a["rank"], "second_rank": b["rank"],
            "first_canonical_level": a["canonical_level"], "second_canonical_level": b["canonical_level"]}

def evaluate_relation(lower_layer: str, higher_layer: str, relation: str) -> Dict[str, Any]:
    lower, higher = level_rank(lower_layer), level_rank(higher_layer)
    if lower["status"] != PASS or higher["status"] != PASS:
        return {"status": UNDETERMINED, "compatible": False, "authorized": False, "reason": "unknown_normative_level"}
    rel = str(relation).strip().lower()
    if rel not in {"specify", "strengthen", "contradict", "equal"}:
        return {"status": UNDETERMINED, "compatible": False, "authorized": False, "reason": "unknown_normative_relation"}
    lower_rank, higher_rank = lower["rank"], higher["rank"]
    if rel == "contradict":
        return {"status": CONFLICT, "compatible": False, "authorized": False, "reason": "higher_normative_constraint_contradicted"}
    if rel == "equal":
        ok = lower_rank == higher_rank
        return {"status": PASS if ok else CONFLICT, "compatible": ok, "authorized": False,
                "reason": "same_normative_level" if ok else "distinct_levels_cannot_be_declared_equal"}
    if lower_rank > higher_rank:
        return {"status": PASS, "compatible": True, "authorized": False, "reason": "lower_layer_may_%s_higher_layer" % rel}
    return {"status": CONFLICT, "compatible": False, "authorized": False, "reason": "reverse_or_same_level_normative_dependency"}

def validate_hierarchy() -> Dict[str, Any]:
    ranks = _rank_map()
    required = ("GENESIS", "DNA_H", "DNA_L0", "DNA_L1", "CCAD", "Constitution_Operational",
                "Governance_Contextual", "Institution_Rules", "Mission_Policy", "Local_Procedure",
                "Individual_Preference", "Decision", "Action")
    complete = all(name in ranks for name in required)
    branch_parallel = ranks.get("DNA_H") == ranks.get("DNA_L0")
    strict_core = (ranks["GENESIS"] < ranks["DNA_H"] < ranks["DNA_L1"] < ranks["CCAD"]
                   < ranks["Constitution_Operational"] < ranks["Governance_Contextual"])
    legacy_compatible = all(level_rank(x)["status"] == PASS for x in NORMATIVE_LEVELS)
    upstream = dna_fundamental.fundamental_manifest()
    upstream_ok = (upstream.get("primitive") == "dna_fundamental"
        and upstream.get("boundaries", {}).get("optimization_never_bypasses_higher_constraints") is True
        and upstream.get("boundaries", {}).get("does_not_grant_runtime_authority") is True)
    valid = bool(complete and branch_parallel and strict_core and legacy_compatible and upstream_ok)
    return {"primitive": PRIMITIVE, "status": PASS if valid else FAIL, "valid": valid,
            "level_count": len(NORMATIVE_LEVELS), "canonical_level_count": len(ranks), "precedence_group_count": len(CANONICAL_LEVEL_GROUPS),
            "canonical_hierarchy_complete": complete, "dna_h_dna_l0_parallel": branch_parallel,
            "strict_core_precedence_verified": strict_core, "legacy_api_compatible": legacy_compatible,
            "g2_dna_fundamental_reuse_verified": upstream_ok,
            "functional_conclusion_only": True, "phenomenology_undetermined": True}

def manifest() -> Dict[str, Any]:
    return {"primitive": PRIMITIVE, "description": DESCRIPTION, "version": VERSION,
            "schema_version": SCHEMA_VERSION, "scope": SCOPE, "normative_levels": NORMATIVE_LEVELS,
            "canonical_level_groups": deepcopy(CANONICAL_LEVEL_GROUPS),
            "execution_dependencies": EXECUTION_DEPENDENCIES, "boundaries": deepcopy(BOUNDARIES),
            "transversal_referentials": deepcopy(TRANSVERSAL_REFERENTIALS),
            "upstream_primitive": dna_fundamental.PRIMITIVE, "upstream_version": dna_fundamental.P088_VERSION,
            "functional_conclusion_only": True, "phenomenology_undetermined": True}
