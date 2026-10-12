from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a071/a071_rrp9_12_final_disposition_v2.json"
def d(): return json.loads(P.read_text())
def test_root_materiality(): assert d()["RRP9"]["root_materiality"]=="ROOT" and d()["RRP9"]["causal_path_complete"] is True
def test_inconclusive_eliminated(): assert d()["RRP10"]["historical_inconclusive_eliminated"] is True
def test_final_disposition(): assert d()["RRP12"]["final_disposition"]=="ROOT + RESOLVED_EMPIRICALLY" and d()["RRP12"]["scenario_verdict"]=="RESISTED"
def test_boundaries(): assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
