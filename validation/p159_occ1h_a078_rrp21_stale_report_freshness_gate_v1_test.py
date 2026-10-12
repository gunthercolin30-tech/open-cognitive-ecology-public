from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a078/a078_rrp21_stale_report_freshness_gate_v1.json"
def d(): return json.loads(P.read_text())
def test_control(): assert d()["experiment"]["baseline"]["accepted"] is True
def test_stale_rejected(): assert d()["experiment"]["stale_case"]["stored_report_still_says_valid"] is True and d()["experiment"]["stale_case"]["fresh_verification_rejected"] is True and d()["experiment"]["stale_case"]["consumer_decision"]=="REJECT_STALE_REPORT"
def test_degradation(): assert d()["experiment"]["stale_case"]["source_drift_detected"] is True and d()["RRP21"]["candidate_verdict"]=="RESISTED_BOUNDED"
def test_boundaries(): assert d()["boundaries"]=={"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
