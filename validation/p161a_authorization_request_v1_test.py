from copy import deepcopy
from ontology.p160_normative_decision_sealing import build_normative_decision
from ontology.p161_authorization_request import *

def decision():
 r={"request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF"}
 a={"status":"CONTEXT_READY","proposal_envelope":{"request_id":"R1"},"normative_decision_request":{"semantic_hash":"RF"},"decision_context_fingerprint":{"semantic_hash":"CTX"},"constitutional_snapshot":{"snapshot_semantic_hash":"SNAP","compiled_profile_hash":"PROF"},"expected_effect_envelope":{"semantic_hash":"EFF"},"artifact_hash":"A"}
 b={"bindings":{"runtime_context_fingerprint":"CTX","snapshot_hash":"SNAP","profile_hash":"PROF"},"norm_context":{"applicable_norms":[{"rule_id":"N1"}]},"blockers":[],"artifact_hash":"B"}
 c={"constitutive_filter_result":"PASS","bindings":deepcopy(b["bindings"]),"upstream_p160b_artifact_hash":"B","artifact_hash":"C"}
 d={"conflict_assessment":{"conflict_class":"C0"},"bindings":{"p160c_artifact_hash":"C","p160c_upstream_p160b_artifact_hash":"B","runtime_bindings":deepcopy(b["bindings"])},"artifact_hash":"D"}
 e={"status":"COMPLIANT_RESOLUTION_FOUND","request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","resolution_hash":"E"}
 f={"authority_status":"VALID","request_id":"R1","request_fingerprint":"RF","bindings":{"runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","authority_context_fingerprint":"AUTHCTX"},"scope":{"action_class":["A"]},"purpose":"govern","temporal_bounds":{"valid":True},"resolution_hash":"F"}
 action={"action_class":"A","target":"T","purpose":"govern","parameters":{},"capabilities":["C1","C2"],"scope":{"action_class":["A"],"zones":["Z1","Z2"]},"affected_entities":["X"],"resource_effects":[]}
 return build_normative_decision(r,a,b,c,d,e,f,action=action)

def req(**kw):
 p=dict(normative_decision=decision(),requester="human:R",proposed_executor="agent:E",target="T",purpose="govern",requested_scope={"action_class":["A"],"zones":["Z1"]},requested_capabilities=["C1"],requested_validity={"not_before":"2026-10-01T08:00:00Z","expires_at":"2026-10-01T09:00:00Z"},requested_use_policy="SINGLE_USE",approval_evidence_refs=[],created_at="2026-10-01T07:59:00Z")
 p.update(kw); return build_authorization_request(**p)

def test_manifest_non_sovereign():
 m=manifest(); assert all(m[k] is False for k in BOUNDARIES)
def test_valid_narrow_request():
 d=decision(); r=req(normative_decision=d); assert r["request_state"]=="REQUESTED"; assert verify_authorization_request(r,d)["status"]=="PASS"
def test_determinism(): assert req()["request_hash"]==req()["request_hash"]
def test_scope_widening_rejected(): assert "REQUESTED_SCOPE_WIDENS_P160" in req(requested_scope={"action_class":["A","B"]})["validation_errors"]
def test_capability_widening_rejected(): assert "REQUESTED_CAPABILITIES_WIDEN_P160" in req(requested_capabilities=["C1","C3"])["validation_errors"]
def test_target_drift_rejected(): assert "TARGET_MUST_MATCH_P160_ACTION" in req(target="OTHER")["validation_errors"]
def test_purpose_drift_rejected(): assert "PURPOSE_MUST_MATCH_P160_ACTION" in req(purpose="OTHER")["validation_errors"]
def test_unbounded_validity_rejected(): assert "REQUESTED_VALIDITY_MUST_BE_BOUNDED" in req(requested_validity={"not_before":"2026-10-01T08:00:00Z"})["validation_errors"]
def test_bounded_multi_use_needs_limit(): assert "BOUNDED_MULTI_USE_REQUIRES_POSITIVE_MAX_USES" in req(requested_use_policy="BOUNDED_MULTI_USE")["validation_errors"]
def test_tamper_detected():
 d=decision(); r=req(normative_decision=d); r["target"]="OTHER"; assert verify_authorization_request(r,d)["status"]=="FAIL"
def test_request_is_not_authorization():
 r=req(); assert r["authorization_created"] is False and r["authorization_token_created"] is False and r["capability_created"] is False and r["execution_performed"] is False and r["p162_opened"] is False
