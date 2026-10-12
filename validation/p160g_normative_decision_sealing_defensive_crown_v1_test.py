from copy import deepcopy
import json
from ontology.p160_normative_decision_sealing import (
    build_normative_decision,
    canonical_sha256,
    manifest,
    verify_normative_decision,
)

def base():
    r={"request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF"}
    a={"status":"CONTEXT_READY","proposal_envelope":{"request_id":"R1"},"normative_decision_request":{"semantic_hash":"RF"},"decision_context_fingerprint":{"semantic_hash":"CTX"},"constitutional_snapshot":{"snapshot_semantic_hash":"SNAP","compiled_profile_hash":"PROF"},"expected_effect_envelope":{"semantic_hash":"EFF"},"artifact_hash":"A","emergency_context":{"active":False}}
    b={"bindings":{"runtime_context_fingerprint":"CTX","snapshot_hash":"SNAP","profile_hash":"PROF"},"norm_context":{"applicable_norms":[{"rule_id":"N1"}]},"blockers":[],"artifact_hash":"B"}
    c={"constitutive_filter_result":"PASS","bindings":deepcopy(b["bindings"]),"upstream_p160b_artifact_hash":"B","artifact_hash":"C"}
    d={"conflict_assessment":{"conflict_class":"C0"},"bindings":{"p160c_artifact_hash":"C","p160c_upstream_p160b_artifact_hash":"B","runtime_bindings":deepcopy(b["bindings"])},"artifact_hash":"D"}
    e={"status":"COMPLIANT_RESOLUTION_FOUND","request_id":"R1","request_fingerprint":"RF","runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","resolution_hash":"E"}
    f={"authority_status":"VALID","request_id":"R1","request_fingerprint":"RF","bindings":{"runtime_context_fingerprint":"CTX","constitutional_snapshot_hash":"SNAP","compiled_profile_hash":"PROF","authority_context_fingerprint":"AUTHCTX"},"scope":{"action_class":["A"]},"purpose":"govern","temporal_bounds":{"valid":True},"resolution_hash":"F"}
    action={"action_class":"A","target":"T","purpose":"govern","parameters":{},"capabilities":["C"],"scope":{"action_class":["A"]},"affected_entities":["X"],"resource_effects":[]}
    return [r,a,b,c,d,e,f,action]

def build(x=None):
    x=x or base()
    return build_normative_decision(*x[:7],action=x[7])

def assert_closed(z):
    assert z["normative_eligibility"] != "ELIGIBLE_CANDIDATE"
    assert z["usable_by_p161"] is False
    assert z["authorization_created"] is False
    assert z["authorization_token_created"] is False
    assert z["execution_performed"] is False
    assert z["p161_opened"] is False

def reseal_tampered(z):
    # Adversary knows the public hash algorithm and recomputes both hashes.
    y=deepcopy(z)
    y.pop("artifact_hash",None)
    y["semantic_hash"]=canonical_sha256({k:v for k,v in y.items() if k not in ("decision_id","semantic_hash","decision_seal")})
    y["decision_seal"]["semantic_hash"]=y["semantic_hash"]
    y["artifact_hash"]=canonical_sha256(y)
    return y

def test_crown_01_request_id_mismatch_A():
    x=base(); x[1]["proposal_envelope"]["request_id"]="R2"; assert_closed(build(x))

def test_crown_02_request_fingerprint_mismatch_E():
    x=base(); x[5]["request_fingerprint"]="RF2"; assert_closed(build(x))

def test_crown_03_runtime_context_mismatch_B():
    x=base(); x[2]["bindings"]["runtime_context_fingerprint"]="CTX2"; assert_closed(build(x))

def test_crown_04_snapshot_mismatch_C():
    x=base(); x[3]["bindings"]["snapshot_hash"]="SNAP2"; assert_closed(build(x))

def test_crown_05_profile_mismatch_F():
    x=base(); x[6]["bindings"]["compiled_profile_hash"]="PROF2"; assert_closed(build(x))

def test_crown_06_missing_canonical_binding():
    x=base()
    x[0].pop("compiled_profile_hash")
    x[2]["bindings"].pop("profile_hash")
    x[6]["bindings"].pop("compiled_profile_hash")
    # A still exposes PROF, so canonical profile cannot silently become positive from absence.
    z=build(x)
    assert_closed(z)

def test_crown_07_B_to_C_hash_substitution():
    x=base(); x[3]["upstream_p160b_artifact_hash"]="ATTACK"; assert_closed(build(x))

