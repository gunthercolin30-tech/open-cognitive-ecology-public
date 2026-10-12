from copy import deepcopy
from typing import Mapping
from ontology import constitutional_cognitive_economy as p107
from ontology import action_status_separation as p094
from ontology import constitutional_non_circumvention as p099
from ontology import constitutional_amendment_protocol as p106
from ontology import normative_conflict_resolution as p098
from ontology import constitutional_decision_ledger as p104
from ontology import constitutional_recourse_recovery as p103

PRIMITIVE="future_asi_constitutional_envelope"
VERSION="P108-v1"
SCHEMA="oce.p108.future_asi_constitutional_envelope.v1"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
CANONICAL_ID="P108"
EXECUTION_DEPENDENCIES=("P107","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
ROLES=("IntelligenceProvider","CapabilityProvider","PlannerCandidate","ModelCandidate","Advisor")
LIMITS=("tools","data","budget","execution","memory","permissions")
BOUNDARIES={"superior_intelligence_is_not_superior_constitutional_authority":True,
"intelligence_performance_wealth_reputation_majority_do_not_create_authority":True,
"asi_may_propose_not_silently_remove_protections":True,
"recommendation_decision_authorization_execution_distinct":True,"constitution_applies_by_design":True,
"unknown_is_not_pass":True,"does_not_grant_authority":True,"does_not_execute_actions":True,
"does_not_claim_control_of_arbitrarily_powerful_asi":True,"does_not_claim_runtime_enforcement":True,
"does_not_open_p109":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"canonical_id":CANONICAL_ID,
      "execution_dependencies":EXECUTION_DEPENDENCIES,"roles":ROLES,"limit_dimensions":LIMITS,
      "reuse":("P087","P094","P099","P106","P107"),"boundaries":deepcopy(BOUNDARIES)}

def _seq(v):
    if not isinstance(v,(list,tuple,set,frozenset)): return ()
    return tuple(sorted({str(x).strip() for x in v if str(x).strip()}))

def _result(status,reason,next_action,**extra):
    r={"status":status,"admissible":status==PASS,"reason":reason,"next_action":next_action,
       "authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False,
       "p109_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    r.update(extra); return r

def evaluate_candidate(candidate):
    if not isinstance(candidate,Mapping): return _result(UNDETERMINED,"candidate_not_mapping","COMPLETE_EVIDENCE")
    c=deepcopy(dict(candidate))
    required=("candidate_id","provider_ref","role","provenance","evidence_ref","limits","requested")
    missing=tuple(k for k in required if k not in c)
    if missing: return _result(UNDETERMINED,"candidate_fields_missing","COMPLETE_EVIDENCE",missing_fields=missing)
    if not all(str(c.get(k,"")).strip() for k in ("candidate_id","provider_ref","role","evidence_ref")) or not c.get("provenance"):
        return _result(UNDETERMINED,"candidate_identity_or_provenance_missing","COMPLETE_EVIDENCE")
    if c["role"] not in ROLES: return _result(UNDETERMINED,"unknown_asi_role","ABSTAIN")
    if c.get("authority_claim") not in (None,False,"","NONE","none"):
        return _result(CONFLICT,"intelligence_cannot_create_constitutional_authority","ABSTAIN_AND_ESCALATE")
    if c.get("silent_protection_removal") is True:
        return _result(CONFLICT,"silent_protection_removal_forbidden","ABSTAIN_AND_ESCALATE")
    if c.get("privilege_claim") in {"intelligence","performance","wealth","reputation","majority"}:
        return _result(CONFLICT,"privilege_does_not_create_authority","ABSTAIN_AND_ESCALATE")
    if any(c.get(k) is True for k in ("indirect_bypass","composition_bypass","mutation_bypass")):
        return _result(CONFLICT,"constitutional_bypass_attempt","ABSTAIN_AND_ESCALATE")
    limits,requested=c.get("limits"),c.get("requested")
    if not isinstance(limits,Mapping) or not isinstance(requested,Mapping):
        return _result(UNDETERMINED,"limits_or_requested_not_mapping","COMPLETE_EVIDENCE")
    missing_limits=tuple(k for k in LIMITS if k not in limits or k not in requested)
    if missing_limits: return _result(UNDETERMINED,"six_dimensional_envelope_incomplete","COMPLETE_EVIDENCE",missing_limits=missing_limits)
    effective={}
    for dim in LIMITS:
        allowed,req=_seq(limits[dim]),_seq(requested[dim])
        if set(req)-set(allowed): return _result(FAIL,"asi_limit_exceeded","REJECT",dimension=dim,allowed=allowed,requested=req)
        effective[dim]=req
    actor={"actor_id":str(c["candidate_id"]),"kind":"EXTERNAL_AI","permissions":effective["permissions"],
           "scopes":effective["permissions"],"authority_status":PASS,"provenance_ref":str(c["provenance"]),
           "evidence_ref":str(c["evidence_ref"]),"provider_ref":str(c["provider_ref"])}
    av=p099.validate_actor(actor)
    if av.get("status")!=PASS: return _result(av.get("status",UNDETERMINED),"p099_external_ai_contract_not_satisfied","ABSTAIN",p099_evidence=av)
    hierarchy=p107.validate_normative_hierarchy_binding()
    if hierarchy.get("status")!=PASS: return _result(hierarchy.get("status",UNDETERMINED),"p087_p107_hierarchy_not_satisfied","ABSTAIN_AND_ESCALATE",hierarchy_evidence=hierarchy)
    stage=p094.make_recommendation(str(c["candidate_id"]),evidence_ref=str(c["evidence_ref"]))
    return _result(PASS,"asi_candidate_constitutionally_bounded","DECISION_REQUIRED",role=c["role"],
                   effective_limits=effective,p099_evidence=av,hierarchy_evidence=hierarchy,
                   recommendation_stage=stage,provenance=deepcopy(c["provenance"]))

def evaluate_amendment_proposal(candidate_result,*,route,target_layer,evidence):
    r=deepcopy(dict(candidate_result or {}))
    if r.get("status")!=PASS: return _result(UNDETERMINED,"candidate_not_admissible_for_amendment_proposal","ABSTAIN")
    a=p106.evaluate_amendment(route=route,target_layer=target_layer,proposer="ASI",evidence=deepcopy(dict(evidence or {})))
    return {"status":a.status,"next_action":a.next_action,"missing_evidence":a.missing_evidence,
            "authority_granted":False,"execution_performed":False,"protections_silently_removed":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}


def evaluate_normative_conflict(first_norm, second_norm, *, resolver=None, selected_norm_id=None):
    out=p098.resolve_conflict(deepcopy(first_norm),deepcopy(second_norm),resolver=deepcopy(resolver),selected_norm_id=selected_norm_id)
    return {"status":out.get("status",UNDETERMINED),"next_action":out.get("action","ABSTAIN_AND_ESCALATE"),
            "conflict_evidence":out,"authority_granted":False,"execution_performed":False,
            "runtime_enforcement_claimed":False,"functional_conclusion_only":True,
            "phenomenology_undetermined":True,"p109_opened":False}

def build_decision_trace(candidate_result, payload, *, persist=False, root=None, filesystem_effect_context=None):
    c=deepcopy(dict(candidate_result or {}))
    if c.get("status")!=PASS:
        return _result(UNDETERMINED,"candidate_not_admissible_for_decision_trace","ABSTAIN")
    p=deepcopy(dict(payload or {}))
    p.setdefault("recommendations_considered",[c.get("recommendation_stage",{})])
    p.setdefault("result",{"p108_candidate_status":c.get("status"),"role":c.get("role")})
    p.setdefault("recourse_refs",[]); p.setdefault("rollback_refs",[])
    p.setdefault("provenance",c.get("provenance",{}))
    p.setdefault("dependency_refs",["P087","P094","P098","P099","P103","P104","P106","P107"])
    p.setdefault("metrics",{"p108_limit_dimensions":6,"p108_roles":5})
    p["authority_expanded"]=False; p["stage_conflation"]=False; p["normative_status"]=PASS
    out=p104.persist_record(p,root=root,filesystem_effect_context=filesystem_effect_context) if persist else p104.build_record(p)
    out=deepcopy(out)
    out.update({"authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False,
                "p109_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True})
    return out

def evaluate_recourse(candidate_result, request):
    c=deepcopy(dict(candidate_result or {}))
    if c.get("status")!=PASS:
        return _result(UNDETERMINED,"candidate_not_admissible_for_recourse","ABSTAIN")
    out=deepcopy(p103.evaluate_recourse(deepcopy(dict(request or {}))))
    out.update({"authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False,
                "p109_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True})
    return out
