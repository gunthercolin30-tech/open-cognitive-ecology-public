from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a071/a071_rrp21_remaining_common_tcb_coverage_v2.json"
def d(): return json.loads(P.read_text())
def test_parser_diversity(): assert d()["experiments"]["python_json_parser"]["divergence_detected"] is True
def test_sha_diversity(): assert d()["experiments"]["python_hashlib_sha256"]["divergence_detected"] is True
def test_builder_diversity(): assert d()["experiments"]["occ_normative_ir_real_builder"]["divergence_detected"] is True
def test_coverage_and_boundaries():
 x=d(); assert x["coverage"]["all_disclosed_common_tcb_components_have_bounded_experiment"] is True; assert x["RRP22"]["status"]=="INDEPENDENT_REQUALIFICATION_REQUIRED"; assert x["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
