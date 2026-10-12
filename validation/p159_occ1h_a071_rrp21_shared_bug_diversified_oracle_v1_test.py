from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a071/a071_rrp21_shared_bug_diversified_oracle_v1.json"
def d(): return json.loads(P.read_text())
def test_shared_helper_defect_detected():
 x=d()["experiments"]["shared_canonical_sha256_helper_defect"]; assert x["two_dependent_paths_agree_on_defective_value"] is True; assert x["diversified_oracle_detects_divergence"] is True
def test_control_agrees():
 assert d()["experiments"]["unmodified_control"]["all_paths_agree"] is True
def test_scope_is_bounded():
 x=d(); assert x["RRP21"]["status"]=="COMPLETE_BOUNDED"; assert x["RRP22"]["status"]=="INDEPENDENT_REQUALIFICATION_REQUIRED"; assert x["epistemic_limits"]["does_not_establish_resistance_to_every_common_tcb_component"] is True
def test_boundaries():
 assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
