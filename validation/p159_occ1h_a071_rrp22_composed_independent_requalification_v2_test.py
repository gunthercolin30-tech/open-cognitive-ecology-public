from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a071/a071_rrp22_composed_independent_requalification_v2.json"
def d(): return json.loads(P.read_text())
def test_four_components(): assert set(d()["independent_requalification"]["component_results"])=={"python_json_parser","python_hashlib_sha256","ontology.occ_normative_ir.canonical_sha256","ontology.occ_normative_ir_real_builder"}
def test_composed_result(): assert d()["RRP22"]["status"]=="PASSED_COMPOSED_BOUNDED" and d()["RRP22"]["return_to_rrp9_12_required"] is True
def test_no_overclaim(): assert d()["epistemic_limits"]["no_claim_of_absence_of_all_possible_shared_bugs"] is True
def test_boundaries(): assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
