"""P160-G — NormativeDecision & Decision Sealing. Functional-only."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

PRIMITIVE="p160_normative_decision_sealing"
VERSION="P160-G-v1"
SCHEMA="oce.p160g.normative_decision.v1"
ELIGIBILITY=("ELIGIBLE_CANDIDATE","INELIGIBLE","UNDETERMINED","REVIEW_REQUIRED","ESCALATION_REQUIRED","NO_LEGITIMATE_ACTION_AVAILABLE","SAFE_MODE_REQUIRED","CONSTITUTIONAL_DORMANCY_REQUIRED","FORK_REQUIRED","REFOUNDING_REQUIRED")
LIFECYCLE=("DRAFT","ASSEMBLED","VALIDATED","SEALED","STALE","SUPERSEDED","INVALIDATED")
BOUNDARIES={"authority_created":False,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}
FUNCTIONAL_ONLY={"functional_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}

def _canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_sha256(v): return sha256(_canonical(v).encode()).hexdigest()
def _map(v): return v if isinstance(v,Mapping) else {}
def _path(v,*paths):
    for path in paths:
        cur=v; ok=True
        for key in path:
            if not isinstance(cur,Mapping) or key not in cur: ok=False; break
            cur=cur[key]
        if ok:return cur
    return None

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"scope":"P160-G_ONLY",
      "doctrines":["NORMATIVE_ELIGIBILITY != AUTHORIZATION != EXECUTION","SEALED != AUTHORIZED","AUTHORITY_VALID != AUTHORIZATION","DECISION_VALIDITY_IS_INTERSECTION_NOT_UNION","SEALED_DECISION_IMMUTABLE"],
      "eligibility_domain":list(ELIGIBILITY),"lifecycle_domain":list(LIFECYCLE),
      "does_not_call":["P095.authorize","P161","execute","call_tool","issue_token"],**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}

def _canonical_bindings(req,a,b,f):
    return {
      "request_id":req.get("request_id") or _path(a,("proposal_envelope","request_id")),
      "request_fingerprint":req.get("request_fingerprint") or _path(a,("normative_decision_request","semantic_hash")),
      "runtime_context_fingerprint":req.get("runtime_context_fingerprint") or _path(a,("decision_context_fingerprint","semantic_hash")) or _path(b,("bindings","runtime_context_fingerprint")) or _path(f,("bindings","runtime_context_fingerprint")),
      "constitutional_snapshot_hash":req.get("constitutional_snapshot_hash") or _path(a,("constitutional_snapshot","snapshot_semantic_hash")) or _path(b,("bindings","snapshot_hash")) or _path(f,("bindings","constitutional_snapshot_hash")),
      "compiled_profile_hash":req.get("compiled_profile_hash") or _path(b,("bindings","profile_hash")) or _path(f,("bindings","compiled_profile_hash"))}

def _evidence(a,b,c,d,e,f):
    return {
      "A":{"request_id":_path(a,("proposal_envelope","request_id")),"request_fingerprint":_path(a,("normative_decision_request","semantic_hash")),"runtime_context_fingerprint":_path(a,("decision_context_fingerprint","semantic_hash")),"constitutional_snapshot_hash":_path(a,("constitutional_snapshot","snapshot_semantic_hash")),"compiled_profile_hash":_path(a,("constitutional_snapshot","compiled_profile_hash"))},
      "B":{"runtime_context_fingerprint":_path(b,("bindings","runtime_context_fingerprint")),"constitutional_snapshot_hash":_path(b,("bindings","snapshot_hash")),"compiled_profile_hash":_path(b,("bindings","profile_hash"))},
      "C":{"runtime_context_fingerprint":_path(c,("bindings","runtime_context_fingerprint")),"constitutional_snapshot_hash":_path(c,("bindings","snapshot_hash")),"compiled_profile_hash":_path(c,("bindings","profile_hash")),"upstream_b_hash":c.get("upstream_p160b_artifact_hash")},
      "D":{"runtime_context_fingerprint":_path(d,("bindings","runtime_bindings","runtime_context_fingerprint")),"constitutional_snapshot_hash":_path(d,("bindings","runtime_bindings","snapshot_hash")),"compiled_profile_hash":_path(d,("bindings","runtime_bindings","profile_hash")),"upstream_c_hash":_path(d,("bindings","p160c_artifact_hash")),"upstream_b_hash":_path(d,("bindings","p160c_upstream_p160b_artifact_hash"))},
      "E":{"request_id":e.get("request_id"),"request_fingerprint":e.get("request_fingerprint"),"runtime_context_fingerprint":e.get("runtime_context_fingerprint"),"constitutional_snapshot_hash":e.get("constitutional_snapshot_hash"),"compiled_profile_hash":e.get("compiled_profile_hash")},
      "F":{"request_id":f.get("request_id"),"request_fingerprint":f.get("request_fingerprint"),"runtime_context_fingerprint":_path(f,("bindings","runtime_context_fingerprint")) or f.get("runtime_context_fingerprint"),"constitutional_snapshot_hash":_path(f,("bindings","constitutional_snapshot_hash")) or f.get("constitutional_snapshot_hash"),"compiled_profile_hash":_path(f,("bindings","compiled_profile_hash")) or f.get("compiled_profile_hash")}}

def _check_bindings(canon,ev,b,c,d):
    errors=[]
    for k,v in canon.items():
        if v in (None,"","UNKNOWN"): errors.append("CANONICAL_BINDING_UNRESOLVED:"+k)
    for comp,vals in ev.items():
        for k,v in vals.items():
            if k.startswith("upstream_") or v in (None,"","UNKNOWN"): continue
            if k in canon and v!=canon[k]: errors.append("BINDING_MISMATCH:%s:%s"%(comp,k))
    if b.get("artifact_hash") and ev["C"].get("upstream_b_hash")!=b.get("artifact_hash"): errors.append("UPSTREAM_HASH_MISMATCH:C:B")
    if c.get("artifact_hash") and ev["D"].get("upstream_c_hash")!=c.get("artifact_hash"): errors.append("UPSTREAM_HASH_MISMATCH:D:C")
    if b.get("artifact_hash") and ev["D"].get("upstream_b_hash")!=b.get("artifact_hash"): errors.append("UPSTREAM_HASH_MISMATCH:D:B")
    return not errors,errors

def _eligibility(a,b,c,d,e,f,binding_ok):
    if not binding_ok:return "UNDETERMINED",["CROSS_BINDING_NOT_PROVEN"]
    if a.get("status") not in (None,"CONTEXT_READY"):return "UNDETERMINED",["RUNTIME_CONTEXT_NOT_READY"]
    if b.get("blockers"):return "UNDETERMINED",["NORM_RESOLUTION_BLOCKED"]
    cs=c.get("constitutive_filter_result") or c.get("status")
    if cs in ("FAIL","CONFLICT"):return "INELIGIBLE",["CONSTITUTIVE_"+str(cs)]
    if cs not in (None,"PASS","CONSTITUTIVE_OK"):return "UNDETERMINED",["CONSTITUTIVE_UNDETERMINED"]
    es=e.get("status") or e.get("resolution_status") or e.get("ccad_status")
    em={"REVIEW_REQUIRED":"REVIEW_REQUIRED","ARBITRATION_PENDING":"REVIEW_REQUIRED","ESCALATION_REQUIRED":"ESCALATION_REQUIRED","CONFLICT_UNRESOLVED":"UNDETERMINED","NO_LEGITIMATE_ACTION_AVAILABLE":"NO_LEGITIMATE_ACTION_AVAILABLE","SAFE_MODE_REQUIRED":"SAFE_MODE_REQUIRED","FORK_REQUIRED":"FORK_REQUIRED","REFOUNDING_REQUIRED":"REFOUNDING_REQUIRED"}
    if es in em:return em[es],["CCAD_"+str(es)]
    auth=f.get("authority_status")
    if auth!="VALID":
        if auth in ("UNAVAILABLE","HUMAN_RESERVED_UNAVAILABLE"):return "ESCALATION_REQUIRED",["AUTHORITY_"+str(auth)]
        if auth in ("UNDETERMINED",None):return "UNDETERMINED",["AUTHORITY_UNDETERMINED"]
        return "INELIGIBLE",["AUTHORITY_"+str(auth)]
    dc=_path(d,("conflict_assessment","conflict_class")) or d.get("conflict_class")
    if dc in ("C5","C6") and es not in ("TRAGIC_CHOICE_CONFIRMED","NO_LEGITIMATE_ACTION_AVAILABLE","FORK_REQUIRED","REFOUNDING_REQUIRED","SAFE_MODE_REQUIRED"):
        return "UNDETERMINED",["HARD_CONFLICT_NOT_RESOLVED"]
    return "ELIGIBLE_CANDIDATE",[]

def _action_digest(action):
    fields=("action_class","target","purpose","parameters","capabilities","scope","affected_entities","resource_effects")
    p={k:deepcopy(action.get(k,"UNKNOWN")) for k in fields}
    p["unknown_fields"]=sorted(k for k in fields if p[k] in (None,"","UNKNOWN"))
    p["semantic_hash"]=canonical_sha256({k:p[k] for k in fields})
    return p

def build_normative_decision(request,runtime_context_a,norm_resolution_b,constitutive_assessment_c,conflict_assessment_d,ccad_resolution_e,authority_resolution_f,*,action,normative_preconditions=None,normative_postconditions=None,review_requirements=None,rollback_plan=None,uncertainties=None):
    req=deepcopy(dict(_map(request))); a,b,c,d,e,f=[deepcopy(dict(_map(x))) for x in (runtime_context_a,norm_resolution_b,constitutive_assessment_c,conflict_assessment_d,ccad_resolution_e,authority_resolution_f)]
    act=deepcopy(dict(_map(action)))
    cb=_canonical_bindings(req,a,b,f); ev=_evidence(a,b,c,d,e,f); bok,berr=_check_bindings(cb,ev,b,c,d)
    elig,reasons=_eligibility(a,b,c,d,e,f,bok)
    ad=_action_digest(act)
    if ad["unknown_fields"] and elig=="ELIGIBLE_CANDIDATE": elig="UNDETERMINED"; reasons.append("ACTION_DIGEST_INCOMPLETE")
    prov={"A_artifact_hash":a.get("artifact_hash"),"B_artifact_hash":b.get("artifact_hash"),"C_artifact_hash":c.get("artifact_hash"),"D_artifact_hash":d.get("artifact_hash"),"E_resolution_hash":e.get("resolution_hash") or e.get("artifact_hash"),"F_resolution_hash":f.get("resolution_hash") or f.get("artifact_hash")}
    missing=sorted(k for k,v in prov.items() if v in (None,"","UNKNOWN"))
    if missing and elig=="ELIGIBLE_CANDIDATE": elig="UNDETERMINED"; reasons.append("UPSTREAM_PROVENANCE_INCOMPLETE")
    eff=deepcopy(a.get("expected_effect_envelope",{})); effh=eff.get("semantic_hash") if isinstance(eff,Mapping) else None
    authctx=f.get("authority_context_fingerprint") or _path(f,("bindings","authority_context_fingerprint"))
    fresh={"max_age":req.get("decision_max_age","UNKNOWN"),"required_state_hashes":{"constitutional_snapshot_hash":cb["constitutional_snapshot_hash"],"compiled_profile_hash":cb["compiled_profile_hash"],"runtime_context_fingerprint":cb["runtime_context_fingerprint"],"authority_context_fingerprint":authctx,"expected_effect_envelope_hash":effh},"revalidate_on":["profile","snapshot","authority","target","material_facts","emergency","related_actions","effect_envelope"],"materiality_aware":True}
    dcf=canonical_sha256({"request":cb["request_fingerprint"],"context":cb["runtime_context_fingerprint"],"snapshot":cb["constitutional_snapshot_hash"],"profile":cb["compiled_profile_hash"],"authority":authctx,"relation_state":req.get("relation_state_hash","UNKNOWN"),"emergency":deepcopy(a.get("emergency_context","UNKNOWN")),"effect_envelope":effh})
    payload={"schema":SCHEMA,"version":VERSION,"request_id":cb["request_id"],"request_fingerprint":cb["request_fingerprint"],"decision_context_fingerprint":dcf,"bindings":cb,"binding_evidence":ev,"bindings_checked":bok,"binding_errors":berr,"action_digest":ad,
      "normative_basis":{"applicable_norms":deepcopy(_path(b,("norm_context","applicable_norms")) or []),"constitutive_guards_ref":c.get("artifact_hash"),"conflict_assessment_ref":d.get("artifact_hash"),"ccad_resolution_ref":prov["E_resolution_hash"],"authority_resolution_ref":prov["F_resolution_hash"]},
      "normative_eligibility":elig,"eligibility_reasons":reasons,"authority_status":f.get("authority_status"),"authority_scope":deepcopy(f.get("scope",{})),"authority_purpose":deepcopy(f.get("purpose")),"authority_temporal_bounds":deepcopy(f.get("temporal_bounds",{})),
      "normative_preconditions":deepcopy(list(normative_preconditions or [])),"normative_postconditions":deepcopy(list(normative_postconditions or [])),"review_requirements":deepcopy(list(review_requirements or [])),"rollback_plan":deepcopy(dict(rollback_plan or {})),"uncertainties":deepcopy(list(uncertainties or [])),
      "expected_effect_envelope_hash":effh,"decision_freshness_policy":fresh,"decision_provenance":prov,"upstream_provenance_complete":not missing,
      "decision_validity_rule":"INTERSECTION_NORMATIVE_CCAD_AUTHORITY_CONTEXT_FRESHNESS","scope_merge_rule":"INTERSECTION_NEVER_UNION","purpose_merge_rule":"INTERSECTION_NEVER_UNION",
      "lifecycle":"SEALED","transaction_state":"COMMITTED","usable_by_p161":elig=="ELIGIBLE_CANDIDATE" and bok and not missing,
      "decision_trace":["components_validated","bindings_checked","eligibility_derived","conditions_merged","invalidation_triggers_derived","payload_built","hash_computed","sealed","committed"],**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
    sem=canonical_sha256(payload)
    result=deepcopy(payload); result["decision_id"]="ND-"+sem[:24]; result["semantic_hash"]=sem
    result["decision_seal"]={"seal_type":"SHA256_CANONICAL_PAYLOAD","semantic_hash":sem,"proves":["integrity","provenance_binding"],"proves_authorization":False,"proves_execution_right":False}
    result["artifact_hash"]=canonical_sha256(result)
    return result

def verify_normative_decision(value):
    if not isinstance(value,Mapping):return {"status":"FAIL","reason":"NOT_MAPPING",**deepcopy(BOUNDARIES)}
    x=deepcopy(dict(value)); art=x.pop("artifact_hash",None); artok=art==canonical_sha256(x)
    sem=x.get("semantic_hash"); seal=_map(x.get("decision_seal")); semok=sem==seal.get("semantic_hash")
    bok=all(x.get(k) is False for k in BOUNDARIES); life=x.get("lifecycle")=="SEALED" and x.get("transaction_state")=="COMMITTED"
    return {"status":"PASS" if artok and semok and bok and life else "FAIL","artifact_hash_valid":artok,"seal_hash_bound":semok,"boundaries_preserved":bok,"sealed_and_committed":life,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
