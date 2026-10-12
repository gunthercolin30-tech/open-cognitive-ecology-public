from pathlib import Path
import json, shutil
from ontology import occ1h_historical_results_immutability as h
ROOT=Path(__file__).resolve().parents[1]
def _repo(tmp_path):
    target=tmp_path/"repo"; shutil.copytree(ROOT/"validation_artifacts/p159/occ1h",target/"validation_artifacts/p159/occ1h"); return target
def test_real_history_verified_and_materialized():
    r=h.build(ROOT); assert r["verified"] is True and r["scenario_count"]==105; assert h.verify_materialized(ROOT) is True
    assert not r["authorization_created"] and not r["execution_performed"]; assert not r["occ1h_closed"] and not r["occ1i_opened"]; assert not r["p159_final_lock"] and not r["p160_opened"]
def test_bitflip_fails_closed(tmp_path):
    root=_repo(tmp_path); p=root/"validation_artifacts/p159/occ1h/h4_execution_bundle_v1.json"; p.write_bytes(p.read_bytes()+b" "); r=h.build(root)
    assert not r["verified"] and any(x.startswith("HASH_DRIFT:") for x in r["errors"])
def test_removal_fails_closed(tmp_path):
    root=_repo(tmp_path); (root/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json").unlink(); r=h.build(root)
    assert not r["verified"] and any(x.startswith("MISSING:") for x in r["errors"])
def test_historical_verdict_rewrite_fails_closed(tmp_path):
    root=_repo(tmp_path); p=root/"validation_artifacts/p159/occ1h/h6_execution_bundle_v1.json"; d=json.loads(p.read_text()); d["rows"][0]["verdict"]="RESISTED"; p.write_text(json.dumps(d,sort_keys=True),encoding="utf-8"); assert h.build(root)["verified"] is False
def test_old_inconclusive_cannot_disappear(tmp_path):
    root=_repo(tmp_path); p=root/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json"; d=json.loads(p.read_text()); d["rows"]=[x for x in d["rows"] if x["attack_id"]!="A095"]; p.write_text(json.dumps(d,sort_keys=True),encoding="utf-8"); assert h.build(root)["verified"] is False
def test_bundle_substitution_fails_closed(tmp_path):
    root=_repo(tmp_path); a=root/"validation_artifacts/p159/occ1h/h4_execution_bundle_v1.json"; b=root/"validation_artifacts/p159/occ1h/h5_execution_bundle_v1.json"; a.write_bytes(b.read_bytes()); assert h.build(root)["verified"] is False
def test_materialized_evidence_tamper_detected(tmp_path):
    root=_repo(tmp_path); h.materialize(root); p=root/"validation_artifacts/p159/occ1h/historical_results_immutability_v1.json"; p.write_bytes(p.read_bytes()+b" "); assert h.verify_materialized(root) is False