def test_crown_08_C_to_D_hash_substitution():
    x=base(); x[4]["bindings"]["p160c_artifact_hash"]="ATTACK"; assert_closed(build(x))

def test_crown_09_B_to_D_hash_substitution():
    x=base(); x[4]["bindings"]["p160c_upstream_p160b_artifact_hash"]="ATTACK"; assert_closed(build(x))

def test_crown_10_unknown_constitutive_never_positive():
    x=base(); x[3]["constitutive_filter_result"]="UNKNOWN"; assert_closed(build(x))

def test_crown_11_unknown_authority_never_positive():
    x=base(); x[6]["authority_status"]="UNDETERMINED"; assert_closed(build(x))

def test_crown_12_hard_conflict_without_E_resolution_never_positive():
    x=base(); x[4]["conflict_assessment"]["conflict_class"]="C5"; x[5]["status"]="COMPLIANT_RESOLUTION_FOUND"; assert_closed(build(x))

def test_crown_13_missing_action_target_never_positive():
    x=base(); x[7].pop("target"); assert_closed(build(x))

def test_crown_14_missing_upstream_provenance_never_positive():
    x=base(); x[5].pop("resolution_hash"); assert_closed(build(x))

def test_crown_15_authority_valid_never_authorizes():
    z=build()
    assert z["authority_status"]=="VALID"
    assert z["normative_eligibility"]=="ELIGIBLE_CANDIDATE"
    assert z["authorization_created"] is False
    assert z["authorization_token_created"] is False
    assert z["decision_seal"]["proves_authorization"] is False
    assert z["decision_seal"]["proves_execution_right"] is False

def test_crown_16_manifest_has_no_authorization_or_execution_boundary():
    m=manifest()
    for k in ("authority_created","authorization_created","authorization_token_created","execution_performed","p161_opened"):
        assert m[k] is False

def test_crown_17_injected_authorization_token_detected():
    z=build(); z["authorization_token"]={"token":"ATTACK"}
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_18_boundary_flip_detected():
    z=build(); z["authorization_created"]=True
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_19_execution_flip_detected():
    z=build(); z["execution_performed"]=True
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_20_p161_open_flip_detected():
    z=build(); z["p161_opened"]=True
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_21_eligibility_tamper_detected():
    z=build(); z["normative_eligibility"]="INELIGIBLE"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_22_action_digest_tamper_detected():
    z=build(); z["action_digest"]["target"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_23_scope_union_tamper_detected():
    z=build(); z["authority_scope"]={"action_class":["A","B"]}
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_24_purpose_tamper_detected():
    z=build(); z["authority_purpose"]="expanded-purpose"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_25_profile_binding_tamper_detected():
    z=build(); z["bindings"]["compiled_profile_hash"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_26_snapshot_binding_tamper_detected():
    z=build(); z["bindings"]["constitutional_snapshot_hash"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_27_context_binding_tamper_detected():
    z=build(); z["bindings"]["runtime_context_fingerprint"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_28_effect_envelope_tamper_detected():
    z=build(); z["expected_effect_envelope_hash"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_29_authority_freshness_tamper_detected():
    z=build(); z["decision_freshness_policy"]["required_state_hashes"]["authority_context_fingerprint"]="OTHER"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_30_lifecycle_stale_detected():
    z=build(); z["lifecycle"]="STALE"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_31_uncommitted_detected():
    z=build(); z["transaction_state"]="PREPARE"
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_32_seal_hash_tamper_detected():
    z=build(); z["decision_seal"]["semantic_hash"]="0"*64
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_33_artifact_hash_tamper_detected():
    z=build(); z["artifact_hash"]="0"*64
    assert verify_normative_decision(z)["status"]=="FAIL"

def test_crown_34_deterministic_replay():
    a=build(); b=build()
    assert a["semantic_hash"]==b["semantic_hash"]
    assert a["artifact_hash"]==b["artifact_hash"]
    assert json.dumps(a,sort_keys=True,separators=(",",":"))==json.dumps(b,sort_keys=True,separators=(",",":"))

def test_crown_35_recomputed_hash_cannot_legitimize_boundary_flip():
    z=build(); z["authorization_created"]=True
    z=reseal_tampered(z)
    v=verify_normative_decision(z)
    assert v["status"]=="FAIL"
    assert v["boundaries_preserved"] is False

def test_crown_36_recomputed_hash_attack_on_p161_boundary_fails():
    z=build(); z["p161_opened"]=True
    z=reseal_tampered(z)
    assert verify_normative_decision(z)["status"]=="FAIL"
