from validation import p159_occ1k_source_backed_materialization_assessment_v1 as a

def test_canonical_source_gap_is_explicit():
    r=a.build(); f=r["facts"]
    assert f["ccad_conflict_partition_unresolved"]
    assert f["constitution_partition_unresolved"]
    assert f["governance_partition_unresolved"]

def test_code_taxonomy_is_not_promoted_to_canonical_binding():
    r=a.build()
    assert r["facts"]["ccad_spec_has_conflict_taxonomy"]
    assert r["assessment"]["S7.CCAD"]["status"]=="UNRESOLVED"
    assert not r["assessment"]["S7.CCAD"]["materialization_performed"]

def test_no_zero_relation_pass_for_composition():
    r=a.build()
    assert r["facts"]["cnp_relations_empty"]
    assert r["assessment"]["S8.COMPOSITION"]["status"]=="UNRESOLVED"

def test_s10_remains_partial_without_source_bound_mapping():
    r=a.build()
    assert r["assessment"]["S10.ENFORCEMENT"]["status"]=="PARTIAL"
    assert r["facts"]["s10_runtime_graph_not_proven"]

def test_no_history_or_runtime_boundary_violation():
    c=a.build()["conclusion"]
    assert not c["historical_occ1d_rewritten"]
    assert not c["canonical_occ1a_rewritten"]
    assert not c["synthetic_relations_created"]
    assert not c["runtime_graph_invented"] and not c["runtime_binding_created"]
    assert not c["p160b_opened"]

def test_flb3_remains_blocked_and_r9_is_governed():
    r=a.build(); c=r["conclusion"]
    assert c["fl_b3"]=="BLOCKED"
    assert not c["lock_ready"] and not c["lock_granted"]
    assert c["next_required_step"]=="R9_GOVERNED_UPSTREAM_SEMANTIC_BINDING_REMEDIATION"
    assert "never infer a SAFE relation" in " ".join(r["r9_constraints"])

def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
