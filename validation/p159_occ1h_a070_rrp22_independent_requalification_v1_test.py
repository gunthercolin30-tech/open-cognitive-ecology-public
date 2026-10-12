from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/"validation_artifacts/p159/occ1h/a070/a070_rrp22_independent_requalification_v1.json"
def d():return json.loads(P.read_text())
def test_passed_and_return():
 x=d();assert x["RRP22"]["status"]=="PASSED";assert x["RRP22"]["candidate_verdict"]=="RESISTED";assert x["RRP22"]["return_to_rrp9_12_required"] is True
def test_reproductions():
 r=d()["RRP22"]["reproductions"];assert r["ordinary"]["verdict"]=="ADMISSIBLE_CONTROL";assert r["nested"]["verdict"]=="ADMISSIBLE_CONTROL";assert r["nonfinite"]["verdict"]=="RESISTED";assert r["invalid"]["verdict"]=="INVALID_INPUT_CONTROL"
def test_epistemic_limit():
 e=d()["epistemic_limits"];assert e["strict_valid_json_root_counterexample_not_established_by_nonfinite_fixture_alone"] is True;assert e["does_not_prove_absence_of_all_shared_tcb"] is True
def test_boundaries():
 assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
