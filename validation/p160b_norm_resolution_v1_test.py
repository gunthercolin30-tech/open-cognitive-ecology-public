from ontology import p160_norm_resolution as p

def _profile(rules):
    return {"artifact_hash":"p159-profile-hash","source_map":{"N1":"src:1"},"rules":rules}

def _ctx():
    return {"constitutional_snapshot":{"snapshot_semantic_hash":"snap-hash"},"decision_context_fingerprint":{"fingerprint":"ctx-fp"}}

def test_applies_and_trace_boundaries():
    rules=[{"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.actor.role","op":"EQ","value":"operator"}],"scope_constraints":{"status":"BOUNDED"},"temporal_constraints":{"status":"BOUNDED"},"uncertainty_semantics":{"unknown_never_promoted_to_true":True}}]
    out=p.resolve_norms({"actor":{"role":"operator"}},_profile(rules),_ctx())
    assert out["norm_context"]["applicable_norms"]==["R1"]
    assert out["normative_applicability"][0]["compliance"]=="UNRESOLVED"
    assert out["bindings"]["profile_hash"]=="p159-profile-hash"
    assert out["bindings"]["snapshot_hash"]=="snap-hash"
    assert out["bindings"]["runtime_context_fingerprint"]=="ctx-fp"
    assert p.verify_norm_context(out)["status"]=="PASS"
    assert out["authorization_created"] is False and out["execution_performed"] is False

def test_unknown_never_becomes_does_not_apply():
    rules=[{"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.missing","op":"EQ","value":True}]}]
    out=p.resolve_norms({},_profile(rules),_ctx())
    assert out["norm_context"]["undetermined_norms"]==["R1"]
    assert out["norm_context"]["non_applicable_norms"]==[]
    assert out["normative_applicability"][0]["compliance"]=="UNRESOLVED"

def test_positive_false_is_does_not_apply():
    rules=[{"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.kind","op":"EQ","value":"A"}]}]
    out=p.resolve_norms({"kind":"B"},_profile(rules),_ctx())
    assert out["norm_context"]["non_applicable_norms"]==["R1"]
    assert out["normative_applicability"][0]["compliance"]=="NOT_APPLICABLE"

def test_always_evaluate_survives_missing_predicate():
    rules=[{"rule_id":"L0.3","source_norm_ids":["DNA-L0.3"],"always_evaluate":True,"conditions":[]}]
    out=p.resolve_norms({},_profile(rules),_ctx())
    assert out["norm_context"]["applicable_norms"]==["L0.3"]

def test_unsupported_condition_fails_closed():
    rules=[{"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.x","op":"MAGIC","value":1}]}]
    out=p.resolve_norms({"x":1},_profile(rules),_ctx())
    assert out["norm_context"]["undetermined_norms"]==["R1"]

def test_determinism_and_tamper_detection():
    rules=[{"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.x","op":"EQ","value":1}]}]
    a=p.resolve_norms({"x":1},_profile(rules),_ctx()); b=p.resolve_norms({"x":1},_profile(rules),_ctx())
    assert a==b
    a["norm_context"]["applicable_norms"]=[]
    assert p.verify_norm_context(a)["status"]=="FAIL"

def test_manifest_exact_scope():
    m=p.manifest()
    assert m["scope"]=="P160-B_ONLY"
    assert m["artifacts"]==["norm_context","normative_applicability","norm_resolution_trace"]
    assert m["boundaries"]["constitutive_filter_performed"] is False
    assert m["boundaries"]["conflict_arbitration_performed"] is False
    assert m["boundaries"]["authority_resolved"] is False

def test_scope_unresolved_and_expiry_fail_closed():
    r={"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.x","op":"EQ","value":1}],"scope_constraints":{"status":"UNRESOLVED"}}
    out=p.resolve_norms({"x":1},_profile([r]),_ctx())
    assert out["normative_applicability"][0]["applicability"]=="UNDETERMINED"
    r["scope_constraints"]={"status":"BOUNDED"}; r["temporal_constraints"]={"status":"EXPIRED"}
    out=p.resolve_norms({"x":1},_profile([r]),_ctx())
    assert out["normative_applicability"][0]["applicability"]=="DOES_NOT_APPLY"

def test_evidence_uncertainty_not_promoted():
    for status in ("CONTESTED","F1","TIMEOUT","PREDICTED"):
        r={"rule_id":"R1","source_norm_ids":["N1"],"conditions":[{"field":"request.x","op":"EQ","value":1}],"evidence_status":status}
        out=p.resolve_norms({"x":1},_profile([r]),_ctx())
        assert out["normative_applicability"][0]["applicability"]=="UNDETERMINED"

def test_always_evaluate_does_not_bypass_expiry():
    r={"rule_id":"L0.3","source_norm_ids":["DNA-L0.3"],"always_evaluate":True,"conditions":[],"temporal_constraints":{"status":"EXPIRED"}}
    out=p.resolve_norms({},_profile([r]),_ctx())
    assert out["normative_applicability"][0]["applicability"]=="DOES_NOT_APPLY"
