from validation import p159_occ1k_flb3_boundary_reconciliation_audit_v1 as a

def test_three_unresolved_findings_preserved():
    r=a.build()
    assert r["static_findings"]["S7.CCAD"]["result"]=="UNRESOLVED"
    assert r["static_findings"]["S8.COMPOSITION"]["result"]=="UNRESOLVED"
    assert r["static_findings"]["S10.ENFORCEMENT"]["result"]=="UNRESOLVED"

def test_p160_boundary_is_explicit():
    r=a.build()
    assert r["facts"]["p159_boundary_explicit"]
    assert r["facts"]["technical_remediation_not_authorized_within_p159"]

def test_bounded_fixture_is_not_runtime_materialization():
    r=a.build()
    assert r["facts"]["bounded_fixture_not_real_runtime"]
    assert r["facts"]["no_runtime_consumers_created"]

def test_fail_closed_boundaries():
    r=a.build(); c=r["conclusion"]
    assert c["fl_b3"]=="BLOCKED"
    assert not c["p159_new_runtime_binding_authorized"]
    assert not c["p160b_opened"] and not c["lock_ready"] and not c["lock_granted"]
    assert not c["runtime_binding_created"]

def test_deterministic():
    assert a.build()["semantic_hash"]==a.build()["semantic_hash"]
