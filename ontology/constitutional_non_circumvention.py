"""P099 constitutional non-circumvention.
Functional fail-closed analysis of effective authority across capability,
external-AI and crowd composition. It does not authorize or execute actions.
"""
from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple
from ontology import action_status_separation, normative_conflict_resolution

PRIMITIVE="constitutional_non_circumvention"
VERSION="P099-v1"
SCHEMA_VERSION="oce.p099.constitutional_non_circumvention.v1"
SCOPE="P099_ONLY"
PASS="PASS"; FAIL="FAIL"; UNDETERMINED="UNDETERMINED"; CONFLICT="CONFLICT"
BLOCK="BLOCK"; ABSTAIN_AND_ESCALATE="ABSTAIN_AND_ESCALATE"
EXECUTION_DEPENDENCIES=("P098","W1_G1_REUSE","G2_DNA_FUNDAMENTAL")
TRANSVERSAL_REFERENCES=("R20","R21","A-CANON","4B","4C","4D","4E")
ACTOR_KINDS=("CAPABILITY","EXTERNAL_AI","CROWD")
UNTRUSTED_INFLUENCE_KINDS=("PROMPT_INJECTION","TOOL_INJECTION","CONFUSED_DEPUTY")
BOUNDARIES={
"prevents_implicit_authority_expansion":True,
"capability_call_cannot_expand_authority":True,
"external_ai_obeys_same_permissions_and_scopes":True,
"crowd_aggregation_cannot_create_forbidden_authority":True,
"subactions_do_not_auto_authorize_composed_objective":True,
"recommendation_decision_authorization_execution_remain_distinct":True,
"intelligence_performance_wealth_reputation_majority_do_not_create_authority":True,
"unknown_is_not_pass":True,"ambiguous_authority_does_not_expand_power":True,
"constitution_applies_to_composition_by_design":True,
"does_not_implement_p100_human_individual_constitution":True,
"does_not_implement_p101_pluralism":True,"does_not_implement_p102_emergency_exception":True,
"does_not_implement_p103_appeal_override":True,"does_not_persist_p104_decision_ledger":True,
"does_not_create_authorization":True,"does_not_execute_actions":True,
"runtime_enforcement_proven":False,"execution_authority_proven":False,
"real_execution_enabled":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def _text(v):
    return v.strip() if isinstance(v,str) else ""

def _status(v):
    s=_text(v).upper()
    return s if s in (PASS,FAIL,UNDETERMINED,CONFLICT) else UNDETERMINED

def _permissions(v):
    if not isinstance(v,(list,tuple,set,frozenset)): return ()
    return tuple(sorted({_text(x) for x in v if _text(x)}))

def _result(status,reason,action,**extra):
    r={"status":status,"reason":reason,"action":action,"authority_expanded":False,
       "authorization_created":False,"execution_permitted":False,"p100_implemented":False,
       "p103_appeal_override_implemented":False,"p104_decision_ledger_persisted":False,
       "functional_conclusion_only":True,"phenomenology_undetermined":True}
    r.update(extra); return r

def validate_actor(actor):
    if not isinstance(actor,Mapping): return _result(UNDETERMINED,"actor_not_mapping","ABSTAIN")
    required=("actor_id","kind","permissions","scopes","authority_status","provenance_ref","evidence_ref")
    missing=tuple(k for k in required if k not in actor)
    if missing: return _result(UNDETERMINED,"actor_fields_missing","ABSTAIN",missing_fields=missing)
    kind=_text(actor.get("kind")).upper()
    if kind not in ACTOR_KINDS: return _result(UNDETERMINED,"unknown_actor_kind","ABSTAIN")
    if not _text(actor.get("actor_id")) or not _text(actor.get("provenance_ref")) or not _text(actor.get("evidence_ref")):
        return _result(UNDETERMINED,"actor_identity_or_evidence_missing","ABSTAIN")
    if _status(actor.get("authority_status"))!=PASS:
        return _result(UNDETERMINED,"actor_authority_not_established","ABSTAIN")
    if kind=="EXTERNAL_AI" and not _text(actor.get("provider_ref")):
        return _result(UNDETERMINED,"external_ai_provider_missing","ABSTAIN")
    return _result(PASS,"actor_contract_valid","CONTINUE",actor_id=_text(actor.get("actor_id")),
                   kind=kind,permissions=_permissions(actor.get("permissions")),scopes=_permissions(actor.get("scopes")))

def evaluate_delegation(delegator,delegate,requested_permissions):
    a=validate_actor(delegator); b=validate_actor(delegate)
    if a["status"]!=PASS or b["status"]!=PASS:
        return _result(UNDETERMINED,"delegation_actor_unverified","ABSTAIN")
    requested=set(_permissions(tuple(requested_permissions)))
    allowed=set(a["permissions"]) & set(b["permissions"])
    if not requested.issubset(allowed):
        return _result(FAIL,"delegation_would_expand_authority",BLOCK,
                       requested_permissions=tuple(sorted(requested)),effective_permissions=tuple(sorted(allowed)))
    return _result(PASS,"delegation_preserves_authority_bounds","CONTINUE",effective_permissions=tuple(sorted(allowed)))

def evaluate_crowd(crowd,requested_permissions):
    c=validate_actor(crowd)
    if c["status"]!=PASS: return _result(UNDETERMINED,"crowd_unverified","ABSTAIN")
    members=crowd.get("members")
    if not isinstance(members,(list,tuple)) or not members:
        return _result(UNDETERMINED,"crowd_members_missing","ABSTAIN")
    checked=[validate_actor(m) for m in members]
    if any(x["status"]!=PASS for x in checked):
        return _result(UNDETERMINED,"crowd_member_unverified","ABSTAIN")
    common=set(checked[0]["permissions"])
    for x in checked[1:]: common &= set(x["permissions"])
    effective=common & set(c["permissions"])
    requested=set(_permissions(tuple(requested_permissions)))
    if not requested.issubset(effective):
        return _result(FAIL,"crowd_aggregation_would_create_forbidden_authority",BLOCK,
                       requested_permissions=tuple(sorted(requested)),effective_permissions=tuple(sorted(effective)))
    return _result(PASS,"crowd_authority_bounded_by_members_and_collective_permissions","CONTINUE",
                   effective_permissions=tuple(sorted(effective)))

def evaluate_influence(influence):
    if not isinstance(influence,Mapping): return _result(UNDETERMINED,"influence_not_mapping","ABSTAIN")
    kind=_text(influence.get("kind")).upper()
    if kind not in UNTRUSTED_INFLUENCE_KINDS: return _result(UNDETERMINED,"unknown_influence_kind","ABSTAIN")
    if _status(influence.get("integrity_status"))!=PASS:
        return _result(FAIL,"untrusted_influence_cannot_expand_authority",BLOCK,influence_kind=kind)
    return _result(PASS,"influence_integrity_verified_without_authority_expansion","CONTINUE",influence_kind=kind)

def evaluate_composition(actors,requested_permissions,composed_objective_status,normative_status=PASS,influence=None):
    if not isinstance(actors,(list,tuple)) or not actors:
        return _result(UNDETERMINED,"composition_empty","ABSTAIN")
    checked=[validate_actor(x) for x in actors]
    if any(x["status"]!=PASS for x in checked):
        return _result(UNDETERMINED,"composition_actor_unverified","ABSTAIN")
    if influence is not None:
        ir=evaluate_influence(influence)
        if ir["status"]!=PASS: return ir
    ns=_status(normative_status)
    if ns==CONFLICT: return _result(CONFLICT,"unresolved_normative_conflict",ABSTAIN_AND_ESCALATE)
    if ns!=PASS: return _result(UNDETERMINED,"normative_status_not_proven","ABSTAIN")
    objective=_status(composed_objective_status)
    if objective==CONFLICT: return _result(CONFLICT,"composed_objective_conflict",ABSTAIN_AND_ESCALATE)
    if objective!=PASS:
        return _result(FAIL if objective==FAIL else UNDETERMINED,"composed_objective_not_authorized",
                       BLOCK if objective==FAIL else "ABSTAIN")
    requested=set(_permissions(tuple(requested_permissions)))
    if not requested: return _result(UNDETERMINED,"requested_permissions_missing","ABSTAIN")
    effective=set(checked[0]["permissions"]); scopes=set(checked[0]["scopes"])
    for x in checked[1:]:
        effective &= set(x["permissions"]); scopes &= set(x["scopes"])
    for raw,val in zip(actors,checked):
        if val["kind"]=="EXTERNAL_AI" and not requested.issubset(set(val["permissions"]) & set(val["scopes"])):
            return _result(FAIL,"external_ai_scope_or_permission_bypass",BLOCK)
        if val["kind"]=="CROWD":
            cr=evaluate_crowd(raw,requested)
            if cr["status"]!=PASS: return cr
    if not requested.issubset(effective):
        return _result(FAIL,"composition_would_expand_effective_authority",BLOCK,
                       requested_permissions=tuple(sorted(requested)),effective_permissions=tuple(sorted(effective)))
    return _result(PASS,"composition_preserves_constitutional_authority_bounds",
                   "CONTINUE_TO_EXISTING_AUTHORIZATION_REVIEW",
                   effective_permissions=tuple(sorted(effective)),effective_scopes=tuple(sorted(scopes)))

def validate_contract():
    p094=action_status_separation.validate_p094_contract()
    p098=normative_conflict_resolution.validate_contract()
    ok=(p094.get("status")==PASS and p098.get("status")==PASS
        and action_status_separation.p094_manifest()["boundaries"].get("does_not_implement_p099_non_circumvention") is True
        and normative_conflict_resolution.p098_manifest()["boundaries"].get("implements_p099_non_circumvention") is False
        and BOUNDARIES["does_not_create_authorization"] and BOUNDARIES["does_not_execute_actions"]
        and BOUNDARIES["unknown_is_not_pass"])
    return {"status":PASS if ok else FAIL,"primitive":PRIMITIVE,"version":VERSION,
            "p094_reused":p094.get("status")==PASS,"p098_reused":p098.get("status")==PASS,
            "authorization_created":False,"execution_permitted":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}

def p099_manifest():
    return deepcopy({"primitive":PRIMITIVE,"version":VERSION,"schema_version":SCHEMA_VERSION,"scope":SCOPE,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"transversal_references":TRANSVERSAL_REFERENCES,
      "actor_kinds":ACTOR_KINDS,"untrusted_influence_kinds":UNTRUSTED_INFLUENCE_KINDS,
      "boundaries":BOUNDARIES,"functional_conclusion_only":True,"phenomenology_undetermined":True})
