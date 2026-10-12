from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
from ontology import occ1h_h6_posthardening_evidence as ev
from ontology import occ1h_preclose_evidence as pre
def test_materialized_transition_and_preclose():
    d=json.loads((ROOT/"validation_artifacts/p159/occ1h/h6_a061_a062_posthardening_evidence_v1.json").read_text())
    assert ev.verify_a061_a062_document(d) and ev.verify_a061_a062_materialized(ROOT)
    r=pre.build(ROOT); q={x["canonical_attack_id"]:x for x in r["current_rows"]}
    assert r["current_inconclusive_count"]==22 and len(r["root_inconclusive"])==22; assert "A75" not in r["root_inconclusive"] and "A101" in r["root_inconclusive"] and "A105" in r["root_inconclusive"]
    for aid in ("A61","A62"):
        assert q[aid]["historical_verdict"]=="INCONCLUSIVE" and q[aid]["current_verdict"]=="DETECTED"
def test_boundaries_closed():
    r=pre.build(ROOT)
    assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
