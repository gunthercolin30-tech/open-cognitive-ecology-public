from pathlib import Path
import json,shutil
from ontology import occ1h_preclose_evidence as p
from ontology import occ1h_a075_post_correction_evidence as e
ROOT=Path(__file__).resolve().parents[1]
def rows(r): return {x["canonical_attack_id"]:x for x in r["current_rows"]}
def test_a075_formal_root_reevaluation_real_state():
    assert e.verify_materialized(ROOT)
    r=p.build(ROOT); d=rows(r)
    assert r["current_inconclusive_count"]==22 and "A75" not in r["root_inconclusive"]
    assert d["A75"]["historical_verdict"]=="INCONCLUSIVE" and d["A75"]["current_verdict"]=="RESISTED"
    assert d["A101"]["current_verdict"]=="INCONCLUSIVE" and d["A105"]["current_verdict"]=="INCONCLUSIVE"
    assert r["closure_admissible"] is False
    assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
def test_a075_evidence_degrades_fail_closed(tmp_path):
    target=tmp_path/"repo"; shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",target/"validation_artifacts/p159/occ1h")
    ap=target/"validation_artifacts/p159/occ1h/a075_post_correction_evidence_v1.json"
    d=json.loads(ap.read_text()); d["current_verdict"]="INCONCLUSIVE"; ap.write_text(json.dumps(d)+"\n")
    assert not e.verify_materialized(target)
    r=p.build(target); assert r["status"]=="INCOMPLETE" and "a075_post_correction_evidence_v1.json" in r.get("invalid_inputs",[])
def test_a075_historical_and_dependencies_not_promoted():
    d=json.loads((ROOT/"validation_artifacts/p159/occ1h/h7_execution_bundle_v1.json").read_text())
    h={str(x.get("attack_id")):x for x in d["rows"]}; assert (h.get("A075") or h.get("A75"))["verdict"]=="INCONCLUSIVE"
    a=p.build(ROOT); b=p.build(ROOT); assert a==b
    rr=rows(a); assert rr["A101"]["current_verdict"]=="INCONCLUSIVE" and rr["A105"]["current_verdict"]=="INCONCLUSIVE"
