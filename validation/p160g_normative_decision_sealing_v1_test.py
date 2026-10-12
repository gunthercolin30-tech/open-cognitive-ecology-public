from copy import deepcopy
from ontology.p160_normative_decision_sealing import *

def base():
 r={"request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF"}
 a={"status":"CONTEXT_READY","proposal_envelope":{"request_id":"R1"},"normative_decision_request":{"semantic_hash":"RF"},"decision_context_fingerprint":{"semantic_hash":"CTX"},"constitutional_snapshot":{"snapshot_semantic_hash":"SNAP","compiled_profile_hash":"PROF"},"expected_effect_envelope":{"semantic_hash":"EFF"},"artifact_hash":"A"}
 b={"bindings":{"runtime_context_fingerprint":"CTX","snapshot_hash":"SNAP","profile_hash":"PROF"},"norm_context":{"applicable_norms":[{"rule_id":"N1"}]},"blockers":[],"artifact_hash":"B"}
 c={"constitutive_filter_result":"PASS","bindings":deepcopy(b["bindings"]),"upstream_p160b_artifact_hash":"B","artifact_hash":"C"}
 d={"conflict_assessment":{"conflict_class":"C0"},"bindings":{"p160c_artifact_hash":"C","p160c_upstream_p160b_artifact_hash":"B","runtime_bindings":deepcopy(b["bindings"])},"artifact_hash":"D"}
 e={"status":"COMPLIANT_RESOLUTION_FOUND","request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","resolution_hash":"E"}
 f={"authority_status":"VALID","request_id":"R1","request_fingerprint":"RF","bindings":{"runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","authority_context_fingerprint":"AUTHCTX"},"scope":{"action_class":["A"]},"purpose":"govern","temporal_bounds":{"valid":True},"resolution_hash":"F"}
 action={"action_class":"A","target":"T","purpose":"govern","parameters":{},"capabilities":["C"],"scope":{"action_class":["A"]},"affected_entities":["X"],"resource_effects":[]}
 return r,a,b,c,d,e,f,action
def run(x=None):
 x=x or base(); return build_normative_decision(*x[:7],action=x[7])
def test_manifest_boundaries():
 m=manifest(); assert all(m[k] is False for k in ("authority_created","authorization_created","authorization_token_created","execution_performed","p161_opened"))
def test_happy_path():
 z=run(); assert z["normative_eligibility"]=="ELIGIBLE_CANDIDATE"; assert z["authority_status"]=="VALID"; assert z["authorization_created"] is False; assert z["usable_by_p161"] is True; assert verify_normative_decision(z)["status"]=="PASS"
def test_determinism(): assert run()["artifact_hash"]==run()["artifact_hash"]
def test_binding_mismatch():
 x=list(base()); x[5]=deepcopy(x[5]); x[5]["compiled_profile_hash"]="OTHER"; z=run(x); assert z["normative_eligibility"]=="UNDETERMINED" and not z["bindings_checked"]
def test_chain_mismatch():
 x=list(base()); x[3]=deepcopy(x[3]); x[3]["upstream_p160b_artifact_hash"]="OTHER"; assert run(x)["normative_eligibility"]=="UNDETERMINED"
def test_constitutive_fail():
 x=list(base()); x[3]=deepcopy(x[3]); x[3]["constitutive_filter_result"]="FAIL"; assert run(x)["normative_eligibility"]=="INELIGIBLE"
def test_constitutive_unknown():
 x=list(base()); x[3]=deepcopy(x[3]); x[3]["constitutive_filter_result"]="UNDETERMINED"; assert run(x)["normative_eligibility"]=="UNDETERMINED"
def test_review_escalation():
 x=list(base()); x[5]=deepcopy(x[5]); x[5]["status"]="REVIEW_REQUIRED"; assert run(x)["normative_eligibility"]=="REVIEW_REQUIRED"
 x=list(base()); x[5]=deepcopy(x[5]); x[5]["status"]="ESCALATION_REQUIRED"; assert run(x)["normative_eligibility"]=="ESCALATION_REQUIRED"
def test_authority_valid_not_authorization():
 z=run(); assert z["authority_status"]=="VALID" and z["authorization_created"] is False and z["decision_seal"]["proves_authorization"] is False
def test_authority_invalid():
 x=list(base()); x[6]=deepcopy(x[6]); x[6]["authority_status"]="INVALID"; assert run(x)["normative_eligibility"]=="INELIGIBLE"
def test_human_unavailable():
 x=list(base()); x[6]=deepcopy(x[6]); x[6]["authority_status"]="HUMAN_RESERVED_UNAVAILABLE"; assert run(x)["normative_eligibility"]=="ESCALATION_REQUIRED"
def test_action_incomplete():
 x=list(base()); x[7]=deepcopy(x[7]); del x[7]["target"]; assert run(x)["normative_eligibility"]=="UNDETERMINED"
def test_missing_provenance():
 x=list(base()); x[4]=deepcopy(x[4]); x[4].pop("artifact_hash"); assert run(x)["normative_eligibility"]=="UNDETERMINED"
def test_tamper():
 z=run(); z["normative_eligibility"]="INELIGIBLE"; assert verify_normative_decision(z)["status"]=="FAIL"
def test_intersection_rules():
 z=run(); assert z["scope_merge_rule"]=="INTERSECTION_NEVER_UNION" and z["purpose_merge_rule"]=="INTERSECTION_NEVER_UNION"
def test_sealed_committed():
 z=run(); assert z["lifecycle"]=="SEALED" and z["transaction_state"]=="COMMITTED"; z["transaction_state"]="PREPARE"; assert verify_normative_decision(z)["status"]=="FAIL"
