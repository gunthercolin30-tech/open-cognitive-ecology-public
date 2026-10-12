from copy import deepcopy
from ontology.p160_normative_decision_sealing import build_normative_decision
from ontology.p161_normative_decision_verification import *

def fixture():
 r={"request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","decision_max_age":3600}
 a={"status":"CONTEXT_READY","proposal_envelope":{"request_id":"R1"},"normative_decision_request":{"semantic_hash":"RF"},"decision_context_fingerprint":{"semantic_hash":"CTX"},"constitutional_snapshot":{"snapshot_semantic_hash":"SNAP","compiled_profile_hash":"PROF"},"expected_effect_envelope":{"semantic_hash":"EFF"},"artifact_hash":"A"}
 b={"bindings":{"runtime_context_fingerprint":"CTX","snapshot_hash":"SNAP","profile_hash":"PROF"},"norm_context":{"applicable_norms":[{"rule_id":"N1"}]},"blockers":[],"artifact_hash":"B"}
 c={"constitutive_filter_result":"PASS","bindings":deepcopy(b["bindings"]),"upstream_p160b_artifact_hash":"B","artifact_hash":"C"}
 d={"conflict_assessment":{"conflict_class":"C0"},"bindings":{"p160c_artifact_hash":"C","p160c_upstream_p160b_artifact_hash":"B","runtime_bindings":deepcopy(b["bindings"])},"artifact_hash":"D"}
 e={"status":"COMPLIANT_RESOLUTION_FOUND","request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","resolution_hash":"E"}
 f={"authority_status":"VALID","request_id":"R1","request_fingerprint":"RF","bindings":{"runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","authority_context_fingerprint":"AUTHCTX"},"scope":{"action_class":["A"]},"purpose":"govern","temporal_bounds":{"valid":True},"resolution_hash":"F"}
 action={"action_class":"A","target":"T","purpose":"govern","parameters":{},"capabilities":["C"],"scope":{"action_class":["A"]},"affected_entities":["X"],"resource_effects":[]}
 nd=build_normative_decision(r,a,b,c,d,e,f,action=action,normative_preconditions=[],normative_postconditions=[])
 req={"authorization_request_id":"AR1","normative_decision_id":nd["decision_id"],"normative_decision_hash":nd["artifact_hash"],"action_digest":nd["action_digest"]["semantic_hash"],"requested_scope":{"action_class":["A"]},"constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","runtime_context_fingerprint":"CTX","authority_context_ref":"AUTHCTX"}
 state=deepcopy(nd["decision_freshness_policy"]["required_state_hashes"]); persisted={"status":"COMMITTED","artifact_hash":nd["artifact_hash"]}; return nd,req,state,persisted

def run():
 nd,r,s,p=fixture();return verify_for_authorization(r,nd,current_state=s,persisted_state=p)
def test_happy():assert run()["status"]=="VERIFIED"
def test_determinism():assert run()["verification_hash"]==run()["verification_hash"]
def test_non_sovereign():
 x=run();assert x["authorization_created"] is False and x["execution_performed"] is False and x["p162_opened"] is False
def test_tamper():
 nd,r,s,p=fixture();nd["normative_eligibility"]="INELIGIBLE";assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="REJECTED"
def test_hash_mismatch():
 nd,r,s,p=fixture();r["normative_decision_hash"]="0"*64;assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="REJECTED"
def test_action_drift():
 nd,r,s,p=fixture();r["action_digest"]="1"*64;assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="REJECTED"
def test_profile_drift():
 nd,r,s,p=fixture();s["compiled_profile_hash"]="OTHER";assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="RETURN_TO_P160"
def test_authority_drift():
 nd,r,s,p=fixture();s["authority_context_fingerprint"]="OTHER";assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="RETURN_TO_P160"
def test_missing_state():
 nd,r,s,p=fixture();s.pop("expected_effect_envelope_hash");assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="UNRESOLVED"
def test_superseded():
 nd,r,s,p=fixture();p["status"]="SUPERSEDED";assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="RETURN_TO_P160"
def test_missing_persistence():
 nd,r,s,p=fixture();assert verify_for_authorization(r,nd,current_state=s,persisted_state=None)["status"]=="UNRESOLVED"
def test_scope_widening():
 nd,r,s,p=fixture();r["requested_scope"]={"action_class":["A","B"]};assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]=="REJECTED"
def test_unknown_max_age():
 nd,r,s,p=fixture();nd["decision_freshness_policy"]["max_age"]="UNKNOWN";assert verify_for_authorization(r,nd,current_state=s,persisted_state=p)["status"]!="VERIFIED"
