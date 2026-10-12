from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a071/a071_rrp22_independent_requalification_v1.json"
def d(): return json.loads(P.read_text())
def test_independent_reproduction():
 x=d(); assert x["RRP22"]["status"]=="PASSED_BOUNDED"; assert x["independent_experiment"]["shared_defect_detected"] is True
def test_no_overclaim():
 x=d(); assert x["RRP22"]["a071_fully_resolved"] is False; assert x["RRP22"]["return_to_rrp9_12_required"] is False
def test_remaining_blocker():
 x=d(); assert len(x["remaining_common_tcb_components_not_independently_exercised"])>=1; assert x["final_disposition_candidate"]=="ROOT_UNDETERMINED + BLOCKING"
def test_boundaries():
 assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
