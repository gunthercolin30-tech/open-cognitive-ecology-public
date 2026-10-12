from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a078/a078_rrp9_12_final_disposition_v1.json"
def d(): return json.loads(P.read_text())
def test_disposition(): assert d()["RRP12"]["final_disposition"]=="ROOT + RESOLVED_EMPIRICALLY" and d()["RRP12"]["scenario_verdict"]=="RESISTED"
def test_materiality(): assert d()["RRP9"]["root_materiality"]=="ROOT" and d()["RRP9"]["applicable_root_invariants"]==["DNA.L0.3","DNA.L0.5"]
def test_elimination(): assert d()["RRP10"]["historical_inconclusive_eliminated"] is True and d()["RRP11"]["closure_eligible"] is True
def test_boundaries(): assert d()["boundaries"]=={"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
