from validation import p159_occ1k_canonical_dependency_resolution_v1 as r

def test_canonical_order_resolves_cycle_as_pre_runtime_contract():
    x=r.build()
    assert x["status"]=="CANONICAL_DEPENDENCY_RESOLVED"
    assert x["resolution_class"]=="PRE_RUNTIME_CONTRACT_OBLIGATION"

def test_historical_unresolved_findings_are_preserved():
    x=r.build()
    assert all(v["historical_result"]=="UNRESOLVED" for v in x["historical_static_findings"].values())
    assert not x["effects"]["historical_occ1d_rewritten"]

def test_no_runtime_fact_is_manufactured():
    x=r.build(); e=x["effects"]
    assert not e["runtime_graph_invented"]
    assert not e["runtime_binding_created"]
    assert not e["static_pass_manufactured"]

def test_no_premature_gate_or_lock_promotion():
    x=r.build(); e=x["effects"]
    assert not e["p160b_opened"]
    assert not e["fl_b3_promoted_to_pass"]
    assert not e["lock_ready"] and not e["lock_granted"]

def test_r7_is_explicitly_fail_closed():
    x=r.build()
    rules=" ".join(x["r7_acceptance_rule"])
    assert "fail-closed" in rules
    assert "cannot be represented as an observed runtime fact" in rules
    assert x["effects"]["next_required_step"]=="R7_SUPERSEDING_PRE_RUNTIME_STATIC_CONTRACT_ASSESSMENT"

def test_deterministic():
    assert r.build()["semantic_hash"]==r.build()["semantic_hash"]
