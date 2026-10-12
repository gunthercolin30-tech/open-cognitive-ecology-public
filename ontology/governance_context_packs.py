from __future__ import annotations
from copy import deepcopy
from datetime import date
from typing import Any, Dict, Mapping
from ontology import governance_contextual, normative_hierarchy, constitution_registry

PRIMITIVE="governance_context_packs"; VERSION="P097-v1"; SCHEMA_VERSION="oce.p097.governance_context_pack.v1"; SCOPE="P097_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
REQUIRED_FIELDS=("governance_context_id","version","jurisdiction","sector","organization","mission","laws","policies","risk_profile","effective_date","review_date","provenance","audit")
EXECUTION_DEPENDENCIES=("P096_GOVERNANCE_CONTEXTUAL","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON","4B","4C","4D","4E")
BOUNDARIES={"formal_versioned_context_packs_only":True,"modifies_dna_fundamental":False,"modifies_constitution_core":False,
"resolves_p098_conflicts":False,"implements_p099_non_circumvention":False,"persists_p104_decision_ledger":False,
"creates_authorization":False,"executes_actions":False,"runtime_enforcement_proven":False,"execution_authority_proven":False,
"real_execution_enabled":False,"unknown_promoted_to_pass":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def _present(v): return v is not None and str(v).strip() not in ("","UNKNOWN")
def _date(v):
    if not _present(v): return None
    try: return date.fromisoformat(str(v).strip())
    except (TypeError,ValueError): return None
def _strings(v): return isinstance(v,(tuple,list)) and bool(v) and all(_present(x) for x in v)
def _risk(v): return isinstance(v,Mapping) and _present(v.get("risk_class")) and _present(v.get("provenance"))
def _audit(v): return isinstance(v,Mapping) and all(_present(v.get(k)) for k in ("created_at","created_by","review_status"))
def canonical_pack(pack): return {k:deepcopy(pack.get(k)) for k in sorted(pack.keys())}

def validate_pack(pack,as_of=None):
    if not isinstance(pack,Mapping): return {"status":UNDETERMINED,"reason":"PACK_NOT_MAPPING","valid":False}
    missing=tuple(f for f in REQUIRED_FIELDS if f not in pack)
    if missing: return {"status":UNDETERMINED,"reason":"REQUIRED_FIELDS_MISSING","valid":False,"missing_fields":missing}
    scalar=("governance_context_id","version","jurisdiction","sector","organization","mission","effective_date","review_date","provenance")
    unknown=tuple(f for f in scalar if not _present(pack.get(f)))
    if unknown: return {"status":UNDETERMINED,"reason":"REQUIRED_FIELDS_UNKNOWN","valid":False,"unknown_fields":unknown}
    if not _strings(pack.get("laws")) or not _strings(pack.get("policies")): return {"status":UNDETERMINED,"reason":"LAWS_OR_POLICIES_INCOMPLETE","valid":False}
    if not _risk(pack.get("risk_profile")): return {"status":UNDETERMINED,"reason":"RISK_PROFILE_INCOMPLETE","valid":False}
    if not _audit(pack.get("audit")): return {"status":UNDETERMINED,"reason":"AUDIT_METADATA_INCOMPLETE","valid":False}
    effective,review=_date(pack.get("effective_date")),_date(pack.get("review_date"))
    if effective is None or review is None or review < effective: return {"status":FAIL,"reason":"INVALID_EFFECTIVE_OR_REVIEW_DATE","valid":False}
    relation=str(pack.get("relation_to_constitution","specify")).strip().lower()
    rel=normative_hierarchy.evaluate_relation("Governance_Contextual","Constitution_Operational",relation)
    if rel.get("status")==CONFLICT: return {"status":CONFLICT,"reason":"PACK_CONTRADICTS_HIGHER_NORM","valid":False}
    if rel.get("status")!=PASS: return {"status":UNDETERMINED,"reason":"UNKNOWN_NORMATIVE_RELATION","valid":False}
    declared=pack.get("declared_conflicts_with",())
    if not isinstance(declared,(tuple,list)) or not all(_present(x) for x in declared): return {"status":UNDETERMINED,"reason":"INVALID_DECLARED_CONFLICTS","valid":False}
    check=_date(as_of) if as_of is not None else None
    if as_of is not None and check is None: return {"status":UNDETERMINED,"reason":"INVALID_AS_OF_DATE","valid":False}
    if check is not None and check < effective: return {"status":UNDETERMINED,"reason":"PACK_NOT_YET_EFFECTIVE","valid":False}
    if check is not None and check > review: return {"status":UNDETERMINED,"reason":"PACK_REVIEW_OVERDUE","valid":False}
    return {"status":PASS,"reason":"P097_PACK_VALID","valid":True,"governance_context_id":str(pack["governance_context_id"]),
    "version":str(pack["version"]),"canonical_pack":canonical_pack(pack),"authorization_created":False,"execution_permitted":False,
    "functional_conclusion_only":True,"phenomenology_undetermined":True}

def replace_pack(current,replacement):
    a,b=validate_pack(current),validate_pack(replacement)
    if a.get("status")!=PASS or b.get("status")!=PASS: return {"status":UNDETERMINED,"reason":"INVALID_PACK_FOR_REPLACEMENT","pack":None}
    if str(current.get("governance_context_id"))!=str(replacement.get("governance_context_id")): return {"status":CONFLICT,"reason":"REPLACEMENT_CONTEXT_ID_MISMATCH","pack":None}
    if str(current.get("version"))==str(replacement.get("version")): return {"status":CONFLICT,"reason":"REPLACEMENT_REQUIRES_NEW_VERSION","pack":None}
    return {"status":PASS,"reason":"PACK_REPLACED","pack":canonical_pack(replacement),"authorization_created":False,"execution_permitted":False}

def stack_packs(packs):
    if not isinstance(packs,(tuple,list)) or not packs: return {"status":UNDETERMINED,"reason":"PACK_STACK_EMPTY_OR_INVALID","packs":()}
    normalized=[]; identities=set(); ids=set()
    for pack in packs:
        r=validate_pack(pack)
        if r.get("status")!=PASS: return {"status":r.get("status",UNDETERMINED),"reason":"PACK_STACK_CONTAINS_INVALID_PACK","packs":()}
        identity=(str(pack["governance_context_id"]),str(pack["version"]))
        if identity in identities: return {"status":CONFLICT,"reason":"DUPLICATE_PACK_IDENTITY","packs":()}
        identities.add(identity); ids.add(str(pack["governance_context_id"])); normalized.append(canonical_pack(pack))
    for pack in normalized:
        if set(str(v) for v in pack.get("declared_conflicts_with",())).intersection(ids):
            return {"status":CONFLICT,"reason":"DECLARED_PACK_CONFLICT","action":"ABSTAIN_AND_ESCALATE","packs":tuple(normalized),"p098_resolution_performed":False}
    ordered=tuple(sorted(normalized,key=lambda x:(str(x["governance_context_id"]),str(x["version"]))))
    return {"status":PASS,"reason":"PACK_STACK_STRUCTURALLY_VALID","packs":ordered,"p098_resolution_performed":False,
    "authorization_created":False,"execution_permitted":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def validate_contract():
    a=governance_contextual.validate_contract(); b=constitution_registry.validate_registry(); c=normative_hierarchy.validate_hierarchy()
    ok=a.get("status")==PASS and b.get("status")==PASS and c.get("status")==PASS and len(REQUIRED_FIELDS)==len(set(REQUIRED_FIELDS))
    return {"status":PASS if ok else FAIL,"p096_reuse_ok":a.get("status")==PASS,"p092_registry_reuse_ok":b.get("status")==PASS,
    "p087_hierarchy_reuse_ok":c.get("status")==PASS,"required_field_count":len(REQUIRED_FIELDS),"p098_conflict_resolution_implemented":False,
    "p104_decision_ledger_persisted":False,"authorization_created":False,"execution_permitted":False,
    "functional_conclusion_only":True,"phenomenology_undetermined":True}

def p097_manifest():
    return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,"required_fields":REQUIRED_FIELDS,
    "execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,"boundaries":BOUNDARIES,
    "example_pack_names":("Governance_FR","Governance_CH","Governance_EU","Governance_Industrial","Governance_Healthcare","Governance_Company_X"),
    "example_pack_names_are_identifiers_not_legal_content":True,"p098_conflict_resolution_implemented":False,"p104_decision_ledger_persisted":False,
    "functional_conclusion_only":True,"phenomenology_undetermined":True})
