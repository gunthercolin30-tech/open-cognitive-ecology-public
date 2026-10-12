from pathlib import Path
from ontology import occ1h_a097_posthardening_evidence as ev
from ontology import occ1h_preclose_evidence as pre
ROOT=Path.home()/"open-cognitive-ecology"
def test_a097_evidence_current_and_historical():
    d=ev.build(ROOT); assert ev.verify_document(d)
    assert d["historical_verdict"]=="INCONCLUSIVE" and d["current_verdict"]=="DETECTED"
    assert d["compound_execution"] is True and d["s8_result"]=="FAIL" and d["s5_result"]=="FAIL"
def test_a097_evidence_tamper_fails_closed():
    d=ev.build(ROOT); d=dict(d); d["s5_result"]="PASS"; assert ev.verify_document(d) is False
def test_a097_materialized_and_preclose_transition():
    assert ev.verify_materialized(ROOT)
    r=pre.build(ROOT); assert r["a097_posthardening_verified"] is True
    assert r["current_inconclusive_count"]==22 and len(r["root_inconclusive"])==22; assert "A75" not in r["root_inconclusive"] and "A101" in r["root_inconclusive"] and "A105" in r["root_inconclusive"]
    row=next(x for x in r["current_rows"] if x["canonical_attack_id"]=="A97")
    assert row["historical_verdict"]=="INCONCLUSIVE" and row["current_verdict"]=="DETECTED"
    assert r["closure_admissible"] is False
def test_a097_boundaries():
    r=pre.build(ROOT)
    assert not r["authorization_created"] and not r["execution_performed"]
    assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
