from validation import p159_occ1k_semantic_qualification_v1 as q

def test_twelve_qualifications():
    r=q.build(); assert len(r["qualifications"])==12

def test_no_presence_to_pass_promotion():
    r=q.build(); assert r["counts"]["PASS"]==0
    assert all(x["lock_credit"]=="NOT_GRANTED" for x in r["qualifications"])

def test_b11_stays_blocked_while_fli_debt_open():
    r=q.build(); x=next(v for v in r["qualifications"] if v["gate_id"]=="FL-B11")
    assert x["verdict"]=="BLOCKED"

def test_other_unqualified_evidence_is_inconclusive_not_pass():
    r=q.build()
    vals=[x for x in r["qualifications"] if x["gate_id"]!="FL-B11"]
    assert all(x["verdict"] in ("INCONCLUSIVE","FAIL") for x in vals)

def test_boundaries():
    r=q.build(); assert not r["lock_ready"] and not r["lock_granted"]
    assert r["historical_lock_preserved"] and not r["p160b_opened"]
    assert not r["authorization_created"] and not r["execution_performed"]

def test_deterministic():
    assert q.build()["semantic_hash"]==q.build()["semantic_hash"]
