from validation import p159_occ1k_pre_runtime_static_contract_assessment_v1 as a

def test_s7_s8_are_incomplete_not_runtime_blocked():
    r=a.build()
    assert r["assessments"]["S7.CCAD"]["pre_runtime_contract"]=="INCOMPLETE"
    assert r["assessments"]["S8.COMPOSITION"]["pre_runtime_contract"]=="INCOMPLETE"
    assert not r["assessments"]["S7.CCAD"]["runtime_required_for_completion"]
    assert not r["assessments"]["S8.COMPOSITION"]["runtime_required_for_completion"]

def test_s10_is_partial_contract_not_runtime_fact():
    r=a.build(); s=r["assessments"]["S10.ENFORCEMENT"]
    assert s["pre_runtime_contract"]=="PARTIAL"
    assert s["expected_consumers_declared"]
    assert not s["enforcement_coverage_map_present"]
    assert not s["actual_runtime_reachability_required_in_p159"]

def test_no_empty_relation_pass():
    r=a.build()
    assert r["facts"]["relations_empty"]
    assert not r["conclusion"]["s7_resolved"]
    assert not r["conclusion"]["s8_resolved"]

def test_historical_and_runtime_boundaries():
    r=a.build(); c=r["conclusion"]
    assert not c["historical_occ1d_rewritten"]
    assert not c["runtime_graph_invented"] and not c["runtime_binding_created"]
    assert not c["p160b_opened"]

def test_flb3_remains_blocked():
    r=a.build(); c=r["conclusion"]
    assert c["fl_b3"]=="BLOCKED"
    assert not c["lock_ready"] and not c["lock_granted"]

def test_r8_requires_source_backing_and_unknown_preservation():
    rules=" ".join(a.build()["r8_constraints"])
    assert "canonical source/NIR evidence" in rules
    assert "do not invent SAFE relations" in rules
    assert "UNKNOWN/UNRESOLVED remains blocking" in rules

def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
