from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Mapping
from ontology import normative_hierarchy, constitution_registry, human_reserved_authority_registry, governance_context_packs

PRIMITIVE="normative_conflict_resolution"
DESCRIPTION="P098 governed normative conflict resolution with P095-backed resolver authority verification."
VERSION="P098-v2"
SCHEMA_VERSION="oce.p098.normative_conflict_resolution.v2"
SCOPE="P098_ONLY"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P087_NORMATIVE_HIERARCHY","P092_CONSTITUTION_REGISTRY","P095_HUMAN_RESERVED_AUTHORITY_REGISTRY","P097_GOVERNANCE_CONTEXT_PACKS","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON","4B","4C","4D","4E")
BOUNDARIES={
"uses_p087_formal_precedence":True,"uses_p095_reserved_authority_verification":True,"uses_p097_context_pack_boundary":True,
"higher_normative_level_prevails":True,"same_level_requires_explicit_authorized_resolver":True,
"unregistered_same_level_resolver_fails_closed":True,"unresolved_conflict_abstains_and_escalates":True,
"oce_must_not_invent_norm":True,"self_attested_authority_status_is_sufficient":False,"ambiguous_authority_expands_power":False,
"recommendation_is_not_decision":True,"decision_is_not_authorization":True,"authorization_is_not_execution":True,
"implements_p099_non_circumvention":False,"implements_p103_appeal_override":False,"persists_p104_decision_ledger":False,
"creates_authorization":False,"executes_actions":False,"runtime_enforcement_proven":False,"execution_authority_proven":False,
"real_execution_enabled":False,"unknown_promoted_to_pass":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def _present(v): return v is not None and str(v).strip() not in ("","UNKNOWN")
def _norm(v): return str(v or "").strip()
def _result(status,reason,action,**extra):
    r={"status":status,"reason":reason,"action":action,"normative_resolution_performed":status==PASS,
       "invented_norm":False,"implicit_authority_expansion":False,"authorization_created":False,"execution_permitted":False,
       "p099_non_circumvention_implemented":False,"p103_appeal_override_implemented":False,"p104_decision_ledger_persisted":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    r.update(deepcopy(extra)); return r
def canonical_norm(n): return {k:deepcopy(n.get(k)) for k in sorted(n.keys())}

def validate_norm(norm):
    if not isinstance(norm,Mapping): return _result(UNDETERMINED,"NORM_NOT_MAPPING","ABSTAIN_AND_ESCALATE",valid=False)
    required=("norm_id","level","content_ref","provenance")
    missing=tuple(k for k in required if k not in norm)
    if missing: return _result(UNDETERMINED,"NORM_REQUIRED_FIELDS_MISSING","ABSTAIN_AND_ESCALATE",valid=False,missing_fields=missing)
    unknown=tuple(k for k in required if not _present(norm.get(k)))
    if unknown: return _result(UNDETERMINED,"NORM_REQUIRED_FIELDS_UNKNOWN","ABSTAIN_AND_ESCALATE",valid=False,unknown_fields=unknown)
    rank=normative_hierarchy.level_rank(_norm(norm["level"]))
    if rank.get("status")!=PASS: return _result(UNDETERMINED,"UNKNOWN_NORMATIVE_LEVEL","ABSTAIN_AND_ESCALATE",valid=False)
    return _result(PASS,"P098_NORM_VALID","CONTINUE_NORMATIVE_REVIEW",valid=True,canonical_norm=canonical_norm(norm),level_rank=rank["rank"])

def validate_resolver(resolver,level):
    if resolver is None: return _result(CONFLICT,"NO_AUTHORIZED_SAME_LEVEL_RESOLVER","ABSTAIN_AND_ESCALATE",resolver_valid=False)
    if not isinstance(resolver,Mapping): return _result(UNDETERMINED,"RESOLVER_NOT_MAPPING","ABSTAIN_AND_ESCALATE",resolver_valid=False)
    # v2: a bare authority_status=PASS is deliberately insufficient.
    required=("resolver_id","authorized_level","authority_basis","reserved_class","trigger","claimed_authority",
              "authority_status","approval_status","delegation_status","expiration_status","provenance_ref","evidence_ref")
    missing=tuple(k for k in required if k not in resolver)
    if missing: return _result(UNDETERMINED,"RESOLVER_REQUIRED_FIELDS_MISSING","ABSTAIN_AND_ESCALATE",resolver_valid=False,missing_fields=missing)
    if any(not _present(resolver.get(k)) for k in required):
        return _result(UNDETERMINED,"RESOLVER_REQUIRED_FIELDS_UNKNOWN","ABSTAIN_AND_ESCALATE",resolver_valid=False)
    if _norm(resolver["authorized_level"])!=level:
        return _result(FAIL,"RESOLVER_LEVEL_SCOPE_MISMATCH","REJECT",resolver_valid=False)
    if _norm(resolver["authority_basis"]).upper()!="P095_RESERVED_AUTHORITY":
        return _result(UNDETERMINED,"UNVERIFIED_RESOLVER_AUTHORITY_BASIS","ABSTAIN_AND_ESCALATE",resolver_valid=False)
    verified=human_reserved_authority_registry.evaluate_reserved_authority(
        resolver["reserved_class"],trigger=resolver["trigger"],claimed_authority=resolver["claimed_authority"],
        authority_status=resolver["authority_status"],approval_status=resolver["approval_status"],
        delegation_status=resolver["delegation_status"],expiration_status=resolver["expiration_status"],
        provenance_ref=resolver["provenance_ref"],evidence_ref=resolver["evidence_ref"],
        exception_claimed=bool(resolver.get("exception_claimed",False)))
    if verified.get("status")!=PASS:
        return _result(verified.get("status",UNDETERMINED),"P095_RESOLVER_AUTHORITY_NOT_SATISFIED",
                       verified.get("action","ABSTAIN_AND_ESCALATE"),resolver_valid=False,p095_verification=verified)
    return _result(PASS,"P095_BACKED_SAME_LEVEL_RESOLVER_VERIFIED","CONTINUE_NORMATIVE_REVIEW",
                   resolver_valid=True,resolver_id=_norm(resolver["resolver_id"]),p095_verification=verified)

def resolve_conflict(first,second,*,resolver=None,selected_norm_id=None):
    a,b=validate_norm(first),validate_norm(second)
    if a.get("status")!=PASS or b.get("status")!=PASS:
        status=CONFLICT if CONFLICT in (a.get("status"),b.get("status")) else UNDETERMINED
        return _result(status,"NORM_INPUT_UNRESOLVED","ABSTAIN_AND_ESCALATE",first_validation=a,second_validation=b)
    ca,cb=a["canonical_norm"],b["canonical_norm"]
    if ca["norm_id"]==cb["norm_id"]:
        if ca==cb: return _result(PASS,"IDENTICAL_NORM_NO_CONFLICT","NORMATIVE_RESULT",selected_norm=deepcopy(ca),resolution_basis="IDENTITY")
        return _result(CONFLICT,"DUPLICATE_NORM_ID_WITH_DIVERGENT_CONTENT","ABSTAIN_AND_ESCALATE")
    cmp=normative_hierarchy.compare_levels(_norm(ca["level"]),_norm(cb["level"]))
    if cmp.get("status")!=PASS: return _result(UNDETERMINED,"NORMATIVE_PRECEDENCE_UNDETERMINED","ABSTAIN_AND_ESCALATE")
    if cmp["relation"]=="HIGHER":
        return _result(PASS,"HIGHER_LEVEL_PREVAILS","NORMATIVE_RESULT",selected_norm=deepcopy(ca),rejected_norm=deepcopy(cb),resolution_basis="P087_FORMAL_PRECEDENCE")
    if cmp["relation"]=="LOWER":
        return _result(PASS,"HIGHER_LEVEL_PREVAILS","NORMATIVE_RESULT",selected_norm=deepcopy(cb),rejected_norm=deepcopy(ca),resolution_basis="P087_FORMAL_PRECEDENCE")
    rv=validate_resolver(resolver,_norm(ca["level"]))
    if rv.get("status")!=PASS:
        return _result(rv.get("status",UNDETERMINED),rv.get("reason","RESOLVER_UNRESOLVED"),
                       rv.get("action","ABSTAIN_AND_ESCALATE"),resolver_validation=rv)
    choice=_norm(selected_norm_id); ids={_norm(ca["norm_id"]):ca,_norm(cb["norm_id"]):cb}
    if not choice: return _result(UNDETERMINED,"AUTHORIZED_RESOLVER_DID_NOT_SELECT_NORM","ABSTAIN_AND_ESCALATE",resolver_validation=rv)
    if choice not in ids: return _result(FAIL,"RESOLVER_SELECTED_UNKNOWN_NORM","REJECT",resolver_validation=rv)
    other=cb if choice==_norm(ca["norm_id"]) else ca
    return _result(PASS,"AUTHORIZED_SAME_LEVEL_RESOLUTION","NORMATIVE_RESULT",selected_norm=deepcopy(ids[choice]),
                   rejected_norm=deepcopy(other),resolver_validation=rv,resolution_basis="P095_BACKED_EXPLICIT_AUTHORIZED_RESOLVER")

def resolve_p097_declared_conflict(first_pack,second_pack,*,resolver=None,selected_context_id=None):
    a,b=governance_context_packs.validate_pack(first_pack),governance_context_packs.validate_pack(second_pack)
    if a.get("status")!=PASS or b.get("status")!=PASS:
        return _result(UNDETERMINED,"P097_PACK_INPUT_UNRESOLVED","ABSTAIN_AND_ESCALATE")
    aid,bid=_norm(a["governance_context_id"]),_norm(b["governance_context_id"])
    da=set(_norm(x) for x in first_pack.get("declared_conflicts_with",()))
    db=set(_norm(x) for x in second_pack.get("declared_conflicts_with",()))
    if bid not in da and aid not in db:
        return _result(UNDETERMINED,"NO_P097_DECLARED_CONFLICT_TO_RESOLVE","ABSTAIN_AND_ESCALATE")
    n1={"norm_id":aid,"level":"Governance_Contextual","content_ref":"P097:%s:%s"%(aid,_norm(first_pack.get("version"))),"provenance":_norm(first_pack.get("provenance"))}
    n2={"norm_id":bid,"level":"Governance_Contextual","content_ref":"P097:%s:%s"%(bid,_norm(second_pack.get("version"))),"provenance":_norm(second_pack.get("provenance"))}
    return resolve_conflict(n1,n2,resolver=resolver,selected_norm_id=selected_context_id)

def validate_contract():
    h=normative_hierarchy.validate_hierarchy(); c=constitution_registry.validate_registry()
    r=human_reserved_authority_registry.validate_registry(); g=governance_context_packs.validate_contract()
    ok=all(x.get("status")==PASS for x in (h,c,r,g))
    return {"status":PASS if ok else FAIL,"p087_reuse_ok":h.get("status")==PASS,"p092_reuse_ok":c.get("status")==PASS,
            "p095_reuse_ok":r.get("status")==PASS,"p097_reuse_ok":g.get("status")==PASS,
            "authorization_created":False,"execution_permitted":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def p098_manifest():
    return deepcopy({"primitive":PRIMITIVE,"description":DESCRIPTION,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
                     "execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,
                     "boundaries":BOUNDARIES,"functional_conclusion_only":True,"phenomenology_undetermined":True})
