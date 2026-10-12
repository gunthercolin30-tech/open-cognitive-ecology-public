from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
from ontology import occ1h_h6_posthardening_evidence as ev
from ontology import occ1h_preclose_evidence as pre
def _rows(r): return {x["canonical_attack_id"]:x for x in r["current_rows"]}
def test_h6_posthardening_transition():
    d=json.loads((ROOT/"validation_artifacts/p159/occ1h/h6_posthardening_evidence_v1.json").read_text())
    assert ev.verify_document(d)
    r=pre.build(ROOT); q=_rows(r)
    assert r["current_inconclusive_count"]==22 and len(r["root_inconclusive"])==22; assert "A75" not in r["root_inconclusive"] and "A101" in r["root_inconclusive"] and "A105" in r["root_inconclusive"]
    for aid in ("A58","A59","A60"):
        assert q[aid]["historical_verdict"]=="INCONCLUSIVE"
        assert q[aid]["current_verdict"]=="DETECTED"
    assert q["A61"]["historical_verdict"]=="INCONCLUSIVE" and q["A61"]["current_verdict"]=="DETECTED"
    assert q["A62"]["historical_verdict"]=="INCONCLUSIVE" and q["A62"]["current_verdict"]=="DETECTED"
def test_tamper_fails_closed(tmp_path):
    target=tmp_path/"repo"; shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",target/"validation_artifacts/p159/occ1h")
    p=target/"validation_artifacts/p159/occ1h/h6_posthardening_evidence_v1.json"; d=json.loads(p.read_text())
    d["transitions"][0]["current_verdict"]="RESISTED"; p.write_text(json.dumps(d))
    r=pre.build(target); assert r["status"]=="INCOMPLETE" and r["closure_admissible"] is False
def test_missing_posthardening_fails_closed(tmp_path):
    target=tmp_path/"repo"; shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",target/"validation_artifacts/p159/occ1h")
    (target/"validation_artifacts/p159/occ1h/h6_posthardening_evidence_v1.json").unlink()
    r=pre.build(target); assert r["status"]=="INCOMPLETE" and r["closure_admissible"] is False
def test_boundaries_remain_closed():
    r=pre.build(ROOT)
    assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
