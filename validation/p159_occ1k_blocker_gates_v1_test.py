from validation import p159_occ1k_blocker_gates_v1 as b

def test_exactly_twelve_canonical_gates():
    r=b.build(); assert [g["gate_id"] for g in r["gates"]]==["FL-B%d"%i for i in range(1,13)]

def test_presence_never_becomes_semantic_pass():
    r=b.build()
    assert all(g["lock_credit"]=="NOT_GRANTED" for g in r["gates"])
    assert not r["all_gates_pass"] and not r["lock_ready"] and not r["lock_granted"]

def test_missing_anchor_fails_closed(monkeypatch):
    original=b.GATES["FL-B4"]["anchors"]
    monkeypatch.setitem(b.GATES["FL-B4"],"anchors",["definitely/missing/evidence.json"])
    r=b.build(); g=next(x for x in r["gates"] if x["gate_id"]=="FL-B4")
    assert g["state"]=="EVIDENCE_MISSING"
    monkeypatch.setitem(b.GATES["FL-B4"],"anchors",original)

def test_open_risk_or_debt_blocks_b11():
    r=b.build(); g=next(x for x in r["gates"] if x["gate_id"]=="FL-B11")
    assert r["open_risk_count"]>=1 and r["open_debt_count"]>=1
    assert g["state"]=="BLOCKED"
    assert g["semantic_verdict"]=="BLOCKED_BY_OPEN_RISK_OR_DEBT"

def test_boundaries_preserved():
    r=b.build()
    assert r["historical_lock_preserved"] and not r["p160b_opened"]
    assert not r["authorization_created"] and not r["execution_performed"]

def test_deterministic():
    assert b.build()["semantic_hash"]==b.build()["semantic_hash"]
