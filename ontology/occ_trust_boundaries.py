from __future__ import annotations
PRIMITIVE="occ_trust_boundaries"; VERSION="P159-OCC0-v1"; SCHEMA_VERSION="oce.p159.occ0.trust_boundaries.v1"
SCOPE="P159_OCC0_ONLY"; STATUS="IMPLEMENTED_NOT_LOCKED"
ROLES=("SOURCE","COMPILER","VERIFIER","AUTHORITY","EXECUTION")
COMPILABILITY=("C1","C2","C3")
SOURCE_STATUSES=("COMPILED","STRUCTURED_ONLY","RUNTIME_EVALUATED","HUMAN_JUDGMENT_REQUIRED","UNSUPPORTED")
TCB=("CANONICAL_PARSER","SHA256","SCHEMA_VALIDATOR","DETERMINISTIC_NORMALIZER","INDEPENDENT_CORE_VERIFIER","CRYPTO_PRIMITIVES")
BOUNDARIES={"source_is_compiler":False,"compiler_is_verifier":False,"verifier_is_authority":False,"authority_is_execution":False,
"compiler_creates_norms":False,"compiler_creates_authority":False,"compiler_authorizes":False,"compiler_executes":False,
"compiler_self_certifies":False,"compiler_self_activates":False,"compiler_modifies_sources":False,"compiler_invents_normative_defaults":False,
"llm_in_deterministic_normative_path":False,"network_semantic_dependency":False,"clock_semantic_dependency":False,
"random_semantic_dependency":False,"cwd_semantic_dependency":False,"hostname_semantic_dependency":False,
"hidden_local_state_semantic_dependency":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
CCPP={"CCPP-1":"NO_AUTHORITY_OR_ADMISSIBLE_ACTION_WIDENING","CCPP-2":"NO_NORMATIVE_CREATION","CCPP-3":"NO_SILENT_NORMATIVE_LOSS",
"CCPP-4":"UNKNOWN_NEVER_SATISFIES_REQUIRED_PRECONDITION","CCPP-5":"AUTHORITY_PROVENANCE_PRESERVED",
"CCPP-6":"COMPILATION_FAILURE_NEVER_RELAXES_REQUIREMENTS","CCPP-7":"COMPILATION_IS_NOT_AUTHORIZATION_OR_EXECUTION"}
FAILURE_TAXONOMY={"SOURCE_MISSING":"UNRESOLVED","SOURCE_HASH_MISMATCH":"UNRESOLVED","SOURCE_DRIFT":"UNRESOLVED","SCHEMA_INVALID":"UNRESOLVED",
"AMBIGUOUS":"UNRESOLVED","UNSUPPORTED":"UNSUPPORTED","UNKNOWN_REQUIRED_PRECONDITION":"UNRESOLVED","HUMAN_RESERVED_AUTOMATION":"UNRESOLVED","AUTHORITY_WIDENING":"UNRESOLVED",
"SCOPE_WIDENING":"UNRESOLVED","TEMPORAL_WEAKENING":"UNRESOLVED","PROVENANCE_LOSS":"UNRESOLVED","SEMANTIC_DELTA":"UNRESOLVED"}
THREAT_CLASSES=("NORM_OMISSION","MUST_TO_SHOULD","UNKNOWN_TO_TRUE","HUMAN_RESERVED_TO_AUTOMATED","SCOPE_WIDENING","EXPIRY_REMOVAL",
"DELEGATION_WIDENING","REVIEW_REMOVAL","SOURCE_DRIFT","IGNORED_HASH_MISMATCH","UNSUPPORTED_SKIP","PARSER_AMBIGUITY",
"YAML_JSON_DIVERGENCE","ORDER_DRIFT","CWD_DRIFT","DEPENDENCY_DRIFT","MALICIOUS_PACKAGE")
def classify_compilability(*,deterministic,runtime_facts_required=False,human_judgment_required=False):
    if human_judgment_required:return "C3"
    if runtime_facts_required:return "C2"
    return "C1" if deterministic else "C3"
def fail_closed(reason):
    return {"status":"FAIL","reason":reason,"profile_state":FAILURE_TAXONOMY.get(reason,"UNRESOLVED"),"authorization":False,"execution":False,"relaxed_rule":False}
def _human_reserved_automation(source,compiled):
    return source.get("authority")=="HUMAN_RESERVED" and compiled.get("authority")!="HUMAN_RESERVED"
def _unknown_semantics_weakened(source,compiled):
    return source.get("uncertainty")=="UNKNOWN" and compiled.get("uncertainty") not in ("UNKNOWN","UNRESOLVED")
def evaluate_preservation(source,compiled):
    req=("norm_id","strength","authority","scope","temporal","uncertainty","provenance")
    if any(k not in source for k in req): return fail_closed("SOURCE_MISSING")
    if any(k not in compiled for k in req): return fail_closed("SEMANTIC_DELTA")
    if compiled["norm_id"]!=source["norm_id"]: return fail_closed("SEMANTIC_DELTA")
    if source["strength"] in ("MUST","MUST_NOT") and compiled["strength"]!=source["strength"]: return fail_closed("SEMANTIC_DELTA")
    if _human_reserved_automation(source,compiled): return fail_closed("HUMAN_RESERVED_AUTOMATION")
    if compiled["authority"]!=source["authority"]: return fail_closed("AUTHORITY_WIDENING")
    if compiled["scope"]!=source["scope"]: return fail_closed("SCOPE_WIDENING")
    if compiled["temporal"]!=source["temporal"]: return fail_closed("TEMPORAL_WEAKENING")
    if compiled["provenance"]!=source["provenance"]: return fail_closed("PROVENANCE_LOSS")
    if _unknown_semantics_weakened(source,compiled): return fail_closed("UNKNOWN_REQUIRED_PRECONDITION")
    return {"status":"PASS","profile_state":"UNVERIFIED_COMPILED_PROFILE","authorization":False,"execution":False,"relaxed_rule":False}
def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,"status":STATUS,"roles":ROLES,
    "compilability":COMPILABILITY,"source_statuses":SOURCE_STATUSES,"tcb":TCB,"boundaries":BOUNDARIES,"ccpp":CCPP,
    "failure_taxonomy":FAILURE_TAXONOMY,"threat_classes":THREAT_CLASSES}
