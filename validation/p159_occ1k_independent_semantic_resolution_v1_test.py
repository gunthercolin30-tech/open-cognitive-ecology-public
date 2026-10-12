from validation import p159_occ1k_independent_semantic_resolution_v1 as r

def test_exact_gate_set():
    x=r.build(); assert [g["gate_id"] for g in x["gates"]]==["FL-B%d"%i for i in range(1,13)]

def test_current_evidence_resolves_expected_green_gates():
    x=r.build(); d={g["gate_id"]:g["verdict"] for g in x["gates"]}
    for k in ("FL-B1","FL-B2","FL-B4","FL-B5","FL-B6","FL-B7","FL-B8","FL-B9"):
        assert d[k]=="PASS"

def test_static_root_unresolved_blocks_final_lock():
    x=r.build(); g=next(v for v in x["gates"] if v["gate_id"]=="FL-B3")
    assert g["verdict"]=="BLOCKED"
    assert "S7.CCAD" in g["findings"][0] and "S10.ENFORCEMENT" in g["findings"][0]

def test_final_bundle_and_fresh_nonregression_not_promoted():
    x=r.build(); d={g["gate_id"]:g["verdict"] for g in x["gates"]}
    assert d["FL-B10"]=="INCONCLUSIVE"
    assert d["FL-B12"]=="INCONCLUSIVE"

def test_open_exhaustive_debt_blocks_b11():
    x=r.build(); d={g["gate_id"]:g["verdict"] for g in x["gates"]}
    assert d["FL-B11"]=="BLOCKED"

def test_boundaries_and_determinism():
    a=r.build(); b=r.build()
    assert a["semantic_hash"]==b["semantic_hash"]
    assert not a["lock_ready"] and not a["lock_granted"] and not a["p160b_opened"]
    assert a["historical_lock_preserved"] and not a["authorization_created"] and not a["execution_performed"]
