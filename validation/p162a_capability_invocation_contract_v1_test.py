from copy import deepcopy
from ontology.capability_invocation_request_builder import *
def token():return {"body":{"token_id":"AT1","action_digest":"act","capabilities":["cap.echo"],"target":{"id":"T1"},"purpose":"P1","scope":{"preconditions":["pre"],"postconditions":["post"]}},"token_hash":"TH1"}
def ctx():return build_runtime_invocation_context(runtime_id="R1",executor_instance_id="EI1",host_id="H1",environment="TEST",time="2026-10-01T10:00:00Z",capability_registry_version="CR1",authorization_registry_version="AR1",policy_version="PV1",world_state_fingerprint="W1",resource_state_fingerprint="RS1",security_state_fingerprint="SS1")
def kw():return dict(authorization_token=token(),requester="REQ",executor_id="EX",executor_instance_id="EI1",capability_id="cap.echo",capability_version="1",capability_implementation_id="impl.echo.v1",capability_manifest_hash="MH",operation_id="echo",action_digest="act",target_binding={"id":"T1"},target_fingerprint="TF",purpose_id="P1",environment="TEST",arguments={"x":1},requested_resources={"cpu":1},budget={"cpu":1},runtime_context=ctx(),world_state_ref="WS",world_state_fingerprint="W1",requested_at="2026-10-01T10:00:00Z",invocation_nonce="N1",material_defaults_resolved=True)
def test_positive_deterministic_nonexecuting():
 a=build_invocation_request(**kw());b=build_invocation_request(**kw());assert a["status"]=="REQUESTED" and a["request"]==b["request"];assert not a["authorization_verified"] and not a["capability_accessed"] and not a["execution_performed"];assert a["request"]["expected_preconditions"]==["pre"] and a["request"]["expected_postconditions"]==["post"]
def test_material_bindings_and_mutation_identity():
 base=build_invocation_request(**kw())["request"]
 for key,val in [("executor_instance_id","X"),("capability_version","2"),("purpose_id","P2"),("environment","PRODUCTION"),("target_fingerprint","X")]:
  k=kw();k[key]=val;r=build_invocation_request(**k);assert r["status"]!="REQUESTED" or r["request"]["invocation_request_id"]!=base["invocation_request_id"]
 k=kw();k["arguments"]={"x":2};r=build_invocation_request(**k)["request"];assert r["arguments_digest"]!=base["arguments_digest"] and r["invocation_request_id"]!=base["invocation_request_id"]
 m=deepcopy(base);m["arguments"]["x"]=9;assert assert_requested_immutable(base,m)["status"]=="FAIL"
def test_resource_token_conditions():
 k=kw();k["budget"]={};assert build_invocation_request(**k)["status"]=="MISSING_BINDING"
 k=kw();k["authorization_token"]={"body":{}};assert build_invocation_request(**k)["status"]=="TOKEN_REFERENCE_MISSING"
 k=kw();k["expected_preconditions"]=[];assert build_invocation_request(**k)["reason"]=="P161_PRECONDITION_DROPPED"
def test_child_composition_and_no_inheritance():
 p=build_invocation_request(**kw())["request"];k=kw();k["parent_invocation"]=p;assert build_invocation_request(**k)["reason"]=="CHILD_COMPOSITION_ENVELOPE_REQUIRED"
 e=build_composition_envelope(parent_invocation_id=p["invocation_request_id"],allowed_child_capabilities=["cap.echo"],allowed_child_operations=["echo"],allowed_child_targets=[{"id":"T1"}],allowed_child_purposes=["P1"],resource_budget={"cpu":1},depth=1,fanout=1);k["composition_envelope"]=e;assert build_invocation_request(**k)["status"]=="REQUESTED"
def test_pure_world_model_or_technical_power_never_authorize():
 k=kw();k["effect_class_claim"]="PURE";k["requested_resources"]={"cpu":999};r=build_invocation_request(**k);assert not r["effect_binding"]["pure_claim_is_gate_bypass"] and not r["authorization_verified"] and not r["execution_performed"]
def test_epistemic_boundary():
 m=manifest();assert m["functional_only"] and m["phenomenology_undetermined"] and not m["authorization_created"]
