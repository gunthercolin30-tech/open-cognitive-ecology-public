from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/"validation_artifacts/p159/occ1h/a070/a070_rrp9_12_final_disposition_v1.json"
def d():return json.loads(P.read_text())
def test_strict_probe():
 x=d()["post_rrpf_strict_json_probe"];assert x["both_accept"] and x["semantic_divergence"];assert x["input"]=='{"n":1e400}'
def test_root_materiality():
 x=d();assert x["RRP9"]["ROOT_MATERIALITY_STATUS"]=="ROOT";assert x["RRP9"]["ROOT_INVARIANTS"]==["DNA.L0.3","DNA.L0.5"];assert "same syntactically valid governed JSON input" in x["RRP9"]["ROOT_CAUSAL_PATH"]
def test_final_disposition():
 x=d();assert x["RRP10"]["REMAINING_BLOCKER"] is None;assert x["RRP12"]["FINAL_DISPOSITION"]=="ROOT + RESOLVED_EMPIRICALLY";assert x["RRP12"]["scenario_verdict"]=="RESISTED";assert x["RRP12"]["criticality_changed"] is False
def test_boundaries():
 assert d()["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
