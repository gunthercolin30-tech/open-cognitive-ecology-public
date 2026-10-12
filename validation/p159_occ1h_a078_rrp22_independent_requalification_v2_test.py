from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a078/a078_rrp22_independent_requalification_v2.json"
def d(): return json.loads(P.read_text())
def test_status(): assert d()["RRP22"]["status"]=="PASSED_BOUNDED"
def test_stale(): assert d()["independent_experiment"]["stale_case"]["decision"]=="REJECT_STALE_REPORT" and d()["independent_experiment"]["stale_case"]["stored_report_still_valid"] is True
def test_return(): assert d()["RRP22"]["return_to_rrp9_12_required"] is True and d()["RRP22"]["candidate_verdict"]=="RESISTED"
def test_boundaries(): assert d()["boundaries"]=={"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
