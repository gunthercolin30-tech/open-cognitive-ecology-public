from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Mapping
PRIMITIVE="runtime_precondition_evaluator"; VERSION="P162-D-v1"
TYPES={"NORMATIVE","TECHNICAL","SAFETY","RESOURCE","TARGET","TEMPORAL","WORLD_STATE","SECURITY","HUMAN_STATE","COMPOSITION"}
PREDICATES={"AND","OR","NOT","COMPARE","IN_SET","MATCH_HASH","VERSION_EQ","THRESHOLD","TIME_WINDOW","EXISTS"}
RECHECK={"CHECK_ONCE","RECHECK_AT_RESERVATION","RECHECK_AT_EFFECT_BOUNDARY","CONTINUOUSLY_MONITORED"}
EVIDENCE_CLASSES={"OBSERVATION","ATTESTATION","SIGNED_STATE","PROCEDURAL","PREDICTION"}
FAILURE_BEHAVIORS={"BLOCK","RETURN_TO_P160","RETURN_TO_P161","REPLAN_REQUIRED","SAFE_MODE_REQUIRED"}
RECHECK_RANK={"CHECK_ONCE":0,"RECHECK_AT_RESERVATION":1,"RECHECK_AT_EFFECT_BOUNDARY":2,"CONTINUOUSLY_MONITORED":3}
UNKNOWN={None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE"}
def cj(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha(x): return hashlib.sha256(cj(x).encode()).hexdigest()
def known(x):
    try: return x not in UNKNOWN
    except TypeError: return x is not None
def manifest(): return {"primitive":PRIMITIVE,"version":VERSION,"authorization_created":False,"reservation_created":False,"token_consumed":False,"capability_accessed":False,"execution_performed":False,"p162e_opened":False,"functional_only":True,"phenomenology_undetermined":True}
def predicate_registry():
    x={"schema":"oce.p162d.precondition_predicate_registry.v1","version":"1","predicates":sorted(PREDICATES)}
    x["registry_hash"]=sha(x); return x
def build_runtime_context_snapshot(**k):
    req=("runtime_id","host_id","executor_instance_id","environment","time","capability_instance","token_state_version","capability_registry_version","policy_version","security_ref","resource_ref","world_ref","target_ref")
    if any(not known(k.get(a)) for a in req): raise ValueError("INVALID_RUNTIME_CONTEXT_SNAPSHOT")
    x={"schema":"oce.p162d.runtime_context_snapshot.v1",**{a:deepcopy(k[a]) for a in req}}
    x["hash"]=sha(x); return x
def _fail(status,action,failures): return {"status":status,"required_action":action,"failures":sorted(set(failures)),**manifest()}
def _eval(p):
    req=("precondition_id","type","predicate","required_state","observed_state","evidence_class","evidence_refs","freshness","materiality","failure_behavior","recheck_stage")
    if not isinstance(p,Mapping) or any(k not in p for k in req): return None,"MISSING_PRECONDITION_FIELD"
    if p["type"] not in TYPES: return None,"INVALID_PRECONDITION_TYPE"
    if p["predicate"] not in PREDICATES: return None,"PREDICATE_NOT_CANONICAL"
    if p["recheck_stage"] not in RECHECK: return None,"INVALID_RECHECK_STAGE"
    if p["evidence_class"] not in EVIDENCE_CLASSES: return None,"INVALID_EVIDENCE_CLASS"
    if p["failure_behavior"] not in FAILURE_BEHAVIORS: return None,"INVALID_FAILURE_BEHAVIOR"
    minimum=p.get("minimum_recheck_stage")
    if minimum is not None and minimum not in RECHECK: return None,"INVALID_MINIMUM_RECHECK_STAGE"
    if minimum and RECHECK_RANK[p["recheck_stage"]]<RECHECK_RANK[minimum]: return None,"RECHECK_STAGE_DOWNGRADE"
    if p.get("mandatory") is False: return None,"MANDATORY_PRECONDITION_DOWNGRADE"
    if p["evidence_class"] in {"OBSERVATION","ATTESTATION","SIGNED_STATE"}:
        meta=p.get("evidence_metadata")
        if not isinstance(meta,Mapping): return None,"EVIDENCE_METADATA_MISSING"
        if not known(meta.get("source_id")) or meta.get("health_status")!="HEALTHY": return None,"EVIDENCE_SOURCE_UNHEALTHY"
        if meta.get("calibration_required") is True and meta.get("calibration_status")!="VALID": return None,"EVIDENCE_CALIBRATION_INVALID"
        if meta.get("provenance_status")!="VERIFIED": return None,"EVIDENCE_PROVENANCE_INVALID"
    if p["freshness"]!="FRESH": status="STALE"
    elif not known(p["observed_state"]): status="UNKNOWN"
    elif p["evidence_class"]=="PREDICTION" and p.get("prediction_allowed") is not True: status="UNKNOWN"
    else:
        op,a,b=p["predicate"],p["observed_state"],p["required_state"]
        try:
            if op in ("COMPARE","MATCH_HASH","VERSION_EQ"): ok=a==b
            elif op=="EXISTS": ok=known(a)
            elif op=="IN_SET": ok=isinstance(b,(list,tuple,set)) and a in b
            elif op=="THRESHOLD": ok=float(a)>=float(b)
            elif op=="NOT": ok=not bool(a)
            else: ok=bool(a)
        except Exception: ok=False
        status="SATISFIED" if ok else "NOT_SATISFIED"
    r={"precondition_id":p["precondition_id"],"type":p["type"],"required_state":deepcopy(p["required_state"]),"observed_state":deepcopy(p["observed_state"]),"evidence_class":p["evidence_class"],"evidence_refs":deepcopy(p["evidence_refs"]),"status":status,"confidence":p.get("confidence"),"freshness":p["freshness"],"materiality":p["materiality"],"failure_behavior":p["failure_behavior"],"recheck_stage":p["recheck_stage"]}
    r["hash"]=sha(r); return r,None
def evaluate_runtime_preconditions(*,invocation_request,token_verification_receipt,capability_binding_receipt,runtime_snapshot,world_snapshot,target_snapshot,resource_snapshot,security_snapshot,composition_snapshot,preconditions,assessed_at):
    failures=[]
    if token_verification_receipt.get("status")!="TOKEN_USABLE_FOR_GATE" or not known(token_verification_receipt.get("receipt_hash")): failures.append("TOKEN_NOT_USABLE")
    if capability_binding_receipt.get("verification_status")!="BOUND_VERIFIED" or not known(capability_binding_receipt.get("binding_receipt_hash")): failures.append("CAPABILITY_BINDING_NOT_VERIFIED")
    body={k:v for k,v in runtime_snapshot.items() if k!="hash"}
    if runtime_snapshot.get("schema")!="oce.p162d.runtime_context_snapshot.v1" or runtime_snapshot.get("hash")!=sha(body): failures.append("RUNTIME_SNAPSHOT_INVALID")
    if runtime_snapshot.get("executor_instance_id")!=invocation_request.get("executor_instance_id") or runtime_snapshot.get("environment")!=invocation_request.get("environment"): failures.append("RUNTIME_INVOCATION_MISMATCH")
    for name,s in (("WORLD",world_snapshot),("TARGET",target_snapshot),("RESOURCE",resource_snapshot),("SECURITY",security_snapshot),("COMPOSITION",composition_snapshot)):
        if not isinstance(s,Mapping) or not known(s.get("snapshot_hash")): failures.append(name+"_SNAPSHOT_UNKNOWN")
        elif s.get("freshness")!="FRESH": failures.append(name+"_SNAPSHOT_STALE")
    if target_snapshot.get("target_binding")!=invocation_request.get("target_binding") or target_snapshot.get("target_fingerprint")!=invocation_request.get("target_fingerprint"): failures.append("TARGET_STATE_DRIFTED")
    if security_snapshot.get("trust_status")!="TRUSTED" or security_snapshot.get("compromise_flag") is not False: failures.append("SECURITY_CONTEXT_UNTRUSTED")
    if security_snapshot.get("sandbox_status") not in (None,"VALID") or security_snapshot.get("host_integrity") not in (None,"VERIFIED") or security_snapshot.get("credential_broker_status") not in (None,"VALID"): failures.append("SECURITY_CONTEXT_UNTRUSTED")
    if world_snapshot.get("temporal_consistency") not in (None,"CONSISTENT") or target_snapshot.get("temporal_consistency") not in (None,"CONSISTENT") or resource_snapshot.get("temporal_consistency") not in (None,"CONSISTENT"): failures.append("TEMPORAL_CONTEXT_CONFLICT")
    if any(s.get("clock_skew_status") not in (None,"WITHIN_BOUND") for s in (world_snapshot,target_snapshot,resource_snapshot,security_snapshot,composition_snapshot)): failures.append("CLOCK_SKEW_UNBOUNDED")
    if composition_snapshot.get("status")!="SATISFIED": failures.append("COMPOSITION_PRECONDITION_FAILED")
    if composition_snapshot.get("mutual_exclusion_conflict") is True or composition_snapshot.get("rolling_window_status") not in (None,"SATISFIED") or composition_snapshot.get("shared_budget_status") not in (None,"SATISFIED"): failures.append("COMPOSITION_PRECONDITION_FAILED")
    if resource_snapshot.get("status") not in ("AVAILABLE","SUFFICIENT"): failures.append("RESOURCE_STATE_INSUFFICIENT")
    if resource_snapshot.get("reserved") is True: failures.append("RESOURCE_SNAPSHOT_MUST_NOT_RESERVE")
    if world_snapshot.get("evidence_class")=="PREDICTION" and world_snapshot.get("prediction_allowed") is not True: failures.append("WORLD_STATE_UNDETERMINED")
    if invocation_request.get("emergency_required") is True and world_snapshot.get("emergency_status")!="ACTIVE": failures.append("EMERGENCY_ENDED")
    if invocation_request.get("rollback_required") is True and world_snapshot.get("rollback_status")!="AVAILABLE": failures.append("ROLLBACK_IMPOSSIBLE")
    if not isinstance(preconditions,list) or not preconditions: failures.append("REQUIRED_PRECONDITIONS_MISSING")
    ids={p.get("precondition_id") for p in preconditions if isinstance(p,Mapping)}
    for e in invocation_request.get("expected_preconditions",[]):
        eid=e.get("precondition_id") if isinstance(e,Mapping) else e
        if eid not in ids: failures.append("MANDATORY_UPSTREAM_PRECONDITION_DROPPED")
    results=[]
    for p in preconditions if isinstance(preconditions,list) else []:
        r,e=_eval(p)
        if e: failures.append(e); continue
        results.append(r)
        if r["status"]!="SATISFIED": failures.append("PRECONDITION_"+r["status"])
        if r["type"]=="SAFETY" and r["status"]!="SATISFIED": failures.append("SAFETY_INTERLOCK_FAILED")
    if failures:
        if "TOKEN_NOT_USABLE" in failures: return _fail("PRECONDITIONS_UNDETERMINED","RETURN_TO_P161",failures)
        if "CAPABILITY_BINDING_NOT_VERIFIED" in failures: return _fail("PRECONDITIONS_UNDETERMINED","REPLAN_REQUIRED",failures)
        if "TEMPORAL_CONTEXT_CONFLICT" in failures or "CLOCK_SKEW_UNBOUNDED" in failures: return _fail("CONTEXT_CONFLICTING","REPLAN_REQUIRED",failures)
        if "WORLD_STATE_UNDETERMINED" in failures: return _fail("WORLD_STATE_UNDETERMINED","REPLAN_REQUIRED",failures)
        if "RESOURCE_STATE_INSUFFICIENT" in failures: return _fail("RESOURCE_STATE_INSUFFICIENT","REPLAN_REQUIRED",failures)
        if "TARGET_STATE_DRIFTED" in failures: return _fail("TARGET_STATE_DRIFTED","REPLAN_REQUIRED",failures)
        if "SAFETY_INTERLOCK_FAILED" in failures: return _fail("SAFETY_INTERLOCK_FAILED","SAFE_MODE_REQUIRED",failures)
        if "SECURITY_CONTEXT_UNTRUSTED" in failures: return _fail("PRECONDITIONS_UNDETERMINED","SAFE_MODE_REQUIRED",failures)
        if "EMERGENCY_ENDED" in failures: return _fail("PRECONDITIONS_NOT_SATISFIED","RETURN_TO_P160",failures)
        if "ROLLBACK_IMPOSSIBLE" in failures: return _fail("PRECONDITIONS_NOT_SATISFIED","REPLAN_REQUIRED",failures)
        if any("STALE" in f for f in failures): return _fail("CONTEXT_STALE","REPLAN_REQUIRED",failures)
        return _fail("PRECONDITIONS_UNDETERMINED","REPLAN_REQUIRED",failures)
    a={"schema":"oce.p162d.runtime_precondition_assessment.v1","assessment_id":"PA-"+sha([invocation_request.get("invocation_request_id"),runtime_snapshot["hash"],assessed_at])[:24],"invocation_request_id":invocation_request.get("invocation_request_id"),"token_verification_receipt_hash":token_verification_receipt["receipt_hash"],"capability_binding_receipt_hash":capability_binding_receipt["binding_receipt_hash"],"runtime_snapshot_hash":runtime_snapshot["hash"],"world_snapshot_hash":world_snapshot["snapshot_hash"],"target_snapshot_hash":target_snapshot["snapshot_hash"],"resource_snapshot_hash":resource_snapshot["snapshot_hash"],"precondition_results":results,"uncertainty_results":[{"precondition_id":r["precondition_id"],"confidence":r["confidence"],"status":"BOUNDED" if r["confidence"] is not None else "UNQUANTIFIED"} for r in results],"temporal_consistency":"CONSISTENT","context_freshness":"FRESH","overall_status":"PRECONDITIONS_SATISFIED","required_action":"PROCEED_TO_P162_E","assessed_at":assessed_at}
    a["assessment_hash"]=sha(a)
    return {"status":"PRECONDITIONS_SATISFIED","assessment":a,**manifest()}
