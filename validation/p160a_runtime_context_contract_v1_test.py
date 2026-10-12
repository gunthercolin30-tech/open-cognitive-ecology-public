from copy import deepcopy
from ontology import p160_runtime_context_contract as p


def req():
    return {
        "request_id": "R-1", "actor": {"actor_id":"A-1","claimed_role":"operator"},
        "proposed_action": {"action_class":"READ","parameters":{"x":1}},
        "target": {"target_id":"T-1"}, "capabilities_required":["read"], "purpose":"diagnostic",
        "expected_effects":{"intended_effects":["observe"],"foreseeable_effects":[],"side_effects":[],"affected_entities":["T-1"],"irreversibility":"LOW","effect_uncertainty":"LOW","tolerances":{}},
        "affected_entities":["T-1"], "resource_use":{"cpu":"low"}, "risk_context":"LOW",
        "human_impact":"NONE_KNOWN", "emergency_context":{"emergency_id":"E-0","declared":False},
        "coalition_context":{"coalition_id":"C-0","members":[]}, "delegation_context":{"delegations":[]},
        "recent_related_actions":[], "constitutional_snapshot_hash":"a"*64, "compiled_profile_hash":"b"*64,
    }


def snap():
    return {k: ("b"*64 if k=="compiled_profile_hash" else "c"*64) for k in p.SNAPSHOT_FIELDS}


def test_complete_context_ready_and_non_authorizing():
    s=snap(); built=p.build_constitutional_snapshot(s); r=req()
    r["constitutional_snapshot_hash"]=built["snapshot_semantic_hash"]
    r["compiled_profile_hash"]=s["compiled_profile_hash"]
    x=p.build_runtime_context(r,constitutional_snapshot=s,evidence=[],history_complete=True)
    assert x["status"]=="CONTEXT_READY"
    assert x["constitutional_snapshot_binding_match"] is True
    assert x["compiled_profile_binding_match"] is True
    assert x["authorization_created"] is False and x["authorization_token_created"] is False
    assert x["execution_performed"] is False and x["p161_opened"] is False
    assert p.verify_runtime_context(x)["status"]=="PASS"


def test_missing_fact_is_unknown_and_never_favorable():
    r=req(); r.pop("purpose")
    x=p.build_runtime_context(r,constitutional_snapshot=snap(),history_complete=True)
    assert x["status"]=="CONTEXT_INCOMPLETE"
    assert "purpose" in x["missing_request_fields"]
    assert x["unknown_is_favorable_default"] is False


def test_claimed_authority_stays_claim():
    r=req(); r["actor"]["claimed_role"]="CONSTITUENT"
    x=p.build_runtime_context(r,constitutional_snapshot=snap(),history_complete=True)
    assert x["claims"]["actor"]["epistemic_status"]=="CLAIMED"
    assert x["claims"]["actor"]["verified"] is False
    assert x["authority_resolved"] is False


def test_claimed_emergency_not_promoted_active():
    r=req(); r["emergency_context"]={"emergency_id":"E-X","declared":True,"claimed_active":True}
    x=p.build_runtime_context(r,constitutional_snapshot=snap(),history_complete=True)
    assert x["emergency_context"]["epistemic_status"]=="CLAIMED"
    assert x["emergency_context"]["verified"] is False


def test_history_truncation_is_analysis_incomplete():
    x=p.build_runtime_context(req(),constitutional_snapshot=snap(),history_complete=False)
    assert x["composite_action_context"]["analysis_incomplete"] is True
    assert "RELATED_ACTION_HISTORY_INCOMPLETE_OR_UNKNOWN" in x["blockers"]


def test_duplicate_evidence_root_not_independent():
    ev=[{"evidence_id":"1","source_ref":"S1","evidence_root":"ROOT"},{"evidence_id":"2","source_ref":"S2","evidence_root":"ROOT"}]
    x=p.build_runtime_context(req(),constitutional_snapshot=snap(),evidence=ev,history_complete=True)
    assert x["context_evidence_bundle"]["duplicate_evidence_roots"]==["ROOT"]
    assert x["context_evidence_bundle"]["independence_inferred_from_duplicate_count"] is False


