from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h4 as h4

ROOT=Path(__file__).resolve().parents[1]

def test_h4_complete_range():
    r=h4.run(ROOT)
    assert r["scenario_count"]==12
    assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(31,43)]

def test_h4_executable_transformations_detected():
    r=h4.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
    for aid in ("A031","A032","A033","A034","A035","A036","A037","A038","A039"):
        assert d[aid]["verdict"]=="DETECTED",(aid,d[aid])

def test_h4_bounded_representation_gaps_not_laundered():
    r=h4.run(ROOT); d={x["attack_id"]:x for x in r["rows"]}
    assert d["A040"]["verdict"]=="INCONCLUSIVE"
    assert d["A041"]["verdict"]=="INCONCLUSIVE"
    assert d["A042"]["verdict"]=="INCONCLUSIVE"
    assert r["verdict_counts"]["VIOLATED"]==0

def test_h4_no_authority_execution_or_closure():
    r=h4.run(ROOT)
    assert r["authorization_created"] is False
    assert r["execution_performed"] is False
    assert r["occ1h_closed"] is False
    assert r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False
    assert r["p160_opened"] is False

def test_h4_deterministic_verdict_projection():
    a=h4.run(ROOT); b=h4.run(ROOT)
    assert [(x["attack_id"],x["verdict"],x["observed_reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["observed_reason"]) for x in b["rows"]]
