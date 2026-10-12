from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h5 as h5

ROOT=Path(__file__).resolve().parents[1]

def test_h5_canonical_range_and_count():
    r=h5.run(ROOT)
    assert r["scenario_count"]==10
    assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(43,53)]

def test_h5_non_compensatory_and_no_false_success():
    r=h5.run(ROOT)
    assert r["verdict_counts"]["VIOLATED"]==0
    assert r["inconclusive_not_resisted"] is True
    assert all(x["verdict"] in ("DETECTED","INCONCLUSIVE") for x in r["rows"])

def test_h5_evidence_bound():
    r=h5.run(ROOT)
    for row in r["rows"]:
        if row["verdict"]=="DETECTED":
            assert row["causal_evidence"].get("artifact")
        else:
            assert row["detector"]=="REPRESENTATION_BOUNDARY"

def test_h5_no_authority_execution_or_closure():
    r=h5.run(ROOT)
    assert r["authorization_created"] is False
    assert r["execution_performed"] is False
    assert r["occ1h_closed"] is False
    assert r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False
    assert r["p160_opened"] is False

def test_h5_deterministic_projection():
    a=h5.run(ROOT); b=h5.run(ROOT)
    assert [(x["attack_id"],x["verdict"],x["observed_reason"]) for x in a["rows"]] == \
           [(x["attack_id"],x["verdict"],x["observed_reason"]) for x in b["rows"]]
