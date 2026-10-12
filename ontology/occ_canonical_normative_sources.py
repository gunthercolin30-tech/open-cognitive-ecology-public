from __future__ import annotations
import hashlib, json
PRIMITIVE="occ_canonical_normative_sources"
VERSION="P159-OCC1A-foundation-v1"
STATUS="IMPLEMENTED_FOUNDATION_NOT_CLOSED"
NORMATIVE_STRENGTHS=("MUST","MUST_NOT","SHOULD","SHOULD_NOT","MAY")
LEVELS=("GENESIS","DNA_H","DNA_L0","DNA_L1","CCAD","CONSTITUTION","GOVERNANCE","POLICY")
FORMALIZATION=("F0_HUMAN_INTERPRETIVE","F1_STRUCTURED","F2_MACHINE_TESTABLE","F3_FORMALLY_VERIFIED")
ADOPTION_STATES=("DRAFT","PROPOSED","ADOPTED","ACTIVE","SUSPENDED","SUPERSEDED","RETIRED","INVALIDATED")
PACKAGE_STATES=("DRAFT","VALIDATED","CERTIFIED","ACTIVE","SUPERSEDED","REVOKED")
REFERENCE_TYPES=("semantic_reference","runtime_dependency","derivation_dependency","authority_dependency")
AUTHORITY_SEMANTICS=("grants","restricts","reserves","delegates")
HUMAN_ROLES=("CONSTITUENT_SOURCE","CONSTITUTIONAL_AUTHORITY","GOVERNANCE_AUTHORITY","OPERATIONAL_AUTHORITY","AFFECTED_PERSON","REPRESENTATIVE")
FORBIDDEN_AUTHORITY=("ROOT_OVERRIDE_ALL",)
NSI={"NSI-1":"STABLE_UNIQUE_ID","NSI-2":"NO_SILENT_ACTIVE_NORM_LOSS","NSI-3":"NO_LOWER_LAYER_REDEFINITION",
"NSI-4":"AUTHORITY_GRANT_HAS_LEGITIMACY_PROVENANCE","NSI-5":"UNKNOWN_PRESERVED","NSI-6":"CCAD_CANNOT_OVERRIDE_GENESIS_OR_DNA",
"NSI-7":"FILE_ORDER_NON_NORMATIVE","NSI-8":"COMMENTS_NON_NORMATIVE","NSI-9":"PUBLISHED_PACKAGE_IMMUTABLE",
"NSI-10":"HISTORICAL_VERSIONS_RECONSTRUCTIBLE","NSI-11":"MACHINE_READABLE_IS_NOT_FORMAL_PROOF","NSI-12":"NO_CODE_EXECUTION_IN_SOURCES"}
def canonical_bytes(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))+chr(10)).encode("utf-8")
def semantic_hash(obj): return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def evaluate_active_norm_completeness(active_source_ids,compiled_ids):
    # Executable NSI-2: active canonical norms may not silently disappear.
    if not isinstance(active_source_ids,(list,tuple,set)) or not isinstance(compiled_ids,(list,tuple,set)):
        return {"status":"FAIL","reason":"NSI_2_INVALID_INPUT","missing_active_norm_ids":[]}
    src={x for x in active_source_ids if isinstance(x,str) and x}
    compiled={x for x in compiled_ids if isinstance(x,str) and x}
    missing=sorted(src-compiled)
    return {"status":"FAIL" if missing else "PASS",
            "reason":"NSI_2_ACTIVE_NORM_LOSS" if missing else "NSI_2_COMPLETE",
            "missing_active_norm_ids":missing}

def validate_identifier(norm_id):
    return isinstance(norm_id,str) and bool(norm_id) and not any(c.isspace() for c in norm_id) and norm_id.startswith(("GENESIS.","DNA.","CCAD.","CONSTITUTION.","GOVERNANCE.","POLICY."))
def validate_norm_record(r):
    req=("id","version","level","strength","formalization","text","structure","executable_semantics","status","provenance")
    missing=[k for k in req if k not in r]
    if missing: return {"status":"FAIL","reason":"MISSING_FIELDS","missing":missing}
    if not validate_identifier(r["id"]): return {"status":"FAIL","reason":"INVALID_ID"}
    if r["level"] not in LEVELS or r["strength"] not in NORMATIVE_STRENGTHS or r["formalization"] not in FORMALIZATION: return {"status":"FAIL","reason":"INVALID_VOCABULARY"}
    if r["status"] not in ADOPTION_STATES: return {"status":"FAIL","reason":"INVALID_ADOPTION_STATE"}
    if not isinstance(r["provenance"],list) or not r["provenance"]: return {"status":"FAIL","reason":"BROKEN_LINEAGE"}
    if "ROOT_OVERRIDE_ALL" in json.dumps(r,sort_keys=True): return {"status":"FAIL","reason":"FORBIDDEN_ROOT_OVERRIDE"}
    return {"status":"PASS","reason":"STRUCTURALLY_VALID_NOT_CERTIFIED"}
def validate_reference(ref,known_ids):
    if not isinstance(ref,dict) or ref.get("type") not in REFERENCE_TYPES: return {"status":"FAIL","reason":"INVALID_REFERENCE"}
    if ref.get("target") not in known_ids: return {"status":"FAIL","reason":"BROKEN_NORM_REFERENCE"}
    return {"status":"PASS"}
def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"levels":LEVELS,"strengths":NORMATIVE_STRENGTHS,
    "formalization":FORMALIZATION,"adoption_states":ADOPTION_STATES,"package_states":PACKAGE_STATES,
    "reference_types":REFERENCE_TYPES,"authority_semantics":AUTHORITY_SEMANTICS,"human_roles":HUMAN_ROLES,
    "forbidden_authority":FORBIDDEN_AUTHORITY,"nsi":NSI,"functional_conclusion_only":True,"phenomenology_undetermined":True}
