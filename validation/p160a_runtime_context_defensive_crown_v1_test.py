from validation import p160a_runtime_context_defensive_crown_v1 as c

def test_defensive_crown_all_resisted():
    r=c.run_crown()
    assert r["counts"]["total"] == 15
    assert r["counts"]["violated"] == 0

def test_root_scenarios_all_resisted():
    r=c.run_crown()
    assert r["root_counts"] == {"total":7,"violated":0}

def test_crown_is_non_authorizing():
    r=c.run_crown()
    assert r["authorization_created"] is False
    assert r["execution_performed"] is False
    assert r["p160_final_lock"] is False
    assert r["p161_opened"] is False

def test_crown_is_deterministic():
    assert c.run_crown()["semantic_hash"] == c.run_crown()["semantic_hash"]


def test_crown_uses_runtime_fingerprint_contract():
    x=c._ctx(c._request())
    fp=x["decision_context_fingerprint"]
    assert "fingerprint" in fp
    assert fp["fingerprint_complete"] is True