def test_target_or_purpose_changes_fingerprint():
    a=p.build_runtime_context(req(),constitutional_snapshot=snap(),history_complete=True)
    r=req(); r["target"]={"target_id":"T-2"}
    b=p.build_runtime_context(r,constitutional_snapshot=snap(),history_complete=True)
    r2=req(); r2["purpose"]="other"
    c=p.build_runtime_context(r2,constitutional_snapshot=snap(),history_complete=True)
    assert a["decision_context_fingerprint"]["fingerprint"] != b["decision_context_fingerprint"]["fingerprint"]
    assert a["decision_context_fingerprint"]["fingerprint"] != c["decision_context_fingerprint"]["fingerprint"]


def test_tamper_detected():
    x=p.build_runtime_context(req(),constitutional_snapshot=snap(),history_complete=True)
    y=deepcopy(x); y["proposal_envelope"]["declared_purpose"]="laundered"
    assert p.verify_runtime_context(y)["status"]=="FAIL"


def test_deterministic_same_inputs_same_artifact_hash():
    a=p.build_runtime_context(req(),constitutional_snapshot=snap(),history_complete=True)
    b=p.build_runtime_context(req(),constitutional_snapshot=snap(),history_complete=True)
    assert a["artifact_hash"]==b["artifact_hash"]


def _bound_req():
    s = snap()
    built = p.build_constitutional_snapshot(s)
    r = req()
    r["constitutional_snapshot_hash"] = built["snapshot_semantic_hash"]
    r["compiled_profile_hash"] = s["compiled_profile_hash"]
    return r, s


def test_request_and_snapshot_profile_cross_bindings():
    r, s = _bound_req()
    ctx = p.build_runtime_context(r, constitutional_snapshot=s, evidence=[], history_complete=True)
    assert ctx["constitutional_snapshot_binding_match"] is True
    assert ctx["compiled_profile_binding_match"] is True
    assert "normative_decision_request" in ctx


def test_snapshot_mismatch_blocks_context_ready():
    r, s = _bound_req()
    r["constitutional_snapshot_hash"] = "wrong"
    ctx = p.build_runtime_context(r, constitutional_snapshot=s, evidence=[], history_complete=True)
    assert ctx["status"] == "CONTEXT_INCOMPLETE"
    assert "CONSTITUTIONAL_SNAPSHOT_BINDING_MISMATCH_OR_UNKNOWN" in ctx["blockers"]


def test_profile_mismatch_blocks_context_ready():
    r, s = _bound_req()
    r["compiled_profile_hash"] = "wrong"
    ctx = p.build_runtime_context(r, constitutional_snapshot=s, evidence=[], history_complete=True)
    assert ctx["status"] == "CONTEXT_INCOMPLETE"
    assert "COMPILED_PROFILE_BINDING_MISMATCH_OR_UNKNOWN" in ctx["blockers"]


def test_clock_rollback_blocks_context_ready():
    r, s = _bound_req()
    ctx = p.build_runtime_context(
        r, constitutional_snapshot=s, evidence=[], history_complete=True,
        prior_observed_time="2026-09-30T08:00:00Z",
        observed_time="2026-09-30T07:59:59Z",
    )
    assert ctx["clock_continuity"]["state"] == "NON_MONOTONIC"
    assert "CLOCK_ROLLBACK_DETECTED" in ctx["blockers"]


def test_material_change_requires_revalidation():
    r, _ = _bound_req()
    r2 = deepcopy(r)
    r2["target"] = "other-target"
    m = p.classify_material_change(r, r2)
    assert m["material_change"] is True
    assert m["requires_revalidation"] is True
    assert m["authorization_created"] is False


def test_emergency_and_coalition_do_not_self_verify_or_aggregate_authority():
    r, s = _bound_req()
    r["emergency_context"] = {"emergency_id": "E1", "declared_scope": "all", "competent_authority": "claimed"}
    r["coalition_context"] = {"coalition_id": "C1", "members": ["a", "b"], "combined_authority": "governance"}
    ctx = p.build_runtime_context(r, constitutional_snapshot=s, evidence=[], history_complete=True)
    assert ctx["emergency_context"]["active_emergency_established"] is False
    assert ctx["coalition_context"]["authority_aggregation_inferred"] is False


def test_raw_sensitive_evidence_copy_requires_review():
    r, s = _bound_req()
    evidence = [{"evidence_id": "e1", "source_ref": "ref", "raw_sensitive_data_copied": True}]
    ctx = p.build_runtime_context(r, constitutional_snapshot=s, evidence=evidence, history_complete=True)
    assert ctx["privacy_review"]["minimization_satisfied"] is False
    assert "RAW_SENSITIVE_DATA_COPY_REQUIRES_REVIEW" in ctx["blockers"]
