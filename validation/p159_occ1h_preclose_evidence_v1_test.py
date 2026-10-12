from pathlib import Path
import json, shutil
from ontology import occ1h_preclose_evidence as p
ROOT=Path(__file__).resolve().parents[1]

def test_preclose_real_state():
    r=p.build(ROOT)
    assert r["scenarios_accounted"]==105
    assert r["missing_attack_ids"]==[] and r["extra_attack_ids"]==[]
    assert len(r["families_accounted"])==10
    assert r["current_violated_count"]==0
    assert r["current_inconclusive_count"]==22
    assert r["h6_a061_a062_posthardening_verified"] is True
    assert r["h6_posthardening_verified"] is True
    assert r["a075_post_correction_verified"] is True
    assert r["historical_violated"]==["A8","A9"]
    assert r["closure_admissible"] is False

def test_preclose_uses_explicit_root_qualification_without_inference():
    r=p.build(ROOT)
    assert r["root_qualification_complete"] is True
    assert r["root_undetermined"]==[]
    assert "ROOT_CLASSIFICATION_NOT_EXECUTABLY_QUALIFIED" not in r["closure_blockers"]
    assert "ROOT_INCONCLUSIVE_PRESENT" in r["closure_blockers"]
    assert "ACHI_NOT_FULLY_EVIDENCED" in r["closure_blockers"]
    classifications=[x["root_classification"] for x in r["current_rows"]]
    assert classifications.count("ROOT")==105
    assert classifications.count("NON_ROOT")==0
    assert classifications.count("ROOT_UNDETERMINED")==0
    assert r["root_undetermined_count"]==0
    assert "ROOT_UNDETERMINED_PRESENT" not in r["closure_blockers"]

def test_preclose_historical_counterexample_binding():
    r=p.build(ROOT)
    d={x["invariant"]:x for x in r["achi"]}
    assert d["ACHI-8"]["status"]=="PASS"
    assert d["ACHI-9"]["status"]=="PASS"
    assert d["ACHI-11"]["status"]=="INCONCLUSIVE"
    assert d["ACHI-13"]["status"]=="PASS"
    assert "complete H1-H10 historical results are bound to exact immutable SHA-256 identities" in d["ACHI-13"]["reason"]
    assert r["historical_counterexample_verified"] is True
    assert r["historical_counterexample_gap"] is False
    assert "HISTORICAL_COUNTEREXAMPLE_RECORD_GAP" not in r["closure_blockers"]
    assert r["achi_counts"]=={"PASS":15,"INCONCLUSIVE":1,"FAIL":0}
    assert r["closure_admissible"] is False

def test_preclose_historical_binding_degrades_fail_closed(tmp_path):
    target=tmp_path/"repo"
    shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",
                    target/"validation_artifacts/p159/occ1h")
    cdir=target/"validation_artifacts/p159/occ1h/counterexamples"
    if cdir.exists():
        shutil.rmtree(cdir)
    r=p.build(target)
    d={x["invariant"]:x for x in r["achi"]}
    assert r["historical_counterexample_verified"] is False
    assert r["historical_counterexample_gap"] is True
    assert d["ACHI-8"]["status"]=="INCONCLUSIVE"
    assert d["ACHI-9"]["status"]=="INCONCLUSIVE"
    assert d["ACHI-13"]["status"]=="PASS"
    assert "HISTORICAL_COUNTEREXAMPLE_RECORD_GAP" in r["closure_blockers"]
    assert r["closure_admissible"] is False

def test_preclose_boundaries():
    r=p.build(ROOT)
    assert not r["authorization_created"] and not r["execution_performed"]
    assert not r["occ1h_closed"] and not r["occ1i_opened"]
    assert not r["p159_final_lock"] and not r["p160_opened"]

def test_preclose_missing_input_fails_closed(tmp_path):
    target=tmp_path/"repo"
    shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",
                    target/"validation_artifacts/p159/occ1h")
    (target/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json").unlink()
    r=p.build(target)
    assert r["closure_admissible"] is False
    assert r["status"]=="INCOMPLETE"

def test_preclose_deterministic():
    a=p.build(ROOT); b=p.build(ROOT)
    assert a==b
