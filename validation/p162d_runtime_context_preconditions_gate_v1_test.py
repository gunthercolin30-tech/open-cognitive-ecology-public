from copy import deepcopy
from ontology.runtime_precondition_evaluator import build_runtime_context_snapshot,evaluate_runtime_preconditions,predicate_registry
def fx():
    inv={"invocation_request_id":"IR1","executor_instance_id":"EI1","environment":"TEST","target_binding":{"id":"T1"},"target_fingerprint":"TF","expected_preconditions":["P1"]}
    rt=build_runtime_context_snapshot(runtime_id="R1",host_id="H1",executor_instance_id="EI1",environment="TEST",time="2026-10-01T12:00:00Z",capability_instance={"id":"cap.echo","version":"1"},token_state_version="TS1",capability_registry_version="CR1",policy_version="PV1",security_ref="SEC",resource_ref="RES",world_ref="WORLD",target_ref="TARGET")
    pre=[{"precondition_id":"P1","type":"TECHNICAL","predicate":"COMPARE","required_state":"READY","observed_state":"READY","evidence_class":"OBSERVATION","evidence_refs":["E1"],"freshness":"FRESH","materiality":"CRITICAL","failure_behavior":"BLOCK","recheck_stage":"RECHECK_AT_RESERVATION","confidence":1.0,"mandatory":True,"minimum_recheck_stage":"RECHECK_AT_RESERVATION","evidence_metadata":{"source_id":"S1","health_status":"HEALTHY","calibration_required":True,"calibration_status":"VALID","provenance_status":"VERIFIED"}}]
    def s(h,**k): return {"snapshot_hash":h,"freshness":"FRESH",**k}
    return dict(invocation_request=inv,token_verification_receipt={"status":"TOKEN_USABLE_FOR_GATE","receipt_hash":"CRH"},capability_binding_receipt={"verification_status":"BOUND_VERIFIED","binding_receipt_hash":"CBH"},runtime_snapshot=rt,world_snapshot=s("WH",evidence_class="OBSERVATION"),target_snapshot=s("TH",target_binding={"id":"T1"},target_fingerprint="TF"),resource_snapshot=s("RH",status="AVAILABLE",reserved=False),security_snapshot=s("SH",trust_status="TRUSTED",compromise_flag=False),composition_snapshot=s("CH",status="SATISFIED"),preconditions=pre,assessed_at="2026-10-01T12:00:00Z")
def test_positive_deterministic_noncausal():
    x=fx();before=deepcopy(x);a=evaluate_runtime_preconditions(**x);b=evaluate_runtime_preconditions(**x)
    assert a["status"]=="PRECONDITIONS_SATISFIED" and a["assessment"]["assessment_hash"]==b["assessment"]["assessment_hash"] and x==before
    for k in ("authorization_created","reservation_created","token_consumed","capability_accessed","execution_performed","p162e_opened"): assert a[k] is False
def test_unknown_and_stale_fail_closed():
    x=fx();x["preconditions"][0]["observed_state"]="UNKNOWN";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
    x=fx();x["world_snapshot"]["freshness"]="STALE";assert evaluate_runtime_preconditions(**x)["status"]=="CONTEXT_STALE"
def test_prediction_does_not_launder_observation():
    x=fx();x["preconditions"][0]["evidence_class"]="PREDICTION";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_target_drift_detected():
    x=fx();x["target_snapshot"]["target_fingerprint"]="DRIFT";assert evaluate_runtime_preconditions(**x)["status"]=="TARGET_STATE_DRIFTED"
def test_safety_interlock_blocks_token():
    x=fx();x["preconditions"][0].update(type="SAFETY",observed_state="OPEN",required_state="CLOSED");assert evaluate_runtime_preconditions(**x)["status"]=="SAFETY_INTERLOCK_FAILED"
def test_resource_available_is_not_reservation():
    x=fx();r=evaluate_runtime_preconditions(**x);assert r["status"]=="PRECONDITIONS_SATISFIED" and r["reservation_created"] is False
    x=fx();x["resource_snapshot"]["reserved"]=True;assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_security_unknown_not_trusted():
    x=fx();x["security_snapshot"]["trust_status"]="UNKNOWN";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_composition_failure_blocks():
    x=fx();x["composition_snapshot"]["status"]="UNKNOWN";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_mandatory_upstream_precondition_cannot_drop():
    x=fx();x["preconditions"]=[];assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_predicate_injection_and_recheck_invalid_rejected():
    x=fx();x["preconditions"][0]["predicate"]="PYTHON";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
    x=fx();x["preconditions"][0]["recheck_stage"]="SOMETIME";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
def test_registry_is_bounded_and_versioned():
    r=predicate_registry();assert r["version"]=="1" and "PYTHON" not in r["predicates"] and len(r["predicates"])==10
def test_token_and_capability_receipts_required():
    x=fx();x["token_verification_receipt"]["status"]="TOKEN_NOT_USABLE_FOR_GATE";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
    x=fx();x["capability_binding_receipt"]["verification_status"]="UNKNOWN";assert evaluate_runtime_preconditions(**x)["status"]!="PRECONDITIONS_SATISFIED"
